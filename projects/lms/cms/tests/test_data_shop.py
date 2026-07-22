"""
Tests for bolt shop API endpoints — products, cart, orders.
"""

from __future__ import annotations

import pytest
from django_bolt.testing import TestClient


class TestListProducts:
    """GET /apis/shop/products — paginated product list."""

    def test_returns_empty_list_when_no_products(self, test_api):
        """Graceful empty-state: no products → empty list."""
        with TestClient(test_api) as client:
            resp = client.get("/apis/shop/products")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "pagination" in data

    def test_pagination_structure(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/shop/products?page=1&per_page=5")
            data = resp.json()
            assert data["pagination"]["page"] == 1
            assert data["pagination"]["per_page"] == 5
            assert "total" in data["pagination"]
            assert "total_pages" in data["pagination"]

    def test_search_param_passed(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/shop/products?search=course")
            assert resp.status_code == 200

    def test_category_filter(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/shop/products?category=books")
            assert resp.status_code == 200


class TestGetProduct:
    """GET /apis/shop/products/<pk> — single product detail."""

    def test_returns_404_for_nonexistent(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/shop/products/99999")
            assert resp.status_code == 404


class TestCart:
    """GET /apis/shop/cart — current user's cart (auth required)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/shop/cart")
            assert resp.status_code == 401

    def test_returns_empty_cart_for_authenticated(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/shop/cart",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            data = resp.json()
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {data}"
            assert data["status"] == "success"
            assert "results" in data
            assert isinstance(data["results"], list)


class TestAddToCart:
    """POST /apis/shop/cart/add — add item to cart (auth required)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post(
                "/shop/cart/add",
                json={"product_id": 1, "quantity": 1},
            )
            assert resp.status_code == 401

    def test_requires_product_id(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.post(
                "/shop/cart/add",
                json={"quantity": 1},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
            assert "product_id" in resp.text.lower()


class TestOrders:
    """GET /apis/shop/orders — list user orders (auth required)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.get("/apis/shop/orders")
            assert resp.status_code == 401

    def test_returns_empty_orders_list(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.get(
                "/shop/orders",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            data = resp.json()
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {data}"
            assert data["status"] == "success"
            assert "data" in data
            assert "pagination" in data


class TestCreateOrder:
    """POST /apis/shop/orders — create order (auth required)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post(
                "/shop/orders",
                json={"shipping_address": "123 test", "payment_method": "card"},
            )
            assert resp.status_code == 401


class TestCheckout:
    """POST /apis/shop/cart/checkout — checkout (auth required)."""

    def test_returns_401_when_unauthenticated(self, test_api):
        with TestClient(test_api) as client:
            resp = client.post(
                "/shop/cart/checkout",
                json={"shipping_address": "test", "payment_method": "card"},
            )
            assert resp.status_code == 401

    def test_requires_shipping_address_and_payment(self, test_api, auth_token):
        with TestClient(test_api) as client:
            resp = client.post(
                "/shop/cart/checkout",
                json={},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert resp.status_code == 400
