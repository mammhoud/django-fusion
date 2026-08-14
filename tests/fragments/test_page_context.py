"""Tests for django_fusion.fragments.page_context."""

from __future__ import annotations

from django.test import RequestFactory
from django_fusion.fragments.page_context import resolve_page_context


class TestResolvePageContext:
    def test_empty_url_returns_empty_context(self):
        request = RequestFactory().get("/fragments/")
        assert resolve_page_context(request) == {}

    def test_page_path_query_param(self):
        request = RequestFactory().get("/fragments/?page_path=/")
        # Resolving "/" in the test URLConf returns a view; no Wagtail page
        # exists, so context falls back to an generic empty dict.
        context = resolve_page_context(request)
        assert isinstance(context, dict)

    def test_hx_current_url_header(self):
        request = RequestFactory().get(
            "/fragments/",
            HTTP_HX_CURRENT_URL="http://localhost:8000/",
        )
        context = resolve_page_context(request)
        assert isinstance(context, dict)

    def test_page_url_query_param(self):
        request = RequestFactory().get("/fragments/?page_url=http://localhost:8000/")
        context = resolve_page_context(request)
        assert isinstance(context, dict)

    def test_invalid_path_returns_empty_context(self):
        request = RequestFactory().get(
            "/fragments/?page_path=/definitely-not-a-real-page/",
        )
        assert resolve_page_context(request) == {}

    def test_bare_domain_url_defaults_to_root(self):
        request = RequestFactory().get(
            "/fragments/?page_url=http://localhost:8000",
        )
        # Should not raise; local path resolves to "/".
        context = resolve_page_context(request)
        assert isinstance(context, dict)
