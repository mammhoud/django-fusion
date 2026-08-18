"""Tests for the FUSION_RENDER_FIRST → FUSION_RENDER_MODE rename + mixed mode."""

from django.test import override_settings, RequestFactory
import pytest

from django_fusion.config.conf import (
    coerce_render_mode,
    resolve_render_mode_setting,
    resolve_render_first_setting,
)
from django_fusion.routes.rendering.render_mode import (
    header_render_mode,
    negotiate_mixed,
    resolve_render_mode,
    route_render_mode,
    session_render_mode,
)


@pytest.fixture
def rf():
    return RequestFactory()


class TestCoerceRenderMode:
    def test_booleans(self):
        assert coerce_render_mode(True) == "render"
        assert coerce_render_mode(False) == "data"

    def test_strings(self):
        assert coerce_render_mode("render") == "render"
        assert coerce_render_mode("DATA") == "data"
        assert coerce_render_mode("mixed") == "mixed"

    def test_booleanish_strings(self):
        assert coerce_render_mode("true") == "render"
        assert coerce_render_mode("1") == "render"
        assert coerce_render_mode("off") == "data"

    def test_invalid(self):
        assert coerce_render_mode("nonsense") is None
        assert coerce_render_mode(None) is None


class TestResolveRenderModeSetting:
    def test_canonical_string(self):
        with override_settings(FUSION_RENDER_MODE="mixed"):
            assert resolve_render_mode_setting() == "mixed"

    def test_legacy_bool_fallback(self):
        with override_settings(FUSION_RENDER_FIRST=True):
            assert resolve_render_mode_setting() == "render"

    def test_legacy_verbose_name(self):
        with override_settings(FUSION_RENDER_FIRST_DEFAULT=False):
            assert resolve_render_mode_setting() == "data"

    def test_default(self):
        with override_settings():
            assert resolve_render_mode_setting(default="render") == "render"

    def test_first_setting_stays_bool(self):
        with override_settings(FUSION_RENDER_MODE="mixed"):
            assert resolve_render_first_setting() is True


class TestHeaderAndSessionMode:
    def test_header_mode(self, rf):
        request = rf.get("/", HTTP_X_FUSION_RENDER_MODE="mixed")
        assert header_render_mode(request) == "mixed"

    def test_header_mode_invalid(self, rf):
        assert header_render_mode(rf.get("/", HTTP_X_FUSION_RENDER_MODE="wat")) is None

    def test_session_mode(self, rf):
        request = rf.get("/")
        request.session = {"fusion_render_mode": "data"}
        assert session_render_mode(request) == "data"


class TestRouteOverride:
    def test_longest_prefix_wins(self, rf):
        with override_settings(
            FUSION_RENDER_MODE_ROUTES={"/": "render", "/courses/": "mixed", "/courses/deep/": "data"}
        ):
            request = rf.get("/courses/deep/lesson/")
            assert route_render_mode(request) == "data"

    def test_no_match(self, rf):
        with override_settings(FUSION_RENDER_MODE_ROUTES={"/courses/": "mixed"}):
            assert route_render_mode(rf.get("/blog/")) is None

    def test_missing_setting(self, rf):
        with override_settings():
            assert route_render_mode(rf.get("/anything/")) is None


class TestNegotiateMixed:
    def test_json_client_gets_data(self, rf):
        request = rf.get("/", HTTP_ACCEPT="application/json")
        assert negotiate_mixed("mixed", request) == "data"

    def test_browser_gets_render(self, rf):
        assert negotiate_mixed("mixed", rf.get("/", HTTP_ACCEPT="text/html")) == "render"

    def test_non_mixed_unchanged(self, rf):
        assert negotiate_mixed("render", rf.get("/")) == "render"
        assert negotiate_mixed("data", rf.get("/", HTTP_ACCEPT="application/json")) == "data"


class TestResolveRenderMode:
    def test_force_flags(self, rf):
        assert resolve_render_mode(rf.get("/"), force_render_first=True) == "render"
        assert resolve_render_mode(rf.get("/"), force_data_mode=True) == "data"

    def test_header_wins_over_setting(self, rf):
        with override_settings(FUSION_RENDER_MODE="data"):
            request = rf.get("/", HTTP_X_FUSION_RENDER_MODE="render")
            assert resolve_render_mode(request) == "render"

    def test_mixed_negotiates(self, rf):
        with override_settings(FUSION_RENDER_MODE="mixed"):
            assert resolve_render_mode(rf.get("/", HTTP_ACCEPT="application/json")) == "data"
            assert resolve_render_mode(rf.get("/", HTTP_ACCEPT="text/html")) == "render"

    def test_mixed_without_negotiation(self, rf):
        with override_settings(FUSION_RENDER_MODE="mixed"):
            assert resolve_render_mode(rf.get("/"), negotiate=False) == "mixed"

    def test_route_override(self, rf):
        with override_settings(FUSION_RENDER_MODE_ROUTES={"/courses/": "mixed"}):
            assert resolve_render_mode(rf.get("/courses/x/", HTTP_ACCEPT="application/json")) == "data"
