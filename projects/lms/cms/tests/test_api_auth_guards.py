"""Tests for legacy Django JSON API authentication guards."""

from __future__ import annotations

import pytest
from django.test import Client


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/auth/logout/"),
        ("get", "/api/auth/profile/"),
        ("post", "/api/auth/change-password/"),
        ("get", "/api/students/1/enrollments/"),
        ("get", "/api/instructors/1/dashboard/"),
        ("get", "/api/instructors/1/courses/"),
        ("get", "/api/instructors/1/reviews/"),
        ("get", "/api/shop/cart/"),
        ("post", "/api/shop/cart/add/"),
        ("patch", "/api/shop/cart/1/"),
        ("delete", "/api/shop/cart/1/"),
        ("get", "/api/shop/orders/"),
        ("post", "/api/shop/orders/"),
    ],
)
def test_anonymous_user_gets_401_for_guarded_api_routes(method: str, path: str):
    client = Client()
    response = getattr(client, method)(path, data={}, content_type="application/json")

    assert response.status_code == 401
    assert response.json()["status"] == "error"
