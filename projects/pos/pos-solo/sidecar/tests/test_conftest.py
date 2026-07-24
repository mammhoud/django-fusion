"""
Smoke tests for the conftest.py factory fixtures and mock utilities.

Uses plain pytest functions (not unittest TestCase) so that fixture
injection works without pytest-django. The ``django_bootstrap``
session-scoped fixture in conftest.py handles Django setup.
"""

from __future__ import annotations

import json

import pytest


# ══════════════════════════════════════════════════════════════════════════
# Factory fixture smoke tests
# ══════════════════════════════════════════════════════════════════════════

class TestNodeFactory:
    def test_with_custom_id(self, node_factory):
        node = node_factory(node_id="smoke-node")
        assert node.node_id == "smoke-node"
        assert node.status == "online"

    def test_defaults(self, node_factory):
        node = node_factory()
        assert node.node_id.startswith("test-node-")
        assert node.status == "online"


class TestProductFactory:
    def test_with_custom_name(self, product_factory):
        p = product_factory(name="Test Latte", price=4.50)
        assert p.name == "Test Latte"
        assert float(p.price) == 4.50

    def test_defaults(self, product_factory):
        p = product_factory()
        assert p.name.startswith("Product-")
        assert float(p.price) == 9.99


class TestCustomerFactory:
    def test_with_custom_fields(self, customer_factory):
        c = customer_factory(first_name="Alice", email="alice@test.com")
        assert c.first_name == "Alice"
        assert c.email == "alice@test.com"
        assert c.is_active is True


class TestSaleFactory:
    def test_with_explicit_customer(self, sale_factory, customer_factory):
        c = customer_factory()
        sale = sale_factory(customer=c, subtotal=50.00, total=55.00)
        assert sale.customer_id == c.id
        assert float(sale.subtotal) == 50.00

    def test_auto_creates_customer(self, sale_factory):
        sale = sale_factory()
        assert sale.customer is not None
        assert float(sale.subtotal) == 19.99


class TestEmployeeFactory:
    def test_with_custom_role(self, employee_factory):
        emp = employee_factory(first_name="Bob", role="manager")
        assert emp.first_name == "Bob"
        assert emp.role == "manager"


class TestIngredientFactory:
    def test_with_custom_name(self, ingredient_factory):
        ing = ingredient_factory(name="Coffee Beans", unit="kg")
        assert ing.name == "Coffee Beans"
        assert ing.unit == "kg"


class TestRoleFactory:
    def test_with_custom_name(self, role_factory):
        role = role_factory(name="Admin")
        assert role.name == "Admin"
        assert role.permissions.get("can_manage_products") is True


class TestCategoryFactory:
    def test_with_custom_name(self, category_factory):
        cat = category_factory(name="Beverages")
        assert cat.name == "Beverages"


class TestSyncLogFactory:
    def test_with_custom_fields(self, sync_log_factory):
        log = sync_log_factory(node_id="node-1", entity_type="sale")
        assert log.node_id == "node-1"
        assert log.entity_type == "sale"
        assert log.status == "success"


# ══════════════════════════════════════════════════════════════════════════
# Mock utilities smoke tests
# ══════════════════════════════════════════════════════════════════════════

class TestMockRequest:
    """Smoke tests for the MockRequest factory."""

    def test_basic_json_body(self, mock_request):
        req = mock_request(method="POST", body='{"key": "val"}')
        assert req.method == "POST"
        data = req.json_body()
        assert data == {"key": "val"}

    def test_empty_body(self, mock_request):
        req = mock_request()
        data = req.json_body()
        assert data == {}

    def test_headers(self, mock_request):
        req = mock_request(headers={"Authorization": "Bearer token123"})
        assert req.headers["Authorization"] == "Bearer token123"

    def test_query_params(self, mock_request):
        req = mock_request(query={"page": "1"})
        assert req.query_params["page"] == "1"

    def test_factory_returns_fresh_instance_per_call(self, mock_request):
        """Each call to the factory creates a new instance."""
        r1 = mock_request()
        r2 = mock_request()
        assert r1 is not r2


class TestMockResponse:
    """Smoke tests for the MockResponse factory.

    ``mock_response`` returns the ``MockResponse`` class, so each test
    creates its own instance via ``mock_response()``.
    """

    def test_basic_usage(self, mock_response):
        """Verify status, headers, and JSON body round-trip."""
        resp = mock_response()
        resp.set_status(201)
        resp.set_header("X-Custom", "val")

        import asyncio
        asyncio.run(resp.respond(json.dumps({"id": 1}), status_code=201))

        assert resp.status_code == 201
        data = resp.json()
        assert data == {"id": 1}

    def test_default_status(self, mock_response):
        """Verify default status is 200."""
        resp = mock_response()
        assert resp.status_code == 200

    def test_factory_returns_fresh_instance_per_call(self, mock_response):
        """Each call to the factory creates a new instance."""
        r1 = mock_response()
        r2 = mock_response()
        assert r1 is not r2

    def test_respond_accepts_bytes(self, mock_response):
        """respond() handles bytes input and decodes to str."""
        resp = mock_response()
        import asyncio
        asyncio.run(resp.respond(b'{"key": "val"}'))
        assert resp.body == '{"key": "val"}'
        assert resp.json() == {"key": "val"}
