"""Tests for the POS Full django-bolt API.

These tests use Django's AsyncClient against a URLconf that mounts the
BoltAPI under ``/bolt/``. The Django settings are configured by the
session-scoped ``django_bootstrap`` fixture in ``conftest.py``.
"""

from __future__ import annotations

import os
import time

import pytest
import jwt
from django.conf import settings
from django.test import AsyncClient

# Ensure a stable API key for the test session before bolt_api is imported.
os.environ.setdefault("POS_FULL_API_KEY", "test-api-key")

from models.pos import Category, Product  # noqa: E402


URLCONF = "tests.bolt_urlconf"


def _api_key_headers():
    return {"X-API-Key": "test-api-key"}


def _jwt_headers():
    token = jwt.encode(
        {
            "sub": "1",
            "exp": int(time.time()) + 300,
            "iat": int(time.time()),
            "is_staff": True,
            "is_superuser": True,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_health_requires_no_auth(django_bootstrap):
    client = AsyncClient(urlconf=URLCONF)
    response = await client.get("/bolt/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_list_products_requires_auth(django_bootstrap):
    client = AsyncClient(urlconf=URLCONF)
    response = await client.get("/bolt/products")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_products_with_api_key(django_bootstrap, product_factory):
    product = product_factory(name="Bolt Test Product", price=12.99)
    client = AsyncClient(urlconf=URLCONF)
    response = await client.get("/bolt/products", headers=_api_key_headers())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["name"] == "Bolt Test Product" for item in data)


@pytest.mark.asyncio
async def test_list_products_with_jwt(django_bootstrap, product_factory):
    product_factory(name="JWT Product", price=5.00)
    client = AsyncClient(urlconf=URLCONF)
    response = await client.get("/bolt/products", headers=_jwt_headers())
    assert response.status_code == 200
    data = response.json()
    assert any(item["name"] == "JWT Product" for item in data)


@pytest.mark.asyncio
async def test_create_and_retrieve_product(django_bootstrap, category_factory):
    category = category_factory(name="Beverages")
    client = AsyncClient(urlconf=URLCONF)
    payload = {
        "name": "Latte",
        "price": 4.50,
        "category_id": category.id,
        "sku": "LAT-001",
        "stock_quantity": 100,
    }
    response = await client.post(
        "/bolt/products",
        data=payload,
        content_type="application/json",
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    created = response.json()
    assert created["name"] == "Latte"
    assert created["price"] == "4.50"
    assert created["category_id"] == category.id

    response = await client.get(
        f"/bolt/products/{created['id']}",
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    retrieved = response.json()
    assert retrieved["name"] == "Latte"


@pytest.mark.asyncio
async def test_update_and_delete_product(django_bootstrap, product_factory):
    product = product_factory(name="Old Name", price=1.00)
    client = AsyncClient(urlconf=URLCONF)
    response = await client.patch(
        f"/bolt/products/{product.id}",
        data={"name": "New Name", "price": 2.00},
        content_type="application/json",
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "New Name"
    assert updated["price"] == "2.00"

    response = await client.delete(
        f"/bolt/products/{product.id}",
        headers=_api_key_headers(),
    )
    assert response.status_code == 204

    response = await client.get(
        f"/bolt/products/{product.id}",
        headers=_api_key_headers(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_category_and_list(django_bootstrap):
    client = AsyncClient(urlconf=URLCONF)
    response = await client.post(
        "/bolt/categories",
        data={"name": "Pastries"},
        content_type="application/json",
        headers=_api_key_headers(),
    )
    assert response.status_code == 200
    created = response.json()
    assert created["name"] == "Pastries"
    assert created["slug"].startswith("pastries")

    response = await client.get("/bolt/categories", headers=_api_key_headers())
    assert response.status_code == 200
    data = response.json()
    assert any(item["name"] == "Pastries" for item in data)
