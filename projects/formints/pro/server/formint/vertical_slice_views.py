"""
Formint — Vertical-slice HTMX data-only views.

Each endpoint returns ONLY the data fragment (no page chrome, no layout,
no skeleton). Astro owns the shell, skeleton, and lifecycle.

Vertical slice: branch → order → KDS → sync → report
"""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Sum
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from django_fusion.plugins.htmx import is_htmx_request

from models.node import Node
from models.ops import KitchenTicket
from models.pos import Sale, Customer, Product
from models.sync import SyncLog

__all__ = [
    "vertical_orders",
    "vertical_kds",
    "vertical_sync",
    "vertical_report",
]


def _htmx_fragment(request: HttpRequest, template: str, context: dict) -> HttpResponse:
    """Render a data-only fragment with standard HTMX response headers."""
    response = render(request, template, context)
    response["X-Formint-Response-Mode"] = "htmx-data-only"
    response["Cache-Control"] = "no-store"
    return response


def _reject_non_htmx(request: HttpRequest) -> JsonResponse | None:
    if not is_htmx_request(request):
        return JsonResponse(
            {"detail": "HTMX data fragment — use from Astro shell", "product": "formint-pos"},
            status=406,
        )
    return None


def vertical_orders(request: HttpRequest) -> HttpResponse:
    reject = _reject_non_htmx(request)
    if reject:
        return reject

    recent = Sale.objects.select_related("customer").order_by("-sale_date")[:12]
    today_count = Sale.objects.filter(sale_date__date=timezone.localdate()).count()
    today_total = sum(
        float(t or 0)
        for t in Sale.objects.filter(sale_date__date=timezone.localdate()).values_list("total", flat=True)
    )
    return _htmx_fragment(request, "formint/vertical_slice/orders.html", {
        "orders": recent, "today_count": today_count, "today_revenue": today_total,
    })


def vertical_kds(request: HttpRequest) -> HttpResponse:
    reject = _reject_non_htmx(request)
    if reject:
        return reject

    active = KitchenTicket.objects.exclude(status="delivered").order_by("-created_at")[:12]
    pending = KitchenTicket.objects.filter(status="pending").count()
    preparing = KitchenTicket.objects.filter(status="preparing").count()
    ready = KitchenTicket.objects.filter(status="ready").count()
    now = timezone.now()
    overdue = sum(
        1 for t in active
        if t.status not in ("delivered", "ready")
        and t.prepare_time_minutes and t.created_at
        and now > t.created_at + timedelta(minutes=t.prepare_time_minutes)
    )
    return _htmx_fragment(request, "formint/vertical_slice/kds.html", {
        "tickets": active, "pending": pending, "preparing": preparing,
        "ready": ready, "overdue": overdue,
    })


def vertical_sync(request: HttpRequest) -> HttpResponse:
    reject = _reject_non_htmx(request)
    if reject:
        return reject

    nodes = Node.objects.filter(is_active=True)
    total = nodes.count()
    online = nodes.filter(status="online").count()
    offline = total - online
    last_synced = (
        SyncLog.objects.filter(status="success")
        .order_by("-created_at")
        .values_list("created_at", flat=True)
        .first()
    )
    return _htmx_fragment(request, "formint/vertical_slice/sync.html", {
        "total": total, "online": online, "offline": offline,
        "last_synced": last_synced,
        "sync_healthy": online > 0 and offline == 0,
    })


def vertical_report(request: HttpRequest) -> HttpResponse:
    reject = _reject_non_htmx(request)
    if reject:
        return reject

    today = timezone.localdate()
    today_sales = Sale.objects.filter(sale_date__date=today)
    today_count = today_sales.count()
    today_revenue = sum(float(s.total or 0) for s in today_sales)

    week_start = today - timedelta(days=today.weekday())
    week_sales = Sale.objects.filter(sale_date__date__gte=week_start)
    week_count = week_sales.count()
    week_agg = week_sales.aggregate(total=Sum("total"))
    week_revenue = float(week_agg["total"] or 0)

    return _htmx_fragment(request, "formint/vertical_slice/report.html", {
        "today_count": today_count, "today_revenue": today_revenue,
        "week_count": week_count, "week_revenue": week_revenue,
        "product_count": Product.objects.filter(is_active=True).count(),
        "customer_count": Customer.objects.filter(is_active=True).count(),
    })
