"""
Tests for students API endpoints — dashboard, enrollments, progress.
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient


class TestStudentDashboard:
    """GET /apis/students/<pk>/dashboard — student dashboard stats."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/students/1/dashboard")
            assert resp.status_code in (401, 403)

    def test_returns_403_when_accessing_other_users(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/students/99999/dashboard",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            # 99999 doesn't match our test user (id=1) and isn't staff
            assert resp.status_code == 403

    def test_returns_dashboard_for_own_user(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.get(
                f"/students/{test_user.pk}/dashboard",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            data = resp.json()
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {data}"
            assert data["status"] == "success"
            assert "enrolled_courses" in data["data"]
            assert "completed_courses" in data["data"]
            assert "total_hours" in data["data"]

    def test_staff_can_access_any_student(self, test_api, staff_auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.get(
                f"/students/{test_user.pk}/dashboard",
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            data = resp.json()
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {data}"


class TestStudentEnrollments:
    """GET /apis/students/<pk>/enrollments — student enrollments list."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/students/1/enrollments")
            assert resp.status_code in (401, 403)

    def test_returns_enrollments_for_own_user(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.get(
                f"/students/{test_user.pk}/enrollments",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            data = resp.json()
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {data}"
            assert data["status"] == "success"
            assert "data" in data
            assert "pagination" in data


class TestCreateEnrollment:
    """POST /apis/enrollments — create enrollment (auth required)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post("/apis/enrollments", json={"course_id": 1})
            assert resp.status_code == 401

    def test_requires_course_id(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.post(
                "/enrollments",
                json={},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            assert "course_id" in resp.text.lower()

    def test_returns_404_for_nonexistent_course(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.post(
                "/enrollments",
                json={"course_id": 99999},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 404


class TestEnrollmentProgress:
    """GET|POST /apis/enrollments/<pk>/progress — lesson progress."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/enrollments/1/progress")
            assert resp.status_code == 401

    def test_returns_404_for_nonexistent_enrollment(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/enrollments/99999/progress",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 404

    def test_post_requires_lesson_id(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.post(
                "/enrollments/1/progress",
                json={"time_spent": 30},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            assert "lesson_id" in resp.text.lower()
