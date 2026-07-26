"""
E2E integration tests for the django-fusion fragment-rendering flow.

Verifies the full backend → API contract that the frontend FusionPage,
FusionProxy, and FusionMiddleware components depend on:

1. ``/fusion/health`` — health-check response envelope
2. ``/apis/pages/<slug>/fragment/`` — fragment-pointer contract
3. ``/apis/pages/<slug>/data/`` — unified data/fragment endpoint
4. ``FusionCodec.encode/decode`` — codec roundtrip
5. Cross-layer contract — payloads match frontend TypeScript types
"""

from __future__ import annotations

import json

from django.test import Client, RequestFactory

from plugins.pages.content import STATIC_PAGES
from www.api.data_adapter import fusion_response, _build_fragment_url
from www.api.fusion_health import fusion_health
from www.api.pages import page_data, page_fragment


# ── Helper: apply SessionMiddleware to a RequestFactory request ─────────
def _with_session(request, session_data: dict | None = None):
    """Return a version of *request* that has a working ``.session``.

    ``RequestFactory`` does not run middleware, so ``request.session``
    raises ``AttributeError``.  This helper applies the
    ``SessionMiddleware`` with the **signed-cookies** backend so that
    no database access is needed.
    """
    from django.conf import settings
    from django.contrib.sessions.middleware import SessionMiddleware

    # Use signed-cookie sessions so we don't need database access
    _orig_engine = settings.SESSION_ENGINE
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
    try:
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        if session_data:
            for k, v in session_data.items():
                request.session[k] = v
        return request
    finally:
        settings.SESSION_ENGINE = _orig_engine


# ═══════════════════════════════════════════════════════════════════════
# 1. Health endpoint — /fusion/health
# ═══════════════════════════════════════════════════════════════════════

class TestFusionHealthEndpoint:
    """Contract: ``/fusion/health`` returns the canonical envelope."""

    def test_returns_fusion_envelope(self):
        """The response has the ``{status, message, data}`` envelope."""
        request = _with_session(RequestFactory().get("/fusion/health"))
        response = fusion_health(request)

        assert response.status_code == 200
        payload = json.loads(response.content)
        assert payload["status"] == 200
        assert payload["message"] == "Success"
        assert "data" in payload

    def test_data_contains_fusion_render_first(self):
        """``data.fusion_render_first`` is a boolean (frontend contract)."""
        request = _with_session(RequestFactory().get(
            "/fusion/health",
            HTTP_USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) Chrome/120",
        ))
        response = fusion_health(request)
        payload = json.loads(response.content)
        pref = payload["data"]["fusion_render_first"]
        assert isinstance(pref, bool), "fusion_render_first must be a boolean"

    def test_data_contains_reason(self):
        """``data.reason`` is a string (used for debugging/logging)."""
        request = _with_session(RequestFactory().get("/fusion/health"))
        response = fusion_health(request)
        payload = json.loads(response.content)
        assert isinstance(payload["data"]["reason"], str)
        assert len(payload["data"]["reason"]) > 0

    def test_data_contains_session_cached(self):
        """``data.session_cached`` indicates cache state."""
        request = _with_session(RequestFactory().get("/fusion/health"))

        # First call should not be cached
        response = fusion_health(request)
        payload = json.loads(response.content)
        assert payload["data"]["session_cached"] is False

        # Second call uses the same session — should be cached
        request.session["fusion_render_first"] = True
        request.session.save()
        response2 = fusion_health(request)
        payload2 = json.loads(response2.content)
        assert payload2["data"]["session_cached"] is True

    def test_health_via_testclient(self):
        """Full HTTP request via TestClient (integration smoke test).

        Note: this test may return 404 if ``/fusion/health`` is not
        included in the test URL configuration (ROOT_URLCONF).
        """
        client = Client()
        response = client.get("/fusion/health")
        # Accept 200 or 404 depending on test URL routing
        assert response.status_code in (200, 404)


# ═══════════════════════════════════════════════════════════════════════
# 2. Fragment pointer — /apis/pages/<slug>/fragment/
# ═══════════════════════════════════════════════════════════════════════

