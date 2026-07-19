"""
Cloud Master CRM REST API views.
Replaces the old Sanic sidecar CRM API with Django views.

@tested pos-portal/full - Cloud CRM API views
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Company, Contact, Deal

DATA_DIR = Path(__file__).parent.parent / "cloud_data"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ── Dashboard ──────────────────────────────────────────────────────────


@require_GET
def dashboard(request):
    """Get CRM dashboard summary statistics."""
    return JsonResponse({
        "companies": Company.objects.filter(is_active=True).count(),
        "contacts": Contact.objects.filter(is_active=True).count(),
        "deals": Deal.objects.count(),
        "active_deals": Deal.objects.filter(is_closed=False).count(),
        "won_deals": Deal.objects.filter(is_won=True).count(),
        "pipeline_stages": {
            stage: Deal.objects.filter(stage=stage).count()
            for stage, _ in Deal.PIPELINE_CHOICES
        },
    })


# ── Companies ──────────────────────────────────────────────────────────


@require_GET
def list_companies(request):
    """List all active companies."""
    companies = Company.objects.filter(is_active=True).values()
    return JsonResponse({"data": list(companies)})


@csrf_exempt
@require_POST
def create_company(request):
    """Create a new company."""
    data = json.loads(request.body)
    company = Company.objects.create(**data)
    return JsonResponse({"id": company.id, "name": company.name}, status=201)


# ── Contacts ───────────────────────────────────────────────────────────


@require_GET
def list_contacts(request):
    """List all active contacts."""
    contacts = Contact.objects.filter(is_active=True).select_related("company").values(
        "id", "first_name", "last_name", "email", "phone",
        "job_title", "company__name", "source", "created_at",
    )
    return JsonResponse({"data": list(contacts)})


@csrf_exempt
@require_POST
def create_contact(request):
    """Create a new contact."""
    data = json.loads(request.body)
    company_id = data.pop("company_id", None)
    if company_id:
        data["company"] = Company.objects.get(id=company_id)
    contact = Contact.objects.create(**data)
    return JsonResponse({"id": contact.id, "name": str(contact)}, status=201)


# ── Deals ──────────────────────────────────────────────────────────────


@require_GET
def list_deals(request):
    """List all deals."""
    deals = Deal.objects.select_related("contact", "company").values(
        "id", "title", "value", "currency", "stage", "probability",
        "is_won", "is_closed", "contact__first_name", "contact__last_name",
        "company__name", "created_at",
    )
    return JsonResponse({"data": list(deals)})


@csrf_exempt
@require_POST
def create_deal(request):
    """Create a new deal."""
    data = json.loads(request.body)

    # Resolve relations
    contact_id = data.pop("contact_id", None)
    company_id = data.pop("company_id", None)
    if contact_id:
        data["contact"] = Contact.objects.get(id=contact_id)
    if company_id:
        data["company"] = Company.objects.get(id=company_id)

    deal = Deal.objects.create(**data)
    return JsonResponse({"id": deal.id, "title": deal.title}, status=201)
