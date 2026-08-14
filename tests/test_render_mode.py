"""Tests for the canonical render-mode resolver (django_fusion.routes.rendering.render_mode)."""

from __future__ import annotations

import pytest
from django.test import RequestFactory, override_settings
from django_fusion.routes.rendering.render_mode import (
    header_render_first,
    resolve_render_first,
    session_render_first,
)


@pytest.fixture
def rf() -> RequestFactory:
    """Django RequestFactory — provided directly because pytest-django's ``rf``
    fixture is unavailable when Django is configured via ``settings.configure()``."""
    return RequestFactory()


class TestHeaderRenderFirst:
    def test_none_request(self):
        assert header_render_first(None) is None

    def test_true_header(self, rf):
        request = rf.get("/", HTTP_X_FUSION_RENDER_FIRST="true")
        assert header_render_first(request) is True

    def test_false_header(self, rf):
        request = rf.get("/", HTTP_X_FUSION_RENDER_FIRST="false")
        assert header_render_first(request) is False

    def test_missing_header(self, rf):
        assert header_render_first(rf.get("/")) is None

    def test_malformed_header_is_ignored(self, rf):
        request = rf.get("/", HTTP_X_FUSION_RENDER_FIRST="yes")
        assert header_render_first(request) is None


class TestSessionRenderFirst:
    def test_none_request(self):
        assert session_render_first(None) is None

    def test_no_session_attribute(self, rf):
        assert session_render_first(rf.get("/")) is None

    def test_no_stored_value(self, rf):
        request = rf.get("/")
        request.session = {}
        assert session_render_first(request) is None

    def test_explicit_true(self, rf):
        request = rf.get("/")
        request.session = {"fusion_render_first": True}
        assert session_render_first(request) is True

    def test_explicit_false(self, rf):
        request = rf.get("/")
        request.session = {"fusion_render_first": False}
        assert session_render_first(request) is False


class TestResolveRenderFirst:
    def test_force_render_first_wins(self, rf):
        request = rf.get("/", HTTP_X_FUSION_RENDER_FIRST="false")
        assert resolve_render_first(request, force_render_first=True) is True

    def test_force_data_mode_wins(self, rf):
        request = rf.get("/", HTTP_X_FUSION_RENDER_FIRST="true")
        assert resolve_render_first(request, force_data_mode=True) is False

    def test_header_beats_session(self, rf):
        request = rf.get("/", HTTP_X_FUSION_RENDER_FIRST="true")
        request.session = {"fusion_render_first": False}
        assert resolve_render_first(request) is True

    def test_session_beats_default(self, rf):
        request = rf.get("/")
        request.session = {"fusion_render_first": False}
        assert resolve_render_first(request, default=True) is False

    def test_default_beats_setting(self, rf):
        with override_settings(FUSION_RENDER_FIRST=False):
            assert resolve_render_first(rf.get("/"), default=True) is True

    def test_setting_fallback(self, rf):
        with override_settings(FUSION_RENDER_FIRST=True):
            assert resolve_render_first(rf.get("/")) is True
        with override_settings(FUSION_RENDER_FIRST=False):
            assert resolve_render_first(rf.get("/")) is False

    def test_legacy_setting_name_fallback(self, rf):
        with override_settings(FUSION_RENDER_FIRST_DEFAULT=True):
            assert resolve_render_first(rf.get("/")) is True

    def test_setting_default_when_nothing_configured(self, rf):
        # No FUSION_RENDER_FIRST* setting configured → the explicit fallback.
        with override_settings(FUSION_RENDER_FIRST=None, FUSION_RENDER_FIRST_DEFAULT=None):
            assert resolve_render_first(rf.get("/"), setting_default=True) is True
            assert resolve_render_first(rf.get("/")) is False

    def test_fresh_session_is_not_auto_seeded(self, rf):
        """A fresh session must not be auto-seeded to True: the setting default
        must remain reachable for browser traffic."""
        request = rf.get("/")
        request.session = {}
        with override_settings(FUSION_RENDER_FIRST=False):
            assert resolve_render_first(request) is False
            assert "fusion_render_first" not in request.session
