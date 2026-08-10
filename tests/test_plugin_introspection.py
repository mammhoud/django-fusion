"""Tests for the fusion plugin catalog, recommender, tracker and introspection views."""

from __future__ import annotations

import pytest
from django.test import Client

from django_fusion.plugins import PluginRegistry, plugins
from django_fusion.plugins.catalog import CORE_PLUGINS, PLUGIN_CATALOG


@pytest.fixture
def client() -> Client:
    """Django test Client — provided here because pytest-django's
    ``client`` fixture is unavailable when Django is configured via
    ``settings.configure()`` rather than ``DJANGO_SETTINGS_MODULE``."""
    return Client()


class TestPluginCatalog:
    def test_core_plugins_are_catalogued_and_registered(self):
        for name in CORE_PLUGINS:
            spec = plugins.get(name)
            assert spec is not None, f"{name} should be catalogued"
            assert spec.core is True
            assert plugins.is_registered(name), f"{name} should be registered with pluggy"

    def test_catalog_contains_utility_plugin_packages(self):
        names = {spec.name for spec in plugins.catalog()}
        for expected in (
            "django_fusion.plugins.htmx",
            "django_fusion.plugins.unpoly",
            "django_fusion.plugins.apis",
            "django_fusion.plugins.webpack",
            "django_fusion.plugins.debug_tools",
            "django_fusion.plugins.robyn",
        ):
            assert expected in names

    def test_catalog_dict_matches_registry(self):
        assert set(PLUGIN_CATALOG) == {spec.name for spec in plugins.catalog()}


class TestRecommendations:
    def test_recommend_htmx_capability(self):
        specs = plugins.recommend("htmx")
        assert any(s.name == "django_fusion.plugins.htmx" for s in specs)

    def test_recommend_api_capability(self):
        specs = plugins.recommend("api")
        assert any(s.name == "django_fusion.plugins.apis" for s in specs)

    def test_recommend_unknown_capability_is_empty(self):
        assert plugins.recommend("no-such-capability") == []

    def test_capabilities_are_complete(self):
        caps = plugins.capabilities()
        assert {"htmx", "fragments", "sse", "webpack", "introspection"} <= caps


class TestRequestDetection:
    def test_detect_htmx_header(self):
        request = _make_request(headers={"HX-Request": "true"})
        result = plugins.detect(request)
        assert "htmx-request" in result["signals"]
        assert "django_fusion.plugins.htmx" in result["matched"]

    def test_detect_fragment_target(self):
        request = _make_request(headers={"HX-Target": "course-list"})
        result = plugins.detect(request)
        assert "fragment-request" in result["signals"]

    def test_detect_sse_accept(self):
        request = _make_request(headers={"Accept": "text/event-stream"})
        result = plugins.detect(request)
        assert "sse" in result["signals"]

    def test_detect_unpoly_header(self):
        request = _make_request(headers={"X-Up-Target": "#main"})
        result = plugins.detect(request)
        assert "unpoly-request" in result["signals"]
        assert "django_fusion.plugins.unpoly" in result["matched"]

    def test_detect_api_path(self):
        request = _make_request(path="/apis/courses/")
        result = plugins.detect(request)
        assert "api-request" in result["signals"]

    def test_detect_plain_request(self):
        request = _make_request()
        result = plugins.detect(request)
        assert result["signals"] == []


class TestRegistrySummary:
    def test_summary_shape(self):
        summary = plugins.summary()
        assert summary["total"] == len(plugins.catalog())
        assert summary["registered"] >= len(CORE_PLUGINS)
        assert "capabilities" in summary
        plugin_payloads = summary["plugins"]
        assert all("available" in p and "registered" in p for p in plugin_payloads)

    def test_fresh_registry_isolated(self):
        fresh = PluginRegistry()
        assert fresh.summary()["total"] == len(PLUGIN_CATALOG)


class TestTracker:
    def test_record_and_history(self):
        from django_fusion.plugins.tracker import tracker

        tracker.record("auth_buttons", page_path="/login/")
        history = tracker.get_render_history(limit=5)
        assert any(
            event["name"] == "auth_buttons" and event["page_path"] == "/login/"
            for event in history
        )

    def test_stats_snapshot(self):
        from django_fusion.plugins.tracker import tracker

        stats = tracker.stats()
        assert stats["plugins"]["total"] == len(PLUGIN_CATALOG)
        assert "components" in stats
        assert "render_history" in stats
        assert "cache" in stats


class TestIntrospectionViews:
    def test_api_view_returns_json(self, client):
        response = client.get("/fusion/introspection/api/")
        assert response.status_code == 200
        payload = response.json()
        assert payload["plugins"]["total"] == len(PLUGIN_CATALOG)
        assert "detected" in payload
        assert "request" in payload

    def test_dashboard_view_renders(self, client):
        response = client.get("/fusion/introspection/")
        assert response.status_code == 200
        body = response.content.decode()
        assert "Fusion Introspection" in body
        assert "Plugin catalog" in body
        assert "Component usage" in body

    def test_dashboard_detects_htmx_probe(self, client):
        response = client.get(
            "/fusion/introspection/", headers={"HX-Request": "true"}
        )
        body = response.content.decode()
        assert "htmx-request" in body


def _make_request(path: str = "/", headers: dict | None = None):
    """Minimal request stand-in (headers + path) — no Django request needed."""
    class _Headers(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    request = type(
        "_Req",
        (),
        {"headers": _Headers(headers or {}), "path": path, "META": {}},
    )()
    return request
