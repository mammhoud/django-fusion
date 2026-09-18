"""
Customer Display (P3) — read-only order-confirmation display tests.

Covers ``services.customer_display``:
  * ``order_display`` — envelope shape, item rows, totals, order context
    (table/order type from the SaleGroup, then sale JSON meta, then defaults).
  * ``_ticket_status`` — kitchen ticket enrichment, elapsed/remaining math,
    overdue detection.
  * ``active_board`` — live-ticket aggregation, per-status summary, delivered
    orders limited to the recent window.

Plus endpoint tests for ``/customer-display/<sale_id>`` and
``/customer-display/board``.

The service is read-only: it never writes POS records. Models are imported
lazily (the conftest ``django_bootstrap`` fixture configures Django first).
"""

from __future__ import annotations

import json

import pytest

from django.utils import timezone


def _svc():
    import services.customer_display as c

    return c


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.ops import KitchenTicket
    from models.pos import SaleItem, Sale
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    KitchenTicket.objects.all().delete()
    yield


def _sale(table_number="", order_type=None, notes="", **kwargs):
    from models.pos import Customer, Sale

    defaults = {
        "subtotal": 19.99,
        "total": 23.99,
        "tax_amount": 2.00,
        "status": "completed",
        "payment_method": "cash",
        "notes": notes,
        "customer": Customer.objects.create(
            first_name="CD", last_name="Guest", email="cd@test.com",
        ),
    }
    defaults.update(kwargs)
    sale = Sale.objects.create(**defaults)
    if table_number or order_type:
        from models.pos import SaleGroup
        group = SaleGroup.objects.create(
            group_key=f"grp-{sale.id}-{table_number or 'dine'}",
            table_number=table_number,
            order_type=order_type or "dine-in",
        )
        sale.group = group
        sale.save(update_fields=["group"])
    return sale


def _item(sale, name="Latte", qty=2, price=4.5):
    from models.pos import SaleItem

    return SaleItem.objects.create(
        sale=sale, product_name=name, quantity=qty,
        unit_price=price, line_total=round(price * qty, 2),
    )


def _ticket(sale, status="preparing", prep=15, **kwargs):
    from models.ops import KitchenTicket

    return KitchenTicket.objects.create(
        sale=sale, status=status, prepare_time_minutes=prep,
        notes=f"Order for Sale #{sale.id}", **kwargs,
    )


class TestOrderContext:
    def test_uses_sale_group_when_present(self):
        sale = _sale(table_number="T7", order_type="dine-in")
        ctx = _svc().order_context(sale)
        assert ctx == {"order_type": "dine-in", "table_number": "T7"}

    def test_falls_back_to_json_meta(self):
        meta = json.dumps({"order_type": "takeaway", "table_number": "12"})
        sale = _sale(notes=meta)
        ctx = _svc().order_context(sale)
        assert ctx == {"order_type": "takeaway", "table_number": "12"}

    def test_defaults_when_no_context(self):
        sale = _sale()
        ctx = _svc().order_context(sale)
        assert ctx == {"order_type": "dine-in", "table_number": ""}

    def test_free_text_notes_are_ignored(self):
        sale = _sale(notes="Please no onions")
        ctx = _svc().order_context(sale)
        assert ctx == {"order_type": "dine-in", "table_number": ""}


