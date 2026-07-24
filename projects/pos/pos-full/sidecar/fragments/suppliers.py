"""
POS Full — SuppliersFragment.

List of active suppliers with contact information for the suppliers page.

Fragment name: ``pos.suppliers``

Template context::

    {
        "suppliers": [<Supplier>, ...],
        "count": 12,
        "recent_purchase_orders": 3,
    }
"""

from __future__ import annotations

from typing import Any

from fragments import FragmentComponent, register


@register
class SuppliersFragment(FragmentComponent):
    """Active suppliers with contact info and recent PO count."""

    fragment_name = "pos.suppliers"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        from models.inventory import Supplier, PurchaseOrder

        suppliers = Supplier.objects.filter(is_active=True).order_by("name")[:50]
        recent_po_count = PurchaseOrder.objects.filter(
            status__in=("ordered", "received"),
        ).count()

        return {
            "suppliers": list(suppliers),
            "count": suppliers.count(),
            "recent_purchase_orders": recent_po_count,
        }
