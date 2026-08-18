"""Render-first CRM screens and HTMX create interactions."""

from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.core.realtime import safe_publish_workspace_event
from apps.core.resource_tables import resource_table
from apps.core.tenancy import current_workspace_id
from apps.core.views import LoopPageView

from .forms import CompanyForm, ContactForm, DealForm
from .models import Company, Contact, Deal, Pipeline, PipelineStage


def _member_workspace_id(request: HttpRequest) -> int | None:
    try:
        profile = request.user.profile
    except Exception:  # noqa: BLE001 - legacy accounts may predate UserProfile
        profile = None
    return getattr(profile, "workspace_id", None)


def company_rows(request: HttpRequest) -> list[Company]:
    queryset = Company.objects.select_related("workspace", "owner")
    workspace_id = _member_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        return list(queryset.order_by("name")[:50])
    except (OperationalError, ProgrammingError):
        return []


def contact_rows(request: HttpRequest) -> list[Contact]:
    queryset = Contact.objects.select_related("workspace", "company", "owner")
    workspace_id = _member_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        return list(queryset.order_by("last_name", "first_name")[:50])
    except (OperationalError, ProgrammingError):
        return []


def deal_rows(request: HttpRequest) -> list[Deal]:
    queryset = Deal.objects.select_related(
        "workspace", "company", "contact", "pipeline", "stage", "owner"
    )
    workspace_id = _member_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        return list(queryset.order_by("-created_at")[:50])
    except (OperationalError, ProgrammingError):
        return []