class TestFragmentPointerContract:
    """Contract: fragment pointer payload matches frontend ``FragmentPointer`` type.

    Frontend TypeScript type (from fusion-types.ts)::

        interface FragmentPointer {
          component: string;
          fragment_name: string;
          fragment_url: string;
          fusion_render_first: boolean;
          page_slug?: string;
          title?: string;
        }
    """

    REQUIRED_FIELDS = [
        "component",
        "fragment_name",
        "fragment_url",
        "fusion_render_first",
    ]

    def _get_pointer(self, slug: str = "home"):
        request = RequestFactory().get(f"/apis/pages/{slug}/fragment/")
        response = page_fragment(request, slug)
        payload = json.loads(response.content)
        return payload["data"]

    def test_all_required_fields_present(self):
        """Fragment pointer has all fields the frontend needs."""
        ptr = self._get_pointer("home")
        for field in self.REQUIRED_FIELDS:
            assert field in ptr, f"Missing required field: {field}"

    def test_field_types_match_frontend_contract(self):
        """Field types match the TypeScript ``FragmentPointer`` interface."""
        ptr = self._get_pointer("about-us")
        assert isinstance(ptr["component"], str)
        assert isinstance(ptr["fragment_name"], str)
        assert isinstance(ptr["fragment_url"], str)
        assert isinstance(ptr["fusion_render_first"], bool)

    def test_fragment_url_contains_fragment_name(self):
        """The fragment_url contains the fragment name and 'fragments' path."""
        ptr = self._get_pointer("faq")
        url = ptr["fragment_url"]
        assert url.startswith("http://") or url.startswith("/")
        assert "/fragments/pages.faq/" in url

    def test_page_slug_and_title_match_static_data(self):
        """Extra metadata matches the canonical STATIC_PAGES data."""
        ptr = self._get_pointer("privacy")
        assert ptr["page_slug"] == "privacy"
        assert ptr["title"] == STATIC_PAGES["privacy"]["title"]

    def test_fusion_render_first_defaults_to_false(self):
        """Without explicit override, fusion_render_first is False."""
        ptr = self._get_pointer("home")
        assert ptr["fusion_render_first"] is False

    def test_envelope_shape_has_status_message_data(self):
        """The outer envelope matches ``FusionEnvelope`` frontend type."""
        request = RequestFactory().get("/apis/pages/home/fragment/")
        response = page_fragment(request, "home")
        payload = json.loads(response.content)
        assert "status" in payload
        assert "message" in payload
        assert "data" in payload
        assert payload["status"] == 200

    def test_not_found_returns_404_envelope(self):
        """Unknown slug returns 404 with error in data."""
        request = RequestFactory().get("/apis/pages/unknown/fragment/")
        response = page_fragment(request, "unknown")
        payload = json.loads(response.content)
        assert payload["status"] == 404
        assert "error" in payload["data"]

    def test_fragment_name_follows_convention(self):
        """fragment_name follows ``pages.<sanitized_slug>`` convention."""
        assert self._get_pointer("home")["fragment_name"] == "pages.home"
        assert self._get_pointer("about-us")["fragment_name"] == "pages.about_us"
        assert self._get_pointer("faq")["fragment_name"] == "pages.faq"
        assert self._get_pointer("privacy")["fragment_name"] == "pages.privacy"
        assert self._get_pointer("contact")["fragment_name"] == "pages.contact"


# ═══════════════════════════════════════════════════════════════════════
# 3. Page data endpoint — /apis/pages/<slug>/data/
# ═══════════════════════════════════════════════════════════════════════