class TestOrderDisplay:
    def test_missing_sale_returns_none(self):
        assert _svc().order_display(999999) is None

    def test_envelope_shape_and_totals(self):
        sale = _sale(table_number="T3", order_type="dine-in")
        _item(sale, "Espresso", qty=1, price=3.5)
        _item(sale, "Croissant", qty=2, price=2.5)
        d = _svc().order_display(sale.id)
        assert d["sale_id"] == sale.id
        assert d["order_number"] == f"#{sale.id}"
        assert d["table_number"] == "T3"
        assert d["order_type"] == "dine-in"
        assert d["total"] == 23.99
        assert d["item_count"] == 2
        assert len(d["items"]) == 2
        assert d["items"][0]["product_name"] == "Espresso"
        assert d["items"][0]["line_total"] == 3.5

    def test_kitchen_ticket_enrichment(self):
        sale = _sale()
        _ticket(sale, status="preparing", prep=15)
        d = _svc().order_display(sale.id)
        t = d["kitchen_ticket"]
        assert t["status"] == "preparing"
        assert t["prepare_time_minutes"] == 15
        assert t["elapsed_minutes"] >= 0
        assert t["remaining_minutes"] <= 15
        assert t["is_overdue"] is False

    def test_kitchen_ticket_overdue(self):
        from datetime import timedelta

        sale = _sale()
        ticket = _ticket(sale, status="pending", prep=5)
        KitchenTicket = ticket.__class__
        KitchenTicket.objects.filter(id=ticket.id).update(
            created_at=timezone.now() - timedelta(minutes=30)
        )
        t = _svc().order_display(sale.id)["kitchen_ticket"]
        assert t["elapsed_minutes"] >= 30
        assert t["remaining_minutes"] == 0
        assert t["is_overdue"] is True

    def test_no_ticket_returns_none(self):
        sale = _sale()
        d = _svc().order_display(sale.id)
        assert d["kitchen_ticket"] is None


class TestActiveBoard:
    def test_summary_counts(self):
        s1 = _sale()
        s2 = _sale()
        s3 = _sale()
        _ticket(s1, status="pending")
        _ticket(s2, status="preparing")
        _ticket(s3, status="ready")
        board = _svc().active_board()
        assert board["summary"] == {
            "active": 3, "pending": 1, "preparing": 1, "ready": 1,
        }
        assert {o["sale_id"] for o in board["orders"]} == {s1.id, s2.id, s3.id}

    def test_delivered_orders_recent_only(self):
        from datetime import timedelta

        sale = _sale()
        ticket = _ticket(sale, status="delivered", prep=15)
        board = _svc().active_board()
        assert {o["sale_id"] for o in board["orders"]} == {sale.id}
        # Older than 6h are excluded from the board.
        KitchenTicket = ticket.__class__
        KitchenTicket.objects.filter(id=ticket.id).update(
            created_at=timezone.now() - timedelta(hours=8)
        )
        board2 = _svc().active_board()
        assert board2["orders"] == []
        assert board2["summary"]["active"] == 0


class TestEndpoints:
    """View-function tests via RequestFactory.

    The conftest bootstrap is ORM-first (no admin/sessions apps installed,
    no ROOT_URLCONF), so the full URLconf can't be resolved here. The URL
    wiring itself is exercised by the live-verify pass; these tests prove the
    view contract (status codes + payload shapes) directly.
    """

    @pytest.fixture
    def rf(self):
        from django.test import RequestFactory

        return RequestFactory()

    def _order_view(self, rf, sale_id):
        from views_django import customer_display_order

        return customer_display_order(rf.get("/customer-display/"), sale_id)

    def _board_view(self, rf, **query):
        from views_django import customer_display_board

        return customer_display_board(rf.get("/customer-display/board", query))

    def test_order_endpoint(self, rf):
        sale = _sale(table_number="T9", order_type="dine-in")
        _item(sale, "Tea", qty=1, price=2.0)
        resp = self._order_view(rf, sale.id)
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["sale_id"] == sale.id
        assert data["table_number"] == "T9"

    def test_order_endpoint_404(self, rf):
        resp = self._order_view(rf, 999999)
        assert resp.status_code == 404

    def test_board_endpoint(self, rf):
        sale = _sale()
        _ticket(sale, status="preparing")
        resp = self._board_view(rf)
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["summary"]["preparing"] == 1
        assert data["orders"][0]["sale_id"] == sale.id

    def test_board_limit_clamped(self, rf):
        resp = self._board_view(rf, limit=999)
        assert resp.status_code == 200
