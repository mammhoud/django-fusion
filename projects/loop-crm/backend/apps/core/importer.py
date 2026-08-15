"""Tenant-scoped CSV import for the CRM graph (companies/contacts/deals).

The importer parses a CSV upload and creates workspace-scoped records, resolving
forward relations (contact → company, deal → company) by *name within the
caller's workspace only*. A foreign company name simply errors instead of
leaking another tenant's rows.
"""
from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction

from apps.crm.models import Company, Contact, Deal

#: The object types the import screen may target, in dependency order.
IMPORTABLE_OBJECTS = ("companies", "contacts", "deals")

#: Human-readable expected columns per object type (for the UI hint).
EXPECTED_COLUMNS = {
    "companies": ["name", "industry", "website", "email", "phone", "city", "country"],
    "contacts": ["first_name", "last_name", "email", "company", "title", "phone"],
    "deals": ["name", "company", "value", "expected_close_date", "pipeline"],
}


def parse_csv(text: str) -> list[dict[str, str]]:
    """Parse CSV text into a list of dict rows (first row is the header)."""
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def _cell(row: dict[str, str], *keys: str) -> str:
    """Read the first non-empty cell across case-insensitive header aliases."""
    lowered = {key.strip().lower(): value for key, value in row.items()}
    for key in keys:
        value = lowered.get(key.lower(), "") or ""
        if str(value).strip():
            return str(value).strip()
    return ""


def _company_by_name(workspace_id: int, name: str) -> Company | None:
    return Company.objects.filter(workspace_id=workspace_id, name__iexact=name).first()


@transaction.atomic
def import_rows(object_type: str, rows: list[dict], workspace_id: int | None, user=None) -> dict:
    """Create records from parsed rows, returning ``{created, errors}``.

    ``errors`` is a list of ``{row, message}`` (row is 1-based CSV line). The
    whole batch is atomic: a failure on one row rolls back everything, which
    keeps a partial import from leaving half a dataset.
    """
    if workspace_id is None:
        return {"created": 0, "errors": [{"row": 0, "message": "A workspace is required."}]}
    created = 0
    errors: list[dict] = []
    for index, row in enumerate(rows, start=2):
        if object_type == "companies":
            name = _cell(row, "name")
            if not name:
                errors.append({"row": index, "message": "name is required"})
                continue
            Company.objects.create(
                workspace_id=workspace_id,
                name=name,
                industry=_cell(row, "industry"),
                website=_cell(row, "website"),
                email=_cell(row, "email"),
                phone=_cell(row, "phone"),
                city=_cell(row, "city"),
                country=_cell(row, "country"),
            )
        elif object_type == "contacts":
            first_name = _cell(row, "first_name", "firstname")
            last_name = _cell(row, "last_name", "lastname")
            email = _cell(row, "email")
            company_name = _cell(row, "company", "company_name")
            if not (first_name and last_name and email):
                errors.append({"row": index, "message": "first_name, last_name, and email are required"})
                continue
            company = _company_by_name(workspace_id, company_name)
            if company is None:
                errors.append({"row": index, "message": f"company {company_name!r} not found in this workspace"})
                continue
            Contact.objects.create(
                workspace_id=workspace_id,
                company=company,
                first_name=first_name,
                last_name=last_name,
                email=email,
                title=_cell(row, "title"),
                phone=_cell(row, "phone"),
            )
        elif object_type == "deals":
            name = _cell(row, "name")
            company_name = _cell(row, "company", "company_name")
            value = _cell(row, "value", "amount")
            close_date = _cell(row, "expected_close_date", "close_date")
            if not (name and company_name and value and close_date):
                errors.append({"row": index, "message": "name, company, value, and expected_close_date are required"})
                continue
            company = _company_by_name(workspace_id, company_name)
            if company is None:
                errors.append({"row": index, "message": f"company {company_name!r} not found in this workspace"})
                continue
            try:
                value_decimal = Decimal(value)
            except InvalidOperation:
                errors.append({"row": index, "message": f"value {value!r} is not a number"})
                continue
            try:
                parsed_date = date.fromisoformat(close_date)
            except ValueError:
                errors.append({"row": index, "message": f"expected_close_date {close_date!r} is not YYYY-MM-DD"})
                continue
            Deal.objects.create(
                workspace_id=workspace_id,
                company=company,
                name=name,
                value=value_decimal,
                expected_close_date=parsed_date,
            )
        else:
            errors.append({"row": index, "message": f"unknown object type {object_type!r}"})
            continue
        created += 1
    return {"created": created, "errors": errors}
