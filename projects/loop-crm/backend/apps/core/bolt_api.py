"""Canonical django-bolt API for Loop-CRM.

The Bolt API is the primary API road when the optional django-bolt runtime is
installed. The existing ``apps.core.api`` Django views remain mounted under
``/api/v1/`` as a compatibility fallback for local installations that do not
install the Rust-backed runtime.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django_fusion.plugins.apis import build_bolt_auth
from django_fusion.plugins.apis.bolt import (
    build_bolt_api,
    mount_refresh_endpoint,
    mount_token_endpoint,
)

from apps.attribution.models import AttributionTouchpoint
from apps.crm.custom_fields import custom_object_catalog
from apps.crm.models import Company, Contact, Deal, Pipeline
from apps.finance.models import Invoice, Payment, RevenueEvent
from apps.finance.services import revenue_trend_results
from apps.marketing.connectors import platform_catalog
from apps.marketing.models import Campaign, Post, SocialChannel

from .workflows import persisted_workflow_catalog

RESOURCE_MODELS: dict[str, tuple[type[Any], tuple[str, ...]]] = {
    "companies": (Company, ("id", "name", "industry", "website")),
    "contacts": (Contact, ("id", "first_name", "last_name", "email", "title")),
    "deals": (Deal, ("id", "name", "value", "expected_close_date", "stage__name")),
    "pipelines": (Pipeline, ("id", "name", "description", "is_default")),
    "campaigns": (Campaign, ("id", "name", "description", "budget")),
    "channels": (SocialChannel, ("id", "platform", "account_name", "is_active")),
    "posts": (Post, ("id", "content", "scheduled_at", "status")),
    "touchpoints": (
        AttributionTouchpoint,
        ("id", "source", "occurred_at", "weight"),
    ),
    "invoices": (Invoice, ("id", "number", "company__name", "status", "currency", "total", "due_on")),
    "payments": (Payment, ("id", "invoice__number", "amount", "paid_on", "method")),
    "revenue": (RevenueEvent, ("id", "deal__name", "campaign__name", "kind", "amount", "recognized_on")),
}


def _bolt_enabled() -> bool:
    return getattr(settings, "FUSION_BOLT_ENABLED", True)


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


async def _resource_rows(model: type[Any], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    try:
        rows = [
            row
            async for row in model.objects.values(*fields).order_by("-pk")[:100]
        ]
    except (OperationalError, ProgrammingError):
        rows = []
    return [
        {key: _json_value(value) for key, value in row.items()}
        for row in rows
    ]


def _workspace_id(user: Any) -> int | None:
    profile = getattr(user, "profile", None)
    return getattr(profile, "workspace_id", None)


async def _dashboard(workspace_id: int | None = None) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for key, (model, _fields) in RESOURCE_MODELS.items():
        try:
            queryset = model.objects.filter(workspace_id=workspace_id) if workspace_id is not None else model.objects
            counts[key] = await queryset.acount()
        except (OperationalError, ProgrammingError):
            counts[key] = 0
    return {
        "counts": counts,
        "workflow_count": len(persisted_workflow_catalog()),
    }


bolt = None

if _bolt_enabled():
    bolt = build_bolt_api(
        prefix="/bolt",
        title="Loop CRM API",
        version="1.0.0",
        openapi_path="/bolt/docs",
    )


if bolt is not None:
    # A Loop-CRM installation always has a Django SECRET_KEY, so the JWT
    # backend is available even when an API key has not been configured.
    auth_backends = build_bolt_auth()

    try:
        from django_bolt.auth import AllowAny, IsAuthenticated
    except (ImportError, ModuleNotFoundError):  # pragma: no cover - bad runtime
        AllowAny = IsAuthenticated = None

    _public = {
        "auth": [],
        "guards": [AllowAny()] if AllowAny is not None else [],
    }
    _protected = {
        "auth": auth_backends,
        "guards": [IsAuthenticated()] if IsAuthenticated is not None else [],
    }

    if AllowAny is not None:

        @bolt.get("/health", **_public)
        async def health(request: Any) -> dict[str, str]:
            """Public liveness endpoint for the Bolt API."""
            return {"status": "ok", "service": "loop-crm-bolt"}

    token_config = getattr(bolt, "fusion_token_config", None)
    # Token issuance is bound to the authenticated Django user; arbitrary
    # subject/device tokens are intentionally not available on Loop-CRM.
    mount_token_endpoint(bolt, config=token_config, user_required=True)
    mount_refresh_endpoint(bolt, config=token_config)

    @bolt.get("/dashboard", **_protected)
    async def dashboard(request: Any) -> dict[str, Any]:
        return await _dashboard(workspace_id=_workspace_id(getattr(request, "user", None)))

    @bolt.get("/workflows", **_protected)
    async def workflows(request: Any) -> dict[str, Any]:
        results = persisted_workflow_catalog()
        return {"results": results, "count": len(results)}

    @bolt.get("/integrations", **_protected)
    async def integrations(request: Any) -> dict[str, Any]:
        results = platform_catalog()
        return {"results": results, "count": len(results)}

    @bolt.get("/custom-fields", **_protected)
    async def custom_fields(request: Any) -> dict[str, Any]:
        results = custom_object_catalog()
        return {"results": results, "count": len(results)}

    @bolt.get("/revenue/trend", **_protected)
    async def revenue_trend(request: Any) -> dict[str, Any]:
        """Trailing-six-month recognized-revenue trend for the RevOps dashboard."""
        workspace_id = _workspace_id(getattr(request, "user", None))
        queryset = RevenueEvent.objects.all()
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        rows: list[dict[str, Any]] = []
        try:
            queryset = (
                queryset.annotate(month=TruncMonth("recognized_on"))
                .values("month")
                .annotate(total=Sum("amount"), events=Count("id"))
                .order_by("month")
            )
            async for row in queryset:
                rows.append(row)
        except (OperationalError, ProgrammingError):
            rows = []
        return revenue_trend_results(rows)

    def _register_collection(
        resource: str,
        model: type[Any],
        fields: tuple[str, ...],
    ) -> None:
        async def list_resource(request: Any) -> dict[str, Any]:
            results = await _resource_rows(model, fields)
            return {"results": results, "count": len(results), "next": None, "previous": None}

        list_resource.__name__ = f"list_{resource}"
        bolt.get(f"/{resource}", **_protected)(list_resource)

    for _resource, (_model, _fields) in RESOURCE_MODELS.items():
        _register_collection(_resource, _model, _fields)


__all__ = ["RESOURCE_MODELS", "bolt"]
