"""POS Full — split/merge bill service (Mobile Waiter P1).

Implements tableside split-bill and merge workflows on top of the ``Sale`` /
``SaleItem`` / ``SaleGroup`` models:

* ``split_sale`` — move a subset of a sale's items into one or more child
  sales under a new ``SaleGroup``; the original sale keeps any un-split items
  and becomes the parent.
* ``merge_sale`` — move a child sale's items back into its parent and remove
  the child; closes the group when no children remain.
* ``merge_group`` — merge every child of a group back into its parent at once.

Totals are recomputed from line items (subtotal == total for a split child,
since discounts/tax are settled on the parent). All mutations are atomic, and
totals are always read with a fresh query so a caller's prefetched related
cache can never produce a stale total.
"""

from __future__ import annotations

import time
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from models.pos import Sale, SaleGroup, SaleItem


class SplitMergeError(ValueError):
    """Raised for invalid split/merge requests (bad ids, missing items, …)."""


def _recompute_total(sale: Sale) -> None:
    # Fresh aggregate — never trust ``sale.items`` (may be a stale prefetch).
    subtotal = (
        SaleItem.objects.filter(sale=sale).aggregate(t=Sum("line_total"))["t"]
        or Decimal("0")
    )
    sale.subtotal = subtotal
    sale.total = subtotal
    sale.save(update_fields=["subtotal", "total"])


def split_sale(
    sale_id: int,
    splits: list[dict],
    name: str = "",
    table_number: str = "",
    order_type: str = "dine-in",
) -> tuple[SaleGroup, Sale, list[Sale]]:
    """Split ``sale_id`` items into child sales under a new group.

    ``splits`` is a list of dicts, each ``{"item_ids": [...],
    "customer_id": int|None, "payment_method": str, "notes": str}``.
    Returns ``(group, parent_sale, created_children)``.
    """
    try:
        sale = Sale.objects.get(id=sale_id)
    except Sale.DoesNotExist as exc:
        raise SplitMergeError(f"sale {sale_id} not found") from exc

    items_by_id = {item.id: item for item in SaleItem.objects.filter(sale=sale)}

    requested: list[int] = []
    for spec in splits:
        requested.extend(spec.get("item_ids") or [])
    if len(requested) != len(set(requested)):
        raise SplitMergeError("duplicate item_id in split specs")
    missing = [i for i in requested if i not in items_by_id]
    if missing:
        raise SplitMergeError(f"item ids not on sale {sale_id}: {missing}")

    with transaction.atomic():
        group = SaleGroup.objects.create(
            group_key=f"split-{sale.id}-{int(time.time())}",
            name=name or f"Split of Sale #{sale.id}",
            table_number=table_number,
            order_type=order_type,
        )
        sale.group = group
        sale.save(update_fields=["group"])

        created: list[Sale] = []
        for spec in splits:
            item_ids = spec.get("item_ids") or []
            if not item_ids:
                continue
            child = Sale.objects.create(
                customer_id=spec.get("customer_id"),
                subtotal=Decimal("0"),
                tax_amount=Decimal("0"),
                discount_amount=Decimal("0"),
                total=Decimal("0"),
                payment_method=spec.get("payment_method", sale.payment_method),
                status="completed",
                notes=spec.get("notes", ""),
                group=group,
                parent_sale=sale,
            )
            subtotal = Decimal("0")
            for item_id in item_ids:
                item = items_by_id[item_id]
                item.sale = child
                item.save(update_fields=["sale"])
                subtotal += item.line_total or Decimal("0")
            child.subtotal = subtotal
            child.total = subtotal
            child.save(update_fields=["subtotal", "total"])
            created.append(child)

        _recompute_total(sale)  # parent keeps the un-split items
        return group, sale, created


def merge_sale(child_id: int) -> tuple[Sale, SaleGroup | None]:
    """Merge a split child back into its parent and delete the child."""
    try:
        child = Sale.objects.get(id=child_id)
    except Sale.DoesNotExist as exc:
        raise SplitMergeError(f"sale {child_id} not found") from exc

    if child.parent_sale_id is None:
        raise SplitMergeError(f"sale {child_id} is not a split child")

    parent = Sale.objects.get(id=child.parent_sale_id)
    group = child.group

    with transaction.atomic():
        SaleItem.objects.filter(sale=child).update(sale=parent)
        _recompute_total(parent)
        child.delete()

        if group is not None:
            _close_group_if_done(group)
        return parent, group


def merge_group(group_key: str) -> tuple[SaleGroup, list[Sale]]:
    """Merge all children of a group back into their parents and close it."""
    try:
        group = SaleGroup.objects.get(group_key=group_key)
    except SaleGroup.DoesNotExist as exc:
        raise SplitMergeError(f"group {group_key} not found") from exc

    merged: list[Sale] = []
    with transaction.atomic():
        children = list(Sale.objects.filter(group=group, parent_sale__isnull=False))
        for child in children:
            parent = Sale.objects.get(id=child.parent_sale_id)
            SaleItem.objects.filter(sale=child).update(sale=parent)
            _recompute_total(parent)
            merged.append(parent)
            child.delete()
        group.status = "closed"
        group.closed_at = timezone.now()
        group.save(update_fields=["status", "closed_at"])
        return group, merged


def _close_group_if_done(group: SaleGroup) -> None:
    has_children = Sale.objects.filter(group=group, parent_sale__isnull=False).exists()
    if not has_children:
        group.status = "closed"
        group.closed_at = timezone.now()
        group.save(update_fields=["status", "closed_at"])
