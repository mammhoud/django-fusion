"""Render-first finance pages and tenant-scoped HTMX mutations."""
from __future__ import annotations

import datetime

from django.db import OperationalError, ProgrammingError
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.views import LoopPageView

from .forms import InvoiceForm, PaymentForm
from .models import Invoice, Payment, RevenueEvent


def _workspace_id(request: HttpRequest) -> int | None:
    try:
        return request.user.profile.workspace_id
    except Exception:  # noqa: BLE001 - accounts created before profiles exist
        return None


def _scoped(queryset, request):
    workspace_id = _workspace_id(request)
    return queryset.filter(workspace_id=workspace_id) if workspace_id is not None else queryset


def invoice_rows(request):
    try:
        return list(_scoped(Invoice.objects.select_related("company", "deal").order_by("-issued_on"), request)[:50])
    except (OperationalError, ProgrammingError):
        return []


def payment_rows(request):
    try:
        return list(_scoped(Payment.objects.select_related("invoice", "invoice__company").order_by("-paid_on"), request)[:50])
    except (OperationalError, ProgrammingError):
        return []


def revenue_rows(request):
    try:
        return list(_scoped(RevenueEvent.objects.select_related("deal", "campaign", "invoice").order_by("-recognized_on"), request)[:50])
    except (OperationalError, ProgrammingError):
        return []


class FinanceDashboardView(LoopPageView):
    template_name = "dashboard/finance.html"
    module_id = "finance"
    page_title = "Finance"
    page_kicker = "Finance · revenue control"
    page_description = "Turn closed pipeline into invoices, payments, and recognized revenue without losing campaign context."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_finance_context(self.request))
        return context


class InvoiceListView(FinanceDashboardView):
    page_title = "Invoices"
    page_kicker = "Finance · invoices"
    page_description = "Issue customer invoices from real companies and deals, then keep payment state current."


class RevenueListView(FinanceDashboardView):
    page_title = "Revenue"
    page_kicker = "Finance · recognized revenue"
    page_description = "Review revenue events created from won pipeline and trace them back to campaigns and invoices."


class PaymentListView(FinanceDashboardView):
    page_title = "Payments"
    page_kicker = "Finance · payments"
    page_description = "Record receipts against issued invoices and keep outstanding balances honest."


def _finance_context(request):
    return {
        "invoices": invoice_rows(request),
        "payments": payment_rows(request),
        "revenue_events": revenue_rows(request),
        "invoice_form": InvoiceForm(request=request),
        "payment_form": PaymentForm(request=request),
    }


@require_POST
def invoice_create(request: HttpRequest) -> HttpResponse:
    form = InvoiceForm(request.POST, request=request)
    if not form.is_valid():
        return render(request, "dashboard/partials/invoice_form.html", {"invoice_form": form}, status=422)
    form.save()
    return render(request, "dashboard/partials/invoice_success.html", _finance_context(request))


@require_POST
def payment_create(request: HttpRequest) -> HttpResponse:
    form = PaymentForm(request.POST, request=request)
    if not form.is_valid():
        return render(request, "dashboard/partials/payment_form.html", {"payment_form": form}, status=422)
    form.save()
    return render(request, "dashboard/partials/payment_success.html", _finance_context(request))


def _month_first(date: datetime.date, months_ago: int) -> datetime.date:
    year, month = date.year, date.month
    for _ in range(months_ago):
        month -= 1
        if month == 0:
            year -= 1
            month = 12
    return datetime.date(year, month, 1)


def revenue_trend_api(request: HttpRequest) -> JsonResponse:
    """Monthly recognized-revenue totals for the RevOps dashboard trend card.

    Returns the trailing six months (zero-filled when a month has no revenue)
    so the chart shows a real window instead of a sparse list. Scoped to the
    caller's workspace when a profile workspace exists.
    """
    if request.method != "GET":
        return JsonResponse({"detail": "This read endpoint accepts GET only."}, status=405)
    try:
        rows = list(
            _scoped(RevenueEvent.objects.all(), request)
            .annotate(month=TruncMonth("recognized_on"))
            .values("month")
            .annotate(total=Sum("amount"), events=Count("id"))
            .order_by("month")
        )
    except (OperationalError, ProgrammingError):
        rows = []

    by_month = {row["month"]: row for row in rows}
    today = timezone.localdate()
    results = []
    for months_ago in range(5, -1, -1):
        first = _month_first(today, months_ago)
        bucket = by_month.get(first)
        results.append(
            {
                "month": first.strftime("%Y-%m"),
                "label": first.strftime("%b %Y"),
                "total": str(bucket["total"] if bucket else "0.00"),
                "events": bucket["events"] if bucket else 0,
            }
        )
    return JsonResponse(
        {
            "results": results,
            "count": len(results),
            "grand_total": str(sum(Decimal(row["total"]) for row in rows)),
        }
    )