class CompanyListView(LoopPageView):
    template_name = "dashboard/companies.html"
    module_id = "crm"
    page_title = _("Companies")
    page_kicker = _("CRM · companies")
    page_description = _("Build the account graph with firmographics, ownership, and the context behind each relationship.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = company_rows(self.request)
        context.update(
            {
                "companies": rows,
                "company_form": CompanyForm(request=self.request),
                "company_table": resource_table(rows, "companies"),
            }
        )
        return context


class ContactListView(LoopPageView):
    template_name = "dashboard/contacts.html"
    module_id = "crm"
    page_title = _("Contacts")
    page_kicker = _("CRM · contacts")
    page_description = _(
        "Keep people connected to the companies, roles, and conversations that move a deal forward."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = contact_rows(self.request)
        context.update(
            {
                "contacts": rows,
                "contact_form": ContactForm(request=self.request),
                "contact_table": resource_table(rows, "contacts"),
            }
        )
        return context


class DealListView(LoopPageView):
    template_name = "dashboard/deals.html"
    module_id = "crm"
    page_title = _("Deals")
    page_kicker = _("CRM · deals")
    page_description = _("Track qualified revenue from first conversation to a close, with pipeline stages and campaign context intact.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = deal_rows(self.request)
        context.update(
            {
                "deals": rows,
                "deal_form": DealForm(request=self.request),
                "deal_table": resource_table(rows, "deals"),
            }
        )
        return context


def _crm_context(request: HttpRequest, kind: str) -> dict:
    if kind == "companies":
        rows = company_rows(request)
        return {
            "companies": rows,
            "company_form": CompanyForm(request=request),
            "company_table": resource_table(rows, "companies"),
        }
    if kind == "contacts":
        rows = contact_rows(request)
        return {
            "contacts": rows,
            "contact_form": ContactForm(request=request),
            "contact_table": resource_table(rows, "contacts"),
        }
    rows = deal_rows(request)
    return {"deals": rows, "deal_form": DealForm(request=request), "deal_table": resource_table(rows, "deals")}


@require_POST
@login_required
def company_create(request: HttpRequest) -> HttpResponse:
    form = CompanyForm(request.POST, request=request)
    if not form.is_valid():
        return render(
            request, "dashboard/partials/company_form.html", {"company_form": form}, status=422
        )
    company = form.save()
    safe_publish_workspace_event(
        company.workspace_id, "resource.created", {"resource": "companies", "pk": company.pk}
    )
    return render(
        request, "dashboard/partials/company_success.html", _crm_context(request, "companies")
    )


@require_POST
@login_required
def contact_create(request: HttpRequest) -> HttpResponse:
    form = ContactForm(request.POST, request=request)
    if not form.is_valid():
        return render(
            request, "dashboard/partials/contact_form.html", {"contact_form": form}, status=422
        )
    contact = form.save()
    safe_publish_workspace_event(
        contact.workspace_id, "resource.created", {"resource": "contacts", "pk": contact.pk}
    )
    return render(
        request, "dashboard/partials/contact_success.html", _crm_context(request, "contacts")
    )


@require_POST
@login_required
def deal_create(request: HttpRequest) -> HttpResponse:
    form = DealForm(request.POST, request=request)
    if not form.is_valid():
        return render(request, "dashboard/partials/deal_form.html", {"deal_form": form}, status=422)
    deal = form.save()
    safe_publish_workspace_event(
        deal.workspace_id, "resource.created", {"resource": "deals", "pk": deal.pk}
    )
    return render(request, "dashboard/partials/deal_success.html", _crm_context(request, "deals"))


def _workspace_scope(request: HttpRequest):
    try:
        profile = request.user.profile
    except Exception:  # noqa: BLE001
        profile = None
    return getattr(profile, "workspace_id", None)


def _stage_payload(stage: PipelineStage) -> dict:
    return {
        "id": stage.pk,
        "name": stage.name,
        "stage_type": stage.stage_type,
        "color": stage.color,
        "probability": stage.probability,
        "order": stage.order,
    }


def _deal_payload(deal: Deal) -> dict:
    return {
        "id": deal.pk,
        "name": deal.name,
        "company": deal.company.name,
        "company_id": deal.company_id,
        "value": str(deal.value),
        "owner": getattr(deal.owner, "get_full_name", lambda: "")()
        or getattr(deal.owner, "username", ""),
        "expected_close_date": deal.expected_close_date.isoformat(),
        "campaign": deal.campaign.name if deal.campaign_id else None,
    }


@login_required
@ensure_csrf_cookie
def pipeline_board_api(request: HttpRequest) -> JsonResponse:
    """Board payload: pipelines with stages and stage-scoped deals.

    ``ensure_csrf_cookie`` guarantees the ``csrftoken`` cookie is present, so
    the kanban island's subsequent CSRF-protected move POST has a token to
    echo back.
    """
    if request.method != "GET":
        return JsonResponse({"detail": "This read endpoint accepts GET only."}, status=405)
    workspace_id = _workspace_scope(request)
    pipelines = Pipeline.objects.prefetch_related(
        "stages", "deals__company", "deals__owner", "deals__campaign"
    ).order_by("order")
    if workspace_id is not None:
        pipelines = pipelines.filter(workspace_id=workspace_id)
    results = []
    for pipeline in pipelines:
        stages = list(pipeline.stages.all())
        deal_rows = {deal.stage_id: deal for deal in pipeline.deals.all()}
        results.append(
            {
                "id": pipeline.pk,
                "name": pipeline.name,
                "stages": [
                    {
                        **_stage_payload(stage),
                        "deals": [_deal_payload(deal_rows[stage.pk])]
                        if stage.pk in deal_rows
                        else [],
                    }
                    for stage in stages
                ],
            }
        )
    return JsonResponse({"results": results, "count": len(results)})


@login_required
def deal_move_api(request: HttpRequest, pk: int) -> JsonResponse:
    """Move a deal to another stage of its own pipeline (kanban drop).

    Session-authenticated and CSRF-protected; the kanban island echoes the
    ``csrftoken`` cookie back as ``X-CSRFToken`` (see PipelineBoard.tsx). The
    canonical Bolt road authenticates with JWTs and does not need CSRF.
    """
    if request.method not in ("PATCH", "POST"):
        return JsonResponse({"detail": "This endpoint accepts PATCH/POST only."}, status=405)
    workspace_id = current_workspace_id(request)
    deals = Deal.objects.all()
    if workspace_id is not None:
        deals = deals.filter(workspace_id=workspace_id)
    deal = get_object_or_404(deals, pk=pk)
    try:
        payload = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
    stage_id = payload.get("stage_id")
    if stage_id is None:
        return JsonResponse({"detail": "stage_id is required."}, status=400)
    stages = PipelineStage.objects.select_related("pipeline")
    if workspace_id is not None:
        stages = stages.filter(pipeline__workspace_id=workspace_id)
    stage = get_object_or_404(stages, pk=stage_id)
    try:
        deal.transition_to_stage(stage)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    safe_publish_workspace_event(
        deal.workspace_id,
        "resource.updated",
        {"resource": "deals", "pk": deal.pk, "stage_id": stage.pk},
    )
    return JsonResponse({"ok": True, "deal": _deal_payload(deal), "stage_id": stage.pk})
