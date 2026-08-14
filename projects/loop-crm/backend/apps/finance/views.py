"""Render-first finance pages and tenant-scoped HTMX mutations."""
from __future__ import annotations

from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
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
