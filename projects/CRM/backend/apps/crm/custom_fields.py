"""Custom-object metadata for the Loop-CRM data model.

Records already keep tenant-scoped ``custom_attributes`` JSON. This catalog
makes those fields discoverable and editable by a future admin/API surface
without coupling field definitions to provider-specific schemas.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError

from .models import CustomFieldDefinition

CUSTOM_OBJECT_CATALOG = (
    {
        "object": "company",
        "label": "Company",
        "fields": [
            {"key": "lifecycle_stage", "label": "Lifecycle stage", "type": "select"},
            {"key": "territory", "label": "Territory", "type": "text"},
            {"key": "lead_source", "label": "Lead source", "type": "text"},
        ],
    },
    {
        "object": "contact",
        "label": "Contact",
        "fields": [
            {"key": "persona", "label": "Persona", "type": "select"},
            {"key": "consent_status", "label": "Consent status", "type": "select"},
        ],
    },
    {
        "object": "deal",
        "label": "Deal",
        "fields": [
            {"key": "forecast_category", "label": "Forecast category", "type": "select"},
            {"key": "next_step", "label": "Next step", "type": "text"},
            {"key": "source_post_id", "label": "Influencing post", "type": "text"},
        ],
    },
)


def custom_object_catalog(workspace=None):
    """Return built-in and persisted field metadata for a workspace."""
    catalog = [{**item, "fields": [dict(field) for field in item["fields"]]} for item in CUSTOM_OBJECT_CATALOG]
    if workspace is None:
        return catalog
    definitions = CustomFieldDefinition.objects.filter(workspace=workspace, is_active=True)
    by_object = {item["object"]: item for item in catalog}
    for definition in definitions:
        item = by_object.setdefault(
            definition.object_type,
            {"object": definition.object_type, "label": definition.get_object_type_display(), "fields": []},
        )
        item["fields"].append(
            {
                "key": definition.key,
                "label": definition.label,
                "type": definition.field_type,
                "required": definition.required,
                "options": definition.options,
                "description": definition.description,
            }
        )
    return catalog


def validate_custom_attributes(workspace, object_type: str, values: dict[str, Any]) -> dict[str, Any]:
    """Validate a custom-attribute payload against the tenant field catalog."""
    if not isinstance(values, dict):
        raise ValidationError("Custom attributes must be a JSON object.")
    definitions = {
        definition.key: definition
        for definition in CustomFieldDefinition.objects.filter(
            workspace=workspace, object_type=object_type, is_active=True
        )
    }
    unknown = set(values) - set(definitions)
    if unknown:
        raise ValidationError({key: "Unknown custom field." for key in sorted(unknown)})
    cleaned: dict[str, Any] = {}
    for key, definition in definitions.items():
        value = values.get(key)
        if value in (None, "", []):
            if definition.required:
                raise ValidationError({key: "This custom field is required."})
            continue
        if definition.field_type == "boolean" and not isinstance(value, bool):
            raise ValidationError({key: "Expected a boolean value."})
        if definition.field_type == "number":
            try:
                value = str(Decimal(str(value)))
            except Exception as exc:  # noqa: BLE001 - normalize invalid JSON values
                raise ValidationError({key: "Expected a numeric value."}) from exc
        if definition.field_type == "date":
            try:
                date.fromisoformat(str(value))
            except ValueError as exc:
                raise ValidationError({key: "Expected an ISO date (YYYY-MM-DD)."}) from exc
        if definition.field_type in {"select", "multi_select"}:
            selected = value if definition.field_type == "multi_select" else [value]
            if not isinstance(selected, list) or any(item not in definition.options for item in selected):
                raise ValidationError({key: "Value is not one of the configured options."})
            value = selected if definition.field_type == "multi_select" else selected[0]
        cleaned[key] = value
    return cleaned
