"""
Tests for bolt events API endpoints — detail, upcoming, registration.
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient


class TestGetEvent:
    """GET /apis/events/<pk> — single event detail."""

    def test_returns_404_for_nonexistent(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/events/99999")
            assert resp.status_code == 404
            data = resp.json()
            assert data["status"] == "error"

    def test_error_message(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/events/99999")
            assert "not found" in resp.json()["message"].lower()


class TestUpcomingEvents:
    """GET /apis/events/upcoming — upcoming events."""

    def test_returns_empty_list_when_no_events(self, test_api):
        """Graceful empty-state: no events → empty results."""
        with TestClient(test_api) as client:
            resp = client.get("/apis/events/upcoming")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "count" in data
            assert "results" in data
            assert isinstance(data["results"], list)

    def test_response_structure(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/events/upcoming")
            data = resp.json()
            assert "status" in data
            assert "count" in data
            assert "results" in data


class TestRegisterForEvent:
    """POST /apis/events/register — register for an event."""

    def test_requires_event_id_full_name_and_email(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post("/apis/events/register", json={})
            assert resp.status_code == 400
            data = resp.json()
            assert "event_id" in data["message"]
            assert "full_name" in data["message"]
            assert "email" in data["message"]

    def test_requires_full_name(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post(
                "/events/register",
                json={"event_id": 1, "email": "test@example.com"},
            )
            assert resp.status_code == 400
            assert "full_name" in resp.json()["message"]

    def test_returns_404_for_nonexistent_event(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post(
                "/events/register",
                json={
                    "event_id": 99999,
                    "full_name": "Test User",
                    "email": "test@example.com",
                },
            )
            assert resp.status_code == 404
