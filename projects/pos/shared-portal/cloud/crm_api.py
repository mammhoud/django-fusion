"""
Cloud CRM REST API — Sanic Blueprint with full-featured endpoints.

Provides CRUD, search, pagination, filtering, export, and dashboard
endpoints for all CRM entities: Contacts, Companies, Pipelines,
Stages, Deals, Activities, and Notes.

Data is stored in JSON files under POS_DATA_DIR/cloud/ for portability
(same pattern as the sidecar's JSON storage).

Enhancements over sidecar CRM:
  - Paginated list responses with metadata (total, page, per_page)
  - Search query parameter (q=...) across name, email, phone, tags
  - Filter parameters (industry, source, status, priority, etc.)
  - CSV/JSON data export endpoints
  - Dashboard stats (pipeline summary, deal counts, activity timeline)
  - Bulk import (POST with array of entities)

Related Names: crm, api, contacts, companies, pipelines, deals, activities
Tags: #crm #api #cloud #rest #pos-full
"""

from __future__ import annotations

import os
import json
import csv
import io
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from sanic import Blueprint, Request
from sanic.response import json as sanic_json, text as sanic_text


# ---------------------------------------------------------------------------
# Blueprint — mounted at /api/crm in cloud/server.py
# ---------------------------------------------------------------------------

crm_bp = Blueprint("cloud_crm", url_prefix="/api/crm")

# Data directory — set by cloud/server.py before blueprint registration
DATA_DIR: Path = Path(os.environ.get("CLOUD_DATA_DIR", "./cloud_data")) / "crm"


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def _ensure_dir() -> None:
    """Ensure CRM data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_entities(entity_type: str) -> list[dict]:
    """Load all entities of a type from JSON storage."""
    file_path = DATA_DIR / f"{entity_type}.json"
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_entities(entity_type: str, entities: list[dict]) -> None:
    """Save all entities of a type to JSON storage."""
    _ensure_dir()
    file_path = DATA_DIR / f"{entity_type}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2, default=str)


def _now() -> str:
    """Return ISO-8601 timestamp string."""
    return datetime.utcnow().isoformat()


def _new_id() -> str:
    """Return a new UUID string."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Generic CRUD helpers
# ---------------------------------------------------------------------------

def _list_entities(entity_type: str) -> list[dict]:
    """List all active entities."""
    return [e for e in _load_entities(entity_type) if e.get("is_active", True)]


def _get_entity(entity_type: str, entity_id: str) -> dict | None:
    """Get a single entity by ID."""
    for e in _load_entities(entity_type):
        if e["id"] == entity_id:
            return e
    return None


def _create_entity(entity_type: str, data: dict) -> dict:
    """Create a new entity with auto-generated fields."""
    entities = _load_entities(entity_type)
    entity = {
        "id": _new_id(),
        **data,
        "is_active": True,
        "created_at": _now(),
        "updated_at": _now(),
        "synced_at": None,
        "cloud_id": None,
    }
    entities.append(entity)
    _save_entities(entity_type, entities)
    return entity


def _update_entity(entity_type: str, entity_id: str, data: dict) -> dict | None:
    """Update an existing entity by ID. Returns None if not found."""
    entities = _load_entities(entity_type)
    for i, e in enumerate(entities):
        if e["id"] == entity_id:
            # Preserve read-only fields
            for key in ("id", "created_at"):
                data.pop(key, None)
            entities[i].update(data)
            entities[i]["updated_at"] = _now()
            _save_entities(entity_type, entities)
            return entities[i]
    return None


def _delete_entity(entity_type: str, entity_id: str) -> bool:
    """Soft-delete (deactivate) an entity. Returns True if found."""
    entities = _load_entities(entity_type)
    for i, e in enumerate(entities):
        if e["id"] == entity_id:
            entities[i]["is_active"] = False
            entities[i]["updated_at"] = _now()
            _save_entities(entity_type, entities)
            return True
    return False


# ---------------------------------------------------------------------------
# Search & pagination helpers
# ---------------------------------------------------------------------------

