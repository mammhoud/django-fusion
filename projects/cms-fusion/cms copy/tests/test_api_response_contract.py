"""Contract tests for LMS list API responses."""

from __future__ import annotations

from django_bolt.testing import TestClient

EXPECTED_LIST_KEYS = {"results", "count", "next", "previous"}


def test_courses_list_uses_frontend_paginated_response_shape(test_api):
    """Course list responses use the same top-level keys as the frontend."""
    with TestClient(test_api) as client:
        resp = client.get("/apis/courses?page=1&page_size=12")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data) == EXPECTED_LIST_KEYS
        assert isinstance(data["results"], list)
        assert isinstance(data["count"], int)
        assert data["next"] is None or isinstance(data["next"], str)
        assert data["previous"] is None or isinstance(data["previous"], str)
