"""
POS Full — DashboardFragment.

Aggregate counts from core POS models for the dashboard KPI cards.

Fragment name: ``pos.dashboard``

Template context::

    {
        "restaurant_name": "My Restaurant",
        "product_count": 42,
        "customer_count": 17,
        "employee_count": 8,
        "sale_count": 156,
    }
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
        from models.config import DeviceConfig

        product_count = Product.objects.filter(is_active=True).count()
        customer_count = Customer.objects.filter(is_active=True).count()
        employee_count = Employee.objects.filter(is_active=True).count()
        sale_count = Sale.objects.count()

        # Restaurant name from first device config
        config = DeviceConfig.objects.filter(config_key="restaurant_name").first()
        restaurant_name = config.config_value if config else "My Restaurant"

        return {
            "restaurant_name": restaurant_name,
            "product_count": product_count,
            "customer_count": customer_count,
            "employee_count": employee_count,
            "sale_count": sale_count,
        }