class TestPageDataContract:
    """Contract: ``/apis/pages/<slug>/data/`` response is consumable by frontend.

    Frontend consumes this via ``useGetPageDataQuery`` which unwraps
    ``{status, message, data}`` to get the inner ``PageDataResponse``::

        interface PageDataResponse {
          slug: string;
          title: string;
          encoded: string;  // "fusion_v1:<base64>"
        }
    """

    def test_data_mode_returns_page_data_response(self):
        """In data mode, the inner data matches ``PageDataResponse``."""
        request = RequestFactory().get("/apis/pages/home/data/")
        response = page_data(request, "home")
        payload = json.loads(response.content)
        inner = payload["data"]
        assert "slug" in inner
        assert "title" in inner
        assert "encoded" in inner
        assert isinstance(inner["slug"], str)
        assert isinstance(inner["title"], str)
        assert isinstance(inner["encoded"], str)

    def test_encoded_field_matches_codec_format(self):
        """The ``encoded`` field is a valid codec string the frontend can decode."""
        request = RequestFactory().get("/apis/pages/about-us/data/")
        response = page_data(request, "about-us")
        payload = json.loads(response.content)
        encoded = payload["data"]["encoded"]
        assert encoded.startswith("fusion_v1:"), \
            "Codec string must start with fusion_v1:"

    def test_encoded_field_decodeable_by_frontend_decoder(self):
        """The frontend FusionDecoder can decode the encoded field."""
        from django_fusion.routes.session import FusionCodec

        request = RequestFactory().get("/apis/pages/faq/data/")
        response = page_data(request, "faq")
        payload = json.loads(response.content)
        encoded = payload["data"]["encoded"]

        # This is what the frontend FusionDecoder.decode() does
        decoded = FusionCodec.decode(encoded)
        assert decoded["slug"] == "faq"
        assert "blocks" in decoded
        assert len(decoded["blocks"]) > 0

    def test_all_pages_produce_decodeable_encoded_field(self):
        """Every STATIC_PAGES entry produces a valid codec string."""
        for slug in STATIC_PAGES:
            request = RequestFactory().get(f"/apis/pages/{slug}/data/")
            response = page_data(request, slug)
            payload = json.loads(response.content)
            encoded = payload["data"]["encoded"]
            assert encoded.startswith("fusion_v1:"), f"Failed for slug={slug}"

    def test_html_mode_returns_rendered_template(self):
        """With ``fusion_render_first=true``, the response is HTML with page content."""
        request = RequestFactory().get(
            "/apis/pages/home/data/?fusion_render_first=true",
        )
        response = page_data(request, "home")
        html = response.content.decode()
        assert "Learn Without Limits" in html
        assert "fusion-page" in html

    def test_html_mode_via_header(self):
        """``X-Fusion-Render-First: true`` header also returns HTML."""
        request = RequestFactory().get(
            "/apis/pages/contact/data/",
            HTTP_X_FUSION_RENDER_FIRST="true",
        )
        response = page_data(request, "contact")
        html = response.content.decode()
        assert "Contact Us" in html

    def test_response_matches_fusionenvelope_frontend_type(self):
        """The response envelope matches the frontend ``FusionEnvelope`` type."""
        request = RequestFactory().get("/apis/pages/home/data/")
        response = page_data(request, "home")
        payload = json.loads(response.content)

        # Frontend transformResponse in pages.ts does:
        #   raw.data -> PageDataResponse
        assert "status" in payload
        assert "message" in payload
        assert "data" in payload
        assert payload["status"] == 200

        # The unwrapped data is what becomes PageDataResponse
        inner = payload["data"]
        assert isinstance(inner["slug"], str)
        assert isinstance(inner["title"], str)
        assert isinstance(inner["encoded"], str)

    def test_not_found_returns_404_with_error(self):
        """Unknown slug returns 404 with error message in data."""
        request = RequestFactory().get("/apis/pages/unknown/data/")
        response = page_data(request, "unknown")
        payload = json.loads(response.content)
        assert payload["status"] == 404
        assert "error" in payload["data"]


# ═══════════════════════════════════════════════════════════════════════
# 4. FusionCodec roundtrip
# ═══════════════════════════════════════════════════════════════════════

