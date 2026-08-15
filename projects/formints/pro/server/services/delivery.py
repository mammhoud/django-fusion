"""POS Full — Delivery Integration service (P2, Professional+).

Implements delivery platform connectors and outbound order tracking on top
of ``DeliveryProvider`` / ``DeliveryOrder``:

* ``create_provider`` / ``get_provider`` / ``list_providers`` — connector
  registry (Talabat, HungerStation, manual…).
* ``create_delivery_order`` — dispatch an order: links the ``Sale``, computes
  the delivery fee from the ``DeliveryZone`` (base + per-km), snapshots
  customer/subtotal/total, and generates a provider order id.
* ``update_status`` — the order lifecycle (pending → accepted → preparing →
  out_for_delivery → delivered; cancelled/failed branches), recording the
  relevant timestamps and guarding illegal transitions.
* ``cancel_order`` / ``delivery_stats`` — cancellation and per-status stats.
* ``ingest_provider_webhook`` — accept provider callback events and apply the
  status they report (order id matched on ``provider_order_id``).

Money math uses ``Decimal``; fees come from the zone's ``calculate_fee``.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from models.delivery import DeliveryOrder, DeliveryProvider
from models.forge_gaps import DeliveryZone


class DeliveryError(ValueError):
    """Raised for invalid delivery operations."""


# ── Providers ────────────────────────────────────────────────────────────

def create_provider(
    name: str,
    provider_type: str = "manual",
    base_url: str = "",
    api_key: str = "",
    commission_rate=0,
    is_active: bool = True,
) -> DeliveryProvider:
    """Register a delivery platform connector."""
    name = (name or "").strip()
    if not name:
        raise DeliveryError("provider name is required")
    valid_types = {choice for choice, _ in DeliveryProvider.PROVIDER_TYPES}
    if provider_type not in valid_types:
        raise DeliveryError(f"unknown provider type '{provider_type}'")
    if DeliveryProvider.objects.filter(name=name).exists():
        raise DeliveryError(f"provider '{name}' already exists")
    return DeliveryProvider.objects.create(
        name=name,
        provider_type=provider_type,
        base_url=base_url or "",
        api_key=api_key or "",
        commission_rate=Decimal(str(commission_rate)),
        is_active=is_active,
        status="active" if is_active else "disabled",
    )


def get_provider(provider_id) -> DeliveryProvider | None:
    return DeliveryProvider.objects.filter(pk=provider_id).first()


def list_providers() -> list[DeliveryProvider]:
    return list(DeliveryProvider.objects.all())


# ── Delivery orders ──────────────────────────────────────────────────────

def _q(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def create_delivery_order(
    *,
    sale=None,
    provider: DeliveryProvider | None = None,
    customer_name: str = "",
    customer_phone: str = "",
    delivery_address: str = "",
    distance_km=0,
    delivery_zone: DeliveryZone | None = None,
    delivery_type=None,
    subtotal=None,
    total=None,
    notes: str = "",
) -> DeliveryOrder:
    """Dispatch a delivery order.

    The delivery fee is computed from ``delivery_zone`` (``calculate_fee``)
    when a zone is provided; it raises ``DeliveryError`` when the distance
    exceeds the zone's max. Falls back to 0 for manual/own-fleet orders.
    """
    if delivery_zone is not None and delivery_zone.is_active:
        fee = delivery_zone.calculate_fee(float(distance_km))
        if fee is None:
            raise DeliveryError(
                f"distance {distance_km}km exceeds zone '{delivery_zone.name}' max "
                f"({delivery_zone.max_distance}km)"
            )
    else:
        fee = Decimal("0")

    if sale is not None:
        subtotal = subtotal if subtotal is not None else sale.subtotal
        total = total if total is not None else sale.total

    order = DeliveryOrder.objects.create(
        provider=provider,
        provider_order_id=f"DLV-{_q(total) if total else 0}-{__import__('secrets').token_hex(3).upper()}",
        sale=sale,
        delivery_type=delivery_type,
        delivery_zone=delivery_zone,
        customer_name=(customer_name or "").strip(),
        customer_phone=(customer_phone or "").strip(),
        delivery_address=(delivery_address or "").strip(),
        distance_km=_q(distance_km),
        delivery_fee=_q(fee),
        subtotal=_q(subtotal),
        total=_q(total),
        notes=notes or "",
    )
    return order


def get_delivery_order(order_id) -> DeliveryOrder | None:
    return DeliveryOrder.objects.filter(pk=order_id).first()


def update_status(order: DeliveryOrder, status: str) -> DeliveryOrder:
    """Transition a delivery order through its lifecycle.

    Valid forward paths:
      pending → accepted → preparing → out_for_delivery → delivered
      pending → cancelled | failed
      accepted/preparing/out_for_delivery → cancelled | failed
    """
    valid = {choice for choice, _ in DeliveryOrder.STATUS_CHOICES}
    if status not in valid:
        raise DeliveryError(f"unknown status '{status}'")

    flow = [
        "pending", "accepted", "preparing", "out_for_delivery", "delivered",
    ]
    if status == order.status:
        return order
    if status == "delivered" and order.status not in (
        "preparing", "out_for_delivery",
    ):
        raise DeliveryError(
            f"cannot mark {order.status} order as delivered (must be preparing/out_for_delivery)"
        )
    if status in ("cancelled", "failed") and order.status in ("delivered",):
        raise DeliveryError(f"cannot {status} an already delivered order")
    if status in flow and order.status in flow:
        if flow.index(status) <= flow.index(order.status):
            raise DeliveryError(
                f"cannot move {order.status} → {status} (already past that stage)"
            )

    now = timezone.now()
    order.status = status
    if status == "accepted":
        order.accepted_at = now
    elif status == "delivered":
        order.delivered_at = now
    elif status in ("cancelled", "failed"):
        order.cancelled_at = now
    order.save(update_fields=["status", "accepted_at", "delivered_at", "cancelled_at", "updated_at"])
    return order


def cancel_order(order: DeliveryOrder) -> DeliveryOrder:
    """Cancel a delivery order (only before it is delivered)."""
    return update_status(order, "cancelled")


def ingest_provider_webhook(
    provider_order_id: str, status: str,
) -> DeliveryOrder | None:
    """Apply a provider-reported status to the matching order.

    Matches on ``provider_order_id``; returns None when no order matches.
    Illegal transitions are swallowed (the POS state wins).
    """
    order = DeliveryOrder.objects.filter(provider_order_id=provider_order_id).first()
    if order is None:
        return None
    try:
        return update_status(order, status)
    except DeliveryError:
        return order


def delivery_stats() -> dict:
    """Aggregate delivery KPIs: per-status counts + revenue/fee totals."""
    orders = DeliveryOrder.objects.all()
    status_counts: dict[str, int] = {}
    delivered_total = Decimal("0")
    fee_total = Decimal("0")
    for o in orders:
        status_counts[o.status] = status_counts.get(o.status, 0) + 1
        if o.status == "delivered":
            delivered_total += o.total or 0
        fee_total += o.delivery_fee or 0
    return {
        "total_orders": orders.count(),
        "status_counts": status_counts,
        "delivered_total": float(delivered_total),
        "fee_total": float(fee_total),
        "avg_fee": float(fee_total / orders.count()) if orders.count() else 0.0,
    }