def _paginate(
    items: list[dict],
    page: int = 1,
    per_page: int = 50,
) -> dict:
    """Wrap a list of items in a paginated response envelope.

    Returns::
        {
            "data": [...],
            "pagination": {
                "page": 1,
                "per_page": 50,
                "total": 100,
                "total_pages": 2,
            }
        }
    """
    total = len(items)
    total_pages = max(1, -(-total // per_page))  # Ceiling division
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "data": items[start:end],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    }


def _search_entities(
    entity_type: str,
    q: str | None = None,
    filters: dict[str, Any] | None = None,
) -> list[dict]:
    """Search and filter entities.

    Args:
        entity_type: Entity type name (e.g. 'contacts').
        q: Full-text search query matched against name, email, phone, tags.
        filters: Dict of field=value exact-match filters.

    Returns:
        Filtered list of entities.
    """
    entities = _list_entities(entity_type)

    # Text search across key fields
    if q:
        q = q.lower().strip()
        searchable_fields = {
            "contacts": ["first_name", "last_name", "email", "phone", "mobile",
                         "job_title", "tags", "notes", "department"],
            "companies": ["name", "email", "phone", "website", "industry",
                          "tags", "description", "city", "country"],
            "deals": ["title", "description", "lost_reason"],
            "activities": ["subject", "description", "outcome"],
            "notes": ["content"],
            "pipelines": ["name", "description"],
            "stages": ["name"],
        }
        fields = searchable_fields.get(entity_type, [])
        entities = [
            e for e in entities
            if any(
                str(e.get(f, "")).lower().find(q) != -1
                for f in fields
            )
        ]

    # Exact-match filters (e.g. industry=Retail, is_active=true)
    if filters:
        for key, value in filters.items():
            if value is not None and value != "":
                entities = [e for e in entities if str(e.get(key)) == str(value)]

    return entities


def _parse_pagination(request: Request) -> tuple[int, int]:
    """Extract page and per_page from query args with defaults."""
    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", 50))
    except (ValueError, TypeError):
        per_page = 50
    # Clamp
    per_page = max(1, min(per_page, 200))
    page = max(1, page)
    return page, per_page


# ---------------------------------------------------------------------------
# Dashboard / Stats
# ---------------------------------------------------------------------------

@crm_bp.get("/dashboard")
async def dashboard(request: Request):
    """Get CRM dashboard summary statistics."""
    contacts = _list_entities("contacts")
    companies = _list_entities("companies")
    deals = _list_entities("deals")
    activities = _load_entities("activities")

    # Deal pipeline breakdown
    pipeline_stages = {}
    stages = _load_entities("stages")
    stage_map = {s["id"]: s.get("name", "Unknown") for s in stages}
    for deal in deals:
        sname = stage_map.get(deal.get("stage_id", ""), "Unknown")
        pipeline_stages[sname] = pipeline_stages.get(sname, 0) + 1

    # Activity timeline (last 7 days)
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    recent_activities = [
        a for a in activities
        if a.get("created_at", "") >= week_ago
    ]

    active_deals = [d for d in deals if not d.get("is_closed", True)]
    won_deals = [d for d in deals if d.get("is_won", False)]
    total_pipeline_value = sum(d.get("value", 0) for d in active_deals)
    won_value = sum(d.get("value", 0) for d in won_deals)

    return sanic_json({
        "contacts": {
            "total": len(contacts),
            "active": len([c for c in contacts if c.get("is_active", True)]),
        },
        "companies": {
            "total": len(companies),
            "active": len([c for c in companies if c.get("is_active", True)]),
        },
        "deals": {
            "total": len(deals),
            "active": len(active_deals),
            "won": len(won_deals),
            "total_pipeline_value": total_pipeline_value,
            "won_value": won_value,
            "pipeline_breakdown": pipeline_stages,
        },
        "activities": {
            "total": len(activities),
            "recent_7_days": len(recent_activities),
            "overdue": len([
                a for a in activities
                if not a.get("is_completed", False)
                and a.get("due_date") and a["due_date"] < _now()
            ]),
        },
    })


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

@crm_bp.get("/contacts")
async def list_contacts(request: Request):
    """List contacts with search, filtering, and pagination.

    Query params:
        q           Full-text search (name, email, phone, tags, job_title)
        company_id  Filter by company
        source      Filter by lead source
        is_active   Filter by active status (default: active only)
        page        Page number (default: 1)
        per_page    Items per page (default: 50, max: 200)

    Returns paginated response with metadata.
    """
    page, per_page = _parse_pagination(request)
    filters = {
        "company_id": request.args.get("company_id"),
        "source": request.args.get("source"),
        "is_active": request.args.get("is_active"),
    }
    q = request.args.get("q")
    results = _search_entities("contacts", q=q, filters=filters)
    return sanic_json(_paginate(results, page=page, per_page=per_page))


@crm_bp.get("/contacts/<contact_id:str>")
async def get_contact(request: Request, contact_id: str):
    """Get a single contact by ID."""
    contact = _get_entity("contacts", contact_id)
    if not contact:
        return sanic_json({"error": "contact not found"}, status=404)
    return sanic_json(contact)


@crm_bp.post("/contacts")
async def create_contact(request: Request):
    """Create a new contact.

    Required: first_name, last_name
    Optional: email, phone, mobile, job_title, department, company_id,
              address, source, tags, custom_fields, notes, avatar_url
    """
    payload = request.json or {}
    if not payload.get("first_name") or not payload.get("last_name"):
        return sanic_json(
            {"error": "first_name and last_name are required"}, status=400
        )
    contact = _create_entity("contacts", payload)
    return sanic_json(contact, status=201)


@crm_bp.patch("/contacts/<contact_id:str>")
async def update_contact(request: Request, contact_id: str):
    """Update an existing contact."""
    payload = request.json or {}
    contact = _update_entity("contacts", contact_id, payload)
    if not contact:
        return sanic_json({"error": "contact not found"}, status=404)
    return sanic_json(contact)


@crm_bp.delete("/contacts/<contact_id:str>")
async def delete_contact(request: Request, contact_id: str):
    """Soft-delete a contact (sets is_active=False)."""
    if _delete_entity("contacts", contact_id):
        return sanic_json({"status": "deleted"})
    return sanic_json({"error": "contact not found"}, status=404)


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

@crm_bp.get("/companies")
async def list_companies(request: Request):
    """List companies with search, filtering, and pagination.

    Query params:
        q           Full-text search (name, email, industry, city, country)
        industry    Filter by industry
        source      Filter by lead source
        is_active   Filter by active status
        page        Page number (default: 1)
        per_page    Items per page (default: 50, max: 200)
    """
    page, per_page = _parse_pagination(request)
    filters = {
        "industry": request.args.get("industry"),
        "source": request.args.get("source"),
        "is_active": request.args.get("is_active"),
    }
    q = request.args.get("q")
    results = _search_entities("companies", q=q, filters=filters)
    return sanic_json(_paginate(results, page=page, per_page=per_page))


@crm_bp.get("/companies/<company_id:str>")
async def get_company(request: Request, company_id: str):
    """Get a single company by ID."""
    company = _get_entity("companies", company_id)
    if not company:
        return sanic_json({"error": "company not found"}, status=404)
    return sanic_json(company)


@crm_bp.post("/companies")
async def create_company(request: Request):
    """Create a new company.

    Required: name
    Optional: website, email, phone, address, city, state, postal_code,
              country, industry, description, size, source, tags, tax_id
    """
    payload = request.json or {}
    if not payload.get("name"):
        return sanic_json({"error": "name is required"}, status=400)
    company = _create_entity("companies", payload)
    return sanic_json(company, status=201)


@crm_bp.patch("/companies/<company_id:str>")
async def update_company(request: Request, company_id: str):
    """Update an existing company."""
    payload = request.json or {}
    company = _update_entity("companies", company_id, payload)
    if not company:
        return sanic_json({"error": "company not found"}, status=404)
    return sanic_json(company)


@crm_bp.delete("/companies/<company_id:str>")
async def delete_company(request: Request, company_id: str):
    """Soft-delete a company."""
    if _delete_entity("companies", company_id):
        return sanic_json({"status": "deleted"})
    return sanic_json({"error": "company not found"}, status=404)


# ---------------------------------------------------------------------------
# Pipelines & Stages
# ---------------------------------------------------------------------------

@crm_bp.get("/pipelines")
async def list_pipelines(request: Request):
    """List all pipelines with their stages."""
    pipelines = _load_entities("pipelines")
    stages = _load_entities("stages")

    for pipeline in pipelines:
        pipeline["stages"] = [
            s for s in stages
            if s.get("pipeline_id") == pipeline["id"] and s.get("is_active", True)
        ]
        pipeline["stages"].sort(key=lambda s: s.get("display_order", 0))
        pipeline["deals_count"] = len([
            d for d in _list_entities("deals")
            if d.get("pipeline_id") == pipeline["id"]
        ])

    return sanic_json(pipelines)


@crm_bp.post("/pipelines")
async def create_pipeline(request: Request):
    """Create a new pipeline with optional stages."""
    payload = request.json or {}
    if not payload.get("name"):
        return sanic_json({"error": "name is required"}, status=400)

    stages_data = payload.pop("stages", [])
    pipeline = _create_entity("pipelines", payload)

    # Create stages
    for i, stage_data in enumerate(stages_data):
        stage_data["pipeline_id"] = pipeline["id"]
        stage_data.setdefault("display_order", i)
        _create_entity("stages", stage_data)

    pipeline["stages"] = [
        s for s in _load_entities("stages")
        if s.get("pipeline_id") == pipeline["id"]
    ]
    return sanic_json(pipeline, status=201)


@crm_bp.post("/stages")
async def create_stage(request: Request):
    """Create a new stage within a pipeline."""
    payload = request.json or {}
    if not payload.get("name") or not payload.get("pipeline_id"):
        return sanic_json(
            {"error": "name and pipeline_id are required"}, status=400
        )
    stage = _create_entity("stages", payload)
    return sanic_json(stage, status=201)


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------

@crm_bp.get("/deals")
async def list_deals(request: Request):
    """List deals with search, filtering, and pagination.

    Query params:
        q           Full-text search (title, description)
        stage_id    Filter by pipeline stage
        pipeline_id Filter by pipeline
        contact_id  Filter by contact
        company_id  Filter by company
        priority    Filter by priority (low, medium, high, critical)
        is_closed   Filter by closed status
        is_won      Filter by won status
        page        Page number (default: 1)
        per_page    Items per page (default: 50, max: 200)
    """
    page, per_page = _parse_pagination(request)
    filters = {
        "stage_id": request.args.get("stage_id"),
        "pipeline_id": request.args.get("pipeline_id"),
        "contact_id": request.args.get("contact_id"),
        "company_id": request.args.get("company_id"),
        "priority": request.args.get("priority"),
        "is_closed": request.args.get("is_closed"),
        "is_won": request.args.get("is_won"),
        "is_active": request.args.get("is_active"),
    }
    q = request.args.get("q")
    results = _search_entities("deals", q=q, filters=filters)
    return sanic_json(_paginate(results, page=page, per_page=per_page))


@crm_bp.get("/deals/<deal_id:str>")
async def get_deal(request: Request, deal_id: str):
    """Get a single deal by ID."""
    deal = _get_entity("deals", deal_id)
    if not deal:
        return sanic_json({"error": "deal not found"}, status=404)
    return sanic_json(deal)


@crm_bp.post("/deals")
async def create_deal(request: Request):
    """Create a new deal.

    Required: title, stage_id
    Optional: value, currency, priority, description, contact_id,
              company_id, discount_percent, expected_close_date
    """
    payload = request.json or {}
    if not payload.get("title"):
        return sanic_json({"error": "title is required"}, status=400)
    if not payload.get("stage_id"):
        return sanic_json({"error": "stage_id is required"}, status=400)
    deal = _create_entity("deals", payload)
    return sanic_json(deal, status=201)


@crm_bp.patch("/deals/<deal_id:str>")
async def update_deal(request: Request, deal_id: str):
    """Update a deal (e.g., move to a new stage, close as won/lost)."""
    payload = request.json or {}
    deal = _update_entity("deals", deal_id, payload)
    if not deal:
        return sanic_json({"error": "deal not found"}, status=404)
    return sanic_json(deal)


@crm_bp.delete("/deals/<deal_id:str>")
async def delete_deal(request: Request, deal_id: str):
    """Soft-delete a deal."""
    if _delete_entity("deals", deal_id):
        return sanic_json({"status": "deleted"})
    return sanic_json({"error": "deal not found"}, status=404)


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

@crm_bp.get("/activities")
async def list_activities(request: Request):
    """List activities with filtering and pagination.

    Query params:
        contact_id     Filter by contact
        deal_id        Filter by deal
        company_id     Filter by company
        activity_type  Filter by type (meeting, call, email, task, etc.)
        is_completed   Filter by completion status
        page           Page number (default: 1)
        per_page       Items per page (default: 50, max: 200)
    """
    page, per_page = _parse_pagination(request)
    activities = _list_entities("activities")

    # Filtering
    contact_id = request.args.get("contact_id")
    deal_id = request.args.get("deal_id")
    company_id = request.args.get("company_id")
    activity_type = request.args.get("activity_type")
    is_completed = request.args.get("is_completed")

    if contact_id:
        activities = [a for a in activities if a.get("contact_id") == contact_id]
    if deal_id:
        activities = [a for a in activities if a.get("deal_id") == deal_id]
    if company_id:
        activities = [a for a in activities if a.get("company_id") == company_id]
    if activity_type:
        activities = [a for a in activities if a.get("activity_type") == activity_type]
    if is_completed is not None:
        activities = [a for a in activities
                      if str(a.get("is_completed", False)).lower() == is_completed.lower()]

    return sanic_json(_paginate(activities, page=page, per_page=per_page))


@crm_bp.post("/activities")
async def create_activity(request: Request):
    """Create a new activity.

    Required: activity_type, subject
    Optional: description, outcome, duration_minutes, contact_id, deal_id,
              company_id, due_date, is_completed
    """
    payload = request.json or {}
    if not payload.get("activity_type") or not payload.get("subject"):
        return sanic_json(
            {"error": "activity_type and subject are required"}, status=400
        )
    activity = _create_entity("activities", payload)
    return sanic_json(activity, status=201)


@crm_bp.patch("/activities/<activity_id:str>")
async def update_activity(request: Request, activity_id: str):
    """Update an activity (e.g., mark as completed, change due date)."""
    payload = request.json or {}
    activity = _update_entity("activities", activity_id, payload)
    if not activity:
        return sanic_json({"error": "activity not found"}, status=404)
    return sanic_json(activity)


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

@crm_bp.get("/notes")
async def list_notes(request: Request):
    """List notes with entity filtering.

    Query params:
        contact_id  Filter by contact
        deal_id     Filter by deal
        company_id  Filter by company
    """
    notes = _load_entities("notes")
    contact_id = request.args.get("contact_id")
    deal_id = request.args.get("deal_id")
    company_id = request.args.get("company_id")

    if contact_id:
        notes = [n for n in notes if n.get("contact_id") == contact_id]
    if deal_id:
        notes = [n for n in notes if n.get("deal_id") == deal_id]
    if company_id:
        notes = [n for n in notes if n.get("company_id") == company_id]

    # Pinned first
    notes.sort(key=lambda n: (not n.get("is_pinned", False), n.get("created_at", "")), reverse=False)
    return sanic_json(notes)


@crm_bp.post("/notes")
async def create_note(request: Request):
    """Create a new note attached to a contact, deal, or company."""
    payload = request.json or {}
    if not payload.get("content"):
        return sanic_json({"error": "content is required"}, status=400)
    note = _create_entity("notes", payload)
    return sanic_json(note, status=201)


@crm_bp.delete("/notes/<note_id:str>")
async def delete_note(request: Request, note_id: str):
    """Delete a note."""
    if _delete_entity("notes", note_id):
        return sanic_json({"status": "deleted"})
    return sanic_json({"error": "note not found"}, status=404)


# ---------------------------------------------------------------------------
# Data Export
# ---------------------------------------------------------------------------

@crm_bp.get("/export/<entity_type:str>")
async def export_entities(request: Request, entity_type: str):
    """Export entities as CSV.

    Supported types: contacts, companies, deals, activities, notes
    Accept header: text/csv or application/json
    Default format: CSV
    """
    valid_types = {"contacts", "companies", "deals", "activities", "notes"}
    if entity_type not in valid_types:
        return sanic_json({"error": f"invalid entity type: {entity_type}"}, status=400)

    entities = _list_entities(entity_type)
    if not entities:
        return sanic_json({"error": f"no {entity_type} found"}, status=404)

    accept = request.headers.get("accept", "text/csv")

    if "application/json" in accept:
        return sanic_json({
            "entity_type": entity_type,
            "count": len(entities),
            "data": entities,
        })

    # CSV export
    output = io.StringIO()
    fieldnames = list(entities[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(entities)

    return sanic_text(
        output.getvalue(),
        headers={"Content-Type": "text/csv",
                 "Content-Disposition": f'attachment; filename="{entity_type}.csv"'},
    )


@crm_bp.post("/import/<entity_type:str>")
async def import_entities(request: Request, entity_type: str):
    """Bulk-import entities as JSON array.

    Accepts a JSON array of entity objects and creates each one.
    Returns summary with counts of created vs errors.
    """
    valid_types = {"contacts", "companies", "deals", "activities", "notes"}
    if entity_type not in valid_types:
        return sanic_json({"error": f"invalid entity type: {entity_type}"}, status=400)

    payload = request.json
    if not isinstance(payload, list):
        return sanic_json({"error": "payload must be a JSON array"}, status=400)

    created = 0
    errors = 0
    error_details = []

    for i, item in enumerate(payload):
        try:
            _create_entity(entity_type, item)
            created += 1
        except Exception as exc:
            errors += 1
            error_details.append({"index": i, "error": str(exc)})

    return sanic_json({
        "entity_type": entity_type,
        "total": len(payload),
        "created": created,
        "errors": errors,
        "error_details": error_details,
    })


# ---------------------------------------------------------------------------
# Cloud Sync
# ---------------------------------------------------------------------------

@crm_bp.get("/sync/status")
async def sync_status(request: Request):
    """Get current cloud sync status."""
    config = _load_entities("cloud_config")
    queue = _load_entities("sync_queue")
    return sanic_json({
        "config": config[0] if config else None,
        "pending_count": len([q for q in queue if not q.get("is_processing")]),
        "processing_count": len([q for q in queue if q.get("is_processing")]),
        "failed_count": len([
            q for q in queue if q.get("error_count", 0) > 0
        ]),
    })


@crm_bp.post("/sync/config")
async def update_sync_config(request: Request):
    """Update cloud sync configuration."""
    payload = request.json or {}
    configs = _load_entities("cloud_config")
    if configs:
        config = _update_entity("cloud_config", configs[0]["id"], payload)
    else:
        config = _create_entity("cloud_config", payload)
    return sanic_json(config)


@crm_bp.post("/sync/trigger")
async def trigger_sync(request: Request):
    """Manually trigger a sync of all pending changes."""
    queue = _load_entities("sync_queue")
    pending = [q for q in queue if not q.get("is_processing")]
    return sanic_json({
        "triggered": True,
        "items_to_sync": len(pending),
    })


@crm_bp.get("/sync/log")
async def sync_log(request: Request):
    """Get sync history log."""
    log = _load_entities("sync_log")
    limit = request.args.get("limit", 50)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 50
    return sanic_json(log[:limit])


# ---------------------------------------------------------------------------
# Initialize default pipeline on first run
# ---------------------------------------------------------------------------

def init_default_pipeline() -> None:
    """Create a default sales pipeline if none exist.

    Creates a 6-stage pipeline with standard sales stages,
    each with a win probability and display color.

    Stages:
        1. New Lead     (10%)  — Gray
        2. Qualified    (25%)  — Blue
        3. Proposal     (50%)  — Purple
        4. Negotiation  (75%)  — Amber
        5. Closed Won   (100%) — Green
        6. Closed Lost  (0%)   — Red
    """
    _ensure_dir()
    pipelines = _load_entities("pipelines")
    if pipelines:
        return

    # Create default pipeline
    pipeline = _create_entity("pipelines", {
        "name": "Default Sales Pipeline",
        "description": "Standard sales pipeline covering lead capture through close",
        "is_default": True,
    })

    # Create default stages
    default_stages = [
        {"name": "New Lead",      "display_order": 0, "probability": 10.0,  "color": "#94a3b8"},
        {"name": "Qualified",     "display_order": 1, "probability": 25.0,  "color": "#3b82f6"},
        {"name": "Proposal",      "display_order": 2, "probability": 50.0,  "color": "#8b5cf6"},
        {"name": "Negotiation",   "display_order": 3, "probability": 75.0,  "color": "#f59e0b"},
        {"name": "Closed Won",    "display_order": 4, "probability": 100.0, "color": "#22c55e"},
        {"name": "Closed Lost",   "display_order": 5, "probability": 0.0,   "color": "#ef4444"},
    ]

    for stage_data in default_stages:
        stage_data["pipeline_id"] = pipeline["id"]
        _create_entity("stages", stage_data)
@tested shared-portal/cloud - POS-KO → POS rename verified
