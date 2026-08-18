"""Schema-aware django-fusion tables for Loop-CRM finance screens.

Same fusion table component contract as ``apps.crm.tables``: ``headers`` as
``{"key", "label", "sortable"}`` dicts and ``rows`` as row-cell lists aligned
to the headers. Domain formatters keep currency, dates, and status pills
consistent across the receivable ledger, receipt ledger, and revenue events.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.utils.safestring import SafeString, mark_safe
from django_fusion.fragments.tables.row_generator import RowGenerator

from .models import Invoice, Payment, RevenueEvent


def _money(value) -> str:
    if value is None:
        return "—"
    try:
        return f"${Decimal(value):,.2f}"
    except (TypeError, ValueError, InvalidOperation):
        return "—"


def _date(value) -> str:
    return value.strftime("%b %-d, %Y") if value else "—"


def _pill(value) -> SafeString:
    if value is None:
        return mark_safe("—")
    return mark_safe(f'<span class="loop-pill">{value}</span>')


def _invoice_ref(value) -> SafeString:
    if value is None:
        return mark_safe("—")
    return mark_safe(f"<strong>{value}</strong>")


def _rows(headers: list[dict], row_dicts: list[dict]) -> list[list]:
    return [[row.get(col["key"], "—") for col in headers] for row in row_dicts]


def invoice_table(queryset) -> dict:
    """Receivable ledger — company, deal link, status, and amounts."""
    columns = ["number", "company", "deal", "status", "issued_on", "due_on", "total", "outstanding"]
    gen = RowGenerator(
        queryset,
        columns=columns,
        formatters={
            "number": _invoice_ref,
            "company": _pill,
            "deal": _pill,
            "status": _pill,
            "issued_on": _date,
            "due_on": _date,
            "total": _money,
            "outstanding": _money,
        },
    )
    headers = gen.get_columns()
    return {"headers": headers, "rows": _rows(headers, gen.get_rows())}


def payment_table(queryset) -> dict:
    """Receipt ledger — invoice reference, method, amount, and date."""
    columns = ["invoice", "method", "amount", "paid_on", "reference"]
    gen = RowGenerator(
        queryset,
        columns=columns,
        formatters={
            "invoice": _pill,
            "method": _pill,
            "amount": _money,
            "paid_on": _date,
        },
    )
    headers = gen.get_columns()
    return {"headers": headers, "rows": _rows(headers, gen.get_rows())}


def revenue_table(queryset) -> dict:
    """Recognized revenue — deal, campaign, kind, amount, and recognition date."""
    columns = ["deal", "campaign", "kind", "amount", "recognized_on", "external_ref"]
    gen = RowGenerator(
        queryset,
        columns=columns,
        formatters={
            "deal": _pill,
            "campaign": _pill,
            "kind": _pill,
            "amount": _money,
            "recognized_on": _date,
        },
    )
    headers = gen.get_columns()
    return {"headers": headers, "rows": _rows(headers, gen.get_rows())}
