"""
Reports routes — sales, inventory, and cashback reports with date filtering.

Endpoints:
    GET    /reports/sales             — Sales summary with date range + totals
    GET    /reports/sales/cashback    — Cashback summary across sales
    GET    /reports/inventory         — Inventory report with low-stock filter
    GET    /reports/inventory/count   — Per-product stock snapshot with inventory_id filter
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify, Response, Request
from django.db.models import Sum, Count, Q, F

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
        payment_method: Filter by payment method (optional)
    """
    from models.pos import Sale

    date_from = request.query_params.get("date_from", "")
    date_to = request.query_params.get("date_to", "")
    payment_method = request.query_params.get("payment_method", "")

    @sync_to_async
    def _report():
        qs = Sale.objects.exclude(status="cancelled")
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        if payment_method:
            qs = qs.filter(payment_method=payment_method)

        total_count = qs.count()
        agg = qs.aggregate(
            total_revenue=Sum("total"),
            total_cashback=Sum("cashback_amount"),
            total_discount=Sum("discount_amount"),
            total_tax=Sum("tax_amount"),
        )

        return {
            "report_type": "sales",
            "date_from": date_from or "all",
            "date_to": date_to or "now",
            "payment_method": payment_method or "all",
            "summary": {
                "total_orders": total_count,
                "total_revenue": float(agg["total_revenue"] or 0),
                "total_cashback": float(agg["total_cashback"] or 0),
                "total_discounts": float(agg["total_discount"] or 0),
                "total_tax": float(agg["total_tax"] or 0),
                "average_order": round(float(agg["total_revenue"] or 0) / max(total_count, 1), 2),
            },
        }

    return jsonify(await _report())


async def get_cashback_report(request: Request):
    """GET /reports/sales/cashback — Cashback summary across all sales.

    Query params:
        date_from:  Start date (ISO format, optional)
        date_to:    End date (ISO format, optional)
    """
    from models.pos import Sale

    date_from = request.query_params.get("date_from", "")
    date_to = request.query_params.get("date_to", "")

    @sync_to_async
    def _report():
        qs = Sale.objects.exclude(status="cancelled").exclude(cashback_amount=0)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)

        agg = qs.aggregate(
            total_cashback=Sum("cashback_amount"),
            cashback_count=Count("id"),
        )
        total_cb = float(agg["total_cashback"] or 0)
        count_cb = agg["cashback_count"] or 0

        # Top 10 cashback sales
        top_cb = list(
            qs.order_by("-cashback_amount")
            .values("id", "total", "cashback_amount", "payment_method", "created_at")[:10]
        )

        return {
            "report_type": "cashback",
            "date_from": date_from or "all",
            "date_to": date_to or "now",
            "summary": {
                "total_cashback": round(total_cb, 2),
                "cashback_transactions": count_cb,
                "average_cashback": round(total_cb / max(count_cb, 1), 2),
            },
            "top_cashback_sales": [
                {
                    "sale_id": r["id"],
                    "total": float(r["total"]),
                    "cashback": float(r["cashback_amount"]),
                    "payment_method": r["payment_method"],
                    "date": r["created_at"].isoformat() if r.get("created_at") else "",
                }
                for r in top_cb
            ],
        }

    return jsonify(await _report())


# ===========================================================================
# Inventory Count (per-product stock snapshots)
# ===========================================================================


