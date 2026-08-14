"""Tests for django_fusion.routes.rendering.renderers and configurable fusion_render_first."""

import base64
import json
from typing import Any

import pytest
from django.test import RequestFactory
from django_fusion.routes.rendering.renderers import (
    RESPONSE_CODE_GROUPS,
    FusionFragmentPointer,
    FusionFragmentSchema,
    FusionJSONEncoder,
    FusionJSONRenderer,
    _status_to_message,
    fusion_json_response,
)
from django_fusion.routes.rendering.session import FusionCodec, FusionSessionChecker

# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def rf() -> RequestFactory:
    """Django RequestFactory — provided here because pytest-django's
    ``rf`` fixture is unavailable when Django is configured via
    ``settings.configure()`` rather than ``DJANGO_SETTINGS_MODULE``."""
    return RequestFactory()


class TestResponseCodeGroups:
    def test_groups_are_frozensets(self):
        for key in ("information", "success", "redirect", "client_error", "server_error"):
            assert isinstance(RESPONSE_CODE_GROUPS[key], frozenset)

    def test_success_contains_200(self):
        assert 200 in RESPONSE_CODE_GROUPS["success"]
        assert 201 in RESPONSE_CODE_GROUPS["success"]
        assert 404 not in RESPONSE_CODE_GROUPS["success"]

    def test_client_error_extra_codes(self):
        for code in (416, 418, 425, 429, 451):
            assert code in RESPONSE_CODE_GROUPS["client_error"]


class TestStatusToMessage:
    def test_known_statuses(self):
        assert _status_to_message(200) == "Success"
        assert _status_to_message(400) == "Client Error"
        assert _status_to_message(500) == "Server Error"
        assert _status_to_message(301) == "Redirect"
        assert _status_to_message(100) == "Informational"

    def test_unknown_status(self):
        assert _status_to_message(999) == "Unknown Status"


class TestFusionJSONEncoder:
    def test_encoder_exists(self):
        assert issubclass(FusionJSONEncoder, json.JSONEncoder)


class TestFusionJSONRenderer:
    def test_render_returns_json_response(self, rf):
        request = rf.get("/")
        renderer = FusionJSONRenderer()
        response = renderer.render(request, {"key": "value"})

        assert response.status_code == 200
        payload = json.loads(response.content)
        assert payload == {
            "status": 200,
            "message": "Success",
            "data": {"key": "value"},
        }

    def test_render_with_custom_status(self, rf):
        request = rf.get("/")
        renderer = FusionJSONRenderer()
        response = renderer.render(request, {"detail": "not found"}, response_status=404)

        assert response.status_code == 404
        payload = json.loads(response.content)
        assert payload["message"] == "Client Error"
        assert payload["data"] == {"detail": "not found"}

    def test_render_with_custom_message(self, rf):
        request = rf.get("/")
        renderer = FusionJSONRenderer()
        response = renderer.render(request, {}, message="Custom message")

        payload = json.loads(response.content)
        assert payload["message"] == "Custom message"

    def test_render_with_json_dumps_params(self, rf):
        request = rf.get("/")
        renderer = FusionJSONRenderer(json_dumps_params={"indent": 2})
        response = renderer.render(request, {"a": 1})

        assert b"  \"a\":" in response.content

    def test_json_dumps_params_isolation(self):
        """Ensure mutable defaults are not shared across instances."""
        r1 = FusionJSONRenderer(json_dumps_params={"indent": 2})
        r2 = FusionJSONRenderer()

        assert r1.json_dumps_params == {"indent": 2}
        assert r2.json_dumps_params == {}


class TestFusionJsonResponse:
    def test_default_response(self):
        response = fusion_json_response({"foo": "bar"})

        assert response.status_code == 200
        payload = json.loads(response.content)
        assert payload == {
            "status": 200,
            "message": "Success",
            "data": {"foo": "bar"},
        }

    def test_error_response(self):
        response = fusion_json_response({"error": "bad request"}, status=400)

        assert response.status_code == 400
        payload = json.loads(response.content)
        assert payload["message"] == "Client Error"
        assert payload["data"] == {"error": "bad request"}

    def test_custom_message(self):
        response = fusion_json_response({}, message="Keep calm")

        payload = json.loads(response.content)
        assert payload["message"] == "Keep calm"


class TestPydanticSchemas:
    def test_schema_model(self):
        schema = FusionFragmentSchema(
            status=200,
            message="Success",
            data={"component": "pages.home"},
        )
        assert schema.status == 200
        assert schema.data["component"] == "pages.home"

    def test_pointer_model(self):
        pointer = FusionFragmentPointer(
            component="pages.privacy",
            fragment_name="pages.privacy",
            fragment_url="http://example.com/fragments/pages.privacy/",
            fusion_render_first=True,
        )
        assert pointer.fusion_render_first is True


