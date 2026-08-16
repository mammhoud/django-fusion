"""
Employee — django-fusion fragment components (dual-mode).

Each component owns a staff-desk fragment (KPI chips, order inbox rows) and
knows how to build both the template context and the JSON data payload.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Sum
from django.utils import timezone

from django_fusion.routes.components.fragments import FragmentComponent

from shop.models import Order, OrderItem

__all__ = [
    "StatsFragment",
    "OrderRowsFragment",
    "OrderRowFragment",
]


def _today_stats() -> dict[str, Any]:
    """Shared KPI computation: today's orders / revenue / items + open count.

    ``item_count`` is a Python property on ``Order`` (computed from related
    items), so it cannot be aggregated in SQL — ``items_today`` sums the
    actual ``OrderItem.quantity`` rows instead.
    """
    today = timezone.localdate()
    today_orders = Order.objects.filter(created_at__date=today)
    items_today = (
        OrderItem.objects.filter(order__created_at__date=today).aggregate(
            t=Sum("quantity")
        )["t"]
        or 0
    )
    return {
        "orders_today": today_orders.count(),
        "revenue_today": today_orders.aggregate(t=Sum("total"))["t"] or 0,
        "open": Order.objects.exclude(status__in=["completed", "cancelled"]).count(),
        "items_today": items_today,
    }


class StatsFragment(FragmentComponent):
    """KPI chips — refreshed by the dashboard's HTMX poller."""

    fragment_name = "employee.fragments.stats"
    template_name = "employee/fragments/stats.html"
    htmx_only = True

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        context["stats"] = _today_stats()
        return context

    def get_fragment_data(self) -> dict[str, Any]:
        return _today_stats()


class OrderRowsFragment(FragmentComponent):
    """Order inbox rows — filterable by status."""

    fragment_name = "employee.fragments.order_rows"
    template_name = "employee/fragments/order_rows.html"
    htmx_only = True

    def get_queryset(self):
        status = self.request.GET.get("status", "")
        orders = Order.objects.all()
        if status:
            orders = orders.filter(status=status)
        return orders.select_related("user")[:50]

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        context["orders"] = list(self.get_queryset())
        return context

    def get_fragment_data(self) -> dict[str, Any]:
        return {
            "orders": [
                {
                    "id": o.pk,
                    "reference": o.reference,
                    "customer_name": o.customer_name,
                    "status": o.status,
                    "status_display": o.get_status_display(),
                    "order_type": o.get_order_type_display(),
                    "total": str(o.total),
                    "created_at": o.created_at.isoformat(),
                    "items": [
                        {
                            "name": i.product_name,
                            "quantity": i.quantity,
                            "unit_price": str(i.unit_price),
                        }
                        for i in o.items.all()
                    ],
                }
                for o in self.get_queryset().prefetch_related("items")
            ]
        }


class OrderRowFragment(FragmentComponent):
    """Single order row — swapped after a status advance.

    The caller sets ``order`` before invoking ``get_fragment_context`` (the
    POST action resolves the instance once and reuses it), so the fragment
    renders the *updated* row without a second query.
    """

    fragment_name = "employee.fragments.order_row"
    template_name = "employee/fragments/order_row.html"
    htmx_only = True

    order: Order | None = None

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        order = self.order or Order.objects.select_related("user").get(
            pk=kwargs.get("order_id")
        )
        context["order"] = order
        return context
