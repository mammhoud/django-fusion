"""Render-first CRM screens and HTMX create interactions."""
from __future__ import annotations

from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.core.views import LoopPageView

from .forms import CompanyForm, ContactForm, DealForm
from .models import Company, Contact, Deal


def _member_workspace_id(request: HttpRequest) -> int | None:
    try:
        profile = request.user.profile
    except Exception:  # noqa: BLE001 - legacy accounts may predate UserProfile
        profile = None
    return getattr(profile, "workspace_id", None)


def company_rows(request: HttpRequest) -> list[Company]:
    queryset = Company.objects.select_related("workspace", "owner").order_by("name")[:50]
    workspace_id = _member_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        return list(queryset)
    except (OperationalError, ProgrammingError):
        return []


def contact_rows(request: HttpRequest) -> list[Contact]:
    queryset = Contact.objects.select_related("workspace", "company", "owner").order_by("last_name", "first_name")[:50]
    workspace_id = _member_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        return list(queryset)
    except (OperationalError, ProgrammingError):
        return []


def deal_rows(request: HttpRequest) -> list[Deal]:
    queryset = Deal.objects.select_related("workspace", "company", "contact", "pipeline", "stage", "owner").order_by("-created_at")[:50]
    workspace_id = _member_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        return list(queryset)
    except (OperationalError, ProgrammingError):
        return []


class CompanyListView(LoopPageView):
    template_name = "dashboard/companies.html"
    module_id = "crm"
    page_title = "Companies"
    page_kicker = "CRM · companies"
    page_description = "Build the account graph with firmographics, ownership, and the context behind each relationship."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"companies": company_rows(self.request), "company_form": CompanyForm(request=self.request)})
        return context


class ContactListView(LoopPageView):
    template_name = "dashboard/contacts.html"
    module_id = "crm"
    page_title = "Contacts"
    page_kicker = "CRM · contacts"
    page_description = "Keep people connected to the companies, roles, and conversations that move a deal forward."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"contacts": contact_rows(self.request), "contact_form": ContactForm(request=self.request)})
        return context


class DealListView(LoopPageView):
    template_name = "dashboard/deals.html"
    module_id = "crm"
    page_title = "Deals"
    page_kicker = "CRM · deals"
    page_description = "Track qualified revenue from first conversation to a close, with pipeline stages and campaign context intact."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"deals": deal_rows(self.request), "deal_form": DealForm(request=self.request)})
        return context


def _crm_context(request: HttpRequest, kind: str) -> dict:
    if kind == "companies":
        return {"companies": company_rows(request), "company_form": CompanyForm(request=request)}
    if kind == "contacts":
        return {"contacts": contact_rows(request), "contact_form": ContactForm(request=request)}
    return {"deals": deal_rows(request), "deal_form": DealForm(request=request)}


@require_POST
def company_create(request: HttpRequest) -> HttpResponse:
    form = CompanyForm(request.POST, request=request)
    if not form.is_valid():
        return render(request, "dashboard/partials/company_form.html", {"company_form": form}, status=422)
    form.save()
    return render(request, "dashboard/partials/company_success.html", _crm_context(request, "companies"))


@require_POST
def contact_create(request: HttpRequest) -> HttpResponse:
    form = ContactForm(request.POST, request=request)
    if not form.is_valid():
        return render(request, "dashboard/partials/contact_form.html", {"contact_form": form}, status=422)
    form.save()
    return render(request, "dashboard/partials/contact_success.html", _crm_context(request, "contacts"))


@require_POST
def deal_create(request: HttpRequest) -> HttpResponse:
    form = DealForm(request.POST, request=request)
    if not form.is_valid():
        return render(request, "dashboard/partials/deal_form.html", {"deal_form": form}, status=422)
    form.save()
    return render(request, "dashboard/partials/deal_success.html", _crm_context(request, "deals"))
