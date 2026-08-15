"""
Dual-mode fusion views — component (render-first) vs data API road.

Covers ``fusion_dual_views`` (the ``/fusion/views/*`` endpoints that reuse
the read-only POS services through ``django_fusion ... fusion_view``):

* **Data road** — ``X-Fusion-Render-First: false`` returns the canonical
  ``{status, message, data: {encoded, data, view_name}}`` codec envelope
  with the raw payload reachable at ``data.data``.
* **Component road** — ``X-Fusion-Render-First: true`` renders the component
  template (``django_templates/fusion/*.html``) as HTML with the payload in
  the context.
* **Passthrough** — a service ``404`` (JsonResponse) is passed through
  untouched rather than wrapped in a component.
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture(autouse=True)
def _templates():
    """Guarantee the fusion component templates resolve regardless of which
    bootstrap module configured Django first (several bootstrap modules
    configure TEMPLATES['DIRS'] without ``django_templates/``).
    """
    import os

    from django.test import override_settings

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dirs = [os.path.join(base, "django_templates")]

    from django.conf import settings as dj_settings

    templates = list(dj_settings.TEMPLATES)
    if templates and "DIRS" in templates[0]:
        templates[0]["DIRS"] = list(templates[0]["DIRS"]) + dirs
    else:
        templates = [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": dirs,
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                    ],
                },
            }
        ]
    with override_settings(TEMPLATES=templates):
        yield


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.kiosk import KioskCartItem, KioskSession
    from models.ops import KitchenTicket
    from models.pos import Product, SaleItem, Sale
    from models.delivery import DeliveryOrder
    from models.inventory import PurchaseOrder
    from models.giftcard import GiftCard

    DeliveryOrder.objects.all().delete()
    PurchaseOrder.objects.all().delete()
    GiftCard.objects.all().delete()
    InventoryTransaction = None
    try:
        from models.pos import InventoryTransaction
        InventoryTransaction.objects.all().delete()
    except ImportError:
        pass
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    KitchenTicket.objects.all().delete()
    KioskCartItem.objects.all().delete()
    KioskSession.objects.all().delete()
    Product.objects.all().delete()
    yield


def _product(name="Latte", price=4.5, stock=50, active=True):
    from models.pos import Product

    return Product.objects.create(
        name=name, price=price, stock_quantity=stock, is_active=active,
    )


@pytest.fixture
def rf():
    from django.test import RequestFactory

    return RequestFactory()


def _get(rf, path, render_first):
    request = rf.get(path, HTTP_X_FUSION_RENDER_FIRST="true" if render_first else "false")
    return request


class TestForecastViews:
    def test_demand_data_road(self, rf):
        _product("Espresso", 3.5, stock=12)
        from fusion_dual_views import fusion_forecast_demand

        resp = fusion_forecast_demand(_get(rf, "/fusion/views/forecast/demand", False))
        assert resp.status_code == 200
        body = json.loads(resp.content)
        assert body["status"] == 200
        assert body["data"]["view_name"] == "fusion_forecast_demand"
        payload = body["data"]["data"]
        assert payload["advisory"] is True
        # The forecast only projects products with sales history — the seeded
        # product has none, so the row list may be empty; the envelope and
        # contract keys are what matter here.
        assert "products" in payload
        assert "forecast_horizon_days" in payload

    def test_demand_component_road(self, rf):
        _product("Espresso", 3.5, stock=12)
        from fusion_dual_views import fusion_forecast_demand

        resp = fusion_forecast_demand(_get(rf, "/fusion/views/forecast/demand", True))
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/html")
        assert b"fusion-forecast" in resp.content

    def test_inventory_component_road(self, rf):
        _product("Espresso", 3.5, stock=12)
        from fusion_dual_views import fusion_forecast_inventory

        resp = fusion_forecast_inventory(_get(rf, "/fusion/views/forecast/inventory", True))
        assert resp.status_code == 200
        assert b"fusion-inventory" in resp.content


class TestKioskViews:
    def test_catalog_data_road(self, rf):
        _product("Latte", 4.5, stock=10)
        from fusion_dual_views import fusion_kiosk_catalog

        resp = fusion_kiosk_catalog(_get(rf, "/fusion/views/kiosk/catalog", False))
        assert resp.status_code == 200
        payload = json.loads(resp.content)["data"]["data"]
        assert payload["product_count"] == 1

    def test_catalog_component_road(self, rf):
        _product("Latte", 4.5, stock=10)
        from fusion_dual_views import fusion_kiosk_catalog

        resp = fusion_kiosk_catalog(_get(rf, "/fusion/views/kiosk/catalog", True))
        assert resp.status_code == 200
        assert b"fusion-kiosk-catalog" in resp.content


class TestPurchaseViews:
    def test_stats_data_road(self, rf):
        from fusion_dual_views import fusion_purchase_stats

        resp = fusion_purchase_stats(_get(rf, "/fusion/views/purchase-orders/stats", False))
        assert resp.status_code == 200
        payload = json.loads(resp.content)["data"]["data"]
        assert "by_status" in payload
        assert payload["total_orders"] == 0

    def test_stats_component_road(self, rf):
        from fusion_dual_views import fusion_purchase_stats

        resp = fusion_purchase_stats(_get(rf, "/fusion/views/purchase-orders/stats", True))
        assert resp.status_code == 200
        assert b"fusion-purchase-stats" in resp.content


class TestDisplayViews:
    def test_customer_order_missing_sale_passthrough_404(self, rf):
        from fusion_dual_views import fusion_customer_order

        resp = fusion_customer_order(
            _get(rf, "/fusion/views/customer-display/9999", False), 9999
        )
        assert resp.status_code == 404
        assert json.loads(resp.content) == {"error": "Sale not found"}

    def test_gift_cards_data_road(self, rf):
        from fusion_dual_views import fusion_gift_cards

        resp = fusion_gift_cards(_get(rf, "/fusion/views/gift-cards", False))
        assert resp.status_code == 200
        payload = json.loads(resp.content)["data"]["data"]
        assert "card_count" in payload
