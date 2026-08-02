"""Tests for django_fusion.fragments URL-driven fragment rendering."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from django.http import HttpResponse, StreamingHttpResponse
from django.test import Client, override_settings
from django.test.utils import setup_test_environment

from django_fusion.fragments import (
    FragmentRequestRenderer,
    FragmentRequestView,
    clear_fragment_components,
    get_fragment_component,
    register_fragment_component,
    unregister_fragment_component,
)
from django_fusion.fragments.renderer import resolve_template, validate_fragment_name


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def template_dir():
    with tempfile.TemporaryDirectory() as tmp:
        # Create a fragment template that renders a variable.
        fragment_dir = Path(tmp) / "components" / "home"
        fragment_dir.mkdir(parents=True)
        (fragment_dir / "hero.html").write_text("<h1>{{ title }}</h1>")

        # Create an OOB fragment template.
        oob_dir = Path(tmp) / "components" / "oob"
        oob_dir.mkdir(parents=True)
        (oob_dir / "counter.html").write_text(
            '<span data-id="{{ fragment_id }}">{{ count }}</span>'
        )

        # Create a template for the demo component used in component-aware tests.
        demo_dir = Path(tmp) / "components"
        demo_dir.mkdir(parents=True, exist_ok=True)
        (demo_dir / "demo.html").write_text("<p>{{ message }}</p>")

        yield Path(tmp)


@pytest.fixture
def registered_component(template_settings):
    from django_fusion.routes.components.routable import RoutableComponent
    from django_fusion.routes.components.fragments import FragmentComponent

    class DemoComponent(FragmentComponent):
        route_name = "demo"
        route_path = "demo/"
        fragment_name = "components.demo"
        template_name = "components/demo.html"

        def get_fragment_context(self, **kwargs):
            return {"message": "from component"}

    yield DemoComponent
    unregister_fragment_component("components.demo")


@pytest.fixture
def template_settings(template_dir):
    from django.conf import settings

    new_templates = [
        {
            **settings.TEMPLATES[0],
            "DIRS": [str(template_dir), *settings.TEMPLATES[0].get("DIRS", [])],
        }
    ]
    with override_settings(TEMPLATES=new_templates):
        yield


class TestResolveTemplate:
    def test_converts_dotted_name_to_path(self):
        assert resolve_template("components.home.hero") == "components/home/hero.html"

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="Fragment name is required"):
            validate_fragment_name("")

    def test_rejects_invalid_characters(self):
        with pytest.raises(ValueError, match="Invalid fragment name"):
            validate_fragment_name("components/home/hero")


class TestFragmentRequestRenderer:
    def test_render_returns_http_response(self, template_settings):
        from django.test import RequestFactory

        request = RequestFactory().get("/fragments/")
        renderer = FragmentRequestRenderer(request, context={"title": "Hello"})
        response = renderer.render("components.home.hero")

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200
        assert "<h1>Hello</h1>" in response.content.decode()

    def test_render_sets_htmx_header(self, template_settings):
        from django.test import RequestFactory

        request = RequestFactory().get("/fragments/", HTTP_HX_REQUEST="true")
        renderer = FragmentRequestRenderer(request, context={"title": "Hello"})
        response = renderer.render("components.home.hero")

        assert response["HX-Reswap"] == "innerHTML"

    def test_render_sse_stream(self, template_settings):
        from django.test import RequestFactory

        request = RequestFactory().get("/fragments/", HTTP_ACCEPT="text/event-stream")
        renderer = FragmentRequestRenderer(request, context={"title": "Streamed"})
        response = renderer.render("components.home.hero")

        assert isinstance(response, StreamingHttpResponse)
        assert response["Content-Type"] == "text/event-stream"
        content = b"".join(response.streaming_content).decode()
        assert "event: fragment" in content
        assert "<h1>Streamed</h1>" in content

    def test_render_returns_bad_request_when_template_missing(self):
        from django.test import RequestFactory

        request = RequestFactory().get("/fragments/")
        renderer = FragmentRequestRenderer(request)
        response = renderer.render("components.home.missing")

        assert response.status_code == 400
        assert "not found" in response.content.decode().lower()

    def test_render_oob_wraps_with_hx_swap_oob(self, template_settings):
        from django.test import RequestFactory

        request = RequestFactory().get("/fragments/")
        renderer = FragmentRequestRenderer(request, context={"count": 42})
        html = renderer.render_oob("components.oob.counter", "counter-id")

        assert '<div id="counter-id" hx-swap-oob="true">' in html
        assert '<span data-id="counter-id">42</span>' in html

    def test_render_oob_injects_fragment_id_into_context(self, template_settings):
        from django.test import RequestFactory

        request = RequestFactory().get("/fragments/")
        renderer = FragmentRequestRenderer(request)
        html = renderer.render_oob("components.oob.counter", "counter-id")

        # The template renders the injected fragment_id variable.
        assert 'data-id="counter-id"' in html
        assert '<span data-id="counter-id">' in html


class TestFragmentRequestView:
    def test_view_renders_fragment_from_path(self, client, template_settings):
        response = client.get("/fragments/components.home.hero/")
        assert response.status_code == 200
        assert response["Content-Type"] == "text/html; charset=utf-8"

    def test_view_renders_fragment_from_query(self, client, template_settings):
        response = client.get("/fragments/?q=components.home.hero")
        assert response.status_code == 200
        assert response["Content-Type"] == "text/html; charset=utf-8"

    def test_view_streams_sse_when_accept_header_set(self, client, template_settings):
        response = client.get(
            "/fragments/components.home.hero/",
            HTTP_ACCEPT="text/event-stream",
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "text/event-stream"
        content = b"".join(response.streaming_content).decode()
        assert "event: fragment" in content

    def test_view_returns_bad_request_for_invalid_fragment_name(self, client):
        # The invalid "/" character must be passed via the query string
        # because URL path segments cannot contain slashes.
        response = client.get("/fragments/?q=components/invalid/name")
        assert response.status_code == 400

    def test_view_returns_bad_request_without_fragment_name(self, client):
        response = client.get("/fragments/")
        assert response.status_code == 400

    def test_view_merges_page_context_into_rendered_fragment(
        self, client, template_settings, monkeypatch
    ):
        from django_fusion.fragments import views as fragment_views

        monkeypatch.setattr(
            fragment_views, "resolve_page_context", lambda request: {"title": "FromPage"}
        )

        response = client.get("/fragments/components.home.hero/?page_path=/")
        assert response.status_code == 200
        assert "<h1>FromPage</h1>" in response.content.decode()


class TestComponentAwareFragmentRequest:
    def test_component_auto_registers_by_fragment_name(self, registered_component):
        component_class = get_fragment_component("components.demo")
        assert component_class is registered_component

    def test_view_routes_to_registered_component(self, client, registered_component):
        response = client.get("/fragments/components.demo/")
        assert response.status_code == 200
        assert "from component" in response.content.decode()

    def test_view_routes_to_registered_component_with_htmx(self, client, registered_component):
        response = client.get(
            "/fragments/components.demo/",
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200
        assert "from component" in response.content.decode()

    def test_view_falls_back_to_template_for_unregistered_name(self, client, template_settings):
        response = client.get("/fragments/components.home.hero/")
        assert response.status_code == 200
        assert "<h1>" in response.content.decode()

    def test_unregister_removes_component(self, registered_component):
        unregister_fragment_component("components.demo")
        assert get_fragment_component("components.demo") is None
