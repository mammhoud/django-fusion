"""
Dual-mode fusion views — the same read-only service payload as a component
or a data API.

Every view here wraps an existing read-only service with
``django_fusion.routes.rendering.decorators.fusion_view``, so one function
answers two ways depending on the effective render-first mode (header →
session → per-view default → ``FUSION_RENDER_FIRST``):

* **Render-first (component)** — ``template_name`` renders with
  ``{"data": <service payload>, "request": …}`` in the context.
* **Data API** — ``{status, message, data: {encoded, data, view_name}}``
  via ``FusionCodec``, matching the canonical fusion JSON contract.

These are read-only advisory surfaces (forecast, customer display, kiosk,
purchase orders, tables floor, gaming stations, gift cards, deliveries,
CRM dashboard, analytics). Mutation endpoints intentionally stay on their
existing raw JSON views.

URLs are wired in ``configs/urls.py`` under ``/fusion/views/<name>``.
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, JsonResponse

from django_fusion.routes.rendering.decorators import fusion_view

# Read-only services reused from the canonical JSON views.
from services import customer_display as _cd
from services import delivery as _delivery
from services import forecast as _forecast
from services import giftcard as _giftcard
from services import kiosk as _kiosk
from services import purchase_orders as _po
from services import tables as _tables

__all__ = [
    "fusion_forecast_demand",
    "fusion_forecast_stock",
    "fusion_forecast_inventory",
    "fusion_customer_board",
    "fusion_customer_order",
    "fusion_kiosk_catalog",
    "fusion_kiosk_stats",
    "fusion_purchase_alerts",
    "fusion_purchase_stats",
    "fusion_tables_floor",
    "fusion_delivery_stats",
    "fusion_gift_cards",
]


def _qs_int(request: HttpRequest, key: str, default: int) -> int:
    try:
        return max(1, int(request.GET.get(key, default)))
    except (TypeError, ValueError):
        return default


# ── Forecast ────────────────────────────────────────────────────────────────


@fusion_view(template_name="fusion/forecast.html", fusion_render_first=True)
def fusion_forecast_demand(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/forecast/demand — demand projection (read-only)."""
    days = _qs_int(request, "days", 14)
    return _forecast.demand_forecast(days=days)


@fusion_view(template_name="fusion/forecast.html", fusion_render_first=True)
def fusion_forecast_stock(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/forecast/stock — stock advisory (read-only)."""
    days = _qs_int(request, "days", 14)
    lead = _qs_int(request, "lead_time_days", 3)
    return _forecast.stock_advisory(days=days, lead_time_days=lead)


@fusion_view(template_name="fusion/inventory.html", fusion_render_first=True)
def fusion_forecast_inventory(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/forecast/inventory — reorder-point plan (read-only)."""
    days = _qs_int(request, "days", 14)
    lead = _qs_int(request, "lead_time_days", 3)
    return _forecast.inventory_plan(days=days, lead_time_days=lead)


# ── Customer Display ────────────────────────────────────────────────────────


@fusion_view(template_name="fusion/customer_board.html", fusion_render_first=True)
def fusion_customer_board(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/customer-display/board — active orders feed."""
    limit = _qs_int(request, "limit", 20)
    return _cd.active_board(limit=min(limit, 50))


@fusion_view(template_name="fusion/customer_order.html", fusion_render_first=True)
def fusion_customer_order(request: HttpRequest, sale_id: int) -> dict[str, Any] | JsonResponse:
    """GET /fusion/views/customer-display/<sale_id> — one order envelope."""
    display = _cd.order_display(sale_id)
    if display is None:
        return JsonResponse({"error": "Sale not found"}, status=404)
    return display


# ── Kiosk ───────────────────────────────────────────────────────────────────


@fusion_view(template_name="fusion/kiosk_catalog.html", fusion_render_first=True)
def fusion_kiosk_catalog(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/kiosk/catalog — touchscreen catalog (read-only)."""
    return _kiosk.catalog(category_slug=request.GET.get("category", ""))


@fusion_view(template_name="fusion/kiosk_stats.html", fusion_render_first=True)
def fusion_kiosk_stats(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/kiosk/stats — kiosk session stats (read-only)."""
    return _kiosk.kiosk_stats()


# ── Purchase Orders ─────────────────────────────────────────────────────────


@fusion_view(template_name="fusion/purchase_alerts.html", fusion_render_first=True)
def fusion_purchase_alerts(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/purchase-orders/alerts — reorder alerts + open drafts."""
    lead = _qs_int(request, "lead_time_days", 3)
    return _po.reorder_alerts(lead_time_days=lead)


@fusion_view(template_name="fusion/purchase_stats.html", fusion_render_first=True)
def fusion_purchase_stats(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/purchase-orders/stats — PO counts by status."""
    return _po.purchase_order_stats()


# ── Tables / Delivery / Gift Cards ──────────────────────────────────────────


@fusion_view(template_name="fusion/tables_floor.html", fusion_render_first=True)
def fusion_tables_floor(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/tables/floor — live table floor summary."""
    return _tables.floor_summary()


@fusion_view(template_name="fusion/delivery_stats.html", fusion_render_first=True)
def fusion_delivery_stats(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/deliveries/stats — delivery KPIs (read-only)."""
    return _delivery.delivery_stats()


@fusion_view(template_name="fusion/gift_cards.html", fusion_render_first=True)
def fusion_gift_cards(request: HttpRequest) -> dict[str, Any]:
    """GET /fusion/views/gift-cards — gift card overview (read-only)."""
    from models.giftcard import GiftCard, GiftCardTransaction

    cards = GiftCard.objects.all().order_by("-issued_at")[:20]
    txs = GiftCardTransaction.objects.all().order_by("-created_at")[:10]
    return {
        "cards": [
            {
                "code": c.code,
                "balance": float(c.balance),
                "disabled": c.disabled,
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
            }
            for c in cards
        ],
        "card_count": len(cards),
        "transactions": [
            {
                "code": t.gift_card.code if t.gift_card_id else None,
                "tx_type": t.tx_type,
                "amount": float(t.amount),
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in txs
        ],
    }
