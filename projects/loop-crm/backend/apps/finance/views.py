"""Render-first finance pages and tenant-scoped HTMX mutations."""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.db.models.functions import TruncMonth
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.core.realtime import safe_publish_workspace_event
from apps.core.views import LoopPageView

from . import export
from .forms import InvoiceForm, PaymentForm
from .models import Invoice, Payment, RevenueEvent
from .services import revenue_trend_results, trend_aggregates
from .tables import invoice_table, payment_table, revenue_table


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
        return list(
            _scoped(
                Invoice.objects.select_related("company", "deal").order_by("-issued_on"), request
            )[:50]
        )
    except (OperationalError, ProgrammingError):
        return []


def payment_rows(request):
    try:
        return list(
            _scoped(
                Payment.objects.select_related("invoice", "invoice__company").order_by("-paid_on"),
                request,
            )[:50]
        )
    except (OperationalError, ProgrammingError):
        return []


def revenue_rows(request):
    try:
        return list(
            _scoped(
                RevenueEvent.objects.select_related("deal", "campaign", "invoice").order_by(
                    "-recognized_on"
                ),
                request,
            )[:50]
        )
    except (OperationalError, ProgrammingError):
        return []


class FinanceDashboardView(LoopPageView):
    template_name = "dashboard/finance.html"
    module_id = "finance"
    page_title = _("Finance")
    page_kicker = _("Finance · revenue control")
    page_description = _("Turn closed pipeline into invoices, payments, and recognized revenue without losing campaign context.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_finance_context(self.request))
        return context


class InvoiceListView(FinanceDashboardView):
    page_title = _("Invoices")
    page_kicker = _("Finance · invoices")
    page_description = _(
        "Issue customer invoices from real companies and deals, then keep payment state current."
    )


class RevenueListView(FinanceDashboardView):
    page_title = _("Revenue")
    page_kicker = _("Finance · recognized revenue")
    page_description = _("Review revenue events created from won pipeline and trace them back to campaigns and invoices.")


class PaymentListView(FinanceDashboardView):
    page_title = _("Payments")
    page_kicker = _("Finance · payments")
    page_description = _(
        "Record receipts against issued invoices and keep outstanding balances honest."
    )


def _finance_context(request):
    return {
        "invoices": invoice_rows(request),
        "payments": payment_rows(request),
        "revenue_events": revenue_rows(request),
        "invoice_form": InvoiceForm(request=request),
        "payment_form": PaymentForm(request=request),
        "invoice_table": invoice_table(invoice_rows(request)),
        "payment_table": payment_table(payment_rows(request)),
        "revenue_table": revenue_table(revenue_rows(request)),
    }


@require_POST
@login_required
def invoice_create(request: HttpRequest) -> HttpResponse:
    form = InvoiceForm(request.POST, request=request)
    if not form.is_valid():
        return render(
            request, "dashboard/partials/invoice_form.html", {"invoice_form": form}, status=422
        )
    invoice = form.save()
    safe_publish_workspace_event(
        invoice.workspace_id, "resource.created", {"resource": "invoices", "pk": invoice.pk}
    )
    return render(request, "dashboard/partials/invoice_success.html", _finance_context(request))


@require_POST
@login_required
def payment_create(request: HttpRequest) -> HttpResponse:
    form = PaymentForm(request.POST, request=request)
    if not form.is_valid():
        return render(
            request, "dashboard/partials/payment_form.html", {"payment_form": form}, status=422
        )
    payment = form.save()
    safe_publish_workspace_event(
        payment.workspace_id, "resource.created", {"resource": "payments", "pk": payment.pk}
    )
    safe_publish_workspace_event(
        payment.invoice.workspace_id,
        "resource.updated",
        {"resource": "invoices", "pk": payment.invoice_id},
    )
    return render(request, "dashboard/partials/payment_success.html", _finance_context(request))


@login_required
def finance_export(request: HttpRequest) -> HttpResponse:
    """Export the workspace's invoices, payments, or POS revenue as CSV/JSON.

    ``?kind=invoices|payments|pos_revenue&format=csv|json``. Read-only and
    workspace-scoped; the CSV download is attachment-served.
    """
    kind = request.GET.get("kind", "invoices")
    fmt = request.GET.get("format", "csv")
    if kind not in export.EXPORTERS:
        return JsonResponse({"detail": "Unknown export kind."}, status=404)
    if fmt not in {"csv", "json"}:
        return JsonResponse({"detail": "Format must be csv or json."}, status=400)
    workspace_id = _workspace_id(request)
    rows = export.EXPORTERS[kind](workspace_id)
    if fmt == "json":
        return JsonResponse({"results": export.jsonable_rows(rows), "count": len(rows)})
    response = HttpResponse(export.to_csv(rows), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="loop-crm-{kind}.csv"'
    return response


@login_required
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
            .annotate(**trend_aggregates())
            .order_by("month")
        )
    except (OperationalError, ProgrammingError):
        rows = []
    return JsonResponse(revenue_trend_results(rows))
