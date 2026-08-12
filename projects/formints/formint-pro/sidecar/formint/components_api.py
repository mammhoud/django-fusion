"""
Formint — Components API (django-fusion data components over HTTP).

The desktop app consumes django-fusion "components as data" from the sidecar
backend:

    GET /api/v1/components/                    — catalog of available components
    GET /api/v1/components/tables/<resource>/  — table data rows + headers
    GET /api/v1/components/forms/<resource>/   — form field schema (fields/layout)
    GET /api/v1/components/fragments/<name>/   — named fragment data (e.g. branch-summary)

These mirror the HTMX fragment handlers (``/htmx/tables|forms/<resource>/``)
but return the JSON envelope the Astro shell renders directly.  When the
sidecar API is unreachable, the frontend transport falls back to Tauri
invokes (see ``frontend/src/lib/fusion-api.ts``).
"""

from typing import Any

from ninja import Schema
from ninja_extra import api_controller, http_get

from formint.components import (
    FORM_COMPONENTS,
    TABLE_COMPONENTS,
    render_table_rows,
)
from formint.fusion_components import BranchSummaryFragment

__all__ = ["ComponentsController"]


class TableOut(Schema):
    resource: str
    headers: list[dict[str, Any]]
    rows: list[dict[str, Any]]
    count: int


class FormOut(Schema):
    resource: str
    fields: list[dict[str, Any]]
    layout: list[list[str]]


class FragmentOut(Schema):
    name: str
    data: dict[str, Any]


@api_controller("/components", tags=["components"], auto_import=False)
class ComponentsController:
    """django-fusion data components served as JSON (sidecar backend)."""

    # NOTE: handlers are synchronous on purpose — they only read the DB and
    # build component payloads. ninja-extra runs sync handlers in a threadpool,
    # so no sync_to_async wrapping is needed.

    @http_get("/", response={200: dict, 400: dict})
    def catalog(self):
        return 200, {
            "tables": sorted(TABLE_COMPONENTS),
            "forms": sorted(FORM_COMPONENTS),
            "fragments": ["branch-summary"],
        }

    @http_get("/tables/{resource}/", response={200: TableOut, 404: dict, 400: dict})
    def table(self, resource: str):
        component_cls = TABLE_COMPONENTS.get(resource)
        if component_cls is None:
            return 404, {"detail": f"Unknown table resource: {resource}"}

        component = component_cls()
        headers = component.get_table_headers()
        rows = render_table_rows(component, limit=100)
        return 200, TableOut(
            resource=resource,
            headers=headers,
            rows=rows,
            count=len(rows),
        )

    @http_get("/forms/{resource}/", response={200: FormOut, 404: dict, 400: dict})
    def form(self, resource: str):
        component_cls = FORM_COMPONENTS.get(resource)
        if component_cls is None:
            return 404, {"detail": f"Unknown form resource: {resource}"}

        component = component_cls()
        form = component.get_form()
        fields = []
        for name, field in form.fields.items():
            fields.append(
                {
                    "name": name,
                    "label": str(field.label) if field.label else name.replace("_", " ").title(),
                    "required": field.required,
                    "help_text": str(field.help_text) if field.help_text else "",
                    "input_type": _field_input_type(field),
                    "choices": _field_choices(field),
                }
            )
        return 200, FormOut(
            resource=resource,
            fields=fields,
            layout=getattr(component, "form_layout", [[f["name"] for f in fields]]),
        )

    @http_get("/fragments/{name}/", response={200: FragmentOut, 404: dict, 400: dict})
    def fragment(self, name: str):
        if name == "branch-summary":
            return 200, FragmentOut(
                name=name,
                data=BranchSummaryFragment().get_branch_summary(),
            )
        return 404, {"detail": f"Unknown fragment: {name}"}


def _field_input_type(field) -> str:
    """Map a Django form field to a browser input type for the form renderer."""
    from django.forms import (
        BooleanField, ChoiceField, DateField, DateTimeField, DecimalField,
        EmailField, FileField, IntegerField, MultipleChoiceField,
        ModelChoiceField, ModelMultipleChoiceField, Textarea, URLField,
    )

    if isinstance(field.widget, Textarea):
        return "textarea"
    if isinstance(field, (BooleanField,)):
        return "checkbox"
    if isinstance(field, (ModelChoiceField, ChoiceField, MultipleChoiceField, ModelMultipleChoiceField)):
        return "select"
    if isinstance(field, EmailField):
        return "email"
    if isinstance(field, URLField):
        return "url"
    if isinstance(field, (IntegerField, DecimalField)):
        return "number"
    if isinstance(field, DateTimeField):
        return "datetime-local"
    if isinstance(field, DateField):
        return "date"
    if isinstance(field, FileField):
        return "file"
    return "text"


def _field_choices(field) -> list[dict[str, str]]:
    """Extract select choices as [{value, label}] for the form renderer."""
    choices = getattr(field, "choices", None)
    if not choices:
        return []
    return [{"value": str(value), "label": str(label)} for value, label in choices]
