"""Schema-aware django-fusion table projections for the API resource surface.

Every registered Bolt resource gets a fusion table contract — ``headers`` as
``{"key", "label", "type", "sortable"}`` dicts and ``rows`` as row-cell lists
aligned to the headers. Values are rendered through ``RowGenerator`` with
domain formatters (money, dates, owner names) so the JSON the frontend tables
consume stays declarative and the column metadata stays schema-driven.

The table contract is exposed on both API roads:
* ``GET /bolt/tables/{resource}``        (canonical django-bolt, JWT)
* ``GET /api/v1/tables/{resource}/``     (compatibility road, session cookie)

``type`` is one of ``text | money | date | pill | link`` and lets the
frontend table renderer apply the right tactical styling without duplicating
schema knowledge. Cells are plain strings — the renderer wraps pill/link
cells in its own markup.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django_fusion.fragments.tables.row_generator import RowGenerator

from .resources import RESOURCES


def _money(value) -> str:
    if value is None:
        return "—"
    try:
        return f"${Decimal(value):,.0f}"
    except (TypeError, ValueError, InvalidOperation):
        return "—"


def _date(value) -> str:
    if value is None:
        return "—"
    if hasattr(value, "strftime"):
        return value.strftime("%b %-d, %Y")
    return str(value)


def _person(value) -> str:
    if value is None:
        return "Unassigned"
    return getattr(value, "get_full_name", lambda: "")() or getattr(value, "username", "")


def _text(value) -> str:
    return value if value not in (None, "") else "—"


def _rows(headers: list[dict], row_dicts: list[dict]) -> list[list]:
    return [[row.get(col["key"], "—") for col in headers] for row in row_dicts]


#: Per-resource table contract: columns (aligned to ``read_fields`` where
#: possible), value formatters, and column types for the frontend renderer.
RESOURCE_TABLE_COLUMNS: dict[str, dict[str, Any]] = {
    "companies": {
        "columns": [
            "name",
            "industry",
            "email",
            "city",
            "country",
            "annual_revenue",
            "employee_count",
            "owner",
        ],
        "formatters": {"annual_revenue": _money, "owner": _person},
        "types": {
            "name": "text",
            "industry": "pill",
            "email": "text",
            "city": "text",
            "country": "text",
            "annual_revenue": "money",
            "employee_count": "text",
            "owner": "text",
        },
    },
    "contacts": {
        "columns": ["full_name", "title", "company", "email", "phone", "linkedin_url"],
        "formatters": {"linkedin_url": _text},
        "types": {
            "full_name": "text",
            "title": "pill",
            "company": "pill",
            "email": "text",
            "phone": "text",
            "linkedin_url": "link",
        },
    },
    "deals": {
        "columns": [
            "name",
            "company",
            "value",
            "stage",
            "owner",
            "expected_close_date",
            "campaign",
        ],
        "formatters": {"value": _money, "owner": _person, "expected_close_date": _date},
        "types": {
            "name": "text",
            "company": "pill",
            "value": "money",
            "stage": "pill",
            "owner": "text",
            "expected_close_date": "date",
            "campaign": "pill",
        },
    },
    "activities": {
        "columns": ["subject", "activity_type", "status", "deal", "scheduled_at", "completed_at"],
        "formatters": {"scheduled_at": _date, "completed_at": _date},
        "types": {
            "subject": "text",
            "activity_type": "pill",
            "status": "pill",
            "deal": "pill",
            "scheduled_at": "date",
            "completed_at": "date",
        },
    },
    "pipelines": {
        "columns": ["name", "description", "is_default", "order"],
        "formatters": {},
        "types": {"name": "text", "description": "text", "is_default": "pill", "order": "text"},
    },
    "campaigns": {
        "columns": ["name", "description", "budget", "start_date", "end_date"],
        "formatters": {"budget": _money, "start_date": _date, "end_date": _date},
        "types": {
            "name": "text",
            "description": "text",
            "budget": "money",
            "start_date": "date",
            "end_date": "date",
        },
    },
    "channels": {
        "columns": ["platform", "account_name", "is_active"],
        "formatters": {},
        "types": {"platform": "pill", "account_name": "text", "is_active": "pill"},
    },
    "posts": {
        "columns": ["content", "scheduled_at", "status", "channel", "campaign"],
        "formatters": {"scheduled_at": _date},
        "types": {
            "content": "text",
            "scheduled_at": "date",
            "status": "pill",
            "channel": "pill",
            "campaign": "pill",
        },
    },
    "touchpoints": {
        "columns": ["source", "occurred_at", "weight", "deal", "campaign"],
        "formatters": {"occurred_at": _date, "weight": _text},
        "types": {
            "source": "pill",
            "occurred_at": "date",
            "weight": "text",
            "deal": "pill",
            "campaign": "pill",
        },
    },
    "invoices": {
        "columns": ["number", "company", "status", "currency", "total", "due_on"],
        "formatters": {"total": _money, "due_on": _date},
        "types": {
            "number": "text",
            "company": "pill",
            "status": "pill",
            "currency": "text",
            "total": "money",
            "due_on": "date",
        },
    },
    "payments": {
        "columns": ["invoice", "amount", "paid_on", "method", "reference"],
        "formatters": {"amount": _money, "paid_on": _date},
        "types": {
            "invoice": "pill",
            "amount": "money",
            "paid_on": "date",
            "method": "pill",
            "reference": "text",
        },
    },
    "revenue": {
        "columns": ["deal", "campaign", "kind", "amount", "recognized_on"],
        "formatters": {"amount": _money, "recognized_on": _date},
        "types": {
            "deal": "pill",
            "campaign": "pill",
            "kind": "pill",
            "amount": "money",
            "recognized_on": "date",
        },
    },
    "webhooks": {
        "columns": ["url", "events", "is_active", "created_at"],
        "formatters": {"created_at": _date},
        "types": {"url": "text", "events": "pill", "is_active": "pill", "created_at": "date"},
    },
    "email_accounts": {
        "columns": ["provider", "email", "last_synced_at", "is_active"],
        "formatters": {"last_synced_at": _date},
        "types": {
            "provider": "pill",
            "email": "text",
            "last_synced_at": "date",
            "is_active": "pill",
        },
    },
    "email_messages": {
        "columns": ["subject", "sender_email", "direction", "received_at"],
        "formatters": {"received_at": _date},
        "types": {
            "subject": "text",
            "sender_email": "text",
            "direction": "pill",
            "received_at": "date",
        },
    },
}


def table_columns_for(resource: str) -> dict[str, Any]:
    """Column config for a resource, or an explicit-columns fallback."""
    if resource in RESOURCE_TABLE_COLUMNS:
        return RESOURCE_TABLE_COLUMNS[resource]
    read_fields = tuple(f for f in RESOURCES[resource].read_fields if f != "id")
    return {
        "columns": list(read_fields),
        "formatters": {},
        "types": {f: "text" for f in read_fields},
    }


def resource_table(queryset, resource: str) -> dict:
    """Build the fusion table contract for a resource queryset."""
    config = table_columns_for(resource)
    columns = config["columns"]
    gen = RowGenerator(
        queryset,
        columns=columns,
        formatters=config["formatters"],
    )
    headers = gen.get_columns()
    types = config["types"]
    resolved_headers = [{**col, "type": types.get(col["key"], "text")} for col in headers]
    rows = gen.get_rows()
    return {
        "resource": resource,
        "headers": resolved_headers,
        "rows": _rows(resolved_headers, rows),
        "count": len(rows),
    }
