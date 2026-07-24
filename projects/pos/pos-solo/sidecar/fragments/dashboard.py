"""
POS Solo — DashboardFragment.

Aggregate counts from core POS models for the dashboard KPI cards.

Fragment name: ``pos.dashboard``
"""

from __future__ import annotations

from typing import Any

from django.utils import timezone

from django.db.models import Sum

from fragments import FragmentComponent, register


@register
class DashboardFragment(FragmentComponent):
    """Aggregate POS stats for the dashboard landing page."""

    fragment_name = "pos.dashboard"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        from models.pos import Product, Customer, Employee, Sale

        product_count = Product.objects.filter(is_active=True).count()
        customer_count = Customer.objects.filter(is_active=True).count()
        employee_count = Employee.objects.filter(is_active=True).count()
        sale_count = Sale.objects.count()

        return {
            "restaurant_name": "Forge Solo",
            "product_count": product_count,
            "customer_count": customer_count,
            "employee_count": employee_count,
            "sale_count": sale_count,
        }
