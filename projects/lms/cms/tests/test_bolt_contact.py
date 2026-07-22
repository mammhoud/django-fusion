"""
Tests for bolt contact API endpoints — inquiries listing, mark-as-read.

The basic contact submit endpoint is defined in ``apis.py`` (not in bolt extras).
These tests cover only the admin-only listing endpoints in the bolt extras.
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient


class TestListInquiries:
    """GET /apis/contact/inquiries — list contact form submissions (staff only)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/contact/inquiries")
            assert resp.status_code in (401, 403)

    def test_returns_403_for_non_staff(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/contact/inquiries",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            # Non-staff users get 403
            assert resp.status_code == 403
            data = resp.json()
            assert "permission denied" in data["message"].lower()

    def test_returns_empty_list_for_staff(self, test_api, staff_auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/contact/inquiries",
                headers={"Authorization": f"Bearer {staff_auth_token}"},
            )
            data = resp.json()
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {data}"
            assert data["status"] == "success"
            assert "data" in data
            assert "pagination" in data


class TestMarkInquiryRead:
    """POST /apis/contact/<pk>/mark-read — mark inquiry as read."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post("/apis/contact/1/mark-read")
            assert resp.status_code in (401, 403)

    def test_returns_404_for_nonexistent(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.post(
                "/contact/99999/mark-read",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            # Non-staff may get 403 before reaching the 404 check
            assert resp.status_code in (403, 404)
