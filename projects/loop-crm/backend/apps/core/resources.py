"""Single source of truth for the Loop-CRM API resource surface.

Both the canonical django-bolt road (``apps.core.bolt_api``) and the
compatibility road (``apps.core.api``) consume this registry so the field
allowlists, FK validation, tenant scoping, and serialization stay identical
across the two roads. The render-first screens keep their own queryset helpers;
this module only owns the JSON API contract.

Design
------
* ``RESOURCES`` maps a URL resource slug to a :class:`Resource` describing the
  model, the read field projection, the writable field allowlist, and the
  fields required on create.
* Write helpers resolve forward relations inside the caller's workspace (or,
  for the ``auth.User`` owner, by existence) and refuse to create a record
  without a workspace, so a cloud member can never write another tenant's data.
* Serialization mirrors the existing ``_json_value`` convention (Decimal →
  string, date/datetime → ISO-8601).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import OperationalError, ProgrammingError, models

from apps.attribution.models import AttributionTouchpoint
from apps.crm.models import Company, Contact, Deal, Pipeline
from apps.finance.models import Invoice, Payment, RevenueEvent
from apps.marketing.models import Campaign, Post, SocialChannel


@dataclass(frozen=True)
class Resource:
    """The contract for one API resource."""

    model: type[models.Model]
    read_fields: tuple[str, ...]
    write_fields: tuple[str, ...]
    required_fields: tuple[str, ...] = ()


# Read fields preserve the historical projections already exposed on both
# roads; write fields are the allowlist a JSON client may submit.
RESOURCES: dict[str, Resource] = {
    "companies": Resource(
        model=Company,
        read_fields=("id", "name", "industry", "website", "email", "city", "country", "owner_id"),
        write_fields=(
            "name",
            "industry",
            "website",
            "description",
            "phone",
            "email",
            "city",
            "country",
            "annual_revenue",
            "employee_count",
            "custom_attributes",
            "owner_id",
        ),
        required_fields=("name",),
    ),
    "contacts": Resource(
        model=Contact,
        read_fields=("id", "first_name", "last_name", "email", "title", "company_id"),
        write_fields=(
            "company_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "title",
            "linkedin_url",
            "custom_attributes",
            "owner_id",
        ),
        required_fields=("first_name", "last_name", "email", "company_id"),
    ),
    "deals": Resource(
        model=Deal,
        read_fields=("id", "name", "value", "expected_close_date", "stage__name", "company_id", "pipeline_id"),
        write_fields=(
            "company_id",
            "contact_id",
            "name",
            "value",
            "pipeline_id",
            "stage_id",
            "expected_close_date",
            "campaign_id",
            "owner_id",
            "custom_attributes",
        ),
        required_fields=("company_id", "name", "value", "expected_close_date"),
    ),
    "pipelines": Resource(
        model=Pipeline,
        read_fields=("id", "name", "description", "is_default", "order"),
        write_fields=("name", "description", "is_default", "order"),
        required_fields=("name",),
    ),
    "campaigns": Resource(
        model=Campaign,
        read_fields=("id", "name", "description", "budget", "start_date", "end_date"),
        write_fields=("name", "description", "start_date", "end_date", "budget", "owner_id"),
        required_fields=("name",),
    ),
    "channels": Resource(
        model=SocialChannel,
        read_fields=("id", "platform", "account_name", "is_active"),
        # OAuth tokens are never accepted through the resource road; they are
        # set only by the provider OAuth callback flow.
        write_fields=("platform", "account_name", "is_active"),
        required_fields=("platform", "account_name"),
    ),
    "posts": Resource(
        model=Post,
        read_fields=("id", "content", "scheduled_at", "status", "channel_id", "campaign_id"),
        write_fields=("campaign_id", "channel_id", "content", "scheduled_at"),
        required_fields=("channel_id", "content", "scheduled_at"),
    ),
    "touchpoints": Resource(
        model=AttributionTouchpoint,
        read_fields=("id", "source", "occurred_at", "weight", "deal_id", "post_id", "campaign_id"),
        write_fields=("deal_id", "post_id", "campaign_id", "source", "occurred_at", "weight"),
        required_fields=("deal_id", "occurred_at"),
    ),
    "invoices": Resource(
        model=Invoice,
        read_fields=("id", "number", "company__name", "status", "currency", "total", "due_on"),
        write_fields=(
            "number",
            "company_id",
            "contact_id",
            "deal_id",
            "currency",
            "status",
            "issued_on",
            "due_on",
            "subtotal",
            "tax",
            "notes",
        ),
        required_fields=("number", "company_id", "due_on"),
    ),
    "payments": Resource(
        model=Payment,
        read_fields=("id", "invoice__number", "amount", "paid_on", "method"),
        write_fields=("invoice_id", "amount", "paid_on", "method", "reference"),
        required_fields=("invoice_id", "amount"),
    ),
    "revenue": Resource(
        model=RevenueEvent,
        read_fields=("id", "deal__name", "campaign__name", "kind", "amount", "recognized_on"),
        write_fields=("deal_id", "campaign_id", "invoice_id", "kind", "amount", "recognized_on", "metadata"),
        required_fields=("deal_id", "amount"),
    ),
}

#: Historical alias kept for callers that import ``RESOURCE_MODELS``.
RESOURCE_MODELS: dict[str, tuple[type[models.Model], tuple[str, ...]]] = {
    slug: (resource.model, resource.read_fields) for slug, resource in RESOURCES.items()
}


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def serialize(instance: models.Model, read_fields: tuple[str, ...]) -> dict[str, Any]:
    """Project an ORM instance to a JSON-safe dict using *read_fields* lookups."""
    values = instance.__class__.objects.filter(pk=instance.pk).values(*read_fields).first()
    if values is None:
        return {}
    return {key: _json_value(value) for key, value in values.items()}


def _model_has_workspace(model: type[models.Model]) -> bool:
    return any(field.name == "workspace" for field in model._meta.concrete_fields)


def _resolve_relation(resource: Resource, field_name: str, value: Any, workspace_id: int | None, instance: models.Model | None):
    """Resolve a forward relation for a write, scoped to the caller's workspace.

    Returns ``(related_instance, error)``. Workspace-scoped models are filtered
    to the caller's workspace; ``auth.User`` owners are only checked for
    existence. The special ``stage_id`` on a deal is validated against the
    instance's own pipeline.
    """
    field = resource.model._meta.get_field(field_name)
    related_model = field.remote_field.model
    queryset = related_model.objects.filter(pk=value)

    if field_name == "stage_id":
        # A stage is reachable only through the caller's own pipelines; when
        # the instance already knows its pipeline, require the same pipeline.
        if workspace_id is not None:
            queryset = queryset.filter(pipeline__workspace_id=workspace_id)
        if instance is not None and instance.pipeline_id:
            queryset = queryset.filter(pipeline_id=instance.pipeline_id)
    elif _model_has_workspace(related_model) and workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)

    try:
        return queryset.get(), None
    except related_model.DoesNotExist:
        return None, f"{field_name} does not exist or is outside your workspace."


def _apply_payload(resource: Resource, instance: models.Model, data: dict[str, Any], workspace_id: int | None):
    """Apply a validated payload to *instance*, returning ``(instance, errors)``.

    Unknown fields are ignored; only the resource's write allowlist is honored.
    """
    errors: dict[str, str] = {}
    for field_name in resource.write_fields:
        if field_name not in data:
            continue
        value = data[field_name]
        model_field = resource.model._meta.get_field(field_name)
        if getattr(model_field, "is_relation", False):
            related, error = _resolve_relation(resource, field_name, value, workspace_id, instance)
            if error:
                errors[field_name] = error
                continue
            setattr(instance, field_name, related)
        else:
            # Coerce + validate the JSON scalar through the model field's own
            # clean path (types, choices, validators) without the forms-layer
            # blank/null checks that a JSON API must not enforce.
            try:
                cleaned = model_field.clean(value, instance)
            except Exception as exc:  # noqa: BLE001 - normalize bad JSON values
                errors[field_name] = str(exc)
                continue
            setattr(instance, field_name, cleaned)
    return instance, errors


def list_rows(slug: str, workspace_id: int | None) -> list[dict[str, Any]]:
    resource = RESOURCES[slug]
    queryset = resource.model.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    try:
        rows = list(queryset.values(*resource.read_fields)[:100])
    except (OperationalError, ProgrammingError):
        rows = []
    return [{key: _json_value(value) for key, value in row.items()} for row in rows]


def get_row(slug: str, pk: int, workspace_id: int | None) -> dict[str, Any] | None:
    resource = RESOURCES[slug]
    queryset = resource.model.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    instance = queryset.filter(pk=pk).first()
    if instance is None:
        return None
    return serialize(instance, resource.read_fields)


def create_row(slug: str, data: dict[str, Any], workspace_id: int | None) -> tuple[dict | None, dict[str, str], int]:
    """Create a resource row. Returns ``(serialized, errors, status)``."""
    resource = RESOURCES[slug]
    if workspace_id is None and _model_has_workspace(resource.model):
        return None, {"workspace": "A workspace is required to create this resource."}, 400
    missing = [name for name in resource.required_fields if not data.get(name)]
    if missing:
        return None, {name: "This field is required." for name in missing}, 400

    instance = resource.model()
    if workspace_id is not None:
        instance.workspace_id = workspace_id
    instance, errors = _apply_payload(resource, instance, data, workspace_id)
    if errors:
        return None, errors, 400
    try:
        instance.save()
    except Exception as exc:  # noqa: BLE001 - normalize DB constraint failures
        return None, {"__all__": str(exc)}, 400
    return serialize(instance, resource.read_fields), {}, 201


def update_row(slug: str, pk: int, data: dict[str, Any], workspace_id: int | None) -> tuple[dict | None, dict[str, str], int]:
    """Partially update a resource row scoped to the caller's workspace."""
    resource = RESOURCES[slug]
    queryset = resource.model.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    instance = queryset.filter(pk=pk).first()
    if instance is None:
        return None, {}, 404
    instance, errors = _apply_payload(resource, instance, data, workspace_id)
    if errors:
        return None, errors, 400
    try:
        instance.save()
    except Exception as exc:  # noqa: BLE001 - normalize DB constraint failures
        return None, {"__all__": str(exc)}, 400
    return serialize(instance, resource.read_fields), {}, 200


def delete_row(slug: str, pk: int, workspace_id: int | None) -> bool:
    """Delete a resource row scoped to the caller's workspace. Returns success."""
    resource = RESOURCES[slug]
    queryset = resource.model.objects.all()
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    deleted, _ = queryset.filter(pk=pk).delete()
    return deleted > 0


def resolve_resource(slug: str) -> Resource | None:
    return RESOURCES.get(slug)
