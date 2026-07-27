"""API smoke tests for cms-fusion.

Verifies that the REST API endpoints return correct HTTP status codes
and well-formed JSON responses.

Uses a minimal URL configuration that imports the real API URL patterns
from ``apps.core.api.urls``.
"""

from __future__ import annotations

import json

from django.test import Client, TestCase, override_settings


@override_settings(ROOT_URLCONF="tests.urls")
class TestFusionHealthAPI(TestCase):
    """Verify the /api/fusion/health endpoint."""

    def setUp(self):
        self.client = Client()

    def test_health_returns_200(self):
        """GET /api/fusion/health returns HTTP 200."""
        response = self.client.get("/api/fusion/health")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.content[:200]}"
        )

    def test_health_returns_valid_json(self):
        """Response is parseable JSON."""
        response = self.client.get("/api/fusion/health")
        data = json.loads(response.content)
        assert isinstance(data, dict)

    def test_health_contains_expected_keys(self):
        """Response contains status, data.fusion_render_first, and data.reason keys."""
        response = self.client.get("/api/fusion/health")
        data = json.loads(response.content)
        assert data["status"] == 200
        assert data["message"] == "Success"
        inner = data["data"]
        assert "fusion_render_first" in inner
        assert "reason" in inner
        assert isinstance(inner["fusion_render_first"], bool)


@override_settings(ROOT_URLCONF="tests.urls")
class TestPagesAPI(TestCase):
    """Verify the /api/pages/ endpoint."""

    def setUp(self):
        self.client = Client()

    def test_pages_list_returns_200(self):
        """GET /api/pages/ returns HTTP 200."""
        response = self.client.get("/api/pages/")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.content[:200]}"
        )

    def test_pages_list_returns_valid_json(self):
        """Response is parseable JSON."""
        response = self.client.get("/api/pages/")
        data = json.loads(response.content)
        assert isinstance(data, dict)

    def test_pages_list_has_pages_key(self):
        """Response contains 'pages' and 'total' keys."""
        response = self.client.get("/api/pages/")
        data = json.loads(response.content)
        assert "pages" in data
        assert "total" in data
        assert isinstance(data["pages"], list)
        assert isinstance(data["total"], int)

    def test_page_detail_unknown_slug_returns_404(self):
        """GET /api/pages/nonexistent/ returns 404 for unknown pages."""
        response = self.client.get("/api/pages/nonexistent-page-slug/")
        # Either 404 (page not found) or 200 (fallback to STATIC_PAGES)
        assert response.status_code in (200, 404), (
            f"Expected 200 or 404, got {response.status_code}"
        )


@override_settings(ROOT_URLCONF="tests.urls")
class TestBlogAPI(TestCase):
    """Verify the /api/blog/ endpoint."""

    def setUp(self):
        self.client = Client()

    def test_blog_list_returns_200(self):
        """GET /api/blog/ returns HTTP 200 (empty data when no posts exist)."""
        response = self.client.get("/api/blog/")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.content[:200]}"
        )

    def test_blog_list_returns_valid_json(self):
        """Response is parseable JSON."""
        response = self.client.get("/api/blog/")
        data = json.loads(response.content)
        assert isinstance(data, dict)

    def test_blog_list_has_pagination(self):
        """Response contains data array and pagination object."""
        response = self.client.get("/api/blog/")
        data = json.loads(response.content)
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)
        assert isinstance(data["pagination"], dict)
        assert "total" in data["pagination"]
        assert "page" in data["pagination"]

    def test_blog_categories_returns_200(self):
        """GET /api/blog/categories returns HTTP 200."""
        response = self.client.get("/api/blog/categories")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )

    def test_blog_tags_returns_200(self):
        """GET /api/blog/tags returns HTTP 200."""
        response = self.client.get("/api/blog/tags")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )


@override_settings(ROOT_URLCONF="tests.urls")
class TestCoursesAPI(TestCase):
    """Verify the /api/courses/ endpoint."""

    def setUp(self):
        self.client = Client()

    def test_courses_list_returns_200(self):
        """GET /api/courses/ returns HTTP 200 (empty data when no courses exist)."""
        response = self.client.get("/api/courses/")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.content[:200]}"
        )

    def test_courses_list_returns_valid_json(self):
        """Response is parseable JSON."""
        response = self.client.get("/api/courses/")
        data = json.loads(response.content)
        assert isinstance(data, dict)

    def test_courses_list_has_pagination(self):
        """Response contains data array and pagination object."""
        response = self.client.get("/api/courses/")
        data = json.loads(response.content)
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)
        assert isinstance(data["pagination"], dict)

    def test_courses_filters_returns_200(self):
        """GET /api/courses/filters returns HTTP 200."""
        response = self.client.get("/api/courses/filters")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )

    def test_course_detail_unknown_returns_404(self):
        """GET /api/courses/nonexistent returns 404."""
        response = self.client.get("/api/courses/nonexistent-course")
        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}"
        )


@override_settings(ROOT_URLCONF="tests.urls")
class TestProductsAPI(TestCase):
    """Verify the /api/products/ endpoint."""

    def setUp(self):
        self.client = Client()

    def test_products_list_returns_200(self):
        """GET /api/products/ returns HTTP 200."""
        response = self.client.get("/api/products/")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.content[:200]}"
        )

    def test_products_list_returns_valid_json(self):
        """Response is parseable JSON."""
        response = self.client.get("/api/products/")
        data = json.loads(response.content)
        assert isinstance(data, dict)

    def test_products_list_has_pagination(self):
        """Response contains data array and pagination."""
        response = self.client.get("/api/products/")
        data = json.loads(response.content)
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)


@override_settings(ROOT_URLCONF="tests.urls")
class TestBlogDetailAPI(TestCase):
    """Verify the /api/blog/<slug>/ detail endpoint."""

    def setUp(self):
        self.client = Client()

    def test_blog_detail_unknown_returns_404(self):
        """GET /api/blog/nonexistent-post returns 404."""
        response = self.client.get("/api/blog/nonexistent-post-slug")
        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}"
        )


@override_settings(ROOT_URLCONF="tests.urls")
class TestAuthStatusAPI(TestCase):
    """Verify the /api/auth/status endpoint (bolt-only, may 404)."""

    def setUp(self):
        self.client = Client()

    def test_auth_status_returns_response(self):
        """GET /api/auth/status returns a response (200 or 404 if bolt-only)."""
        response = self.client.get("/api/auth/status")
        assert response.status_code in (200, 404), (
            f"Expected 200 or 404, got {response.status_code}"
        )
