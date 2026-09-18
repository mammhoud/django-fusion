"""
Delivery Integration (P2) — providers + delivery orders + webhooks tests.

Covers ``services.delivery``:
  * ``create_provider`` — registry, type validation, duplicates.
  * ``create_delivery_order`` — sale link, zone fee computation (base + per-km),
    out-of-zone rejection, fallback to zero fee for manual delivery.
  * ``update_status`` — lifecycle (pending → accepted → preparing →
    out_for_delivery → delivered), illegal transitions, delivered guard.
  * ``cancel_order`` — cancellation before delivery.
  * ``ingest_provider_webhook`` — provider callback matching on order id.
  * ``delivery_stats`` — per-status counts + fee/total aggregates.

Models and the service are imported lazily (the conftest ``django_bootstrap``
fixture configures Django first).
"""

from __future__ import annotations

import pytest


def _svc():
    import services.delivery as d

    return d


def _models():
    from models.delivery import DeliveryOrder, DeliveryProvider

    return DeliveryOrder, DeliveryProvider


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    DeliveryOrder, DeliveryProvider = _models()
    DeliveryOrder.objects.all().delete()
    DeliveryProvider.objects.all().delete()
    yield


def _sale(**kwargs):
    from models.pos import Customer, Sale

    defaults = {
        "subtotal": 25.00,
        "total": 30.00,
        "tax_amount": 3.00,
        "status": "completed",
        "payment_method": "card",
        "customer": Customer.objects.create(
            first_name="Del", last_name="Cust", email="del@test.com",
        ),
    }
    defaults.update(kwargs)
    return Sale.objects.create(**defaults)


def _zone(name="Zone-1", base_fee=2.0, fee_per_km=0.5, max_distance=10.0):
    from models.forge_gaps import DeliveryZone

    return DeliveryZone.objects.create(
        name=name, base_fee=base_fee,
        fee_per_km=fee_per_km, max_distance=max_distance,
    )


class TestProviders:
    def test_create_provider(self):
        d = _svc()
        provider = d.create_provider(
            "Talabat KW", provider_type="talabat", base_url="https://talabat.example",
            commission_rate=12,
        )
        assert provider.provider_type == "talabat"
        assert provider.is_active is True
        assert provider.status == "active"

    def test_create_provider_requires_name(self):
        d = _svc()
        with pytest.raises(d.DeliveryError):
            d.create_provider("  ")

    def test_create_provider_unknown_type(self):
        d = _svc()
        with pytest.raises(d.DeliveryError):
            d.create_provider("Weird", provider_type="teleport")

    def test_duplicate_provider_rejected(self):
        d = _svc()
        d.create_provider("Talabat")
        with pytest.raises(d.DeliveryError):
            d.create_provider("Talabat")

    def test_list_providers(self):
        d = _svc()
        d.create_provider("Talabat", provider_type="talabat")
        d.create_provider("Own Fleet", provider_type="manual")
        assert len(d.list_providers()) == 2


class TestCreateOrder:
    def test_create_order_with_zone_fee(self):
        d = _svc()
        DeliveryOrder, DeliveryProvider = _models()
        zone = _zone(base_fee=2.0, fee_per_km=0.5)
        order = d.create_delivery_order(
            customer_name="Aisha",
            delivery_address="123 Main St",
            distance_km=4,
            delivery_zone=zone,
        )
        assert order.status == "pending"
        assert order.delivery_address == "123 Main St"
        # 2.0 + 4 * 0.5 = 4.0
        assert float(order.delivery_fee) == 4.0
        assert order.provider_order_id.startswith("DLV-")

    def test_create_order_links_sale(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        sale = _sale()
        order = d.create_delivery_order(sale=sale, customer_name="B")
        assert order.sale_id == sale.pk
        assert float(order.subtotal) == 25.0
        assert float(order.total) == 30.0

    def test_out_of_zone_rejected(self):
        d = _svc()
        zone = _zone(max_distance=5.0)
        with pytest.raises(d.DeliveryError):
            d.create_delivery_order(distance_km=9, delivery_zone=zone)

    def test_manual_delivery_zero_fee(self):
        d = _svc()
        order = d.create_delivery_order(customer_name="Walk-in")
        assert float(order.delivery_fee) == 0.0

    def test_order_with_provider(self):
        d = _svc()
        provider = d.create_provider("HungerStation", provider_type="hungerstation")
        order = d.create_delivery_order(provider=provider, customer_name="C")
        assert order.provider_id == provider.pk


class TestStatusLifecycle:
    def test_full_lifecycle(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        for status in ("accepted", "preparing", "out_for_delivery", "delivered"):
            order = d.update_status(order, status)
        assert order.status == "delivered"
        assert order.delivered_at is not None

    def test_illegal_skip_rejected(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        with pytest.raises(d.DeliveryError):
            d.update_status(order, "delivered")  # must pass through preparing/out_for_delivery

    def test_cannot_rewind(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        d.update_status(order, "accepted")
        with pytest.raises(d.DeliveryError):
            d.update_status(order, "pending")

    def test_unknown_status_rejected(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        with pytest.raises(d.DeliveryError):
            d.update_status(order, "warped")

    def test_cancel_before_delivery(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        order = d.cancel_order(order)
        assert order.status == "cancelled"
        assert order.cancelled_at is not None

    def test_cancel_delivered_rejected(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        for status in ("accepted", "preparing", "out_for_delivery"):
            order = d.update_status(order, status)
        order = d.update_status(order, "delivered")
        with pytest.raises(d.DeliveryError):
            d.cancel_order(order)


class TestWebhook:
    def test_webhook_matches_order_and_applies_status(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        updated = d.ingest_provider_webhook(order.provider_order_id, "accepted")
        assert updated is not None
        assert updated.status == "accepted"
        assert updated.accepted_at is not None

    def test_webhook_unknown_order_returns_none(self):
        d = _svc()
        assert d.ingest_provider_webhook("DLV-NOPE", "accepted") is None

    def test_webhook_illegal_status_keeps_pos_state(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        order = d.create_delivery_order(customer_name="A")
        # delivered requires preparing/out_for_delivery — the provider callback
        # is swallowed and the POS state wins (still pending).
        updated = d.ingest_provider_webhook(order.provider_order_id, "delivered")
        assert updated is not None
        assert updated.status == "pending"


class TestStats:
    def test_stats_aggregates(self):
        d = _svc()
        DeliveryOrder, _ = _models()
        o1 = d.create_delivery_order(customer_name="A", total=30, subtotal=25)
        o1 = d.update_status(o1, "accepted")
        o1 = d.update_status(o1, "preparing")
        o1 = d.update_status(o1, "out_for_delivery")
        o1 = d.update_status(o1, "delivered")
        d.create_delivery_order(customer_name="B", total=50, subtotal=40)

        stats = d.delivery_stats()
        assert stats["total_orders"] == 2
        assert stats["status_counts"]["delivered"] == 1
        assert stats["status_counts"]["pending"] == 1
        assert float(stats["delivered_total"]) == 30.0
