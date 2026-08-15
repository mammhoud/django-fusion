"""
POS Full — Customer Display service (P3).

Read-only, customer-facing order-confirmation display fed by ``Sale`` /
``SaleItem`` / ``KitchenTicket``. Scope per the roadmap: **customer-facing
display for order confirmation**.

This service never mutates POS records — it only reads history and returns
display envelopes a wall screen / confirmation display can render. The
authoritative live state comes from the sale's ``KitchenTicket`` lifecycle
and the sale's own status/totals.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from django.db.models import Count, Q
from django.utils import timezone

from models.ops import KitchenTicket
from models.pos import Sale, SaleItem


def _sale_meta(sale: Sale) -> dict[str, Any]:
    """Parse the structured JSON metadata stored on ``Sale.notes``.

    ``create_sale_with_items`` stores ``order_type`` / ``table_number`` as
    JSON in the sale notes; older sales may have free-text notes instead.
    """
    meta: dict[str, Any] = {}
    notes = (sale.notes or "").strip()
    if notes.startswith("{"):
        try:
            parsed = json.loads(notes)
            if isinstance(parsed, dict):
                meta = parsed
        except (TypeError, ValueError):
            pass
    return meta


def order_context(sale: Sale) -> dict[str, Any]:
    """Resolve order type + table number for a sale.

    Preference order: the linked ``SaleGroup`` (kept in sync by the table
    management service), then the JSON meta stored on the sale, then defaults.
    """
    group = sale.group
    if group is not None:
        return {
            "order_type": group.order_type or "dine-in",
            "table_number": group.table_number or "",
        }
    meta = _sale_meta(sale)
    return {
        "order_type": meta.get("order_type") or "dine-in",
        "table_number": meta.get("table_number") or "",
    }


def _ticket_status(ticket: KitchenTicket | None) -> dict[str, Any] | None:
    """Serialize the kitchen ticket part of the display envelope."""
    if ticket is None:
        return None
    now = timezone.now()
    elapsed_minutes = 0
    if ticket.created_at:
        elapsed_minutes = max(0, int((now - ticket.created_at).total_seconds() // 60))
    remaining_minutes = max(
        0, ticket.prepare_time_minutes - elapsed_minutes
    )
    return {
        "id": ticket.id,
        "status": ticket.status,
        "status_label": ticket.get_status_display(),
        "station": ticket.station.name if ticket.station else None,
        "prepare_time_minutes": ticket.prepare_time_minutes,
        "elapsed_minutes": elapsed_minutes,
        "remaining_minutes": remaining_minutes,
        "is_overdue": (
            ticket.status in ("pending", "preparing")
            and elapsed_minutes > ticket.prepare_time_minutes
        ),
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "notes": ticket.notes or "",
    }


def _item_rows(sale: Sale) -> list[dict[str, Any]]:
    """Serialize the sale's line items for the customer display."""
    items = SaleItem.objects.filter(sale=sale).select_related("product")
    rows = []
    for item in items:
        name = item.product_name or (item.product.name if item.product else "—")
        rows.append({
            "product_name": name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "line_total": float(item.line_total),
        })
    return rows


def order_display(sale_id: int) -> dict[str, Any] | None:
    """Build the display envelope for one sale (order confirmation).

    Returns ``None`` when the sale does not exist.
    """
    try:
        sale = Sale.objects.prefetch_related("items").get(id=sale_id)
    except Sale.DoesNotExist:
        return None

    ticket = KitchenTicket.objects.filter(sale=sale).order_by("created_at").first()
    ctx = order_context(sale)
    return {
        "sale_id": sale.id,
        "order_number": f"#{sale.id}",
        "order_type": ctx["order_type"],
        "table_number": ctx["table_number"],
        "status": sale.status,
        "payment_method": sale.payment_method,
        "subtotal": float(sale.subtotal),
        "tax_amount": float(sale.tax_amount),
        "discount_amount": float(sale.discount_amount),
        "total": float(sale.total),
        "item_count": sale.items.count(),
        "items": _item_rows(sale),
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
        "kitchen_ticket": _ticket_status(ticket),
    }


def active_board(limit: int = 20) -> dict[str, Any]:
    """Active orders for a wall/cycle display.

    Returns every order with a live kitchen ticket (pending / preparing /
    ready) plus the most recent completed orders, newest first. Also exposes
    per-status counts so the screen can show a summary strip.
    """
    now = timezone.now()
    live_statuses = ["pending", "preparing", "ready"]
    ticket_qs = (
        KitchenTicket.objects.select_related("sale", "station")
        .filter(sale__isnull=False)
        .order_by("created_at")
    )
    live_tickets = [t for t in ticket_qs.filter(status__in=live_statuses)]
    recent = ticket_qs.filter(
        Q(status="delivered") | Q(status__in=["ready"]),
        created_at__gte=now - timedelta(hours=6),
    )[: max(0, limit - len(live_tickets))]

    orders = [
        order_display(t.sale_id)
        for t in (live_tickets + list(recent))
        if t.sale_id
    ]
    orders = [o for o in orders if o is not None]

    by_status = dict(
        KitchenTicket.objects.filter(status__in=live_statuses)
        .values("status").annotate(n=Count("id")).values_list("status", "n")
    )
    return {
        "orders": orders,
        "summary": {
            "active": sum(by_status.get(s, 0) for s in live_statuses),
            "pending": by_status.get("pending", 0),
            "preparing": by_status.get("preparing", 0),
            "ready": by_status.get("ready", 0),
        },
        "generated_at": now.isoformat(),
    }
