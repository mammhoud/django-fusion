"""
Self-checkout Kiosk (P3) — self-service kiosk mode tests.

Covers ``services.kiosk``:
  * ``start_session`` — creates an open session, reuses open sessions by key,
    reopens a closed key.
  * ``catalog`` — active products grouped by category; category slug filter.
  * ``add_item`` — cart line creation/increment, stock + availability guards.
  * ``set_quantity`` / ``remove_item`` / ``clear_cart`` — cart mutations.
  * ``cart_summary`` — rows + computed subtotal/tax/total.
  * ``checkout`` — drives the canonical ``sale_checkout`` surface: creates a
    Sale + SaleItems + KitchenTicket, links the sale, closes the session;
    empty cart rejected.
  * ``cancel_session`` / ``kiosk_stats``.

Plus endpoint tests for the ``/kiosk/*`` views (RequestFactory — the conftest
bootstrap is ORM-first and does not resolve the full URLconf).

Models and the service are imported lazily (the conftest ``django_bootstrap``
fixture configures Django first).
"""

from __future__ import annotations

import json

import pytest


def _svc():
    import services.kiosk as k

    return k


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.kiosk import KioskCartItem, KioskSession
    from models.ops import KitchenTicket
    from models.pos import SaleItem, Sale, InventoryTransaction
    InventoryTransaction.objects.all().delete()
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    KitchenTicket.objects.all().delete()
    KioskCartItem.objects.all().delete()
    KioskSession.objects.all().delete()
    yield


def _product(name="Latte", price=4.5, stock=50, active=True):
    from models.pos import Product

    return Product.objects.create(
        name=name, price=price, stock_quantity=stock,
        low_stock_threshold=5, is_active=active, sku=None,
    )


class TestStartSession:
    def test_creates_open_session(self):
        s = _svc().start_session()
        assert s.status == "open"
        assert s.session_key.startswith("kiosk-")

    def test_reuses_open_session_by_key(self):
        first = _svc().start_session(session_key="kiosk-a")
        second = _svc().start_session(session_key="kiosk-a")
        assert first.id == second.id
        assert second.status == "open"

    def test_reopens_closed_key(self):
        k = _svc()
        s = k.start_session(session_key="kiosk-b")
        k.cancel_session(s)
        reopened = k.start_session(session_key="kiosk-b")
        assert reopened.status == "open"
        assert reopened.closed_at is None


class TestCatalog:
    def test_groups_active_products(self):
        from models.pos import Category

        cat = Category.objects.create(name="Drinks", slug="drinks")
        _product("Latte", 4.5, stock=10)
        _product("Espresso", 3.0, stock=10)
        _product(name="Burger", price=9.0, stock=5)
        _product(name="Off Menu", price=1.0, stock=1, active=False)
        data = _svc().catalog()
        assert data["product_count"] == 3
        assert len(data["groups"]["Other"]) == 3
        assert data["groups"]["Other"][0]["in_stock"] is True
        assert all(p["name"] != "Off Menu" for p in data["groups"]["Other"])

    def test_category_filter(self):
        from models.pos import Category, Product

        cat = Category.objects.create(name="Drinks", slug="drinks")
        Product.objects.create(
            name="Latte", price=4.5, stock_quantity=10,
            low_stock_threshold=5, category=cat, sku=None,
        )
        _product(name="Burger", price=9.0, stock=5)
        data = _svc().catalog(category_slug="drinks")
        assert data["product_count"] == 1
        assert data["groups"]["Drinks"][0]["name"] == "Latte"


class TestCart:
    def test_add_item_creates_line(self):
        product = _product()
        k = _svc()
        session = k.start_session()
        item = k.add_item(session, product.id, 2)
        assert item.quantity == 2
        assert item.product_name == "Latte"
        assert float(item.unit_price) == 4.5

    def test_add_item_increments(self):
        product = _product()
        k = _svc()
        session = k.start_session()
        k.add_item(session, product.id, 1)
        item = k.add_item(session, product.id, 2)
        assert item.quantity == 3

    def test_add_item_stock_guard(self):
        product = _product(stock=5)
        k = _svc()
        session = k.start_session()
        with pytest.raises(k.KioskError, match="Insufficient stock"):
            k.add_item(session, product.id, 6)

    def test_add_item_inactive_product_rejected(self):
        product = _product(active=False)
        k = _svc()
        session = k.start_session()
        with pytest.raises(k.KioskError, match="not available"):
            k.add_item(session, product.id, 1)

    def test_set_quantity_and_remove(self):
        product = _product()
        k = _svc()
        session = k.start_session()
        k.add_item(session, product.id, 1)
        item = k.set_quantity(session, product.id, 4)
        assert item.quantity == 4
        k.remove_item(session, product.id)
        assert session.cart_items.count() == 0

    def test_cart_summary(self):
        p1 = _product("Latte", 4.5, stock=10)
        p2 = _product("Croissant", 3.0, stock=10)
        k = _svc()
        session = k.start_session()
        k.add_item(session, p1.id, 2)
        k.add_item(session, p2.id, 1)
        summary = k.cart_summary(session)
        assert summary["item_count"] == 3
        assert summary["subtotal"] == 12.0
        assert summary["tax_amount"] == 0.96
        assert summary["total"] == 12.96


