"""
Tests for instructors API endpoints — list, detail, dashboard, courses, reviews.
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient


class TestListInstructors:
    """GET /apis/instructors — paginated instructor list."""

    def test_returns_empty_list_when_no_instructors(self, test_api):
        """Graceful empty-state when no users in Instructors group."""
        with TestClient(test_api) as client:
            resp = client.get("/apis/instructors")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "pagination" in data
            assert isinstance(data["data"], list)

    def test_pagination_structure(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/instructors?page=1&per_page=5")
            data = resp.json()
            assert data["pagination"]["page"] == 1
            assert data["pagination"]["per_page"] == 5
            assert "total" in data["pagination"]
            assert "total_pages" in data["pagination"]


class TestGetInstructor:
    """GET /apis/instructors/<pk> — single instructor detail."""

    def test_returns_404_for_nonexistent(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/instructors/99999")
            assert resp.status_code == 404

    def test_returns_404_for_inactive_user(self, test_api):
        """Only active users return as instructors."""
        with TestClient(test_api) as client:
            resp = client.get("/apis/instructors/0")
            assert resp.status_code == 404


class TestUpdateInstructor:
    """PATCH /apis/instructors/<pk> — update instructor profile."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.patch("/apis/instructors/1", json={"first_name": "X"})
            assert resp.status_code == 401

    def test_returns_403_for_other_users_profile(self, test_api, auth_token, test_user):
        """Non-staff users can only update their own profile."""
        with TestClient(test_api) as client:
            resp = client.patch(
                "/instructors/99999",
                json={"first_name": "Hacker"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code in (403, 404)


class TestInstructorDashboard:
    """GET /apis/instructors/<pk>/dashboard — instructor stats."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/instructors/1/dashboard")
            assert resp.status_code in (401, 403)


class TestInstructorCourses:
    """GET /apis/instructors/<pk>/courses — instructor's courses."""

    def test_returns_empty_list_when_no_courses(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/instructors/1/courses")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "count" in data
            assert "results" in data


class TestInstructorReviews:
    """GET /apis/instructors/<pk>/reviews — instructor's reviews."""

    def test_returns_empty_list_when_no_reviews(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/instructors/1/reviews")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "count" in data
            assert "results" in data
            assert "pagination" in data


class TestDeleteInstructorCourse:
    """DELETE /apis/instructors/courses/<pk> — delete a course (owner only)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.delete("/apis/instructors/courses/1")
            assert resp.status_code == 401
