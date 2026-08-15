"""POS Full — AI Forecasting service (P2, Professional/SaaS).

Read-only advisory analytics built from POS history. Per the django-fusion
LLM/MCP enhancement plan, AI output here is **advisory by default**: none of
these functions create, update, or delete POS records — they only read
``Sale`` / ``SaleItem`` / ``Product`` / ``InventoryTransaction`` and return
recommendations a human (or an approved MCP workflow) can act on.

Surface:
  * ``demand_forecast``  — per-product daily demand projection (simple moving
    average + trend factor over the lookback window).
  * ``stock_advisory``   — days-of-cover + suggested reorder quantities,
    driven by forecast demand and each product's ``low_stock_threshold``.
  * ``waste_analysis``   — waste/disposal aggregation with estimated cost.
  * ``sales_insights``   — top movers, growth vs the previous period, and
    plain-language recommendation strings.
  * ``full_report``      — one advisory envelope for the dashboard.

All math is pure statistics over ``completed`` sales; no model changes.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from models.pos import InventoryTransaction, Product, Sale, SaleItem


# ── helpers ───────────────────────────────────────────────────────────────

def _window_bounds(days: int) -> tuple:
    """Return (current_start, current_end, prev_start, prev_end) day bounds.

    Windows are whole calendar days ending yesterday so buckets are exact.
    """
    cur_end = timezone.localdate() - timedelta(days=1)
    cur_start = cur_end - timedelta(days=days - 1)
    prev_end = cur_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    return cur_start, cur_end, prev_start, prev_end


def _sale_ids_in(start, end):
    return list(
        Sale.objects.filter(
            sale_date__date__gte=start, sale_date__date__lte=end,
            status="completed",
        ).values_list("id", flat=True)
    )


def _product_demand(start, end) -> dict:
    """Per-product name → (units, revenue) over a window."""
    ids = _sale_ids_in(start, end)
    if not ids:
        return {}
    rows = (
        SaleItem.objects.filter(sale_id__in=ids)
        .values("product_name")
        .annotate(units=Sum("quantity"), revenue=Sum("line_total"))
    )
    return {
        r["product_name"]: (int(r["units"] or 0), float(r["revenue"] or 0))
        for r in rows
    }


# ── demand forecast ───────────────────────────────────────────────────────

def demand_forecast(days: int = 14, lookback: int = 28) -> dict:
    """Project per-product daily demand for the next ``days`` days.

    Uses a simple moving average of units/day over ``lookback`` days, then
    applies a trend factor (recent 7-day average vs the whole window average)
    so growing products forecast higher. Returns advisory rows only.
    """
    days = max(1, min(int(days), 90))
    lookback = max(7, min(int(lookback), 365))

    cur_start, cur_end, prev_start, prev_end = _window_bounds(lookback)
    whole = _product_demand(cur_start, cur_end)
    # Recent 7-day slice for trend detection.
    recent_start = cur_end - timedelta(days=6)
    recent = _product_demand(recent_start, cur_end)

    products = Product.objects.filter(is_active=True)
    forecast = []
    for p in products:
        name = p.name
        units_whole, _ = whole.get(name, (0, 0.0))
        units_recent, _ = recent.get(name, (0, 0.0))
        avg_whole = units_whole / lookback
        avg_recent = units_recent / 7
        if avg_whole <= 0:
            continue  # no history — skip (or treat as 0 demand)
        # Trend factor: how much the recent daily rate differs from the base.
        trend = (avg_recent / avg_whole) if avg_whole > 0 else 1.0
        trend = min(max(trend, 0.5), 2.0)  # clamp 0.5x–2x
        projected_daily = avg_whole * trend
        forecast.append({
            "product_id": p.id,
            "product_name": name,
            "sku": p.sku or "",
            "avg_daily_units": round(avg_whole, 2),
            "recent_daily_units": round(avg_recent, 2),
            "trend_factor": round(trend, 2),
            "projected_daily_units": round(projected_daily, 2),
            "projected_days_total": round(projected_daily * days, 1),
            "current_stock": p.stock_quantity,
            "low_stock_threshold": p.low_stock_threshold,
        })

    forecast.sort(key=lambda r: r["projected_days_total"], reverse=True)
    return {
        "window_days": lookback,
        "forecast_horizon_days": days,
        "generated_at": timezone.now().isoformat(),
        "advisory": True,
        "products": forecast,
    }


# ── stock advisory ────────────────────────────────────────────────────────

def stock_advisory(days: int = 14, lead_time_days: int = 3) -> dict:
    """Reorder recommendations from forecast demand × lead time.

    For each active product: days-of-cover (current stock ÷ daily demand) and
    a suggested reorder quantity when projected demand over the lead window
    exceeds current stock or the product is already below its low-stock
    threshold.
    """
    demand = demand_forecast(days=days, lookback=28)
    lead = max(1, int(lead_time_days))
    rows = []
    for row in demand["products"]:
        stock = row["current_stock"]
        daily = row["projected_daily_units"]
        cover = (stock / daily) if daily > 0 else None
        needed_over_lead = daily * lead
        threshold = row.get("low_stock_threshold", 0)
        below_threshold = stock <= 0 or stock < threshold
        if daily <= 0 or (not below_threshold and stock >= needed_over_lead):
            continue  # healthy — omit from the advisory
        reorder = max(round(needed_over_lead) - stock, 0)
        rows.append({
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "current_stock": stock,
            "projected_daily_units": daily,
            "days_of_cover": round(cover, 1) if cover is not None else None,
            "needed_over_lead_days": round(needed_over_lead, 1),
            "suggested_reorder_quantity": reorder,
            "reason": "below low-stock threshold" if below_threshold else "projected demand exceeds stock over lead time",
        })
    return {
        "lead_time_days": lead,
        "generated_at": timezone.now().isoformat(),
        "advisory": True,
        "reorders": rows,
    }


# ── waste analysis ────────────────────────────────────────────────────────

def waste_analysis(days: int = 30) -> dict:
    """Aggregate waste/disposal transactions with estimated cost.

    Cost is estimated from the product's ``cost_price`` (0 when unset).
    """
    days = max(1, min(int(days), 365))
    start = timezone.localdate() - timedelta(days=days)
    txns = InventoryTransaction.objects.filter(
        transaction_type="waste", created_at__date__gte=start,
    ).select_related("product")

    total_units = 0
    total_cost = Decimal("0")
    per_product: dict[str, dict] = {}
    for txn in txns:
        qty = txn.quantity
        cost = Decimal(str(txn.product.cost_price or 0)) * qty
        total_units += qty
        total_cost += cost
        entry = per_product.setdefault(txn.product.name, {
            "product_name": txn.product.name,
            "units": 0, "estimated_cost": 0.0,
        })
        entry["units"] += qty
        entry["estimated_cost"] = round(float(Decimal(str(entry["estimated_cost"])) + cost), 2)

    return {
        "window_days": days,
        "total_wasted_units": total_units,
        "estimated_cost": float(total_cost),
        "advisory": True,
        "by_product": sorted(
            per_product.values(), key=lambda r: r["estimated_cost"], reverse=True,
        ),
    }


# ── sales insights ────────────────────────────────────────────────────────

def sales_insights(days: int = 30) -> dict:
    """Sales advisory: movers, growth vs prior period, and recommendations."""
    days = max(7, min(int(days), 365))
    cur_start, cur_end, prev_start, prev_end = _window_bounds(days)

    cur = _product_demand(cur_start, cur_end)
    prev = _product_demand(prev_start, prev_end)

    current_revenue = sum(v[1] for v in cur.values())
    previous_revenue = sum(v[1] for v in prev.values())
    growth = (
        ((current_revenue - previous_revenue) / previous_revenue * 100)
        if previous_revenue > 0 else None
    )

    top = sorted(cur.items(), key=lambda kv: kv[1][1], reverse=True)[:10]
    top_products = [
        {"product_name": name, "units": v[0], "revenue": round(v[1], 2)}
        for name, v in top
    ]

    # Fast risers: present in both periods with >50% unit growth and at least
    # 5 units in the current window.
    risers = []
    for name, (units, _rev) in cur.items():
        prev_units = prev.get(name, (0, 0.0))[0]
        if prev_units >= 5 and units >= 5 and units > prev_units * 1.5:
            risers.append({
                "product_name": name,
                "current_units": units,
                "previous_units": prev_units,
                "growth_pct": round((units - prev_units) / prev_units * 100, 1),
            })
    risers.sort(key=lambda r: r["growth_pct"], reverse=True)

    recommendations = []
    if risers:
        recommendations.append(
            f"Rising demand for {', '.join(r['product_name'] for r in risers[:3])} "
            "— consider promoting and restocking ahead of the trend."
        )
    if current_revenue == 0 and previous_revenue > 0:
        recommendations.append("No completed sales in the current window.")
    elif growth is not None and growth < 0:
        recommendations.append(f"Revenue is down {abs(round(growth, 1))}% vs the previous period — review menu mix and opening hours.")
    elif growth is not None:
        recommendations.append(f"Revenue is up {round(growth, 1)}% vs the previous period — keep the momentum.")
    if top_products:
        recommendations.append(
            f"Top seller: {top_products[0]['product_name']} ({top_products[0]['revenue']} revenue)."
        )

    return {
        "window_days": days,
        "current_revenue": round(current_revenue, 2),
        "previous_revenue": round(previous_revenue, 2),
        "growth_pct": round(growth, 2) if growth is not None else None,
        "top_products": top_products,
        "rising_products": risers,
        "recommendations": recommendations,
        "advisory": True,
    }


# ── full report ───────────────────────────────────────────────────────────

def full_report(days: int = 14) -> dict:
    """One advisory envelope combining demand, stock, waste, and insights."""
    return {
        "generated_at": timezone.now().isoformat(),
        "advisory": True,
        "demand": demand_forecast(days=days),
        "stock": stock_advisory(days=days),
        "waste": waste_analysis(days=max(days, 30)),
        "insights": sales_insights(days=max(days, 30)),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Inventory Forecasting (P3) — superset of the stock advisory
# ═══════════════════════════════════════════════════════════════════════════
#
# Adds the operational layer the roadmap's Inventory Forecasting asks for on
# top of ``stock_advisory``:
#   * ``inventory_plan``       — per-product reorder point, safety stock, and
#     projected stock-out date (planning stays advisory/read-only).
#   * ``generate_reorder_orders`` — the explicit operator action: turns the
#     plan into real ``PurchaseOrder`` drafts (status=draft, no stock
#     movement until the operator orders/receives them).


def _round2(value: Decimal | float) -> float:
    return round(float(value), 2)


def _inventory_plan_rows(days: int = 14, lead_time_days: int = 3,
                         safety_factor: float = 0.5) -> list[dict]:
    """Per-product planning rows: reorder point + safety stock + stock-out."""
    demand = demand_forecast(days=days, lookback=28)
    lead = max(1, int(lead_time_days))
    safety = min(max(float(safety_factor), 0.0), 2.0)
    rows = []
    for row in demand["products"]:
        stock = row["current_stock"]
        daily = row["projected_daily_units"]
        threshold = row.get("low_stock_threshold", 0)
        lead_demand = daily * lead
        safety_stock = round(lead_demand * safety, 1)
        reorder_point = round(lead_demand + safety_stock, 1)
        cover = (stock / daily) if daily > 0 else None
        stock_out_in = int(stock / daily) if (daily > 0 and stock > 0) else (0 if stock <= 0 else None)
        needs_reorder = (
            daily > 0
            and (stock <= 0 or stock < threshold or stock <= reorder_point)
        )
        suggested_qty = 0
        if needs_reorder:
            # Bring stock back to reorder point + one lead window of cover.
            suggested_qty = max(int(reorder_point + lead_demand - stock), 0)
        product = Product.objects.filter(id=row["product_id"]).first()
        rows.append({
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "sku": row["sku"],
            "cost_price": float(product.cost_price or 0) if product else 0.0,
            "current_stock": stock,
            "projected_daily_units": daily,
            "days_of_cover": round(cover, 1) if cover is not None else None,
            "lead_time_days": lead,
            "lead_demand": round(lead_demand, 1),
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "projected_stock_out_in_days": stock_out_in,
            "needs_reorder": needs_reorder,
            "suggested_order_quantity": suggested_qty,
            "reason": (
                "out of stock" if stock <= 0 else
                "below low-stock threshold" if stock < threshold else
                "at/below reorder point" if stock <= reorder_point else ""
            ),
        })
    rows.sort(key=lambda r: (
        not r["needs_reorder"],
        r["projected_stock_out_in_days"] is None,
        r["projected_stock_out_in_days"] if r["projected_stock_out_in_days"] is not None else 10**9,
    ))
    return rows


def inventory_plan(days: int = 14, lead_time_days: int = 3,
                   safety_factor: float = 0.5) -> dict:
    """Full inventory plan: reorder points, safety stock, stock-out dates.

    Superset of ``stock_advisory``: adds safety stock, the reorder point,
    and the projected stock-out date per product, plus a combined summary.
    Stays read-only/advisory.
    """
    rows = _inventory_plan_rows(days, lead_time_days, safety_factor)
    reorders = [r for r in rows if r["needs_reorder"]]
    stock_out = [r for r in rows if r["needs_reorder"]]
    total_value = sum(
        (r["suggested_order_quantity"] or 0) * r["cost_price"]
        for r in reorders
    )
    return {
        "window_days": 28,
        "lead_time_days": max(1, int(lead_time_days)),
        "safety_factor": min(max(float(safety_factor), 0.0), 2.0),
        "generated_at": timezone.now().isoformat(),
        "advisory": True,
        "summary": {
            "products_planned": len(rows),
            "needs_reorder": len(reorders),
            "projected_stock_out": len(stock_out),
            "suggested_order_value": _round2(total_value),
        },
        "products": rows,
    }


def generate_reorder_orders(days: int = 14, lead_time_days: int = 3,
                            safety_factor: float = 0.5,
                            supplier_id: int | None = None) -> dict:
    """Create draft purchase orders from the inventory plan (operator action).

    Turns the advisory suggestions into real ``PurchaseOrder`` records at
    ``status="draft"`` with line items (product, quantity, cost price from
    the product). Drafts move no stock — ordering/receiving is a separate
    operator step — so this stays an explicit, non-destructive action.

    ``supplier_id`` picks the vendor; when omitted the first active supplier
    is used. Returns the created purchase orders (empty list when nothing
    needs reordering).
    """
    from models.inventory import PurchaseOrder, PurchaseOrderItem, Supplier

    rows = _inventory_plan_rows(days, lead_time_days, safety_factor)
    reorders = [r for r in rows if r["needs_reorder"] and r["suggested_order_quantity"] > 0]
    if not reorders:
        return {
            "advisory": True,
            "created_orders": 0,
            "orders": [],
            "note": "No products need reordering — no purchase orders created.",
        }

    if supplier_id:
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            raise ValueError(f"Supplier {supplier_id} not found")
    else:
        supplier = Supplier.objects.filter(is_active=True).order_by("name").first()
        if supplier is None:
            raise ValueError("No active supplier found — create a supplier first")

    po = PurchaseOrder.objects.create(
        supplier=supplier,
        reference_number=f"RF-{timezone.localdate():%Y%m%d}-{PurchaseOrder.objects.count() + 1:03d}",
        status="draft",
        total_amount=Decimal("0"),
        expected_date=timezone.localdate() + timedelta(days=max(1, int(lead_time_days))),
        notes=(
            f"Auto-generated from inventory forecast "
            f"(lead {max(1, int(lead_time_days))}d, safety {safety_factor}x)."
        ),
    )
    total = Decimal("0")
    for r in reorders:
        product = Product.objects.get(id=r["product_id"])
        cost = Decimal(str(r["cost_price"]))
        total += cost * r["suggested_order_quantity"]
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=product,
            product_name=r["product_name"],
            quantity=r["suggested_order_quantity"],
            cost_per_unit=cost,
        )
    po.total_amount = total
    po.save(update_fields=["total_amount"])

    return {
        "advisory": True,
        "created_orders": 1,
        "orders": [{
            "id": po.id,
            "reference_number": po.reference_number,
            "supplier": po.supplier.name,
            "status": po.status,
            "expected_date": po.expected_date.isoformat() if po.expected_date else None,
            "total_amount": float(po.total_amount),
            "item_count": po.items.count(),
        }],
    }