async def get_inventory_count(request: Request):
    """GET /reports/inventory/count — Per-product stock snapshot.

    Query params:
        inventory_id: Filter by inventory location (default: main)
        low_stock:    true to show only items at or below threshold
        category_id:  Filter by category ID (optional)
    """
    from models.pos import Product, InventoryTransaction

    inventory_id = request.query_params.get("inventory_id", "")
    low_stock_only = request.query_params.get("low_stock", "").lower() == "true"
    category_id = request.query_params.get("category_id", "")

    @sync_to_async
    def _count():
        qs = Product.objects.filter(is_active=True)
        if category_id:
            qs = qs.filter(category_id=category_id)

        results = []
        for product in qs.select_related("category"):
            # Net stock from transactions for this product + inventory
            tx_filter = Q(product=product)
            if inventory_id:
                tx_filter &= Q(inventory_id=inventory_id)
            txs = InventoryTransaction.objects.filter(tx_filter)

            # Sum stock: 'in' adds, 'out'/'transfer_out'/'waste' subtracts, 'return'/'restock'/'transfer_in' adds
            stock_in = (
                txs.filter(transaction_type__in=["in", "return", "restock", "transfer_in"]).aggregate(
                    total=Sum("quantity")
                )["total"]
                or 0
            )
            stock_out = (
                txs.filter(transaction_type__in=["out", "adjustment", "transfer_out", "waste"]).aggregate(
                    total=Sum("quantity")
                )["total"]
                or 0
            )
            current_stock = int(stock_in) - int(stock_out)

            # Inventory info
            inventory_ids = list(
                txs.values_list("inventory_id", flat=True).distinct()[:10]
            )

            item = {
                "product_id": product.id,
                "name": product.name,
                "sku": product.sku or "",
                "category": product.category.name if product.category else "",
                "current_stock": max(current_stock, 0),
                "low_stock_threshold": product.low_stock_threshold,
                "is_low_stock": current_stock <= product.low_stock_threshold,
                "inventory_ids": inventory_ids or ["main"],
                "price": float(product.price),
            }
            if low_stock_only:
                if current_stock <= product.low_stock_threshold:
                    results.append(item)
            else:
                results.append(item)

        results.sort(key=lambda x: x["current_stock"])

        return {
            "report_type": "inventory_count",
            "inventory_id": inventory_id or "all",
            "total_products": len(results),
            "low_stock_count": sum(1 for r in results if r["is_low_stock"]),
            "data": results,
        }

    return jsonify(await _count())


# ===========================================================================
# Inventory Report (existing — low-stock ingredient report)
# ===========================================================================


async def get_inventory_report(request: Request):
    """GET /reports/inventory — Inventory report.

    Query params:
        low_stock:  true to show only items at or below reorder level
        inventory_id: Filter by inventory location
    """
    from models.pos import Product, InventoryTransaction

    low_stock = request.query_params.get("low_stock", "").lower() == "true"
    inventory_id = request.query_params.get("inventory_id", "")

    @sync_to_async
    def _report():
        qs = InventoryTransaction.objects.all()
        if inventory_id:
            qs = qs.filter(inventory_id=inventory_id)

        if not low_stock:
            total = qs.count()
            products_count = Product.objects.filter(is_active=True).count()
            return {
                "report_type": "inventory",
                "filter": "all",
                "total_transactions": total,
                "active_products": products_count,
                "inventory_id": inventory_id or "all",
            }

        results = []
        products = list(Product.objects.filter(is_active=True))
        for product in products:
            tx_filter = Q(product=product)
            if inventory_id:
                tx_filter &= Q(inventory_id=inventory_id)

            txs = InventoryTransaction.objects.filter(tx_filter)
            stock_in = (
                txs.filter(transaction_type__in=["in", "return", "restock", "transfer_in"])
                .aggregate(total=Sum("quantity"))["total"]
                or 0
            )
            stock_out = (
                txs.filter(transaction_type__in=["out", "adjustment", "transfer_out", "waste"])
                .aggregate(total=Sum("quantity"))["total"]
                or 0
            )
            net = int(stock_in) - int(stock_out)

            if net <= product.low_stock_threshold:
                results.append({
                    "product_id": product.id,
                    "name": product.name,
                    "sku": product.sku or "",
                    "current_stock": max(net, 0),
                    "low_stock_threshold": product.low_stock_threshold,
                    "status": "low_stock",
                })

        results.sort(key=lambda x: x["current_stock"])
        return {
            "report_type": "inventory",
            "filter": "low_stock",
            "inventory_id": inventory_id or "all",
            "total_items": len(results),
            "data": results,
        }

    return jsonify(await _report())


# ===========================================================================
# Inventory Transfers
# ===========================================================================


