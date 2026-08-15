"""Tests for the function-view dual-mode decorator
(``django_fusion.routes.rendering.decorators``).

Covers ``fusion_view``:
  * data-API road — codec-encoded JSON payload shape (encoded/data/view_name).
  * render-first road — HTML from the template with ``data`` in context.
  * header override switches roads on the same view.
  * ``force_data_mode`` hard override.
  * no-template fallback (JSON with rendered=False).
  * plain dict data passthrough; HttpResponse passthrough.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.test import RequestFactory, override_settings
from django_fusion.routes.rendering.decorators import fusion_view
from django_fusion.routes.rendering.session import FusionCodec


@pytest.fixture
def rf() -> RequestFactory:
    """Django RequestFactory — pytest-django's ``rf`` is unavailable when
    Django is configured via ``settings.configure()``."""
    return RequestFactory()


# Template dir for the render-first road tests (see test_component_tag.py
# for the same pattern).
_TEST_TEMPLATES = str(
    Path(__file__).resolve().parent / "test_rendering_decorators" / "templates"
)


@pytest.fixture
def fusion_templates():
    """Provide a TEMPLATES config that resolves the local test templates."""
    from django.conf import settings as dj_settings

    templates = list(dj_settings.TEMPLATES)
    templates[0]["DIRS"] = templates[0].get("DIRS", []) + [_TEST_TEMPLATES]
    with override_settings(TEMPLATES=templates):
        yield


def _sample_view(request, **kwargs):
    return {"products": ["Latte", "Croissant"], "total": 2}


def _decorated(**opts):
    return fusion_view(**opts)(_sample_view)


class TestDataApiRoad:
    def test_defaults_to_data_api_when_setting_false(self, rf):
        with override_settings(FUSION_RENDER_FIRST=False):
            resp = _decorated()(rf.get("/products/"))
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("application/json")
        body = json.loads(resp.content)
        assert body["status"] == 200
        data = body["data"]
        assert data["view_name"] == "_sample_view"
        assert FusionCodec.decode(data["encoded"]) == {
            "products": ["Latte", "Croissant"], "total": 2,
        }

    def test_data_api_via_header(self, rf):
        with override_settings(FUSION_RENDER_FIRST=True):  # setting says render-first
            request = rf.get("/products/", HTTP_X_FUSION_RENDER_FIRST="false")
            resp = _decorated(template_name="products/list.html")(request)
        assert resp["Content-Type"].startswith("application/json")
        body = json.loads(resp.content)
        assert FusionCodec.decode(body["data"]["encoded"])["total"] == 2

    def test_force_data_mode(self, rf):
        with override_settings(FUSION_RENDER_FIRST=True):
            resp = _decorated(template_name="products/list.html",
                              force_data_mode=True)(rf.get("/products/"))
        body = json.loads(resp.content)
        assert body["data"]["view_name"] == "_sample_view"


class TestRenderFirstRoad:
    def test_renders_template_with_data(self, rf, fusion_templates):
        with override_settings(FUSION_RENDER_FIRST=True):
            resp = _decorated(
                template_name="products/list.html"
            )(rf.get("/products/"))
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/html")
        html = resp.content.decode()
        assert "Latte" in html
        assert 'data-mode="True"' in html

    def test_render_first_via_header(self, rf, fusion_templates):
        with override_settings(FUSION_RENDER_FIRST=False):
            request = rf.get("/products/", HTTP_X_FUSION_RENDER_FIRST="true")
            resp = _decorated(template_name="products/list.html")(request)
        assert resp["Content-Type"].startswith("text/html")

    def test_no_template_falls_back_to_json(self, rf):
        with override_settings(FUSION_RENDER_FIRST=True):
            resp = _decorated()(rf.get("/products/"))
        body = json.loads(resp.content)
        assert body["data"]["rendered"] is False
        assert body["data"]["reason"] == "no-template"


class TestPassthrough:
    def test_http_response_passthrough(self, rf):
        from django.http import HttpResponseRedirect

        def redirect_view(request):
            return HttpResponseRedirect("/elsewhere/")

        with override_settings(FUSION_RENDER_FIRST=True):
            resp = fusion_view(template_name="x.html")(redirect_view)(rf.get("/"))
        assert resp.status_code == 302
        assert resp["Location"] == "/elsewhere/"

    def test_context_processors_merge(self, rf, fusion_templates):
        def extra(request):
            return {"site_name": "Formint"}

        with override_settings(FUSION_RENDER_FIRST=True):
            resp = _decorated(template_name="products/list.html",
                              context_processors=[extra])(rf.get("/"))
        assert "Formint" in resp.content.decode()
