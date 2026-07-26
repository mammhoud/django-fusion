"""
Tests for blog API endpoints — detail, featured, related posts, categories.
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient


class TestGetBlogPost:
    """GET /apis/blog/<pk> — single blog post detail."""

    def test_returns_404_for_nonexistent(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/99999")
            assert resp.status_code == 404
            data = resp.json()
            assert data["status"] == "error"

    def test_error_message(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/99999")
            assert "not found" in resp.json()["message"].lower()


class TestFeaturedPosts:
    """GET /apis/blog/featured — featured blog posts."""

    def test_returns_empty_list_when_no_posts(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/featured")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "count" in data
            assert "results" in data
            assert isinstance(data["results"], list)

    def test_structure(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/featured")
            data = resp.json()
            assert "status" in data
            assert "count" in data
            assert "results" in data


class TestRelatedPosts:
    """GET /apis/blog/<pk>/related — related posts."""

    def test_returns_404_for_nonexistent_post(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/99999/related")
            assert resp.status_code == 404

    def test_returns_empty_for_unknown_related(self, test_api):
        """Without a matching post, we can't test related posts.
        Just verify the endpoint is registered and reachable."""
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/1/related")
            if resp.status_code == 404:
                assert "not found" in resp.json()["message"].lower()


class TestBlogCategories:
    """GET /apis/blog/categories — blog categories."""

    def test_returns_categories(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/categories")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "count" in data
            assert "results" in data
            # Empty categories list is valid
            assert isinstance(data["results"], list)

    def test_category_structure(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/blog/categories")
            data = resp.json()
            if len(data["results"]) > 0:
                cat = data["results"][0]
                assert "id" in cat
                assert "name" in cat
                assert "slug" in cat
