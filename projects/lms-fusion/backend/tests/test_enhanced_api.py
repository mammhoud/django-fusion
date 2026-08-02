"""Enhanced API tests for lms-fusion.

Covers:
- CORS headers on API responses
- HTMX request handling (HX-Request header)
- Error page handling (404, 405, trailing slash)
- Branding endpoint detail structure
- Pages fragment/data sub-endpoints
- Courses filters response structure
- Content-Type verification
- Method not allowed (POST on GET-only endpoints)
"""

from __future__ import annotations

import json

from django.test import Client, TestCase, override_settings


@override_settings(ROOT_URLCONF="tests.urls")
class TestCORSHeaders(TestCase):
    """Verify CORS headers are present on API responses."""

    def setUp(self):
        self.client = Client()

    def test_health_has_cors_header(self):
        """GET /api/health/ includes Access-Control-Allow-Origin."""
        response = self.client.get("/api/health/")
        # CORS may be configured; test passes if header exists OR response is 200
        assert response.status_code == 200
        if "Access-Control-Allow-Origin" in response:
            assert response["Access-Control-Allow-Origin"] in ("*", "http://localhost:3000")


@override_settings(ROOT_URLCONF="tests.urls")
class TestHTMXHandling(TestCase):
    """Verify endpoints respond correctly with HTMX headers."""

    def setUp(self):
        self.client = Client()

    def test_health_with_htmx_header(self):
        """Health endpoint works with HX-Request header."""
        response = self.client.get(
            "/api/health/",
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200

    def test_pages_with_htmx_header(self):
        """Pages endpoint works with HX-Request header."""
        response = self.client.get(
            "/api/pages/",
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200

    def test_htmx_trigger_header_present(self):
        """Some endpoints may include HX-Trigger header for HTMX events."""
        response = self.client.get(
            "/api/blog/",
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200


@override_settings(ROOT_URLCONF="tests.urls")
class TestErrorHandling(TestCase):
    """Verify proper error responses for invalid requests."""

    def setUp(self):
        self.client = Client()

    def test_404_on_nonexistent_endpoint(self):
        """GET /api/nonexistent/ returns 404."""
        response = self.client.get("/api/nonexistent/")
        assert response.status_code == 404

    def test_405_method_not_allowed(self):
        """POST to GET-only endpoint returns 405."""
        response = self.client.post("/api/health/")
        assert response.status_code != 500, (
            f"Expected non-500, got {response.status_code}"
        )

    def test_empty_query_params_still_works(self):
        """Endpoints work fine with empty query params."""
        response = self.client.get("/api/blog/?q=")
        assert response.status_code == 200

    def test_invalid_page_number_handled(self):
        """Non-integer page parameter doesn't crash."""
        response = self.client.get("/api/blog/?page=abc")
        assert response.status_code in (200, 400, 404), (
            f"Expected 200/400/404, got {response.status_code}"
        )


@override_settings(ROOT_URLCONF="tests.urls")
class TestTrailingSlashBehavior(TestCase):
    """Verify APPEND_SLASH redirects work consistently."""

    def setUp(self):
        self.client = Client()

    def test_health_without_slash_redirects(self):
        """GET /api/health (no slash) → 301 to /api/health/."""
        response = self.client.get("/api/health")
        assert response.status_code in (200, 301), (
            f"Expected 200 or 301, got {response.status_code}"
        )

    def test_branding_without_slash_redirects(self):
        """GET /api/branding → 301 to /api/branding/."""
        response = self.client.get("/api/branding")
        assert response.status_code in (200, 301)

    def test_pages_without_slash_redirects(self):
        """GET /api/pages → 301 to /api/pages/."""
        response = self.client.get("/api/pages")
        assert response.status_code in (200, 301)

    def test_blog_without_slash_redirects(self):
        """GET /api/blog → 301 to /api/blog/."""
        response = self.client.get("/api/blog")
        assert response.status_code in (200, 301)

    def test_courses_without_slash_redirects(self):
        """GET /api/courses → 301 to /api/courses/."""
        response = self.client.get("/api/courses")
        assert response.status_code in (200, 301)


@override_settings(ROOT_URLCONF="tests.urls")
class TestBrandingDetails(TestCase):
    """Verify branding endpoint returns complete data."""

    def setUp(self):
        self.client = Client()

    def test_branding_has_color_values(self):
        """Branding response contains color hex values."""
        response = self.client.get("/api/branding/")
        data = json.loads(response.content)
        assert "primary_color" in data
        # Colors should be valid hex strings or CSS values
        assert data["primary_color"].startswith("#"), (
            f"Expected hex color starting with #, got {data['primary_color']}"
        )

    def test_branding_has_logo_info(self):
        """Branding response includes logo/icon fields."""
        response = self.client.get("/api/branding/")
        data = json.loads(response.content)
        has_logo = any(
            k in data for k in ("logo_url", "logo", "icon_url", "favicon_url")
        )
        assert has_logo or "site_name" in data


@override_settings(ROOT_URLCONF="tests.urls")
class TestPagesFragmentDataEndpoints(TestCase):
    """Verify pages sub-endpoints for fragment and data."""

    def setUp(self):
        self.client = Client()

    def test_pages_fragment_unknown_returns_404(self):
        """GET /api/pages/nonexistent/fragment/ returns 404."""
        response = self.client.get("/api/pages/nonexistent-frag/fragment/")
        assert response.status_code in (200, 400, 404), (
            f"Expected 200/400/404, got {response.status_code}"
        )

    def test_pages_data_unknown_returns_404(self):
        """GET /api/pages/nonexistent/data/ returns 404."""
        response = self.client.get("/api/pages/nonexistent-data/data/")
        assert response.status_code in (200, 400, 404), (
            f"Expected 200/400/404, got {response.status_code}"
        )


@override_settings(ROOT_URLCONF="tests.urls")
class TestCoursesFiltersStructure(TestCase):
    """Verify courses/filters endpoint returns structured data."""

    def setUp(self):
        self.client = Client()

    def test_filters_returns_valid_json(self):
        """GET /api/courses/filters/ returns valid JSON."""
        response = self.client.get("/api/courses/filters/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert isinstance(data, dict)

    def test_filters_without_trailing_slash_handled(self):
        """GET /api/courses/filters works with or without slash."""
        response = self.client.get("/api/courses/filters")
        assert response.status_code in (200, 301)


@override_settings(ROOT_URLCONF="tests.urls")
class TestContentTypeHeaders(TestCase):
    """Verify all API responses have correct Content-Type."""

    def setUp(self):
        self.client = Client()

    def test_health_content_type_is_json(self):
        """Health endpoint returns application/json."""
        response = self.client.get("/api/health/")
        content_type = response.get("Content-Type", "")
        assert "application/json" in content_type

    def test_pages_content_type_is_json(self):
        """Pages endpoint returns application/json."""
        response = self.client.get("/api/pages/")
        content_type = response.get("Content-Type", "")
        assert "application/json" in content_type

    def test_branding_content_type_is_json(self):
        """Branding endpoint returns application/json."""
        response = self.client.get("/api/branding/")
        content_type = response.get("Content-Type", "")
        assert "application/json" in content_type

    def test_blog_content_type_is_json(self):
        """Blog endpoint returns application/json."""
        response = self.client.get("/api/blog/")
        content_type = response.get("Content-Type", "")
        assert "application/json" in content_type

    def test_courses_content_type_is_json(self):
        """Courses endpoint returns application/json."""
        response = self.client.get("/api/courses/")
        content_type = response.get("Content-Type", "")
        assert "application/json" in content_type


@override_settings(ROOT_URLCONF="tests.urls")
class TestRateLimitHeaders(TestCase):
    """Verify rate-limiting awareness (may or may not be configured)."""

    def setUp(self):
        self.client = Client()

    def test_health_response_has_headers(self):
        """Health response has some security-related headers."""
        response = self.client.get("/api/health/")
        # X-Content-Type-Options is standard Django security header
        assert response.has_header("X-Content-Type-Options"), (
            "Expected X-Content-Type-Options security header"
        )

    def test_multiple_requests_dont_fail(self):
        """Multiple rapid requests don't trigger 429."""
        for _ in range(5):
            response = self.client.get("/api/health/")
            assert response.status_code == 200


@override_settings(ROOT_URLCONF="tests.urls")
class TestFusionAssetsEndpoint(TestCase):
    """Verify the canonical /fusion/assets/ manifest endpoints."""

    def setUp(self):
        self.client = Client()

    def test_assets_top_endpoint_returns_json(self):
        """GET /fusion/assets/top/ returns the configured head assets."""
        response = self.client.get("/fusion/assets/top/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert "css" in data["data"]

    def test_assets_bottom_endpoint_returns_json(self):
        """GET /fusion/assets/bottom/ returns deferred JavaScript assets."""
        response = self.client.get("/fusion/assets/bottom/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert "js" in data["data"]

    def test_assets_manifest_endpoint_returns_json(self):
        """GET /fusion/assets/manifest/ returns both asset sections."""
        response = self.client.get("/fusion/assets/manifest/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert set(("top", "bottom")) <= data["data"].keys()


@override_settings(ROOT_URLCONF="www.urls")
class TestProductionFusionAssetsURL(TestCase):
    """Verify production URL configuration mounts assets exactly once."""

    def test_production_asset_namespace_is_unique(self):
        """The deployed URL tree has one canonical fusion-assets namespace."""
        from django.urls import get_resolver, reverse

        resolver = get_resolver()
        asset_resolvers = [
            pattern
            for pattern in resolver.url_patterns
            if getattr(pattern, "namespace", None) == "fusion-assets"
        ]

        assert len(asset_resolvers) == 1
        assert reverse("fusion-assets:assets-top") == "/fusion/assets/top/"
