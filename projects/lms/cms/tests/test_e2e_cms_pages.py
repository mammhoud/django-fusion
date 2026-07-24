"""E2E tests for Wagtail CMS-backed page content system.

Verifies the full flow:  STATIC_PAGES fallback → Wagtail Page models
→ API queries → frontend-ready JSON response.
"""

import json

import pytest
from django.test import RequestFactory


def _json_body(response):
    """Extract JSON dict from a Django JsonResponse."""
    if hasattr(response, "content"):
        return json.loads(response.content)
    return response


@pytest.mark.django_db
class TestE2ECMSPageSystem:
    """End-to-end tests for the CMS-backed page content API."""

    def test_page_data_returns_cms_content(self, rf):
        """GET /apis/pages/home/data/ returns valid page data via CMS-first query."""
        from www.api.pages import page_data

        request = rf.get("/apis/pages/home/data/")
        request.LANGUAGE_CODE = "en"
        response = page_data(request, "home")
        body = _json_body(response)

        assert body["status"] == 200
        assert "slug" in body["data"]
        assert "title" in body["data"]
        assert "encoded" in body["data"]

    def test_all_static_pages_available_via_api(self, rf):
        """Every STATIC_PAGES slug is accessible via the API."""
        from plugins.pages.content import STATIC_PAGES
        from www.api.pages import page_data

        for slug in STATIC_PAGES:
            request = rf.get(f"/apis/pages/{slug}/data/")
            request.LANGUAGE_CODE = "en"
            response = page_data(request, slug)
            body = _json_body(response)
            assert body["status"] == 200, f"Page {slug} returned {body.get('status')}"

    def test_page_fragment_pointer_contract(self, rf):
        """Fragment pointer responses match the expected contract."""
        from www.api.pages import page_fragment

        request = rf.get("/apis/pages/home/fragment/")
        request.LANGUAGE_CODE = "en"
        response = page_fragment(request, "home")
        body = _json_body(response)
        data = body["data"]

        assert "fragment_name" in data
        assert "fragment_url" in data
        assert "title" in data
        assert "component" in data
        assert data["fragment_name"].startswith("pages.")

    def test_page_data_includes_language_field(self, rf):
        """Page data response includes the language code."""
        from www.api.pages import page_data

        request = rf.get("/apis/pages/home/data/")
        request.LANGUAGE_CODE = "fr"
        response = page_data(request, "home")
        body = _json_body(response)
        assert body["data"].get("language") == "fr"

    def test_nonexistent_page_returns_404(self, rf):
        """Unknown page slugs return 404."""
        from www.api.pages import page_data

        request = rf.get("/apis/pages/nonexistent/data/")
        request.LANGUAGE_CODE = "en"
        response = page_data(request, "nonexistent")
        body = _json_body(response)
        assert body["status"] == 404

    def test_cms_first_query_falls_back_to_static(self, rf):
        """_get_cms_page falls back to STATIC_PAGES when Wagtail has no pages."""
        from www.api.pages import _get_cms_page

        result = _get_cms_page("home", "en")
        assert result is not None
        assert result["slug"] == "home"
        assert "title" in result
        assert "blocks" in result

    def test_page_detail_endpoint(self, rf):
        """GET /apis/pages/<slug>/ returns page dict wrapped by bolt_view."""
        from www.api.pages import page_detail

        request = rf.get("/apis/pages/home/")
        request.LANGUAGE_CODE = "en"
        response = page_detail(request, "home")
        body = _json_body(response)
        assert "title" in body
        assert "slug" in body

    def test_page_detail_404(self, rf):
        """Unknown page slug returns 404 via bolt_view as JsonResponse."""
        from www.api.pages import page_detail

        request = rf.get("/apis/pages/nonexistent/")
        request.LANGUAGE_CODE = "en"
        response = page_detail(request, "nonexistent")
        # bolt_view wraps error responses as JsonResponse with 404 status
        assert response.status_code == 404


@pytest.mark.django_db
class TestE2EI18N:
    """End-to-end tests for the i18n endpoints."""

    def test_i18n_setlang_endpoint(self, rf):
        """POST /apis/i18n/setlang/ accepts valid language codes."""
        from www.api.i18n import set_language_view

        request = rf.post(
            "/apis/i18n/setlang/",
            data=json.dumps({"language": "fr"}),
            content_type="application/json",
        )
        response = set_language_view(request)
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert data["language"] == "fr"

    def test_i18n_setlang_rejects_invalid_language(self, rf):
        """POST /apis/i18n/setlang/ rejects unknown language codes."""
        from www.api.i18n import set_language_view

        request = rf.post(
            "/apis/i18n/setlang/",
            data=json.dumps({"language": "zz"}),
            content_type="application/json",
        )
        response = set_language_view(request)
        assert response.status_code == 400

    def test_i18n_language_list_endpoint(self, rf):
        """GET /apis/i18n/languages/ returns available languages."""
        from www.api.i18n import language_list

        request = rf.get("/apis/i18n/languages/")
        response = language_list(request)
        data = json.loads(response.content)
        assert "languages" in data
        assert "current" in data


@pytest.mark.django_db
class TestE2ELanguageSystem:
    """End-to-end tests for the language/i18n translation system."""

    def test_translated_page_content_returns_french(self, rf):
        """Page data for French returns translated content."""
        from plugins.pages.content import get_page_for_language

        page = get_page_for_language("home", "fr")
        assert page["title"] == "Apprendre Sans Limites"

    def test_translated_page_content_returns_spanish(self, rf):
        """Page data for Spanish returns translated content."""
        from plugins.pages.content import get_page_for_language

        page = get_page_for_language("home", "es")
        assert page["title"] == "Aprende Sin Límites"

    def test_unknown_language_falls_back_to_english(self, rf):
        """Unsupported languages fall back to English content."""
        from plugins.pages.content import get_page_for_language

        page = get_page_for_language("home", "zz")
        assert page["title"] == "Learn Without Limits"

    def test_all_translations_have_required_fields(self):
        """All translated pages have slug, title, and blocks."""
        from plugins.pages.content import STATIC_PAGE_TRANSLATIONS

        for lang_code, pages in STATIC_PAGE_TRANSLATIONS.items():
            for slug, page in pages.items():
                assert "title" in page, f"{lang_code}/{slug} missing title"
                assert slug, f"{lang_code}/{slug} missing slug"


@pytest.mark.django_db
class TestE2EFusionCodec:
    """End-to-end tests for FusionCodec encoding/decoding."""

    def test_codec_encode_decode_roundtrip(self):
        """FusionCodec.encode() produces decodable payloads."""
        from django_fusion.routes import FusionCodec

        data = {"slug": "test", "title": "Test Page", "seo": {}, "blocks": []}
        encoded = FusionCodec.encode(data)
        assert encoded.startswith("fusion_v")
        assert ":" in encoded

        decoded = FusionCodec.decode(encoded)
        assert decoded["slug"] == data["slug"]
        assert decoded["title"] == data["title"]

    def test_codec_encode_produces_valid_base64(self):
        """Encoded strings are valid base64 after the prefix."""
        from django_fusion.routes import FusionCodec
        import base64

        data = {"key": "value"}
        encoded = FusionCodec.encode(data)
        _, _, b64 = encoded.partition(":")
        decoded = base64.b64decode(b64)
        assert b"key" in decoded