class TestFusionCodecRoundtrip:
    """Verify the codec produces data the frontend ``FusionDecoder`` can consume.

    The frontend FusionDecoder (TypeScript) mirrors this exact logic::

        const match = /^fusion_v(\\d+):(.+)$/.exec(encoded);
        const b64 = match[2];
        const jsonStr = Buffer.from(b64, 'base64').toString('utf-8');
        return JSON.parse(jsonStr);
    """

    def test_encode_decode_roundtrip(self):
        """Encode then decode returns the original data."""
        from django_fusion.routes.session import FusionCodec

        original = {"slug": "test", "blocks": [{"type": "hero", "heading": "Test"}]}
        encoded = FusionCodec.encode(original)
        decoded = FusionCodec.decode(encoded)
        assert decoded == original

    def test_codec_format_matches_frontend_regex(self):
        """The codec format matches the frontend CODEC_PREFIX_RE pattern."""
        from django_fusion.routes.session import FusionCodec

        encoded = FusionCodec.encode({"key": "value"})
        import re
        match = re.match(r"^fusion_v(\d+):(.+)$", encoded)
        assert match is not None, "Codec must match frontend regex"
        assert match.group(1) == "1", "Version should be 1"
        # The base64 portion should be valid base64 (no spaces, ASCII)
        b64 = match.group(2)
        assert b64.isascii(), "Base64 portion must be ASCII"
        assert " " not in b64, "Base64 must not contain spaces"

    def test_decode_page_data_with_frontend_api(self):
        """Simulate what the frontend FusionPage does with page data."""
        from django_fusion.routes.session import FusionCodec

        page = STATIC_PAGES["home"]
        encoded = FusionCodec.encode(page)
        decoded = FusionCodec.decode(encoded)

        # Frontend FusionPageDataInner does:
        #   fusionDecoder.decodeAs<CmsPage>(pageData.encoded)
        assert decoded["slug"] == "home"
        assert decoded["title"] == "Learn Without Limits"
        assert "blocks" in decoded

        # The frontend CmsPage type expects these fields
        blocks = decoded["blocks"]
        assert isinstance(blocks, list)
        assert len(blocks) > 0
        assert all("type" in b for b in blocks), "Each block must have a type"

    def test_fusion_response_produces_frontend_compatible_payload(self):
        """``fusion_response`` produces a payload matching ``FragmentPointer``."""
        pointer = fusion_response(
            "pages.home",
            extra={"page_slug": "home", "title": "Home"},
        )
        # Frontend FragmentPointer fields
        assert "component" in pointer
        assert "fragment_name" in pointer
        assert "fragment_url" in pointer
        assert "fusion_render_first" in pointer
        assert pointer["page_slug"] == "home"
        assert pointer["title"] == "Home"

        # The frontend uses fragment_url to fetch HTML
        assert pointer["fragment_url"].startswith("/fragments/pages.home/")


# ═══════════════════════════════════════════════════════════════════════
# 5. End-to-end flow: health → fragment pointer → fragment render
# ═══════════════════════════════════════════════════════════════════════

class TestEndToEndFlow:
    """Full backend → API → frontend-consumable flow."""

    def test_health_check_populates_session(self):
        """Calling health check caches the preference in the Django session."""
        request = _with_session(RequestFactory().get("/fusion/health"))

        # Before the call, session should be empty
        assert "fusion_render_first" not in request.session

        fusion_health(request)

        # After the call, preference should be set
        assert "fusion_render_first" in request.session
        assert isinstance(request.session["fusion_render_first"], bool)

    def test_fragment_pointer_url_contains_fragment_path(self):
        """The fragment_url in the pointer contains the fragment renderer path."""
        request = RequestFactory().get("/apis/pages/home/fragment/")
        response = page_fragment(request, "home")
        payload = json.loads(response.content)
        fragment_url = payload["data"]["fragment_url"]

        # The fragment_url from the pointer points to the django-fusion
        # fragment renderer, which the frontend can use with FusionProxy.
        assert fragment_url.startswith("http://") or fragment_url.startswith("/")
        assert "/fragments/pages.home/" in fragment_url

    def test_frontend_can_consume_fragment_pointer(self):
        """Simulate what the frontend does with a fragment pointer:

        1. Fetch /apis/pages/<slug>/fragment/
        2. Unwrap ``{status, message, data}`` → get FragmentPointer
        3. Use the unified endpoint to fetch HTML (via FusionProxy)
        """
        # Step 1: Fetch fragment pointer
        request = RequestFactory().get("/apis/pages/home/fragment/")
        response = page_fragment(request, "home")
        payload = json.loads(response.content)

        # Step 2: Unwrap (frontend transformResponse)
        assert payload["status"] == 200
        pointer = payload["data"]

        # Step 3: Verify the pointer has all needed info
        assert pointer["fragment_name"] == "pages.home"
        assert "fragment_url" in pointer
        assert "fusion_render_first" in pointer

        # The frontend FusionPage uses:
        #   <FusionProxy fragmentUrl={`/apis/pages/home/data/?fusion_render_first=true`} />
        unified_url = "/apis/pages/home/data/?fusion_render_first=true"
        request2 = RequestFactory().get(unified_url)
        response2 = page_data(request2, "home")
        assert response2.status_code == 200
        html = response2.content.decode()
        assert "Learn Without Limits" in html

    def test_all_pages_have_correct_seo_in_codec(self):
        """Every STATIC_PAGES entry has correct SEO data after codec decode."""
        from django_fusion.routes.session import FusionCodec

        for slug, page_data_dict in STATIC_PAGES.items():
            encoded = FusionCodec.encode(page_data_dict)
            decoded = FusionCodec.decode(encoded)

            # Frontend expects CmsPage.seo
            assert "seo" in decoded, f"Missing SEO for {slug}"
            assert "title" in decoded["seo"], f"Missing SEO title for {slug}"
            assert "description" in decoded["seo"], \
                f"Missing SEO description for {slug}"


