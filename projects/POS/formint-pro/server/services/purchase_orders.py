"""
POS Full — Purchase-order workflow service (Reorder Workflow follow-up).

Completes the procurement loop that Inventory Forecasting starts: drafts are
ordered, received (stock-in via ``InventoryTransaction``), or cancelled, and
the operator gets reorder alerts driven by the same forecast plan.

Scope:
  * ``list_purchase_orders`` — PO listing (filter by status, supplier).
  * ``create_purchase_order`` — manual draft PO (supplier + line items).
  * ``mark_ordered``          — draft → ordered.
  * ``receive_purchase_order`` — ordered → received; creates ``in``
    ``InventoryTransaction`` rows, bumps product stock + received quantities,
    recomputes the total (supports partial receipt per line).
  * ``cancel_purchase_order`` — draft/ordered → cancelled.
  * ``reorder_alerts``        — products at/below reorder point + open drafts.
  * ``purchase_order_stats``  — counts by status + outstanding value.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction as db_transaction
from django.utils import timezone

from models.inventory import PurchaseOrder, PurchaseOrderItem, Supplier
from models.pos import InventoryTransaction, Product


class PurchaseOrderError(Exception):
    """Raised for purchase-order domain violations (illegal transitions…)."""


def list_purchase_orders(status: str = "") -> list[dict[str, Any]]:
    qs = PurchaseOrder.objects.select_related("supplier").prefetch_related("items")
    if status and status != "all":
        qs = qs.filter(status=status)
    qs = qs.order_by("-created_at")[:100]
    return [_ser_po(po, with_items=True) for po in qs]


def _ser_po(po: PurchaseOrder, with_items: bool = False) -> dict[str, Any]:
    data = {
        "id": po.id,
        "reference_number": po.reference_number,
        "supplier": po.supplier.name,
        "supplier_id": po.supplier_id,
        "status": po.status,
        "total_amount": float(po.total_amount),
        "expected_date": po.expected_date.isoformat() if po.expected_date else None,
        "notes": po.notes or "",
        "created_at": po.created_at.isoformat() if po.created_at else None,
    }
    if with_items:
        data["items"] = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "received_quantity": item.received_quantity,
                "cost_per_unit": float(item.cost_per_unit),
            }
            for item in po.items.all()
        ]
    return data


def create_purchase_order(supplier_id: int, items: list[dict],
                          expected_date=None, notes: str = "") -> PurchaseOrder:
    """Create a draft PO with line items.

    ``items``: ``[{product_id, quantity, cost_per_unit?}]`` — cost defaults to
    the product's ``cost_price``. Quantities must be positive.
    """
    if not items:
        raise PurchaseOrderError("At least one line item is required")
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise PurchaseOrderError(f"Supplier {supplier_id} not found")

    with db_transaction.atomic():
        po = PurchaseOrder.objects.create(
            supplier=supplier,
            reference_number=f"PO-{timezone.localdate():%Y%m%d}-{PurchaseOrder.objects.count() + 1:03d}",
            status="draft",
            total_amount=Decimal("0"),
            expected_date=expected_date,
            notes=notes,
        )
        total = Decimal("0")
        for idx, line in enumerate(items):
            quantity = int(line.get("quantity", 0))
            if quantity <= 0:
                raise PurchaseOrderError(f"Item {idx}: quantity must be positive")
            product = None
            product_id = line.get("product_id")
            if product_id:
                product = Product.objects.filter(id=product_id).first()
                if product is None:
                    raise PurchaseOrderError(f"Item {idx}: product {product_id} not found")
            cost = Decimal(str(line.get("cost_per_unit", product.cost_price if product else 0)))
            total += cost * quantity
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=product,
                product_name=line.get("product_name") or (product.name if product else "Item"),
                quantity=quantity,
                cost_per_unit=cost,
            )
        po.total_amount = total
        po.save(update_fields=["total_amount"])
        return po


def mark_ordered(po_id: int) -> PurchaseOrder:
    po = _get(po_id)
    if po.status != "draft":
        raise PurchaseOrderError(f"Cannot order a {po.status} purchase order")
    po.status = "ordered"
    po.save(update_fields=["status"])
    return po


def receive_purchase_order(po_id: int,
                           quantities: dict[int, int] | None = None) -> dict[str, Any]:
    """Receive an ordered PO — stock-in each line via ``InventoryTransaction``.

    ``quantities`` optionally maps product_id → received quantity (partial
    receipt); without it every line is received in full. Full receipt moves
    the PO to ``received``; a partial receipt keeps it ``ordered`` so the
    remaining balance can be received later. Over-receiving is rejected.
    """
    po = _get(po_id)
    if po.status == "received":
        raise PurchaseOrderError("Purchase order already received")
    if po.status == "cancelled":
        raise PurchaseOrderError("Cannot receive a cancelled purchase order")
    if po.status == "draft":
        raise PurchaseOrderError("Order the purchase order before receiving it")

    quantities = quantities or {}
    txns = []
    with db_transaction.atomic():
        for item in po.items.select_related("product"):
            if item.product is None:
                continue  # unlinked legacy line — nothing to stock in
            # Default to the remaining balance so repeat receipts work.
            remaining = item.quantity - item.received_quantity
            received = quantities.get(item.product_id, remaining)
            if received < 0 or item.received_quantity + received > item.quantity:
                raise PurchaseOrderError(
                    f"Over-receipt for '{item.product_name}': "
                    f"{item.received_quantity + received} > ordered {item.quantity}"
                )
            if received == 0:
                continue
            item.received_quantity += received
            item.save(update_fields=["received_quantity"])

            product = Product.objects.select_for_update().get(id=item.product_id)
            product.stock_quantity = (product.stock_quantity or 0) + received
            product.save(update_fields=["stock_quantity", "updated_at"])

            txns.append(
                InventoryTransaction.objects.create(
                    product=product,
                    transaction_type="in",
                    quantity=received,
                    reference=f"po_{po.id}",
                    inventory_id="main",
                    notes=f"Received {received}x {item.product_name} from PO #{po.id}",
                )
            )

        fully_received = all(
            item.received_quantity >= item.quantity
            for item in po.items.all()
        )
        if fully_received:
            po.status = "received"
            po.save(update_fields=["status"])

    return {
        "id": po.id,
        "reference_number": po.reference_number,
        "status": po.status,
        "fully_received": fully_received,
        "received_lines": len(txns),
        "stock_in_units": sum(t.quantity for t in txns),
        "stock_in_value": round(
            sum(float(t.product.cost_price or 0) * t.quantity for t in txns), 2
        ),
    }


def cancel_purchase_order(po_id: int) -> PurchaseOrder:
    po = _get(po_id)
    if po.status in ("received", "cancelled"):
        raise PurchaseOrderError(f"Cannot cancel a {po.status} purchase order")
    po.status = "cancelled"
    po.save(update_fields=["status"])
    return po


def purchase_order_detail(po_id: int) -> dict[str, Any] | None:
    po = _get(po_id, allow_missing=True)
    return _ser_po(po, with_items=True) if po else None


def reorder_alerts(lead_time_days: int = 3, safety_factor: float = 0.5) -> dict[str, Any]:
    """Reorder alerts: products at/below reorder point + open PO drafts.

    Reuses the Inventory Forecasting plan (same advisory math); open PO
    drafts are surfaced so the operator knows a restock is already queued.
    """
    from services.forecast import _inventory_plan_rows

    rows = _inventory_plan_rows(14, lead_time_days, safety_factor)
    alerts = [
        {
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "current_stock": r["current_stock"],
            "reorder_point": r["reorder_point"],
            "projected_stock_out_in_days": r["projected_stock_out_in_days"],
            "reason": r["reason"],
            "suggested_order_quantity": r["suggested_order_quantity"],
        }
        for r in rows if r["needs_reorder"]
    ]
    open_drafts = list(
        PurchaseOrder.objects.filter(status="draft")
        .select_related("supplier").order_by("-created_at")[:20]
    )
    return {
        "lead_time_days": max(1, int(lead_time_days)),
        "generated_at": timezone.now().isoformat(),
        "advisory": True,
        "alert_count": len(alerts),
        "alerts": alerts,
        "open_drafts": [
            {"id": po.id, "reference_number": po.reference_number,
             "supplier": po.supplier.name, "total_amount": float(po.total_amount)}
            for po in open_drafts
        ],
    }


def purchase_order_stats() -> dict[str, Any]:
    from django.db.models import Count, Sum

    by_status = dict(
        PurchaseOrder.objects.values("status")
        .annotate(n=Count("id")).values_list("status", "n")
    )
    outstanding = PurchaseOrder.objects.filter(status="ordered") \
        .aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
    return {
        "by_status": {k: by_status.get(k, 0) for k in
                      ("draft", "ordered", "received", "cancelled")},
        "total_orders": PurchaseOrder.objects.count(),
        "outstanding_value": float(outstanding),
        "open_drafts": by_status.get("draft", 0),
    }


def _get(po_id: int, allow_missing: bool = False) -> PurchaseOrder | None:
    try:
        return PurchaseOrder.objects.select_related("supplier").get(id=po_id)
    except PurchaseOrder.DoesNotExist:
        if allow_missing:
            return None
        raise PurchaseOrderError(f"Purchase order {po_id} not found")