# ===========================================================================
# FusionCodec round-trip tests
# ===========================================================================


# ===========================================================================
# FusionSessionChecker tests
# ===========================================================================


class MockSession(dict):
    """A dict-like session that also supports ``set_expiry()``."""

    def set_expiry(self, seconds: int) -> None:
        pass


class TestFusionSessionChecker:
    """Tests for the session health-check caching behaviour."""

    def test_get_preference_caches_on_first_call(self, rf):
        """First call runs the health check and stores the result in session."""
        request = rf.get("/")
        request.session = MockSession()

        checker = FusionSessionChecker()
        result = checker.get_preference(request)

        # Default browser UA (no User-Agent header) → returns True
        assert result is True
        assert "fusion_render_first" in request.session
        assert request.session["fusion_render_first"] is True

    def test_get_preference_returns_cached_on_second_call(self, rf):
        """Second call returns the cached session value without re-running _check.

        We verify this by manually mutating the session cache after the
        first call.  If the checker re-ran _check() it would overwrite our
        mutation; if it reads the cache it returns our mutated value.
        """
        request = rf.get("/")
        request.session = MockSession()

        checker = FusionSessionChecker()
        result1 = checker.get_preference(request)
        assert result1 is True  # first call caches True

        # Mutate the cached value — a real re-check would overwrite this
        request.session["fusion_render_first"] = False

        result2 = checker.get_preference(request)
        assert result2 is False  # reads cache, does NOT re-run _check

    def test_clear_preference_removes_cached_value(self, rf):
        """``clear_preference`` removes the session key entirely."""
        request = rf.get("/")
        request.session = MockSession()

        checker = FusionSessionChecker()
        checker.get_preference(request)  # caches True
        assert "fusion_render_first" in request.session

        checker.clear_preference(request)
        assert "fusion_render_first" not in request.session

    def test_clear_preference_noop_when_not_cached(self, rf):
        """``clear_preference`` is a no-op when no preference is cached."""
        request = rf.get("/")
        request.session = MockSession()

        checker = FusionSessionChecker()
        # No get_preference() call before — nothing to clear
        checker.clear_preference(request)
        assert "fusion_render_first" not in request.session

    def test_get_preference_caches_browser_ua_as_true(self, rf):
        """A browser-like User-Agent results in ``True``."""
        request = rf.get("/", HTTP_USER_AGENT="Mozilla/5.0 ... Chrome/120")
        request.session = MockSession()

        checker = FusionSessionChecker()
        result = checker.get_preference(request)
        assert result is True

    def test_get_preference_caches_script_ua_as_false(self, rf):
        """A script-based User-Agent (curl) results in ``False``."""
        request = rf.get("/", HTTP_USER_AGENT="curl/8.0")
        request.session = MockSession()

        checker = FusionSessionChecker()
        result = checker.get_preference(request)
        assert result is False

    def test_custom_check_fn_overrides_default_heuristic(self, rf):
        """A custom ``check_fn`` is called instead of the built-in ``_check``."""
        request = rf.get("/")
        request.session = MockSession()

        # Custom check_fn that always returns False
        checker = FusionSessionChecker(check_fn=lambda req: False)
        result = checker.get_preference(request)
        assert result is False

    def test_custom_check_fn_receives_request(self, rf):
        """The custom ``check_fn`` receives the request as its argument."""
        request = rf.get("/", HTTP_USER_AGENT="test-agent")
        request.session = MockSession()

        captured = []

        def custom_check(req):
            captured.append(req)
            return True

        checker = FusionSessionChecker(check_fn=custom_check)
        checker.get_preference(request)

        assert len(captured) == 1
        assert captured[0] is request


