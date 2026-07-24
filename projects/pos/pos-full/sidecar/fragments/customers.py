"""
POS Full — CustomersFragment.

Customer statistics and top-spending customers for the customers page.

Fragment name: ``pos.customers``

Template context::

    {
        "total_customers": 42,
        "active_customers": 38,
        "total_loyalty_points": 15420,
        "total_lifetime_spent": "12345.67",
        "top_customers": [{"name": "...", "total_spent": "..."}, ...],
    }
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Sum

from fragments import FragmentComponent, register


@register
class CustomersFragment(FragmentComponent):
    """Customer aggregate stats and top spenders."""

    fragment_name = "pos.customers"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        from models.pos import Customer

        total_customers = Customer.objects.count()
        active_customers = Customer.objects.filter(is_active=True).count()
        total_loyalty = (
            Customer.objects.aggregate(models_sum=Sum("loyalty_points"))["models_sum"] or 0
        )
        total_spent = (
            Customer.objects.aggregate(models_sum=Sum("total_spent"))["models_sum"]
            or Decimal("0.00")
        )

        # Top 5 customers by lifetime spend
        top_customers = list(
            Customer.objects.filter(is_active=True)
            .order_by("-total_spent")[:5]
            .values("first_name", "last_name", "total_spent", "email")
        )

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "total_loyalty_points": total_loyalty,
            "total_lifetime_spent": str(total_spent),
            "top_customers": [
                {
                    "name": f"{c['first_name']} {c['last_name']}".strip(),
                    "total_spent": str(c["total_spent"]),
                    "email": c.get("email", ""),
                }
                for c in top_customers
            ],
        }
