"""Accounting export: invoices, payments, and POS revenue as CSV or JSON.

Exports are workspace-scoped and read-only — a member only ever sees their own
tenant's ledger. CSV uses ``csv.DictWriter``; JSON returns the same rows with
values coerced to strings so the two formats stay interchangeable.
"""
from __future__ import annotations

import csv
import io
import json
from decimal import Decimal

from apps.finance.models import Invoice, Payment
from apps.pos.models import PosSale

INVOICE_FIELDS = ("number", "company__name", "status", "currency", "subtotal", "tax", "total", "issued_on", "due_on")
PAYMENT_FIELDS = ("invoice__number", "amount", "paid_on", "method", "reference")
POS_FIELDS = ("external_id", "sale_date", "subtotal", "tax_amount", "discount_amount", "total", "payment_method", "status")


def invoice_export_rows(workspace_id: int):
    return list(
        Invoice.objects.filter(workspace_id=workspace_id)
        .values(*INVOICE_FIELDS)
        .order_by("-issued_on")
    )


def payment_export_rows(workspace_id: int):
    return list(
        Payment.objects.filter(workspace_id=workspace_id)
        .values(*PAYMENT_FIELDS)
        .order_by("-paid_on")
    )


def pos_revenue_export_rows(workspace_id: int):
    return list(
        PosSale.objects.filter(workspace_id=workspace_id)
        .values(*POS_FIELDS)
        .order_by("-sale_date")
    )


EXPORTERS = {
    "invoices": invoice_export_rows,
    "payments": payment_export_rows,
    "pos_revenue": pos_revenue_export_rows,
}


def _stringify(value) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def jsonable_rows(rows: list[dict]) -> list[dict]:
    return [{key: _stringify(value) for key, value in row.items()} for row in rows]


def to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _stringify(value) for key, value in row.items()})
    return buffer.getvalue()


def export_rows(workspace_id: int, kind: str) -> list[dict]:
    """Return raw (uncoerced) rows for the requested export kind."""
    return EXPORTERS[kind](workspace_id)


def export_json(workspace_id: int, kind: str) -> str:
    return json.dumps(jsonable_rows(EXPORTERS[kind](workspace_id)))
