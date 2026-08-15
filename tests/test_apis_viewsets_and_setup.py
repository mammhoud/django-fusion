"""Tests for ``FusionApiViewset`` and ``FusionSetupRedirectMiddleware``.

Covers:

- Settings-driven viewset resolution + ``mount_api_viewsets`` URL patterns.
- Declarative viewset CRUD against a real model (``auth.Group``) with
  tenant scoping disabled.
- ``FusionSetupRedirectMiddleware`` app-name resolution, predicate
  evaluation, redirect + loop-guard + exclude handling.

Run with::

    cd libs/django-fusion && uv run pytest tests/test_apis_viewsets_and_setup.py -v
"""

from __future__ import annotations

import itertools
import json
from types import SimpleNamespace
from typing import Any

import pytest
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from django.test import RequestFactory, override_settings
from django_fusion.core.middlewares.setup import FusionSetupRedirectMiddleware
from django_fusion.plugins.apis.viewsets import (
    FusionApiViewset,
    get_api_viewset,
    mount_api_viewsets,
    register_api_viewset,
)

pytestmark = pytest.mark.django_db(transaction=True)

_counter = itertools.count()


def _uid(name: str) -> str:
    return f"{name}_{next(_counter)}"


# ---------------------------------------------------------------------------
# Viewset: settings-driven model config + mount
# ---------------------------------------------------------------------------


class TestViewsetRegistry:
    def test_mount_registered_programmatic(self) -> None:
        slug = _uid("groups")
        viewset = type("GroupApiViewset", (FusionApiViewset,), {
            "model": Group,
            "read_fields": ("id", "name"),
            "write_fields": ("name",),
            "required_fields": ("name",),
            "tenant_field": None,
        })
        register_api_viewset(slug, viewset)
        patterns = mount_api_viewsets(prefix="api/")
        names = {p.name for p in patterns if slug in (p.name or "")}
        assert f"fusion_api_{slug}_list" in names
        assert f"fusion_api_{slug}_detail" in names

    @override_settings(FUSION_API_VIEWSETS={
        "settings_groups": {
            "model": "auth.Group",
            "read_fields": ["id", "name"],
            "write_fields": ["name"],
            "required_fields": ["name"],
        }
    })
    def test_settings_driven_resolution(self) -> None:
        viewset = get_api_viewset("settings_groups")
        assert viewset is not None
        assert viewset.model is Group
        assert viewset.read_fields == ("id", "name")
        assert viewset.tenant_field == "workspace_id"  # default retained


class TestViewsetCrud:
    def test_crud_round_trip(self, rf: RequestFactory) -> None:
        viewset = type("GroupApiViewset", (FusionApiViewset,), {
            "model": Group,
            "read_fields": ("id", "name"),
            "write_fields": ("name",),
            "required_fields": ("name",),
            "tenant_field": None,
            "fusion_render_first": False,
        })()

        create = viewset.post(
            rf.post("/", data='{"name": "ops"}', content_type="application/json")
        )
        assert create.status_code == 201
        group_id = Group.objects.get(name="ops").id

        listing = viewset.get(rf.get("/"))
        assert listing.status_code == 200
        payload = json.loads(listing.content)
        rows = payload["data"]["data"]["results"]
        assert any(row["name"] == "ops" for row in rows)

        patch = viewset.patch(
            rf.patch(f"/{group_id}/", data='{"name": "revops"}', content_type="application/json"),
            pk=group_id,
        )
        assert patch.status_code == 200
        assert Group.objects.get(id=group_id).name == "revops"

        delete = viewset.delete(rf.delete(f"/{group_id}/"), pk=group_id)
        assert delete.status_code == 200
        assert not Group.objects.filter(id=group_id).exists()

    def test_create_requires_fields(self, rf: RequestFactory) -> None:
        viewset = type("GroupApiViewset", (FusionApiViewset,), {
            "model": Group,
            "read_fields": ("id", "name"),
            "write_fields": ("name",),
            "required_fields": ("name",),
            "tenant_field": None,
            "fusion_render_first": False,
        })()
        response = viewset.post(
            rf.post("/", data="{}", content_type="application/json")
        )
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Setup redirect middleware
# ---------------------------------------------------------------------------


def _resolver(app_name: str | None, viewset_app: str | None = None) -> Any:
    url_name = SimpleNamespace(extra={})
    if viewset_app:
        url_name.extra["app"] = SimpleNamespace(app_name=viewset_app)
    return SimpleNamespace(url_name=url_name, app_name=app_name, namespace=None)


class TestSetupRedirectMiddleware:
    def _mw(self) -> FusionSetupRedirectMiddleware:
        return FusionSetupRedirectMiddleware(lambda r: HttpResponse("OK"))

    def test_resolve_app_name_from_extra(self) -> None:
        request = SimpleNamespace(resolver_match=_resolver(None, viewset_app="loop_crm"))
        assert self._mw().resolve_app_name(request) == "loop_crm"

    def test_resolve_app_name_fallback(self) -> None:
        request = SimpleNamespace(resolver_match=_resolver("loop_crm"))
        assert self._mw().resolve_app_name(request) == "loop_crm"

    def test_evaluate_predicate_forms(self) -> None:
        mw = self._mw()
        assert mw.evaluate_predicate(lambda r: True, None) is True
        assert mw.evaluate_predicate(False, None) is False
        assert mw.evaluate_predicate(None, None) is False

    @override_settings(FUSION_SETUP_REDIRECTS={
        "loop_crm": {"predicate": True, "url": "/setup/"}
    })
    def test_redirect_when_unconfigured(self) -> None:
        request = SimpleNamespace(
            resolver_match=_resolver(None, viewset_app="loop_crm"),
            path="/crm/",
        )
        result = self._mw().process_view(request, lambda r: None, [], {})
        assert isinstance(result, HttpResponseRedirect)
        assert result["Location"] == "/setup/"

    @override_settings(FUSION_SETUP_REDIRECTS={
        "loop_crm": {"predicate": True, "url": "/setup/"}
    })
    def test_loop_guard_no_redirect_on_setup_url(self) -> None:
        request = SimpleNamespace(
            resolver_match=_resolver(None, viewset_app="loop_crm"),
            path="/setup/",
        )
        assert self._mw().process_view(request, lambda r: None, [], {}) is None

    @override_settings(FUSION_SETUP_REDIRECTS={
        "loop_crm": {"predicate": True, "url": "/setup/", "exclude": ["/api/"]}
    })
    def test_excluded_path_not_redirected(self) -> None:
        request = SimpleNamespace(
            resolver_match=_resolver(None, viewset_app="loop_crm"),
            path="/api/v1/companies/",
        )
        assert self._mw().process_view(request, lambda r: None, [], {}) is None
