"""Tests for the Bolt data adapter helper functions."""

from __future__ import annotations

import pytest
from django.test import RequestFactory

from django_fusion.routes import RoutableComponent
from www.api.data_adapter import fusion_response, _build_fragment_url


class DummyComponent(RoutableComponent):
    route_name = "dashboard"
    route_path = "dashboard/"
    fragment_name = "lms.dashboard"
    fusion_render_first = True


class DefaultNameComponent(RoutableComponent):
    route_name = "report"
    route_path = "reports/"
    # fragment_name intentionally omitted -> derived from route_name


class FalseRenderComponent(RoutableComponent):
    route_name = "legacy"
    route_path = "legacy/"
    fragment_name = "lms.legacy"
    fusion_render_first = False


class NonInstantiableComponent(RoutableComponent):
    """A component class that cannot be instantiated without arguments.

    Used to verify the class-attribute fallback path in ``fusion_response``.
    """

    route_name = "static"
    route_path = "static/"
    fragment_name = "lms.static"
    fusion_render_first = True

    def __init__(self, required_arg: str) -> None:
        super().__init__()
        self.required_arg = required_arg


class TestFusionResponse:
    """Tests for ``fusion_response`` returning canonical fragment pointers."""

    def test_component_class(self):
        payload = fusion_response(DummyComponent)
        assert payload["component"] == "DummyComponent"
        assert payload["fragment_name"] == "lms.dashboard"
        assert payload["fusion_render_first"] is True
        assert payload["fragment_url"] == "/fragments/lms.dashboard/"

    def test_component_instance(self):
        payload = fusion_response(DummyComponent())
        assert payload["component"] == "DummyComponent"
        assert payload["fragment_name"] == "lms.dashboard"
        assert payload["fusion_render_first"] is True

    def test_derived_fragment_name(self):
        payload = fusion_response(DefaultNameComponent)
        assert payload["fragment_name"] == "components.report"

    def test_string_component(self):
        payload = fusion_response("components.hero")
        assert payload["component"] == "components.hero"
        assert payload["fragment_name"] == "components.hero"
        # String components default to False when no explicit override
        assert payload["fusion_render_first"] is False
        assert payload["fragment_url"] == "/fragments/components.hero/"

    def test_override_fusion_render_first(self):
        payload = fusion_response(DummyComponent, fusion_render_first=False)
        assert payload["fusion_render_first"] is False

    def test_component_fusion_render_first_false(self):
        payload = fusion_response(FalseRenderComponent)
        assert payload["fusion_render_first"] is False

    def test_extra_merged(self):
        payload = fusion_response(DummyComponent, extra={"foo": "bar", "count": 1})
        assert payload["foo"] == "bar"
        assert payload["count"] == 1
        # canonical keys still present
        assert payload["fragment_name"] == "lms.dashboard"

    def test_relative_url_when_no_request(self):
        payload = fusion_response(DummyComponent)
        assert payload["fragment_url"] == "/fragments/lms.dashboard/"

    def test_absolute_url_with_django_request(self):
        request = RequestFactory().get("/")
        payload = fusion_response(DummyComponent, request=request)
        assert payload["fragment_url"] == "http://testserver/fragments/lms.dashboard/"

    def test_raises_for_unresolvable_component(self):
        class NoNameComponent(RoutableComponent):
            pass

        with pytest.raises(ValueError, match="Cannot resolve fragment_name"):
            fusion_response(NoNameComponent)

    def test_non_instantiable_component_class_uses_class_attribute(self):
        """If a component class cannot be instantiated, fragment_name is read
        from the class attribute and the payload is still produced."""
        payload = fusion_response(NonInstantiableComponent)
        assert payload["component"] == "NonInstantiableComponent"
        assert payload["fragment_name"] == "lms.static"
        assert payload["fusion_render_first"] is True

    def test_extra_cannot_override_canonical_keys(self):
        """Canonical keys should always win over ``extra`` data."""
        payload = fusion_response(
            DummyComponent,
            extra={
                "component": "evil",
                "fragment_name": "evil.fragment",
                "custom_key": "kept",
            },
        )
        assert payload["component"] == "DummyComponent"
        assert payload["fragment_name"] == "lms.dashboard"
        assert payload["custom_key"] == "kept"

    def test_invalid_fragment_name_raises_value_error(self):
        """Invalid fragment names are rejected before a URL is built."""
        with pytest.raises(ValueError, match="Invalid fragment_name"):
            fusion_response("bad name!")


class TestBuildFragmentUrl:
    """Tests for the fragment URL builder helper."""

    def test_relative_when_no_request(self):
        assert _build_fragment_url("lms.dashboard") == "/fragments/lms.dashboard/"

    def test_django_request(self):
        request = RequestFactory().get("/")
        assert (
            _build_fragment_url("lms.dashboard", request)
            == "http://testserver/fragments/lms.dashboard/"
        )

    def test_bolt_like_request_with_url(self):
        class FakeRequest:
            url = "http://localhost:8082/apis/courses/"
            scheme = "http"

        assert (
            _build_fragment_url("lms.dashboard", FakeRequest())
            == "http://localhost:8082/fragments/lms.dashboard/"
        )

    def test_request_with_host_header(self):
        class FakeRequest:
            scheme = "https"
            headers = {"host": "example.com"}

        assert (
            _build_fragment_url("lms.dashboard", FakeRequest())
            == "https://example.com/fragments/lms.dashboard/"
        )
