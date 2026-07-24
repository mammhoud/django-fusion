"""
POS Solo — InventoryFragment.

Inventory and stock-level statistics for the inventory management page.

Fragment name: ``pos.inventory``
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce

from fragments import FragmentComponent, register


@register
class InventoryFragment(FragmentComponent):
    """Inventory aggregate stats and low-stock alerts."""

    fragment_name = "pos.inventory"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        from models.pos import Product, InventoryTransaction
        from models.extra import Ingredient

        total_products = Product.objects.filter(is_active=True).count()
        total_ingredients = Ingredient.objects.filter(is_active=True).count()

        low_stock = list(
            Ingredient.objects.filter(
                is_active=True,
                current_quantity__lte=F("reorder_level"),
            )
            .order_by("current_quantity")[:20]
            .values("name", "current_quantity", "reorder_level", "unit")
        )

        recent_tx_count = InventoryTransaction.objects.filter(
            transaction_type__in=("in", "out", "adjustment"),
        ).count()

        inv_value = (
            Ingredient.objects.filter(is_active=True)
            .aggregate(
                total=Coalesce(
                    Sum(F("current_quantity") * F("cost_per_unit")),
                    Value(Decimal("0.00")),
                )
            )["total"]
            or Decimal("0.00")
        )

        return {
            "total_products": total_products,
            "total_ingredients": total_ingredients,
            "low_stock_items": [
                {
                    "name": i["name"],
                    "quantity": float(i["current_quantity"]),
                    "reorder_level": float(i["reorder_level"]),
                    "unit": i["unit"],
                }
                for i in low_stock
            ],
            "recent_transactions": recent_tx_count,
            "total_inventory_value": str(inv_value),
        }
