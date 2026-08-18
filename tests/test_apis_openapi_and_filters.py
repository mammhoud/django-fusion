"""Tests for ``FusionApiViewset`` query surfaces and the OpenAPI builder.

Covers the declarative query-parameter filtering, search, ordering and
pagination added to the ``apis`` plugin, plus the Django-native OpenAPI 3.1
builder/views that mirror django-bolt's ``/docs`` + ``/docs/openapi.json``
contract.

Run with::

    cd libs/django-fusion && uv run pytest tests/test_apis_openapi_and_filters.py -v
"""

from __future__ import annotations

import json

import pytest
from django.contrib.auth.models import Group
from django.test import RequestFactory, override_settings

from django_fusion.plugins.apis.openapi import OpenAPISpec, openapi_docs, openapi_json
from django_fusion.plugins.apis.viewsets import FusionApiViewset

pytestmark = pytest.mark.django_db(transaction=True)


def _group_viewset(**extra):
    attrs = {
        "model": Group,
        "read_fields": ("id", "name"),
        "write_fields": ("name",),
        "required_fields": ("name",),
        "tenant_field": None,
        "fusion_render_first": False,
    }
    attrs.update(extra)
    return type("GroupApiViewset", (FusionApiViewset,), attrs)()


def _list_names(response) -> list[str]:
    payload = json.loads(response.content)
    return [row["name"] for row in payload["data"]["data"]["results"]]


# ---------------------------------------------------------------------------
# Viewset filtering / search / ordering / pagination
# ---------------------------------------------------------------------------


class TestViewsetQuerySurface:
    def test_filter_fields_exact_match(self, rf: RequestFactory) -> None:
        Group.objects.create(name="alpha")
        Group.objects.create(name="beta")
        viewset = _group_viewset(filter_fields=("name",))

        response = viewset.get(rf.get("/", {"name": "alpha"}))
        assert response.status_code == 200
        assert _list_names(response) == ["alpha"]

    def test_filter_ignores_undeclared_fields(self, rf: RequestFactory) -> None:
        Group.objects.create(name="alpha")
        viewset = _group_viewset()  # no filter_fields

        response = viewset.get(rf.get("/", {"name": "nope"}))
        assert response.status_code == 200
        # Unlisted param must be ignored, not raise FieldError.
        assert len(_list_names(response)) == 1

    def test_search_across_fields(self, rf: RequestFactory) -> None:
        Group.objects.create(name="cardiology")
        Group.objects.create(name="oncology")
        Group.objects.create(name="radiology")
        viewset = _group_viewset(search_fields=("name",))

        response = viewset.get(rf.get("/", {"q": "ology"}))
        assert _list_names(response) == ["cardiology", "oncology", "radiology"]

    def test_ordering_allowlist(self, rf: RequestFactory) -> None:
        Group.objects.create(name="bravo")
        Group.objects.create(name="alpha")
        Group.objects.create(name="charlie")
        viewset = _group_viewset(ordering_fields=("name",))

        asc = viewset.get(rf.get("/", {"ordering": "name"}))
        assert _list_names(asc) == ["alpha", "bravo", "charlie"]

        desc = viewset.get(rf.get("/", {"ordering": "-name"}))
        assert _list_names(desc) == ["charlie", "bravo", "alpha"]

    def test_pagination_metadata(self, rf: RequestFactory) -> None:
        for index in range(25):
            Group.objects.create(name=f"group-{index:02d}")
        viewset = _group_viewset(ordering_fields=("name",), page_size=10)

        response = viewset.get(rf.get("/", {"ordering": "name", "limit": 10, "page": 2}))
        payload = json.loads(response.content)
        data = payload["data"]["data"]

        assert data["total"] == 25
        assert data["count"] == 10
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["results"][0]["name"] == "group-10"

    def test_offset_style_pagination(self, rf: RequestFactory) -> None:
        for index in range(5):
            Group.objects.create(name=f"group-{index}")
        viewset = _group_viewset(ordering_fields=("name",), page_size=2)

        response = viewset.get(rf.get("/", {"ordering": "name", "limit": 2, "offset": 2}))
        payload = json.loads(response.content)
        data = payload["data"]["data"]
        assert [row["name"] for row in data["results"]] == ["group-2", "group-3"]
        assert data["page"] == 2


# ---------------------------------------------------------------------------
# OpenAPI builder + views
# ---------------------------------------------------------------------------


