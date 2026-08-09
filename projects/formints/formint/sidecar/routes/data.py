"""
POS Full — Data access routes (transactions, analytics, legacy model wrappers).

Provides HTTP endpoints for data that is computed/aggregated from existing
Django ORM models rather than stored as separate model tables.

Endpoints:
    GET  /transactions         — Sale-based transaction list (wraps Sale + SaleItem)
    GET  /analytics            — Aggregated analytics from Sale/Product data
    GET  /analytics/summary    — Quick KPI summary (counts, totals)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify, Request
from django.db.models import Sum, Count, Q

from routes import state as S

logger = logging.getLogger("pos_full_server.data")


# ===========================================================================
# /transactions — wraps Sale + SaleItem as flat transaction list
# ===========================================================================


async def list_transactions(request: Request):
    """GET /transactions — List sales as flat transaction records.

    Each transaction wraps a Sale with its SaleItem line items.

    Query params:
        limit:  Max results (default 50)
        offset: Pagination offset (default 0)
    """
    from models.pos import Sale, SaleItem

    limit_str = request.query_params.get("limit", "50")
    offset_str = request.query_params.get("offset", "0")

    @sync_to_async
    def _query():
        qs = Sale.objects.all().order_by("-created_at")
        total = qs.count()
        sales = qs[int(offset_str):int(offset_str) + int(limit_str)]

        result = []
        for sale in sales:
            items = list(sale.items.all().values(
                "product_name", "quantity", "unit_price", "line_total",
            ))
            result.append({
                "id": sale.id,
                "items": [
                    {
                        "name": i["product_name"],
                        "price": float(i["unit_price"]),
                        "quantity": i["quantity"],
                        "unit": "pcs",
                        "subtotal": float(i["line_total"]),
                    }
                    for i in items
                ],
                "total_amount": float(sale.total),
                "currency": "USD",
                "date": sale.sale_date.strftime("%Y-%m-%d") if sale.sale_date else "",
                "time": sale.sale_date.strftime("%H:%M") if sale.sale_date else "",
                "order_type": sale.payment_method or "dine-in",
                "status": sale.status or "completed",
            })

        return {"data": result, "total": total, "returned": len(result)}

    return jsonify(await _query())


async def get_transaction_detail(request, pk: int):
    """GET /transactions/:pk — Single transaction with items."""
    from models.pos import Sale

    @sync_to_async
    def _query():
        try:
            sale = Sale.objects.get(id=pk)
        except Sale.DoesNotExist:
            return None

        items = list(sale.items.all().values(
            "product_name", "quantity", "unit_price", "line_total",
        ))
        return {
            "id": sale.id,
            "items": [
                {
                    "name": i["product_name"],
                    "price": float(i["unit_price"]),
                    "quantity": i["quantity"],
                    "unit": "pcs",
                    "subtotal": float(i["line_total"]),
                }
                for i in items
            ],
            "total_amount": float(sale.total),
            "currency": "USD",
            "date": sale.sale_date.strftime("%Y-%m-%d") if sale.sale_date else "",
            "time": sale.sale_date.strftime("%H:%M") if sale.sale_date else "",
            "order_type": sale.payment_method or "dine-in",
            "status": sale.status or "completed",
        }

    result = await _query()
    if result is None:
        return S._error(404, "Transaction not found")
    return jsonify(result)


# ===========================================================================
# /analytics — aggregated sales/product analytics
# ===========================================================================


async def get_analytics(request: Request):
    """GET /analytics — Aggregated analytics data.

    Returns daily revenue, top products, product distribution, and summary
    computed from Sale + SaleItem data.
    """
    from models.pos import Sale, SaleItem, Product

    @sync_to_async
    def _compute():
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Daily revenue (last 30 days) — use TruncDate for portability
        from django.db.models.functions import TruncDate
        recent_sales = Sale.objects.filter(
            sale_date__gte=thirty_days_ago, status="completed",
        )
        daily = (
            recent_sales
            .annotate(day=TruncDate("sale_date"))
            .values("day")
            .annotate(
                revenue=Sum("total"),
                orders=Count("id"),
            )
            .order_by("day")
        )

        daily_revenue = [
            {"date": d["day"], "revenue": float(d["revenue"] or 0), "orders": d["orders"]}
            for d in daily
        ]

        # Top products (all time)
        top_items = (
            SaleItem.objects
            .values("product_name")
            .annotate(
                sales=Sum("quantity"),
                revenue=Sum("line_total"),
            )
            .order_by("-revenue")[:10]
        )

        top_products = [
            {
                "name": t["product_name"],
                "sales": int(t["sales"] or 0),
                "revenue": float(t["revenue"] or 0),
            }
            for t in top_items
        ]

        # Product distribution (category-wise sales)
        by_category = (
            SaleItem.objects
            .filter(product__category__isnull=False)
            .values("product__category__name")
            .annotate(value=Sum("quantity"))
            .order_by("-value")
        )

        product_distribution = [
            {"name": c["product__category__name"], "value": int(c["value"] or 0)}
            for c in by_category
        ]

        # Summary
        all_completed = Sale.objects.filter(status="completed")
        agg = all_completed.aggregate(
            total_revenue=Sum("total"),
            total_orders=Count("id"),
        )
        total_rev = float(agg["total_revenue"] or 0)
        total_orders = agg["total_orders"] or 0

        return {
            "daily_revenue": daily_revenue,
            "top_products": top_products,
            "product_distribution": product_distribution,
            "summary": {
                "total_orders": total_orders,
                "total_revenue": total_rev,
                "average_order_value": round(total_rev / max(total_orders, 1), 2),
            },
        }

    return jsonify(await _compute())


# ===========================================================================
# Route registration
# ===========================================================================


def register_data_routes(app):
    """Register all data access route handlers."""

    @app.get("/transactions")
    async def _transactions_list(request: Request):
        return await list_transactions(request)

    @app.get("/transactions/:pk")
    async def _transactions_detail(request, pk: int):
        return await get_transaction_detail(request, pk)

    @app.get("/analytics")
    async def _analytics(request: Request):
        return await get_analytics(request)

    logger.info("Registered data routes (3 endpoints: transactions, transaction/:pk, analytics)")
