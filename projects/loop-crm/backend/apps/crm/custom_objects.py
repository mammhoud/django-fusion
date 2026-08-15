"""Custom-object runtime schema — declarative definitions + validated JSON rows.

A workspace can add a new object type (``CustomObjectDefinition``) and write
rows (``CustomObjectRecord``) without a migration. Validation lives here, at
the service boundary, so both the API road and any future screen share one
honest contract and never persist an unvalidated field value.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

from .models import CustomObjectDefinition

FIELD_TYPES = {
    "text",
    "textarea",
    "number",
    "boolean",
    "date",
    "url",
    "email",
    "select",
    "multi_select",
}


def validate_definition_fields(fields) -> list[dict]:
    """Normalize and validate a declarative field list.

    Returns the canonical ``[{key, label, type, required, options}]`` shape or
    raises ``ValidationError`` on duplicate keys, unknown types, or a select
    field without an options list.
    """
    if not isinstance(fields, list):
        raise ValidationError("Fields must be a JSON list.")
    normalized: list[dict] = []
    seen: set[str] = set()
    for field in fields:
        if not isinstance(field, dict):
            raise ValidationError("Each field must be a JSON object.")
        key = str(field.get("key") or "").strip().lower().replace(" ", "_")
        field_type = str(field.get("type") or "text")
        if not key:
            raise ValidationError("Each field needs a key.")
        if field_type not in FIELD_TYPES:
            raise ValidationError(f"Unknown field type: {field_type}.")
        if key in seen:
            raise ValidationError(f"Duplicate field key: {key}.")
        seen.add(key)
        options = field.get("options") or []
        if field_type in {"select", "multi_select"} and not isinstance(options, list):
            raise ValidationError(f"Field {key} needs an options list.")
        normalized.append(
            {
                "key": key,
                "label": str(field.get("label") or key),
                "type": field_type,
                "required": bool(field.get("required")),
                "options": [str(o) for o in options] if field_type in {"select", "multi_select"} else [],
            }
        )
    return normalized


def validate_record_data(definition: CustomObjectDefinition, data) -> dict:
    """Validate a record payload against the definition's field schema.

    Returns a cleaned dict (numbers coerced to strings, dates validated,
    select values checked against the configured options) or raises
    ``ValidationError`` with per-field messages.
    """
    if not isinstance(data, dict):
        raise ValidationError("Record data must be a JSON object.")
    fields = {field["key"]: field for field in (definition.fields or [])}
    unknown = set(data) - set(fields)
    if unknown:
        raise ValidationError({key: "Unknown field." for key in sorted(unknown)})

    cleaned: dict = {}
    for key, spec in fields.items():
        value = data.get(key)
        if value in (None, "", []):
            if spec["required"]:
                raise ValidationError({key: "This field is required."})
            continue
        field_type = spec["type"]
        if field_type == "number":
            try:
                value = str(Decimal(str(value)))
            except Exception as exc:  # noqa: BLE001 - normalize invalid JSON
                raise ValidationError({key: "Expected a number."}) from exc
        elif field_type == "boolean":
            if not isinstance(value, bool):
                raise ValidationError({key: "Expected a boolean."})
        elif field_type == "date":
            try:
                date.fromisoformat(str(value))
            except ValueError as exc:
                raise ValidationError({key: "Expected an ISO date (YYYY-MM-DD)."}) from exc
        elif field_type in {"select", "multi_select"}:
            selected = value if field_type == "multi_select" else [value]
            if not isinstance(selected, list) or any(item not in spec["options"] for item in selected):
                raise ValidationError({key: "Value is not one of the configured options."})
            value = selected if field_type == "multi_select" else selected[0]
        else:
            value = str(value)
        cleaned[key] = value
    return cleaned
