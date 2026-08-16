"""
Purchase Order workflow (Reorder Workflow follow-up) tests.

Covers ``services.purchase_orders``:
  * ``create_purchase_order`` — draft PO with lines, cost defaults, guards.
  * ``mark_ordered`` — draft → ordered; illegal transitions rejected.
  * ``receive_purchase_order`` — stock-in via ``InventoryTransaction`` (``in``
    type), product stock bump, received quantities, full vs partial receipt,
    over-receipt guard, draft/cancelled guards.
  * ``cancel_purchase_order`` — draft/ordered → cancelled.
  * ``reorder_alerts`` — reuses the forecast plan; open-draft surfacing.
  * ``purchase_order_stats`` — counts by status + outstanding value.

Plus endpoint tests for the ``/purchase-orders*`` views (RequestFactory).

Models are imported lazily (the conftest ``django_bootstrap`` fixture
configures Django first).
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from django.utils import timezone


def _svc():
    import services.purchase_orders as p

    return p


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.inventory import PurchaseOrderItem, PurchaseOrder, Supplier
    from models.pos import InventoryTransaction, SaleItem, Sale
    InventoryTransaction.objects.all().delete()
    PurchaseOrderItem.objects.all().delete()
    PurchaseOrder.objects.all().delete()
    Supplier.objects.all().delete()
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    yield


def _supplier(name="Acme"):
    from models.inventory import Supplier

    return Supplier.objects.create(name=name, is_active=True)


def _product(name="Espresso", cost=1.2, stock=100, threshold=10):
    from models.pos import Product

    return Product.objects.create(
        name=name, price=3.5, cost_price=cost, stock_quantity=stock,
        low_stock_threshold=threshold, sku=None,
    )


def _po(supplier=None, status="draft", **kw):
    from models.inventory import PurchaseOrder

    s = supplier or _supplier()
    return PurchaseOrder.objects.create(
        supplier=s,
        reference_number=f"PO-T-{PurchaseOrder.objects.count() + 1:03d}",
        status=status,
        total_amount=kw.pop("total_amount", 0),
        **kw,
    )


def _po_line(po, product, qty=10, cost=None):
    from models.inventory import PurchaseOrderItem

    cost = cost if cost is not None else (product.cost_price or 0)
    return PurchaseOrderItem.objects.create(
        purchase_order=po, product=product,
        product_name=product.name, quantity=qty, cost_per_unit=cost,
    )


class TestCreatePurchaseOrder:
    def test_creates_draft_with_lines(self):
        s = _supplier()
        p = _product(cost=1.2)
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 10}])
        assert po.status == "draft"
        assert po.items.count() == 1
        item = po.items.first()
        assert item.product_id == p.id
        assert float(item.cost_per_unit) == 1.2
        assert float(po.total_amount) == 12.0

    def test_empty_items_rejected(self):
        s = _supplier()
        with pytest.raises(Exception, match="line item"):
            _svc().create_purchase_order(s.id, [])

    def test_unknown_supplier_rejected(self):
        with pytest.raises(Exception, match="Supplier"):
            _svc().create_purchase_order(999999, [{"quantity": 1}])

    def test_negative_quantity_rejected(self):
        s = _supplier()
        with pytest.raises(Exception, match="positive"):
            _svc().create_purchase_order(s.id, [{"quantity": 0}])


class TestLifecycle:
    def test_order_then_receive(self):
        from models.pos import InventoryTransaction

        s = _supplier()
        p = _product(stock=50, cost=1.2)
        po = _svc().create_purchase_order(
            s.id, [{"product_id": p.id, "quantity": 10, "cost_per_unit": 1.2}]
        )
        _svc().mark_ordered(po.id)
        po.refresh_from_db()
        assert po.status == "ordered"

        result = _svc().receive_purchase_order(po.id)
        po.refresh_from_db()
        assert po.status == "received"
        assert result["fully_received"] is True
        assert result["stock_in_units"] == 10
        assert result["stock_in_value"] == 12.0

        p.refresh_from_db()
        assert p.stock_quantity == 60
        assert InventoryTransaction.objects.filter(
            product=p, transaction_type="in", reference=f"po_{po.id}"
        ).count() == 1

    def test_cannot_receive_draft(self):
        s = _supplier()
        p = _product()
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 5}])
        with pytest.raises(Exception, match="Order the purchase order"):
            _svc().receive_purchase_order(po.id)

    def test_cannot_receive_twice(self):
        s = _supplier()
        p = _product()
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 5}])
        _svc().mark_ordered(po.id)
        _svc().receive_purchase_order(po.id)
        with pytest.raises(Exception, match="already received"):
            _svc().receive_purchase_order(po.id)

    def test_partial_receipt_keeps_ordered(self):
        s = _supplier()
        p = _product(stock=0, cost=1.0)
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 10}])
        _svc().mark_ordered(po.id)
        result = _svc().receive_purchase_order(po.id, quantities={p.id: 4})
        po.refresh_from_db()
        assert po.status == "ordered"  # not fully received
        assert result["fully_received"] is False
        p.refresh_from_db()
        assert p.stock_quantity == 4
        # Receive the rest
        result2 = _svc().receive_purchase_order(po.id)
        po.refresh_from_db()
        assert po.status == "received"
        p.refresh_from_db()
        assert p.stock_quantity == 10

    def test_over_receipt_rejected(self):
        s = _supplier()
        p = _product()
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 5}])
        _svc().mark_ordered(po.id)
        with pytest.raises(Exception, match="Over-receipt"):
            _svc().receive_purchase_order(po.id, quantities={p.id: 6})

    def test_cancel_draft_and_ordered(self):
        s = _supplier()
        p = _product()
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 5}])
        _svc().cancel_purchase_order(po.id)
        po.refresh_from_db()
        assert po.status == "cancelled"

    def test_cannot_cancel_received(self):
        s = _supplier()
        p = _product()
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 5}])
        _svc().mark_ordered(po.id)
        _svc().receive_purchase_order(po.id)
        with pytest.raises(Exception, match="Cannot cancel"):
            _svc().cancel_purchase_order(po.id)


class TestAlertsAndStats:
    def _seed_demand(self, product, days=28, qty=10):
        from models.pos import Customer, Sale, SaleItem

        for d in range(1, days + 1):
            sale = Sale.objects.create(
                customer=Customer.objects.create(
                    first_name=f"PO{d}", last_name="T", email=f"po{d}@t.com",
                ),
                subtotal=product.price * qty, total=product.price * qty,
                tax_amount=0, status="completed",
                sale_date=timezone.now() - timedelta(days=d),
            )
            SaleItem.objects.create(
                sale=sale, product=product, product_name=product.name,
                quantity=qty, unit_price=product.price,
                line_total=round(product.price * qty, 2),
            )

    def test_reorder_alerts_flags_low_stock(self):
        p = _product(stock=5, threshold=10)
        self._seed_demand(p, days=28, qty=10)
        alerts = _svc().reorder_alerts(lead_time_days=3)
        assert alerts["alert_count"] == 1
        assert alerts["alerts"][0]["product_name"] == "Espresso"
        assert alerts["alerts"][0]["reason"] == "below low-stock threshold"

    def test_reorder_alerts_surfaces_open_drafts(self):
        s = _supplier()
        p = _product()
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 5}])
        alerts = _svc().reorder_alerts()
        assert any(d["id"] == po.id for d in alerts["open_drafts"])

    def test_stats(self):
        s = _supplier()
        p = _product(cost=1.0)
        po = _svc().create_purchase_order(s.id, [{"product_id": p.id, "quantity": 10}])
        _svc().mark_ordered(po.id)
        stats = _svc().purchase_order_stats()
        assert stats["by_status"]["ordered"] == 1
        assert stats["open_drafts"] == 0
        assert stats["outstanding_value"] == 10.0


class TestEndpoints:
    @pytest.fixture
    def rf(self):
        from django.test import RequestFactory

        return RequestFactory()

    def _post(self, rf, path, body=None):
        return rf.post(path, data=json.dumps(body or {}), content_type="application/json")

    def test_create_and_receive_endpoint(self, rf):
        from views_django import (
            purchase_orders, purchase_order_action, purchase_order_detail,
        )

        s = _supplier()
        p = _product(stock=20, cost=1.0)

        resp = purchase_orders(self._post(rf, "/purchase-orders", {
            "supplier_id": s.id,
            "items": [{"product_id": p.id, "quantity": 10}],
        }))
        assert resp.status_code == 201
        po = json.loads(resp.content)
        assert po["status"] == "draft"
        assert po["items"][0]["quantity"] == 10

        resp = purchase_order_action(self._post(rf, f"/purchase-orders/{po['id']}/order"), po["id"], "order")
        assert json.loads(resp.content)["status"] == "ordered"

        resp = purchase_order_action(self._post(rf, f"/purchase-orders/{po['id']}/receive"), po["id"], "receive")
        result = json.loads(resp.content)
        assert result["status"] == "received"
        assert result["stock_in_units"] == 10

        p.refresh_from_db()
        assert p.stock_quantity == 30

        detail = purchase_order_detail(rf.get(f"/purchase-orders/{po['id']}"), po["id"])
        assert json.loads(detail.content)["status"] == "received"

    def test_alerts_and_stats_endpoints(self, rf):
        from views_django import purchase_order_alerts, purchase_order_stats

        resp = purchase_order_alerts(rf.get("/purchase-orders/alerts"))
        assert resp.status_code == 200
        assert json.loads(resp.content)["advisory"] is True

        resp = purchase_order_stats(rf.get("/purchase-orders/stats"))
        assert resp.status_code == 200
        assert "by_status" in json.loads(resp.content)

    def test_unknown_po_404(self, rf):
        from views_django import purchase_order_detail

        resp = purchase_order_detail(rf.get("/purchase-orders/999999"), 999999)
        assert resp.status_code == 404