async def create_inventory_transfer(request: Request):
    """POST /reports/inventory/transfer — Transfer stock between inventories.

    Body:
        source_inventory:  Source inventory ID
        target_inventory:  Target inventory ID
        items:             List of {product_id, quantity, notes?}
    """
    from models.pos import Product, InventoryTransaction

    body = request.json() or {}
    source = body.get("source_inventory", "")
    target = body.get("target_inventory", "")
    items = body.get("items", [])
    created_by = body.get("created_by", "system")

    if not source or not target:
        return jsonify({"error": "source_inventory and target_inventory required"})
    if not items:
        return jsonify({"error": "items list required"})
    if source == target:
        return jsonify({"error": "source and target must differ"})

    @sync_to_async
    def _transfer():
        batch_ref = f"transfer_{source}_to_{target}_{int(datetime.now().timestamp())}"
        created = []
        errors = []

        for item in items:
            product_id = item.get("product_id")
            quantity = abs(item.get("quantity", 0))
            if not product_id or quantity <= 0:
                errors.append({"product_id": product_id, "error": "Invalid quantity"})
                continue

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                errors.append({"product_id": product_id, "error": "Product not found"})
                continue

            # Check source has enough stock
            txs_filter = Q(product=product) & Q(inventory_id=source)
            stock_in = (
                InventoryTransaction.objects.filter(txs_filter & Q(transaction_type__in=["in", "return", "restock", "transfer_in"]))
                .aggregate(total=Sum("quantity"))["total"]
                or 0
            )
            stock_out = (
                InventoryTransaction.objects.filter(txs_filter & Q(transaction_type__in=["out", "adjustment", "transfer_out", "waste"]))
                .aggregate(total=Sum("quantity"))["total"]
                or 0
            )
            available = int(stock_in) - int(stock_out)
            if available < quantity:
                errors.append({"product_id": product_id, "error": f"Insufficient stock (available: {available})"})
                continue

            # Debit source
            tx_out = InventoryTransaction.objects.create(
                product=product,
                transaction_type="transfer_out",
                quantity=quantity,
                inventory_id=source,
                transfer_to_inventory=target,
                created_by=created_by,
                reference=body.get("reference", ""),
                reference_id=batch_ref,
                notes=item.get("notes", f"Transfer to {target}"),
            )
            # Credit target
            tx_in = InventoryTransaction.objects.create(
                product=product,
                transaction_type="transfer_in",
                quantity=quantity,
                inventory_id=target,
                created_by=created_by,
                reference=batch_ref,
                reference_id=batch_ref,
                notes=item.get("notes", f"Transfer from {source}"),
            )
            created.append({
                "product_id": product_id,
                "product_name": product.name,
                "quantity": quantity,
                "source_transaction_id": tx_out.id,
                "target_transaction_id": tx_in.id,
            })

        return {
            "status": "completed" if not errors else "partial",
            "batch_reference": batch_ref,
            "source": source,
            "target": target,
            "transferred": created,
            "errors": errors,
            "total_items": len(created),
            "source_inventory": source,
            "target_inventory": target,
        }

    return jsonify(await _transfer())


async def get_inventory_transfers(request: Request):
    """GET /reports/inventory/transfers — List inventory transfers.

    Query params:
        inventory_id:  Filter by source or target inventory
        batch_ref:     Filter by batch reference
        limit:         Max results (default 50)
    """
    from models.pos import InventoryTransaction

    inventory_id = request.query_params.get("inventory_id", "")
    batch_ref = request.query_params.get("batch_ref", "")
    limit_str = request.query_params.get("limit", "50")

    @sync_to_async
    def _list():
        qs = InventoryTransaction.objects.filter(
            transaction_type__in=["transfer_out", "transfer_in"]
        ).order_by("-created_at")
        if inventory_id:
            qs = qs.filter(
                Q(inventory_id=inventory_id) | Q(transfer_to_inventory=inventory_id)
            )
        if batch_ref:
            qs = qs.filter(reference_id=batch_ref)

        total = qs.count()
        items = list(qs[: int(limit_str)])
        return {
            "report_type": "inventory_transfers",
            "total": total,
            "returned": len(items),
            "data": [
                {
                    "id": t.id,
                    "product_id": t.product_id,
                    "product_name": t.product.name,
                    "transaction_type": t.transaction_type,
                    "quantity": t.quantity,
                    "inventory_id": t.inventory_id,
                    "transfer_to_inventory": t.transfer_to_inventory,
                    "reference": t.reference or "",
                    "notes": t.notes,
                    "created_by": t.created_by,
                    "created_at": t.created_at.isoformat() if t.created_at else "",
                }
                for t in items
            ],
        }

    return jsonify(await _list())


# ===========================================================================
# Route registration
# ===========================================================================


def register_report_routes(app):
    """Register all report route handlers on the given Robyn app."""

    @app.get("/reports/sales")
    async def _sales_report(request: Request):
        return await get_sales_report(request)

    @app.get("/reports/sales/cashback")
    async def _cashback_report(request: Request):
        return await get_cashback_report(request)

    @app.get("/reports/inventory")
    async def _inventory_report(request: Request):
        return await get_inventory_report(request)

    @app.get("/reports/inventory/count")
    async def _inventory_count(request: Request):
        return await get_inventory_count(request)

    @app.post("/reports/inventory/transfer")
    async def _transfer(request: Request):
        return await create_inventory_transfer(request)

    @app.get("/reports/inventory/transfers")
    async def _transfer_list(request: Request):
        return await get_inventory_transfers(request)

    logger.info("Registered report routes (6 endpoints: sales, cashback, inventory, count, transfer, transfers)")
