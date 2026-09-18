"""
Inventory Forecasting (P3) — reorder-point/safety-stock plan + draft POs.

Covers the superset added on top of ``services.forecast.stock_advisory``:
  * ``inventory_plan`` — reorder point (lead demand + safety stock),
    projected stock-out date, needs_reorder flags, summary aggregation.
  * ``generate_reorder_orders`` — explicit operator action materializing the
    advisory into ``PurchaseOrder`` drafts (status=draft, cost from product,
    no stock movement); empty-plan and missing-supplier branches.

Plus endpoint tests for ``/forecast/inventory`` and
``/forecast/inventory/reorder`` (RequestFactory — the conftest bootstrap is
ORM-first and does not resolve the full URLconf).

Models are imported lazily (the conftest ``django_bootstrap`` fixture
configures Django first).
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from django.utils import timezone


def _svc():
    import services.forecast as f

    return f


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.inventory import PurchaseOrderItem, PurchaseOrder, Supplier
    from models.pos import InventoryTransaction, SaleItem, Sale
    PurchaseOrderItem.objects.all().delete()
    PurchaseOrder.objects.all().delete()
    Supplier.objects.all().delete()
    InventoryTransaction.objects.all().delete()
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    yield


def _product(name="Espresso", price=3.5, cost=1.2, stock=100, threshold=10, sku=None, **kw):
    from models.pos import Product

    return Product.objects.create(
        name=name, price=price, cost_price=cost, stock_quantity=stock,
        low_stock_threshold=threshold, sku=sku, **kw,
    )


def _sale_with_items(product, days_ago=1, qty=10):
    from models.pos import Customer, Sale, SaleItem

    sale = Sale.objects.create(
        customer=Customer.objects.create(
            first_name="IF", last_name="Test", email=f"if{days_ago}@t.com",
        ),
        subtotal=product.price * qty, total=product.price * qty,
        tax_amount=0, status="completed",
        sale_date=timezone.now() - timedelta(days=days_ago),
    )
    SaleItem.objects.create(
        sale=sale, product=product, product_name=product.name,
        quantity=qty, unit_price=product.price,
        line_total=round(product.price * qty, 2),
    )
    return sale


def _seed_demand(product, days=28, qty=10):
    """Create completed sales across the lookback window (daily demand = qty)."""
    for d in range(1, days + 1):
        _sale_with_items(product, days_ago=d, qty=qty)


class TestInventoryPlan:
    def test_plan_shape_and_reorder_point_math(self):
        p = _product("Espresso", cost=1.2, stock=100, threshold=10)
        _seed_demand(p, days=28, qty=10)  # daily demand 10
        plan = _svc().inventory_plan(lead_time_days=3, safety_factor=0.5)
        row = next(r for r in plan["products"] if r["product_name"] == "Espresso")
        # lead 3d × 10 = 30; safety = 30 × 0.5 = 15; reorder point = 45
        assert row["lead_demand"] == 30.0
        assert row["safety_stock"] == 15.0
        assert row["reorder_point"] == 45.0
        assert row["current_stock"] == 100
        assert row["needs_reorder"] is False
        assert row["projected_stock_out_in_days"] == 10

    def test_plan_flags_stock_below_reorder_point(self):
        p = _product("Espresso", cost=1.2, stock=40, threshold=10)
        _seed_demand(p, days=28, qty=10)
        plan = _svc().inventory_plan(lead_time_days=3, safety_factor=0.5)
        row = next(r for r in plan["products"] if r["product_name"] == "Espresso")
        assert row["needs_reorder"] is True
        assert row["reason"] == "at/below reorder point"
        assert row["suggested_order_quantity"] > 0

    def test_plan_flags_out_of_stock_first(self):
        p = _product("Espresso", cost=1.2, stock=0, threshold=10)
        _seed_demand(p, days=28, qty=10)
        plan = _svc().inventory_plan(lead_time_days=3)
        row = next(r for r in plan["products"] if r["product_name"] == "Espresso")
        assert row["needs_reorder"] is True
        assert row["reason"] == "out of stock"
        assert row["projected_stock_out_in_days"] == 0

    def test_plan_summary_counts(self):
        p1 = _product("Low Stock", cost=1.0, stock=5, threshold=10)
        p2 = _product("Healthy", cost=1.0, stock=200, threshold=10)
        _seed_demand(p1, days=28, qty=10)
        _seed_demand(p2, days=28, qty=10)
        plan = _svc().inventory_plan(lead_time_days=3)
        assert plan["summary"]["products_planned"] == 2
        assert plan["summary"]["needs_reorder"] == 1
        assert plan["summary"]["projected_stock_out"] == 1

    def test_plan_stays_advisory(self):
        from models.pos import Sale

        p = _product(stock=5, threshold=10)
        _seed_demand(p, days=28, qty=10)
        before = Sale.objects.count()
        _svc().inventory_plan(lead_time_days=3)
        assert Sale.objects.count() == before


class TestGenerateReorderOrders:
    def test_creates_draft_po(self):
        from models.inventory import PurchaseOrder, PurchaseOrderItem

        s = _make_supplier("Acme")
        p = _product("Espresso", cost=1.2, stock=20, threshold=10)
        _seed_demand(p, days=28, qty=10)
        result = _svc().generate_reorder_orders(
            lead_time_days=3, safety_factor=0.5, supplier_id=s.id,
        )
        assert result["created_orders"] == 1
        po = PurchaseOrder.objects.get(id=result["orders"][0]["id"])
        assert po.status == "draft"
        assert po.supplier_id == s.id
        assert po.items.count() == 1
        item = PurchaseOrderItem.objects.get(purchase_order=po)
        assert item.product_id == p.id
        assert item.quantity > 0
        assert float(item.cost_per_unit) == 1.2
        assert float(po.total_amount) == float(item.cost_per_unit) * item.quantity

    def test_creates_po_for_every_reorder_product(self):
        s = _make_supplier("Acme")
        p1 = _product("Low A", cost=1.0, stock=5, threshold=10)
        p2 = _product("Low B", cost=2.0, stock=8, threshold=10)
        _seed_demand(p1, days=28, qty=10)
        _seed_demand(p2, days=28, qty=10)
        result = _svc().generate_reorder_orders(
            lead_time_days=3, supplier_id=s.id,
        )
        assert result["created_orders"] == 1
        assert result["orders"][0]["item_count"] == 2

    def test_healthy_plan_creates_nothing(self):
        s = _make_supplier("Acme")
        p = _product("Healthy", cost=1.0, stock=500, threshold=10)
        _seed_demand(p, days=28, qty=10)
        result = _svc().generate_reorder_orders(
            lead_time_days=3, supplier_id=s.id,
        )
        assert result["created_orders"] == 0
        assert result["orders"] == []

    def test_missing_supplier_raises(self):
        p = _product("Espresso", cost=1.0, stock=5, threshold=10)
        _seed_demand(p, days=28, qty=10)
        with pytest.raises(ValueError, match="No active supplier"):
            _svc().generate_reorder_orders(lead_time_days=3)

    def test_draft_does_not_move_stock(self):
        s = _make_supplier("Acme")
        p = _product("Espresso", cost=1.0, stock=5, threshold=10)
        _seed_demand(p, days=28, qty=10)
        before = p.stock_quantity
        _svc().generate_reorder_orders(lead_time_days=3, supplier_id=s.id)
        p.refresh_from_db()
        assert p.stock_quantity == before


def _make_supplier(name="Acme"):
    from models.inventory import Supplier

    return Supplier.objects.create(name=name, is_active=True)


class TestEndpoints:
    @pytest.fixture
    def rf(self):
        from django.test import RequestFactory

        return RequestFactory()

    def test_inventory_endpoint(self, rf):
        from views_django import forecast_inventory

        p = _product("Espresso", stock=5, threshold=10)
        _seed_demand(p, days=28, qty=10)
        resp = forecast_inventory(rf.get("/forecast/inventory?lead_time_days=3"))
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["advisory"] is True
        assert data["summary"]["needs_reorder"] == 1
        assert any(r["needs_reorder"] for r in data["products"])

    def test_reorder_endpoint(self, rf):
        from views_django import forecast_reorder_orders

        s = _make_supplier("Acme")
        p = _product("Espresso", stock=5, threshold=10)
        _seed_demand(p, days=28, qty=10)
        req = rf.post(
            "/forecast/inventory/reorder",
            data=json.dumps({"supplier_id": s.id}),
            content_type="application/json",
        )
        resp = forecast_reorder_orders(req)
        assert resp.status_code == 201
        data = json.loads(resp.content)
        assert data["created_orders"] == 1
        assert data["orders"][0]["status"] == "draft"

    def test_reorder_endpoint_missing_supplier_400(self, rf):
        from views_django import forecast_reorder_orders

        p = _product("Espresso", stock=5, threshold=10)
        _seed_demand(p, days=28, qty=10)
        req = rf.post(
            "/forecast/inventory/reorder",
            data=json.dumps({}),
            content_type="application/json",
        )
        resp = forecast_reorder_orders(req)
        assert resp.status_code == 400
