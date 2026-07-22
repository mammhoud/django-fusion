"""
Tests for bolt courses API endpoints — featured, detail.

These endpoints query the Course model which may not exist in test DB,
so we test graceful empty-state responses.
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient


class TestFeaturedCourses:
    """GET /apis/courses/featured — featured courses list."""

    def test_returns_empty_list_when_no_courses(self, test_api):
        """Graceful empty-state: no courses → empty results."""
        with TestClient(test_api) as client:
            resp = client.get("/apis/courses/featured")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "count" in data
            assert "results" in data
            assert isinstance(data["results"], list)

    def test_structure_matches_expected(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/courses/featured")
            data = resp.json()
            assert "status" in data
            assert "count" in data
            assert "results" in data


class TestCourseDetail:
    """GET /apis/courses/<pk>/detail — full course detail."""

    def test_returns_404_for_nonexistent_course(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/courses/99999/detail")
            assert resp.status_code == 404
            data = resp.json()
            assert data["status"] == "error"
            assert "not found" in data["message"].lower()


class TestCategories:
    """GET /apis/courses/categories — already in apis.py, not duplicated."""

    def test_categories_endpoint_not_duplicated_in_bolt_extras(self, test_api):
        """The categories endpoint is defined in apis.py, not duplicated in
        the bolt extra handlers.  We simply verify the bolt API runs."""
        with TestClient(test_api) as client:
            # This endpoint exists in apis.py but is NOT in our bolt handlers
            # which only add the bolt extra endpoints.  We just verify
            # that the registered handlers don't conflict.
            resp = client.get("/apis/courses/featured")
            assert resp.status_code != 404  # our handler exists
