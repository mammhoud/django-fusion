"""Tests for the static page content API."""

from __future__ import annotations

import json

from django.test import RequestFactory

from plugins.pages.content import STATIC_PAGES
from www.api.pages import page_data, page_detail, page_fragment


class TestPageDetail:
    """Tests for the JSON page content endpoint."""

    def test_page_detail_returns_home(self):
        request = RequestFactory().get("/apis/pages/home/")
        response = page_detail(request, "home")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["slug"] == "home"
        assert data["title"] == "Learn Without Limits"

    def test_page_detail_not_found(self):
        request = RequestFactory().get("/apis/pages/unknown/")
        response = page_detail(request, "unknown")

        assert response.status_code == 404
        assert json.loads(response.content) == {"status": "error", "message": "Page not found"}


class TestPageFragment:
    """Tests for the fragment-pointer page endpoint."""

    def test_page_fragment_returns_canonical_payload(self):
        request = RequestFactory().get("/apis/pages/home/fragment/")
        response = page_fragment(request, "home")

        assert response.status_code == 200
        payload = json.loads(response.content)
        # The envelope shape: {status, message, data: {pointer}}
        assert payload["status"] == 200
        ptr = payload["data"]
        assert ptr["component"] == "pages.home"
        assert ptr["fragment_name"] == "pages.home"
        # Default is now False (get data instead of render)
        assert ptr["fusion_render_first"] is False
        assert ptr["fragment_url"] == "http://testserver/fragments/pages.home/"
        assert ptr["page_slug"] == "home"
        assert ptr["title"] == STATIC_PAGES["home"]["title"]

    def test_page_fragment_normalizes_index_slug(self):
        request = RequestFactory().get("/apis/pages/fragment/")
        response = page_fragment(request, "")

        assert response.status_code == 200
        payload = json.loads(response.content)
        assert payload["data"]["fragment_name"] == "pages.home"

    def test_page_fragment_not_found(self):
        request = RequestFactory().get("/apis/pages/unknown/fragment/")
        response = page_fragment(request, "unknown")

        assert response.status_code == 404
        payload = json.loads(response.content)
        # The envelope shape: {status, message, data}
        assert payload["status"] == 404
        assert "error" in payload["data"]


class TestPageData:
    """Tests for the unified page_data endpoint (request-arg driven)."""

    def test_default_returns_json_with_codec(self):
        """Without fusion_render_first, page_data returns JSON encoded via FusionCodec."""
        request = RequestFactory().get("/apis/pages/home/data/")
        response = page_data(request, "home")

        assert response.status_code == 200
        payload = json.loads(response.content)
        assert payload["status"] == 200
        assert "data" in payload
        assert payload["data"]["slug"] == "home"
        assert payload["data"]["title"] == STATIC_PAGES["home"]["title"]
        # The encoded field should be a valid codec string
        assert payload["data"]["encoded"].startswith("fusion_v1:")

    def test_false_query_param_returns_json(self):
        """?fusion_render_first=false returns JSON data."""
        request = RequestFactory().get("/apis/pages/home/data/?fusion_render_first=false")
        response = page_data(request, "home")

        assert response.status_code == 200
        payload = json.loads(response.content)
        assert payload["status"] == 200
        assert isinstance(payload["data"]["encoded"], str)

    def test_true_query_param_returns_html(self):
        """?fusion_render_first=true returns rendered HTML."""
        request = RequestFactory().get("/apis/pages/home/data/?fusion_render_first=true")
        response = page_data(request, "home")

        assert response.status_code == 200
        # Should be HTML, not JSON
        content_type = response.get("Content-Type", "")
        assert "text/html" in content_type or "html" in response.content.decode()[:100].lower()
        html = response.content.decode()
        assert "Learn Without Limits" in html
        assert "fusion-page" in html

    def test_true_header_returns_html(self):
        """X-Fusion-Render-First: true header returns rendered HTML."""
        request = RequestFactory().get(
            "/apis/pages/privacy/data/",
            HTTP_X_FUSION_RENDER_FIRST="true",
        )
        response = page_data(request, "privacy")

        assert response.status_code == 200
        html = response.content.decode()
        assert "Privacy Policy" in html
        assert "Introduction" in html

    def test_false_header_returns_json(self):
        """X-Fusion-Render-First: false header returns JSON data."""
        request = RequestFactory().get(
            "/apis/pages/faq/data/",
            HTTP_X_FUSION_RENDER_FIRST="false",
        )
        response = page_data(request, "faq")

        assert response.status_code == 200
        payload = json.loads(response.content)
        assert payload["data"]["slug"] == "faq"

    def test_can_decode_encoded_field(self):
        """The encoded field can be decoded back to the original page data."""
        from django_fusion.routes.session import FusionCodec

        request = RequestFactory().get("/apis/pages/about-us/data/")
        response = page_data(request, "about-us")

        payload = json.loads(response.content)
        encoded = payload["data"]["encoded"]
        decoded = FusionCodec.decode(encoded)
        assert decoded["slug"] == "about-us"
        assert decoded["title"] == STATIC_PAGES["about-us"]["title"]
        assert "blocks" in decoded

    def test_not_found_returns_404_json(self):
        """Unknown slugs return 404 JSON."""
        request = RequestFactory().get("/apis/pages/unknown/data/")
        response = page_data(request, "unknown")

        assert response.status_code == 404
        payload = json.loads(response.content)
        assert "error" in payload["data"]
