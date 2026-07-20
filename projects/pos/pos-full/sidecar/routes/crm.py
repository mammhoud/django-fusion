"""
CRM routes — ported from bolt_api.py for Robyn server integration.

Provides contacts, companies, deals, pipelines, activities, and notes.
Uses Django ORM via routes/state.py (S.Node, S.SyncLog, etc.) and
imports shared.models.crm directly for CRM-specific models.

Endpoints:
    GET    /crm/dashboard         — CRM summary stats
    GET    /crm/contacts          — List contacts (search, paginate)
    GET    /crm/contacts/:id      — Get single contact
    POST   /crm/contacts          — Create contact (pydantic validation)
    GET    /crm/companies         — List companies
    GET    /crm/deals             — List deals (filter by stage)
    POST   /crm/deals             — Create deal (pydantic validation)
    GET    /crm/pipelines         — List pipelines with stages
    GET    /crm/activities        — List activities (filter by contact/deal)
    GET    /crm/notes             — List notes (filter by contact/deal)

@tested pos-full — CRM routes
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify, Response, Request

from routes import state as S

logger = logging.getLogger("pos_full_server.crm")

# ── Pydantic schemas (lazily loaded, same as bolt_api.py) ──

_PYDANTIC_READY = S._PYDANTIC_READY
if _PYDANTIC_READY:
    from pydantic import Field, ConfigDict  # noqa: F811
    try:
        from pydantic import BaseModel as _PydanticModel
    except ImportError:
        _PYDANTIC_READY = False

if _PYDANTIC_READY:

    class ContactSchema(_PydanticModel):
        first_name: str = Field(min_length=1, max_length=200)
        last_name: str = Field(min_length=1, max_length=200)
        email: str | None = None
        phone: str | None = None
        company_id: int | None = None
        model_config = ConfigDict(from_attributes=True, extra="forbid")

    class DealSchema(_PydanticModel):
        title: str = Field(min_length=1, max_length=200)
        value: float = Field(ge=0)
        pipeline_id: int
        stage_id: int
        contact_id: int | None = None
        company_id: int | None = None
        model_config = ConfigDict(from_attributes=True, extra="forbid")





# ===========================================================================
# CRM Dashboard
# ===========================================================================


async def get_crm_dashboard(request: Request):
    """GET /crm/dashboard — CRM summary statistics."""
    from shared.models.crm import Contact, Company, Deal, Activity

    @sync_to_async
    def _stats():
        return {
            "service": "POS Full - CRM Dashboard",
            "contacts": Contact.objects.filter(is_active=True).count(),
            "companies": Company.objects.filter(is_active=True).count(),
            "deals": Deal.objects.filter(is_active=True).count(),
            "activities": Activity.objects.filter(is_completed=False).count(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return jsonify(await _stats())


# ===========================================================================
# Contacts
# ===========================================================================


async def list_crm_contacts(request: Request):
    """GET /crm/contacts — List CRM contacts with search and pagination."""
    from shared.models.crm import Contact
    from django.db.models import Q

    q_param = request.query_params.get("q", "")
    page = int(str(request.query_params.get("page", "1")))
    per_page = min(int(str(request.query_params.get("per_page", "50"))), 200)

    @sync_to_async
    def _q():
        qs = Contact.objects.filter(is_active=True)
        if q_param:
            qs = qs.filter(
                Q(first_name__icontains=q_param)
                | Q(last_name__icontains=q_param)
                | Q(email__icontains=q_param)
            )
        qs = qs.order_by("-created_at")
        return S._paginate(qs, page, per_page)

    result = await _q()
    results = []
    for contact in result["data"]:
        results.append({
            "id": contact.id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company_id": contact.company_id,
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
        })

    return jsonify({
        "data": results,
        "pagination": result["pagination"],
    })


async def get_crm_contact(request: Request, contact_id: int):
    """GET /crm/contacts/:contact_id — Get a single contact by ID."""
    from shared.models.crm import Contact

    @sync_to_async
    def _q():
        try:
            return Contact.objects.get(id=contact_id, is_active=True)
        except Contact.DoesNotExist:
            return None

    contact = await _q()
    if contact is None:
        return S._error(404, "contact not found")

    return jsonify({
        "id": contact.id,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email,
        "phone": contact.phone,
        "company_id": contact.company_id,
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
    })


async def create_crm_contact(request: Request):
    """POST /crm/contacts — Create a new CRM contact."""
    from shared.models.crm import Contact

    try:
        body = request.json() or {}
    except Exception:
        return S._error(400, "invalid JSON body")

    if "first_name" not in body or "last_name" not in body:
        return S._error(400, "first_name and last_name are required")

    if _PYDANTIC_READY:
        try:
            validated = ContactSchema(**body)
            body = validated.model_dump()
        except Exception as exc:
            return S._error(400, f"validation failed: {exc}")

    @sync_to_async
    def _create():
        return Contact.objects.create(
            first_name=body["first_name"],
            last_name=body["last_name"],
            email=body.get("email"),
            phone=body.get("phone"),
            company_id=body.get("company_id"),
        )

    contact = await _create()
    return Response(
        status_code=201,
        headers={"Content-Type": "application/json"},
        description=json.dumps({
            "id": contact.id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company_id": contact.company_id,
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
        }),
    )


# ===========================================================================
# Companies
# ===========================================================================


async def list_crm_companies(request: Request):
    """GET /crm/companies — List CRM companies with search and pagination."""
    from shared.models.crm import Company
    from django.db.models import Q

    q_param = request.query_params.get("q", "")
    page = int(str(request.query_params.get("page", "1")))
    per_page = min(int(str(request.query_params.get("per_page", "50"))), 200)

    @sync_to_async
    def _q():
        qs = Company.objects.filter(is_active=True)
        if q_param:
            qs = qs.filter(Q(name__icontains=q_param) | Q(industry__icontains=q_param))
        qs = qs.order_by("name")
        return S._paginate(qs, page, per_page)

    result = await _q()
    results = []
    for company in result["data"]:
        results.append({
            "id": company.id,
            "name": company.name,
            "website": company.website,
            "phone": company.phone,
            "email": company.email,
            "industry": company.industry,
            "created_at": company.created_at.isoformat() if company.created_at else None,
        })

    return jsonify({
        "data": results,
        "pagination": result["pagination"],
    })


# ===========================================================================
# Deals
# ===========================================================================


async def list_crm_deals(request: Request):
    """GET /crm/deals — List CRM deals with stage filtering and pagination."""
    from shared.models.crm import Deal

    stage_id = int(str(request.query_params.get("stage_id", "0")))
    page = int(str(request.query_params.get("page", "1")))
    per_page = min(int(str(request.query_params.get("per_page", "50"))), 200)

    @sync_to_async
    def _q():
        qs = Deal.objects.filter(is_active=True)
        if stage_id:
            qs = qs.filter(stage_id=stage_id)
        qs = qs.order_by("-created_at")
        return S._paginate(qs, page, per_page)

    result = await _q()
    results = []
    for deal in result["data"]:
        results.append({
            "id": deal.id,
            "title": deal.title,
            "value": deal.value,
            "stage_id": deal.stage_id,
            "pipeline_id": deal.pipeline_id,
            "contact_id": deal.contact_id,
            "company_id": deal.company_id,
            "is_closed": deal.is_closed,
            "is_won": deal.is_won,
            "created_at": deal.created_at.isoformat() if deal.created_at else None,
        })

    return jsonify({
        "data": results,
        "pagination": result["pagination"],
    })


async def create_crm_deal(request: Request):
    """POST /crm/deals — Create a new CRM deal."""
    from shared.models.crm import Deal

    try:
        body = request.json() or {}
    except Exception:
        return S._error(400, "invalid JSON body")

    if "title" not in body or "pipeline_id" not in body or "stage_id" not in body:
        return S._error(400, "title, pipeline_id, and stage_id are required")

    if _PYDANTIC_READY:
        try:
            validated = DealSchema(**body)
            body = validated.model_dump()
        except Exception as exc:
            return S._error(400, f"validation failed: {exc}")

    @sync_to_async
    def _create():
        return Deal.objects.create(
            title=body["title"],
            value=body["value"],
            pipeline_id=body["pipeline_id"],
            stage_id=body["stage_id"],
            contact_id=body.get("contact_id"),
            company_id=body.get("company_id"),
        )

    deal = await _create()
    return Response(
        status_code=201,
        headers={"Content-Type": "application/json"},
        description=json.dumps({
            "id": deal.id,
            "title": deal.title,
            "value": deal.value,
            "stage_id": deal.stage_id,
            "pipeline_id": deal.pipeline_id,
            "created_at": deal.created_at.isoformat() if deal.created_at else None,
        }),
    )


# ===========================================================================
# Pipelines
# ===========================================================================


async def get_crm_pipelines(request: Request):
    """GET /crm/pipelines — List CRM pipelines with their stages."""
    from shared.models.crm import Pipeline

    @sync_to_async
    def _load():
        results = []
        pipelines = list(Pipeline.objects.filter(is_active=True).order_by("name"))
        for pipeline in pipelines:
            stages = []
            for stage in pipeline.stages.filter(is_active=True).order_by("display_order"):
                stages.append({
                    "id": stage.id,
                    "name": stage.name,
                    "display_order": stage.display_order,
                    "probability": stage.probability,
                    "color": stage.color,
                })
            results.append({
                "id": pipeline.id,
                "name": pipeline.name,
                "description": pipeline.description,
                "is_default": pipeline.is_default,
                "stages": stages,
            })
        return results

    return jsonify({"data": await _load()})


# ===========================================================================
# Activities
# ===========================================================================


async def list_crm_activities(request: Request):
    """GET /crm/activities — List CRM activities with filtering."""
    from shared.models.crm import Activity

    contact_id = int(str(request.query_params.get("contact_id", "0")))
    deal_id = int(str(request.query_params.get("deal_id", "0")))
    page = int(str(request.query_params.get("page", "1")))
    per_page = min(int(str(request.query_params.get("per_page", "50"))), 200)

    @sync_to_async
    def _q():
        qs = Activity.objects.all()
        if contact_id:
            qs = qs.filter(contact_id=contact_id)
        if deal_id:
            qs = qs.filter(deal_id=deal_id)
        qs = qs.order_by("-created_at")
        return S._paginate(qs, page, per_page)

    result = await _q()
    results = []
    for activity in result["data"]:
        results.append({
            "id": activity.id,
            "activity_type": activity.activity_type,
            "subject": activity.subject,
            "contact_id": activity.contact_id,
            "deal_id": activity.deal_id,
            "is_completed": activity.is_completed,
            "due_date": activity.due_date.isoformat() if activity.due_date else None,
            "created_at": activity.created_at.isoformat() if activity.created_at else None,
        })

    return jsonify({
        "data": results,
        "pagination": result["pagination"],
    })


# ===========================================================================
# Notes
# ===========================================================================


async def list_crm_notes(request: Request):
    """GET /crm/notes — List CRM notes with filtering."""
    from shared.models.crm import CRMNote

    contact_id = int(str(request.query_params.get("contact_id", "0")))
    deal_id = int(str(request.query_params.get("deal_id", "0")))
    page = int(str(request.query_params.get("page", "1")))
    per_page = min(int(str(request.query_params.get("per_page", "50"))), 200)

    @sync_to_async
    def _q():
        qs = CRMNote.objects.all()
        if contact_id:
            qs = qs.filter(contact_id=contact_id)
        if deal_id:
            qs = qs.filter(deal_id=deal_id)
        qs = qs.order_by("-is_pinned", "-created_at")
        return S._paginate(qs, page, per_page)

    result = await _q()
    results = []
    for note in result["data"]:
        results.append({
            "id": note.id,
            "content": note.content,
            "contact_id": note.contact_id,
            "deal_id": note.deal_id,
            "is_pinned": note.is_pinned,
            "created_at": note.created_at.isoformat() if note.created_at else None,
        })

    return jsonify({
        "data": results,
        "pagination": result["pagination"],
    })


# ===========================================================================
# Route registration
# ===========================================================================


def register_crm_routes(app):
    """Register all CRM route handlers on the given Robyn app.

    @tested pos-full — CRM routes ported from bolt_api.py

    @tested pos-full — CRM routes ported from bolt_api.py
    """

    @app.get("/crm/dashboard")
    async def _crm_dashboard(request: Request):
        return await get_crm_dashboard(request)

    @app.get("/crm/contacts")
    async def _crm_contacts(request: Request):
        return await list_crm_contacts(request)

    @app.get("/crm/contacts/:contact_id")
    async def _crm_contact(request: Request, contact_id: int):
        return await get_crm_contact(request, contact_id)

    @app.post("/crm/contacts")
    async def _crm_contact_create(request: Request):
        return await create_crm_contact(request)

    @app.get("/crm/companies")
    async def _crm_companies(request: Request):
        return await list_crm_companies(request)

    @app.get("/crm/deals")
    async def _crm_deals(request: Request):
        return await list_crm_deals(request)

    @app.post("/crm/deals")
    async def _crm_deal_create(request: Request):
        return await create_crm_deal(request)

    @app.get("/crm/pipelines")
    async def _crm_pipelines(request: Request):
        return await get_crm_pipelines(request)

    @app.get("/crm/activities")
    async def _crm_activities(request: Request):
        return await list_crm_activities(request)

    @app.get("/crm/notes")
    async def _crm_notes(request: Request):
        return await list_crm_notes(request)

    logger.info("Registered CRM routes (10 endpoints)")