class TestFusionCodecRoundTrip:
    """Round-trip tests for the codec that pairs with TypeScript FusionDecoder.

    These tests validate that ``FusionCodec.encode()`` produces output that
    ``FusionCodec.decode()`` can consume.  The format (``fusion_v1:<base64>``)
    is the contract shared with the TypeScript ``FusionDecoder`` class.
    """

    def test_round_trip_simple_dict(self):
        """Encode a simple dict, decode it, and verify the original data."""
        data = {"key": "value", "number": 42}
        encoded = FusionCodec.encode(data)
        assert encoded.startswith("fusion_v1:"), f"Unexpected prefix in {encoded!r}"
        decoded = FusionCodec.decode(encoded)
        assert decoded == data

    def test_round_trip_fragment_pointer(self):
        """Round-trip a realistic fragment-pointer payload."""
        data = {
            "component": "pages.home",
            "fragment_name": "pages.home",
            "fusion_render_first": False,
            "fragment_url": "http://localhost:8000/fragments/pages.home/",
            "page_slug": "home",
            "title": "Learn Without Limits",
            "tags": ["a", "b", "c"],
        }
        encoded = FusionCodec.encode(data)
        decoded = FusionCodec.decode(encoded)
        assert decoded == data

    def test_known_output_format_matches_ts_expectations(self):
        """Verify the encoded output matches what the TypeScript codec expects.

        The TypeScript ``FusionDecoder.decode()`` expects:
        - Prefix: ``fusion_v<version>:``
        - Base64 payload: ``urlsafe_b64encode(json_bytes)``
        - JSON: compact (no whitespace), produced by ``json.dumps(..., separators=(",", ":"))``
        """
        data = {"key": "value"}
        encoded = FusionCodec.encode(data)

        # Must start with version prefix
        assert encoded.startswith("fusion_v1:"), "Missing or wrong version prefix"

        # The base64 part must be urlsafe-base64-decodable
        _prefix, b64 = encoded.split(":", 1)
        decoded_bytes = base64.urlsafe_b64decode(b64)
        decoded_json = decoded_bytes.decode("utf-8")

        # Compact JSON: no extra whitespace
        assert decoded_json == '{"key":"value"}', f"Unexpected JSON format: {decoded_json!r}"
        assert json.loads(decoded_json) == data

    def test_round_trip_nested_complex(self):
        """Round-trip a deeply nested structure."""
        data = {
            "metadata": {
                "version": 2,
                "flags": [True, False, None],
                "nested": {"deep": {"value": 3.14}},
            },
            "items": [
                {"id": 1, "name": "first"},
                {"id": 2, "name": "second"},
            ],
        }
        encoded = FusionCodec.encode(data)
        decoded = FusionCodec.decode(encoded)
        assert decoded == data

    def test_decode_invalid_prefix_raises(self):
        """Invalid prefix should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid codec prefix"):
            FusionCodec.decode("bad_prefix:AAAA")

    def test_decode_empty_prefix_raises(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid codec prefix"):
            FusionCodec.decode("")

    def test_decode_missing_payload_raises(self):
        """Prefix without payload should raise ValueError about missing payload."""
        with pytest.raises(ValueError):
            FusionCodec.decode("fusion_v1:")

    def test_decode_garbage_b64_raises(self):
        """Non-base64 payload should raise an exception."""
        with pytest.raises(Exception):  # noqa: B017
            FusionCodec.decode("fusion_v1:!!!not-base64!!!")

    def test_encode_fragment_pointer_preserves_fields(self):
        """
        ``encode_fragment_pointer()`` should encode the pointer dict
        preserving all fields when ``session_aware`` is ``False``.
        """
        pointer = {
            "component": "pages.test",
            "fragment_name": "pages.test",
            "fusion_render_first": False,
        }
        encoded = FusionCodec.encode_fragment_pointer(pointer)
        decoded = FusionCodec.decode(encoded)
        assert decoded["component"] == "pages.test"
        assert decoded["fusion_render_first"] is False
        assert decoded["fragment_name"] == "pages.test"

    def test_produces_known_string(self):
        """Produce a known encoded string that the TypeScript test can verify."""
        data = {"component": "pages.privacy"}
        encoded = FusionCodec.encode(data)
        # Store this for the TS round-trip test
        assert encoded, "Encoded string must not be empty"
        assert encoded.startswith("fusion_v1:")


class TestFusionRenderFirstSetting:
    def test_default_is_false(self):
        from django_fusion.routes.components.routable import RoutableComponent

        class DummyComponent(RoutableComponent):
            pass

        assert DummyComponent.get_fusion_render_first() is False

    def test_per_class_override(self):
        from django_fusion.routes.components.routable import RoutableComponent

        class TrueComponent(RoutableComponent):
            fusion_render_first = True

        assert TrueComponent.get_fusion_render_first() is True

    def test_setting_fallback(self, monkeypatch: Any) -> None:
        from django_fusion.config.conf import get_settings
        from django_fusion.routes.components.routable import RoutableComponent

        class FallbackComponent(RoutableComponent):
            fusion_render_first = None

        monkeypatch.setattr(
            get_settings(), "render_first_default", True
        )
        assert FallbackComponent.get_fusion_render_first() is True

    def test_legacy_attribute_alias(self) -> None:
        """The old ``FUSION_RENDER_FIRST_DEFAULT`` attribute stays readable."""
        from django_fusion.config.conf import get_settings

        assert get_settings().render_first_default == get_settings().FUSION_RENDER_FIRST_DEFAULT
