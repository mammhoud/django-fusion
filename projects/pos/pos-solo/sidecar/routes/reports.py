"""
Reports routes — ported from bolt_api.py for Robyn server integration.

Provides sales and inventory reports with date filtering.

Endpoints:
    GET    /reports/sales       — Sales summary with date range + totals
    GET    /reports/inventory   — Inventory report with low-stock filter

@tested pos-full — Report routes
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify, Response, Request
from django.db.models import Sum

from routes import state as S

logger = logging.getLogger("pos_full_server.reports")


# ===========================================================================
# Sales Report
# ===========================================================================


async def get_sales_report(request: Request):
    """GET /reports/sales — Sales summary with optional date range.

    Query params:
        date_from:  Start date (ISO format, optional)
        date_to:    End date (ISO format, optional)
    """
    from models.sales import Sale

    date_from = request.query_params.get("date_from", "")
    date_to = request.query_params.get("date_to", "")

    @sync_to_async
    def _report():
        qs = Sale.objects.all()
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)

        total_count = qs.count()
        total_revenue = (qs.aggregate(total=Sum("total_amount"))["total"] or 0)

        return {
            "report_type": "sales",
            "date_from": date_from or "all",
            "date_to": date_to or "now",
            "summary": {
                "total_orders": total_count,
                "total_revenue": float(total_revenue),
                "average_order": round(float(total_revenue) / max(total_count, 1), 2),
            },
        }

    return jsonify(await _report())


# ===========================================================================
# Inventory Report
# ===========================================================================


async def get_inventory_report(request: Request):
    """GET /reports/inventory — Inventory report.

    Query params:
        low_stock:  true to show only items at or below reorder level
    """
    from models.inventory import Ingredient, InventoryTransaction

    low_stock = request.query_params.get("low_stock", "").lower() == "true"

    @sync_to_async
    def _report():
        if not low_stock:
            total = InventoryTransaction.objects.count()
            return {
                "report_type": "inventory",
                "filter": "all",
                "total_items": total,
            }

        results = []
        ingredients = list(Ingredient.objects.filter(is_active=True))
        for ingredient in ingredients:
            txs = list(InventoryTransaction.objects.filter(ingredient=ingredient))
            net = sum(tx.quantity_change for tx in txs)
            if net <= ingredient.reorder_level:
                results.append({
                    "ingredient_id": ingredient.id,
                    "name": ingredient.name,
                    "current_stock": net,
                    "reorder_level": ingredient.reorder_level,
                    "status": "low_stock",
                })

        return {
            "report_type": "inventory",
            "filter": "low_stock",
            "total_items": len(results),
            "data": results,
        }

    return jsonify(await _report())


# ===========================================================================
# Route registration
# ===========================================================================


def register_report_routes(app):
    """Register all report route handlers on the given Robyn app.

    @tested pos-full — Report routes ported from bolt_api.py
    """

    @app.get("/reports/sales")
    async def _sales_report(request: Request):
        return await get_sales_report(request)

    @app.get("/reports/inventory")
    async def _inventory_report(request: Request):
        return await get_inventory_report(request)

    logger.info("Registered report routes (2 endpoints)")
