"""
Tests for auth API endpoints — profile, password change/reset.

Uses ``TestClient`` from django_bolt.testing with a real BoltAPI instance
that has all handlers registered.
"""

from __future__ import annotations

import json

import pytest
from django_bolt.testing import TestClient


class TestGetProfile:
    """GET /apis/auth/profile — return authenticated user profile."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/auth/profile")
            assert resp.status_code == 401
            data = resp.json()
            assert data["status"] == "error"

    def test_returns_profile_with_valid_token(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.get(
                "/auth/profile",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            profile = data["data"]
            assert profile["id"] == test_user.pk
            assert profile["email"] == "test@example.com"
            assert profile["first_name"] == "Test"
            assert profile["last_name"] == "User"
            assert profile["username"] == "testuser"

    def test_profile_includes_role_and_bio(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.get(
                "/auth/profile",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert "role" in data
            assert "bio" in data
            assert "date_joined" in data
            assert "last_login" in data


class TestUpdateProfile:
    """PATCH /apis/auth/profile — update current user profile fields."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.patch(
                "/auth/profile",
                json={"first_name": "Updated"},
            )
            assert resp.status_code == 401

    def test_updates_name_fields(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.patch(
                "/auth/profile",
                json={"first_name": "UpdatedFirst", "last_name": "UpdatedLast"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["first_name"] == "UpdatedFirst"
            assert data["last_name"] == "UpdatedLast"

        # Verify persisted
        test_user.refresh_from_db()
        assert test_user.first_name == "UpdatedFirst"
        assert test_user.last_name == "UpdatedLast"

    def test_updates_email(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.patch(
                "/auth/profile",
                json={"email": "newemail@example.com"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["data"]["email"] == "newemail@example.com"

        test_user.refresh_from_db()
        assert test_user.email == "newemail@example.com"

    def test_ignores_unknown_fields(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.patch(
                "/auth/profile",
                json={"first_name": "Valid", "unknown_field": "should_be_ignored"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["data"]["first_name"] == "Valid"


class TestPasswordReset:
    """POST /apis/auth/password-reset — send reset email."""

    def test_returns_success_even_for_unknown_email(self, test_api):
        """Security: don't leak whether an email exists."""
        with TestClient(test_api) as client:
            resp = client.post(
                "/auth/password-reset",
                json={"email": "nonexistent@example.com"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"

    def test_requires_email(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post("/apis/auth/password-reset", json={})
            assert resp.status_code == 400
            assert "Email is required" in resp.text


class TestChangePassword:
    """POST /apis/auth/change-password — change current user password."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post(
                "/auth/change-password",
                json={"old_password": "x", "new_password": "y"},
            )
            assert resp.status_code == 401

    def test_changes_password_with_valid_old(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.post(
                "/auth/change-password",
                json={"old_password": "password123", "new_password": "newpass1234"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "success"

        # Verify new password works
        test_user.refresh_from_db()
        assert test_user.check_password("newpass1234")
        assert not test_user.check_password("password123")

    def test_rejects_wrong_old_password(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.post(
                "/auth/change-password",
                json={"old_password": "wrongpass", "new_password": "newpass1234"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            assert "incorrect" in resp.json()["message"].lower()

    def test_rejects_short_new_password(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.post(
                "/auth/change-password",
                json={"old_password": "password123", "new_password": "short"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            assert "8 characters" in resp.json()["message"]

    def test_requires_both_fields(self, test_api, auth_token, test_user):
        with TestClient(test_api) as client:
            resp = client.post(
                "/auth/change-password",
                json={"old_password": "password123"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
