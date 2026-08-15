"""
KDS (Kitchen Display System) route handlers.

Provides enriched kitchen ticket endpoints that the Alpine.js KDS page
at /kitchen/ consumes via fetch():

  GET  /kds/tickets/               List tickets (filtered by ?status=)
  GET  /kds/tickets/<id>/          Single ticket detail
  PATCH /kds/tickets/<id>/         Update ticket status
  GET  /kds/items/<sale_id>/       HTMX fragment: sale items for detail modal
  GET  /kds/stats/                 Quick stats (active, overdue counts)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify, Response

from routes import state as S


def register_kds_routes(app):
    """Register KDS-specific route handlers on the Robyn app."""

    # ── Ticket list with enrichment ──────────────────────────────────
    @app.get("/kds/tickets/")
    async def list_tickets(request):
        """Return kitchen tickets enriched with sale data (order_type, table, etc.).

        Query params:
            status  — filter by status (pending, preparing, ready, delivered)
        """
        status_filter = request.query_params.get("status", "").strip() or None

        @sync_to_async
        def _query():
            from models.ops import KitchenTicket
            from models.pos import Sale

            qs = KitchenTicket.objects.select_related("sale").all()
            if status_filter and status_filter != "all":
                qs = qs.filter(status=status_filter)
            qs = qs.order_by("-priority", "created_at")

            tickets = []
            for ticket in qs[:200]:  # safety cap
                data = _ser_ticket(ticket)
                # Enrich with sale info
                sale = ticket.sale
                data["sale_id"] = sale.id
                data["order_type"] = getattr(sale, "order_type", "dine-in")
                data["table_number"] = getattr(sale, "table_number", None)
                data["delivery_address"] = getattr(sale, "delivery_address", None)
                data["total_amount"] = (
                    float(sale.total_amount) if hasattr(sale, "total_amount") and sale.total_amount else None
                )
                tickets.append(data)
            return tickets

        return jsonify(await _query())

    # ── Single ticket detail ─────────────────────────────────────────
    @app.get("/kds/tickets/:pk")
    async def get_ticket(request, pk):
        """Return a single kitchen ticket with full sale enrichment."""
        try:
            ticket_id = int(pk)
        except (TypeError, ValueError):
            return _error(400, f"Invalid ticket ID: {pk}")

        @sync_to_async
        def _query():
            from models.ops import KitchenTicket
            try:
                ticket = KitchenTicket.objects.select_related("sale").get(id=ticket_id)
                data = _ser_ticket(ticket)
                sale = ticket.sale
                data["sale_id"] = sale.id
                data["order_type"] = getattr(sale, "order_type", "dine-in")
                data["table_number"] = getattr(sale, "table_number", None)
                data["delivery_address"] = getattr(sale, "delivery_address", None)
                data["total_amount"] = (
                    float(sale.total_amount) if hasattr(sale, "total_amount") and sale.total_amount else None
                )
                return data
            except KitchenTicket.DoesNotExist:
                return None

        result = await _query()
        if result is None:
            return _error(404, "Ticket not found")
        return jsonify(result)

    # ── Update ticket status ─────────────────────────────────────────
    @app.patch("/kds/tickets/:pk")
    async def update_ticket(request, pk):
        """Update a kitchen ticket's status and/or notes.

        Body: {"status": "preparing", "notes": "..."}
        """
        try:
            ticket_id = int(pk)
        except (TypeError, ValueError):
            return _error(400, f"Invalid ticket ID: {pk}")

        body = request.json() or {}

        @sync_to_async
        def _update():
            from models.ops import KitchenTicket
            from datetime import timezone as tz
            try:
                ticket = KitchenTicket.objects.select_related("sale").get(id=ticket_id)
                if "status" in body:
                    ticket.status = body["status"]
                    # Auto-set completed_at when delivered
                    if body["status"] == "delivered" and not ticket.completed_at:
                        ticket.completed_at = datetime.now(tz.utc)
                if "notes" in body:
                    ticket.notes = body["notes"]
                if "priority" in body:
                    ticket.priority = body["priority"]
                if "prepare_time_minutes" in body:
                    ticket.prepare_time_minutes = body["prepare_time_minutes"]
                ticket.save()

                data = _ser_ticket(ticket)
                sale = ticket.sale
                data["sale_id"] = sale.id
                data["order_type"] = getattr(sale, "order_type", "dine-in")
                data["table_number"] = getattr(sale, "table_number", None)
                data["total_amount"] = (
                    float(sale.total_amount) if hasattr(sale, "total_amount") and sale.total_amount else None
                )
                return data
            except KitchenTicket.DoesNotExist:
                return None

        result = await _update()
        if result is None:
            return _error(404, "Ticket not found")
        return jsonify(result)

    # ── Sale items as HTMX fragment ──────────────────────────────────
    @app.get("/kds/items/:sale_id")
    async def get_sale_items(request, sale_id):
        """Return sale items as an HTML fragment for the KDS detail modal.

        The Alpine.js KDS page uses hx-get on this endpoint to load items
        into the detail modal body.
        """
        try:
            sid = int(sale_id)
        except (TypeError, ValueError):
            return Response(
                status_code=400,
                headers={"Content-Type": "text/html"},
                description="<p class='text-xs text-red-500'>Invalid sale ID</p>",
            )

        @sync_to_async
        def _query():
            from models.pos import Sale, SaleItem
            try:
                sale = Sale.objects.get(id=sid)
                items = SaleItem.objects.filter(sale=sale).select_related("product")
            except Sale.DoesNotExist:
                return None

            if not items.exists():
                return (
                    '<p class="text-xs opacity-50 italic py-3">No items recorded for this order.</p>'
                )

            rows = []
            for item in items:
                product_name = getattr(item, "product_name", "") or (
                    item.product.name if hasattr(item, "product") and item.product else "—"
                )
                price = float(getattr(item, "price", 0) or 0)
                qty = getattr(item, "quantity", 1) or 1
                subtotal = price * qty
                rows.append(
                    f'<div class="flex items-center justify-between py-1.5 px-2 rounded-lg text-xs">'
                    f'<div class="flex items-center gap-2 min-w-0">'
                    f'<span class="w-5 h-5 rounded flex items-center justify-center text-[11px] font-bold shrink-0" '
                    f'style="background:var(--color-surface-raised);color:var(--color-text-secondary)">{qty}</span>'
                    f'<span class="font-medium truncate" style="color:var(--color-text-primary)">{_esc(product_name)}</span>'
                    f'</div>'
                    f'<span class="shrink-0 ml-2" style="color:var(--color-text-secondary)">${subtotal:.2f}</span>'
                    f'</div>'
                )

            total = sum(
                float(getattr(i, "price", 0) or 0) * (getattr(i, "quantity", 1) or 1)
                for i in items
            )
            rows.append(
                f'<div class="flex items-center justify-between py-2 px-2 mt-1 border-t font-bold text-xs" '
                f'style="border-color:var(--color-border-subtle);color:var(--color-text-primary)">'
                f'<span>Total</span><span>${total:.2f}</span></div>'
            )
            return "".join(rows)

        html = await _query()
        if html is None:
            return Response(
                status_code=404,
                headers={"Content-Type": "text/html"},
                description="<p class='text-xs text-red-500'>Sale not found</p>",
            )
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html"},
            description=html,
        )

    # ── Quick stats ──────────────────────────────────────────────────
    @app.get("/kds/stats/")
    async def kds_stats(request):
        """Return quick KDS stats for the dashboard."""
        @sync_to_async
        def _stats():
            from models.ops import KitchenTicket
            from django.db.models import Count, Q
            from datetime import timedelta as td

            total = KitchenTicket.objects.count()
            by_status = dict(
                KitchenTicket.objects.values("status").annotate(n=Count("id")).values_list("status", "n")
            )
            now = datetime.now(timezone.utc)
            recent = KitchenTicket.objects.filter(created_at__gte=now - td(hours=24)).count()
            return {
                "total": total,
                "by_status": by_status,
                "last_24h": recent,
                "pending": by_status.get("pending", 0),
                "preparing": by_status.get("preparing", 0),
                "ready": by_status.get("ready", 0),
                "delivered": by_status.get("delivered", 0),
            }

        return jsonify(await _stats())


# ── Helpers ────────────────────────────────────────────────────────────

def _ser_ticket(ticket) -> dict:
    """Serialize a KitchenTicket to a plain dict with all fields."""
    from decimal import Decimal
    data = {}
    for field in ticket._meta.fields:
        val = getattr(ticket, field.attname, None)
        if isinstance(val, Decimal):
            val = float(val)
        elif isinstance(val, datetime):
            val = val.isoformat() if val else None
        data[field.name] = val
    # Ensure the FK is an int for JSON
    if "sale_id" not in data and hasattr(ticket, "sale_id"):
        data["sale_id"] = ticket.sale_id
    return data


def _esc(text: str) -> str:
    """Minimal HTML escape for sale item names."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _error(status: int, msg: str) -> Response:
    """Build a JSON error response."""
    return Response(
        status_code=status,
        headers={"Content-Type": "application/json"},
        description=json.dumps({"error": msg}),
    )