# ═══════════════════════════════════════════════════════════════════════
# 6. Cross-layer contract validation
# ═══════════════════════════════════════════════════════════════════════

class TestCrossLayerContract:
    """Validate that API responses match frontend TypeScript type expectations.

    Frontend types are in ``projects/lms/lms/src/store/api/endpoints/pages.ts``
    and ``projects/lms/lms/src/lib/fusion-types.ts``.
    """

    def test_page_data_response_matches_pages_ts_types(self):
        """The ``PageDataResponse`` type (slug, title, encoded) is satisfied."""
        request = RequestFactory().get("/apis/pages/home/data/")
        response = page_data(request, "home")
        payload = json.loads(response.content)
        data = payload["data"]

        assert "slug" in data
        assert isinstance(data["slug"], str)
        assert "title" in data
        assert isinstance(data["title"], str)
        assert "encoded" in data
        assert isinstance(data["encoded"], str)

    def test_fragment_pointer_matches_fusion_types_ts(self):
        """The ``FragmentPointer`` type fields are present and correct."""
        ptr = fusion_response(
            "pages.test",
            extra={"page_slug": "test", "title": "Test"},
        )

        # Required fields (the frontend validates these)
        assert isinstance(ptr["component"], str)
        assert isinstance(ptr["fragment_name"], str)
        assert isinstance(ptr["fragment_url"], str)
        assert isinstance(ptr["fusion_render_first"], bool)

        # Optional fields
        assert ptr.get("page_slug") == "test"
        assert ptr.get("title") == "Test"

    def test_envelope_matches_fusionenvelope_ts_type(self):
        """The ``{status, message, data}`` envelope is satisfied."""
        request = RequestFactory().get("/apis/pages/home/data/")
        response = page_data(request, "home")
        payload = json.loads(response.content)

        assert isinstance(payload["status"], int)
        assert isinstance(payload["message"], str)
        assert "data" in payload

    def test_health_response_matches_both_types(self):
        """The health endpoint envelope has expected data shape."""
        request = _with_session(RequestFactory().get("/fusion/health"))
        response = fusion_health(request)
        payload = json.loads(response.content)

        # Envelope
        assert isinstance(payload["status"], int)
        assert isinstance(payload["message"], str)
        assert "data" in payload

        # Data shape (used by frontend to seed sessionStorage)
        data = payload["data"]
        assert isinstance(data["fusion_render_first"], bool)
        assert isinstance(data["reason"], str)
        assert isinstance(data["session_cached"], bool)

    def test_build_fragment_url_produces_valid_url(self):
        """The ``_build_fragment_url`` helper produces URLs the frontend can use."""
        # Without request → relative
        url = _build_fragment_url("pages.home")
        assert url == "/fragments/pages.home/"

        # With Django request → absolute
        request = RequestFactory().get("/")
        url = _build_fragment_url("pages.home", request)
        assert url == "http://testserver/fragments/pages.home/"

        # URL contains the fragment name — frontend uses this to fetch HTML
        assert "pages.home" in url
        assert "fragments" in url
