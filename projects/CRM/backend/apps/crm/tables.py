"""Schema-aware django-fusion tables for Loop-CRM CRM screens.

Each builder returns the fusion table component contract: ``headers`` as a list
of ``{"key", "label", "sortable"}`` dicts and ``rows`` as a list of row-cell
lists aligned to the headers. Values are rendered through ``RowGenerator`` with
domain formatters (money, dates, owner names, stage pills) so the table markup
stays declarative and the data stays schema-driven.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.utils.safestring import SafeString, mark_safe
from django_fusion.fragments.tables.row_generator import RowGenerator

from .models import Company, Contact, Deal


def _money(value) -> str:
    if value is None:
        return "—"
    try:
        return f"${Decimal(value):,.0f}"
    except (TypeError, ValueError, InvalidOperation):
        return "—"


def _date(value) -> str:
    return value.strftime("%b %-d, %Y") if value else "—"


def _person(value) -> str:
    if value is None:
        return "Unassigned"
    return getattr(value, "get_full_name", lambda: "")() or getattr(value, "username", "")


def _pill(value) -> SafeString:
    if value is None:
        return mark_safe("—")
    return mark_safe(f'<span class="loop-pill">{value}</span>')


def _link(value) -> SafeString:
    if not value:
        return mark_safe("—")
    return mark_safe(f'<a href="{value}" target="_blank" rel="noreferrer">Open ↗</a>')


def _rows(headers: list[dict], row_dicts: list[dict]) -> list[list]:
    """Align RowGenerator row dicts to header order."""
    return [[row.get(col["key"], "—") for col in headers] for row in row_dicts]


def company_table(queryset) -> dict:
    """Company directory table — firmographics, revenue, and ownership."""
    columns = [
        "name",
        "industry",
        "city",
        "country",
        "email",
        "annual_revenue",
        "employee_count",
        "owner",
    ]
    gen = RowGenerator(
        queryset,
        columns=columns,
        formatters={"annual_revenue": _money, "owner": _person},
    )
    headers = gen.get_columns()
    return {"headers": headers, "rows": _rows(headers, gen.get_rows())}


def contact_table(queryset) -> dict:
    """People directory table — roles, company, and communication channels."""
    columns = ["full_name", "title", "company", "email", "phone", "linkedin_url"]
    gen = RowGenerator(
        queryset,
        columns=columns,
        formatters={"linkedin_url": _link, "company": _pill},
    )
    headers = gen.get_columns()
    return {"headers": headers, "rows": _rows(headers, gen.get_rows())}


def deal_table(queryset) -> dict:
    """Pipeline revenue table — value, stage, owner, and attribution context."""
    columns = [
        "name",
        "company",
        "value",
        "stage",
        "owner",
        "expected_close_date",
        "campaign",
    ]
    gen = RowGenerator(
        queryset,
        columns=columns,
        formatters={
            "value": _money,
            "stage": _pill,
            "owner": _person,
            "expected_close_date": _date,
            "campaign": _pill,
        },
    )
    headers = gen.get_columns()
    return {"headers": headers, "rows": _rows(headers, gen.get_rows())}