class TestOpenAPISpec:
    def test_minimal_document_shape(self) -> None:
        spec = OpenAPISpec(title="Test API", version="2.1.0", description="Doc")
        document = spec.as_dict()

        assert document["openapi"] == "3.1.0"
        assert document["info"] == {
            "title": "Test API",
            "version": "2.1.0",
            "description": "Doc",
        }
        assert document["paths"] == {}

    def test_add_path_with_summary_tags_params_responses(self) -> None:
        spec = OpenAPISpec(title="Test API")
        spec.add_tag("research", "Research resources")
        spec.add_path(
            "/apis/research/publications/",
            "get",
            summary="List publications",
            description="Returns localized publications.",
            tags=["research"],
            params=[{"name": "lang", "in": "query", "schema": {"type": "string"}}],
            responses={
                200: OpenAPISpec.json_response("OK", {"type": "object"}),
                404: OpenAPISpec.json_response("Not found"),
            },
            operation_id="listPublications",
        )
        document = spec.as_dict()

        operation = document["paths"]["/apis/research/publications/"]["get"]
        assert operation["summary"] == "List publications"
        assert operation["tags"] == ["research"]
        assert operation["operationId"] == "listPublications"
        assert operation["parameters"][0]["name"] == "lang"
        assert operation["responses"]["200"]["content"]["application/json"]["schema"] == {
            "type": "object"
        }
        assert "content" not in operation["responses"]["404"]
        assert document["tags"] == [{"name": "research", "description": "Research resources"}]

    def test_components_and_ref(self) -> None:
        spec = OpenAPISpec(title="Test API")
        spec.add_component_schema("Publication", {"type": "object", "properties": {"id": {"type": "integer"}}})
        ref = OpenAPISpec.ref("Publication")

        assert ref == {"$ref": "#/components/schemas/Publication"}
        assert spec.as_dict()["components"]["schemas"]["Publication"]["properties"]["id"]["type"] == "integer"

    def test_as_json_round_trip(self) -> None:
        spec = OpenAPISpec(title="Test API")
        spec.add_path("/x", "get", responses={200: OpenAPISpec.json_response("OK")})
        parsed = json.loads(spec.as_json())
        assert parsed["paths"]["/x"]["get"]["responses"]["200"]["description"] == "OK"


class TestOpenAPIViews:
    @override_settings(ROOT_URLCONF="tests.urls")
    def test_openapi_json_view(self, rf: RequestFactory) -> None:
        spec = OpenAPISpec(title="View API")
        spec.add_path("/x", "get", responses={200: OpenAPISpec.json_response("OK")})

        response = openapi_json(rf.get("/openapi.json"), spec=spec)
        assert response.status_code == 200
        assert response["Content-Type"].startswith("application/json")
        assert json.loads(response.content)["info"]["title"] == "View API"
        assert "no-cache" in response["Cache-Control"]  # never_cache applied

    def test_openapi_json_view_accepts_callable(self, rf: RequestFactory) -> None:
        spec = OpenAPISpec(title="Callable API")
        response = openapi_json(rf.get("/openapi.json"), spec=lambda: spec)
        assert json.loads(response.content)["info"]["title"] == "Callable API"

    def test_openapi_json_view_missing_spec(self, rf: RequestFactory) -> None:
        response = openapi_json(rf.get("/openapi.json"), spec=None)
        assert response.status_code == 404

    def test_openapi_docs_view(self, rf: RequestFactory) -> None:
        spec = OpenAPISpec(title="Docs API")
        response = openapi_docs(rf.get("/docs/"), spec=spec)
        assert response.status_code == 200
        assert "Docs API" in response.content.decode()
        assert "swagger-ui" in response.content.decode()

    def test_openapi_docs_spec_url_kwarg(self, rf: RequestFactory) -> None:
        spec = OpenAPISpec(title="Docs API")
        response = openapi_docs(rf.get("/docs/"), spec=spec, spec_url="/apis/openapi.json")
        html = response.content.decode()
        assert "url: \"/apis/openapi.json\"" in html

    def test_openapi_docs_spec_url_query_override(self, rf: RequestFactory) -> None:
        spec = OpenAPISpec(title="Docs API")
        response = openapi_docs(rf.get("/docs/?spec_url=/custom.json"), spec=spec, spec_url="/apis/openapi.json")
        html = response.content.decode()
        assert "url: \"/custom.json\"" in html