class TestCheckout:
    def test_checkout_creates_sale_via_checkout_surface(self):
        from models.pos import Sale, SaleItem

        p1 = _product("Latte", 4.5, stock=50)
        p2 = _product("Croissant", 3.0, stock=50)
        k = _svc()
        session = k.start_session()
        k.add_item(session, p1.id, 2)
        k.add_item(session, p2.id, 1)

        result = k.checkout(session, payment_method="card")
        assert result["status"] == "checked_out"
        sale = Sale.objects.get(id=result["sale_id"])
        assert float(sale.total) == 12.96
        assert sale.payment_method == "card"
        assert sale.status == "completed"
        assert SaleItem.objects.filter(sale=sale).count() == 2
        # Stock deducted by the checkout path.
        p1.refresh_from_db()
        assert p1.stock_quantity == 48
        # Session linked + closed.
        session.refresh_from_db()
        assert session.sale_id == sale.id
        assert session.status == "checked_out"

    def test_checkout_empty_cart_rejected(self):
        k = _svc()
        session = k.start_session()
        with pytest.raises(k.KioskError, match="Cart is empty"):
            k.checkout(session)

    def test_checkout_closed_session_rejected(self):
        p = _product()
        k = _svc()
        session = k.start_session()
        k.cancel_session(session)
        with pytest.raises(k.KioskError, match="not open"):
            k.checkout(session)


class TestCancelAndStats:
    def test_cancel_clears_cart_and_closes(self):
        p = _product()
        k = _svc()
        session = k.start_session()
        k.add_item(session, p.id, 1)
        k.cancel_session(session)
        assert session.status == "cancelled"
        assert session.closed_at is not None
        assert session.cart_items.count() == 0

    def test_kiosk_stats(self):
        k = _svc()
        s1 = k.start_session(session_key="stat-1")
        p = _product(stock=10)
        k.add_item(s1, p.id, 1)
        k.checkout(s1)
        k.start_session(session_key="stat-2")  # stays open
        stats = k.kiosk_stats()
        assert stats["open"] == 1
        assert stats["checked_out"] == 1
        assert stats["total_sales"] == 1


class TestEndpoints:
    """View-function tests via RequestFactory (see customer-display tests)."""

    @pytest.fixture
    def rf(self):
        from django.test import RequestFactory

        return RequestFactory()

    def _post(self, rf, path, body=None):
        request = rf.post(path, data=json.dumps(body or {}), content_type="application/json")
        return request

    def test_catalog_endpoint(self, rf):
        _product("Latte", 4.5, stock=10)
        from views_django import kiosk_catalog

        resp = kiosk_catalog(rf.get("/kiosk/catalog"))
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["product_count"] == 1

    def test_sessions_and_checkout_endpoint(self, rf):
        p = _product(stock=10)
        from views_django import (
            kiosk_sessions, kiosk_cart, kiosk_checkout, kiosk_session_detail,
        )

        # Start session
        start_req = self._post(rf, "/kiosk/sessions", {"session_key": "kiosk-ep-1"})
        resp = kiosk_sessions(start_req)
        assert resp.status_code == 201
        key = json.loads(resp.content)["session_key"]

        # Add item
        cart_req = self._post(rf, f"/kiosk/sessions/{key}/cart", {"product_id": p.id, "quantity": 2})
        resp = kiosk_cart(cart_req, key)
        assert resp.status_code == 201
        assert json.loads(resp.content)["cart"]["item_count"] == 2

        # Checkout
        co_req = self._post(rf, f"/kiosk/sessions/{key}/checkout", {"payment_method": "card"})
        resp = kiosk_checkout(co_req, key)
        assert resp.status_code == 201
        result = json.loads(resp.content)
        assert result["status"] == "checked_out"
        assert result["sale_id"] > 0

        # Detail reflects closed status
        detail = kiosk_session_detail(rf.get(f"/kiosk/sessions/{key}"), key)
        assert json.loads(detail.content)["status"] == "checked_out"

    def test_unknown_session_404(self, rf):
        from views_django import kiosk_session_detail

        resp = kiosk_session_detail(rf.get("/kiosk/sessions/nope"), "nope")
        assert resp.status_code == 404
