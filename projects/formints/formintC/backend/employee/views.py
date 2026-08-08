"""
Employee views — staff-only dashboard + order inbox (django-fusion pipeline).

Mirrors the shop app split: full page via ``PageHandler``, HTMX fragments via
``employee.fusion_components`` handled through the ``django-fusion`` dual-mode
contract. All endpoints are gated for staff users.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET, require_POST

from django_fusion.plugins.htmx import is_htmx_request
from django_fusion.routes.pages.handler import PageHandler

from shop.fusion import get_effective_render_first
from shop.models import Order

from .fusion_components import OrderRowFragment, OrderRowsFragment, StatsFragment

__all__ = [
    "dashboard",
    "orders_fragment",
    "stats_fragment",
    "order_status",
]


def _staff_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


staff_required = user_passes_test(_staff_required, login_url="/accounts/login/")


def _not_staff() -> JsonResponse:
    return JsonResponse(
        {"detail": "Staff access required.", "product": "formintc-purchase"},
        status=403,
    )


# ── Dashboard page ─────────────────────────────────────────────────────────


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_required, name="dispatch")
class EmployeeDashboardView(PageHandler):
    """Employee home — today's stats + the live order inbox."""

    template_name = "employee/dashboard.html"
    page_title = "Staff desk"

    def get_context_data(self, request=None, **kwargs):
        context = super().get_context_data(request=request, **kwargs)
        context["order_statuses"] = Order.Status.choices
        return context


dashboard = EmployeeDashboardView.as_view()


# ── HTMX fragments ─────────────────────────────────────────────────────────


@require_GET
def orders_fragment(request: HttpRequest) -> HttpResponse:
    """HTMX — filtered order rows for the inbox."""
    if not request.user.is_authenticated or not _staff_required(request.user):
        return _not_staff()
    if not is_htmx_request(request):
        return JsonResponse({"detail": "HTMX data fragment."}, status=406)

    component = OrderRowsFragment()
    component.setup(request)
    if get_effective_render_first(request):
        response = component.render_fragment_response(component.get_fragment_context())
        response["X-FormintC-Response-Mode"] = "django-fusion-fragment"
    else:
        response = render(request, component.template_name, component.get_fragment_context())
        response["X-FormintC-Response-Mode"] = "htmx-data-only"
    response["Cache-Control"] = "no-store"
    return response


@require_GET
def stats_fragment(request: HttpRequest) -> HttpResponse:
    """HTMX — refreshed KPI chips (polled by the dashboard)."""
    if not request.user.is_authenticated or not _staff_required(request.user):
        return _not_staff()
    if not is_htmx_request(request):
        return JsonResponse({"detail": "HTMX data fragment."}, status=406)

    component = StatsFragment()
    component.setup(request)
    if get_effective_render_first(request):
        response = component.render_fragment_response(component.get_fragment_context())
        response["X-FormintC-Response-Mode"] = "django-fusion-fragment"
    else:
        response = render(request, component.template_name, component.get_fragment_context())
        response["X-FormintC-Response-Mode"] = "htmx-data-only"
    response["Cache-Control"] = "no-store"
    return response


@require_POST
def order_status(request: HttpRequest, order_id: int) -> HttpResponse:
    """HTMX — advance an order's status; returns the updated row + triggers stats refresh."""
    if not request.user.is_authenticated or not _staff_required(request.user):
        return _not_staff()
    if not is_htmx_request(request):
        return JsonResponse({"detail": "HTMX action — use from the Astro shell."}, status=406)

    order = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get("status", "")
    if new_status in Order.Status.values:
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

    # POST actions deliberately stay data-only (no render-first envelope):
    # the Astro shell swaps the row HTML and listens for ordersStatsUpdated.
    component = OrderRowFragment()
    component.order = order
    component.setup(request)
    context = component.get_fragment_context()
    response = render(request, component.template_name, context)
    response["X-FormintC-Response-Mode"] = "htmx-data-only"
    response["HX-Trigger"] = "ordersStatsUpdated"
    response["Cache-Control"] = "no-store"
    return response
