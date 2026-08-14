"""Canonical django-bolt API for Loop-CRM.

The Bolt API is the primary API road when the optional django-bolt runtime is
installed. The existing ``apps.core.api`` Django views remain mounted under
``/api/v1/`` as a compatibility fallback for local installations that do not
install the Rust-backed runtime.

Both roads consume ``apps.core.resources`` so the resource contract, write
allowlist, FK validation, tenant scoping, and serialization are identical.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django_fusion.plugins.apis import (
    build_bolt_auth,
    generate_msgspec_schema,
)
from django_fusion.plugins.apis.bolt import (
    build_bolt_api,
    mount_refresh_endpoint,
    mount_token_endpoint,
)

from apps.crm.custom_fields import custom_object_catalog
from apps.finance.models import RevenueEvent
from apps.finance.services import revenue_trend_results
from apps.marketing.connectors import platform_catalog

from .resources import (
    RESOURCES,
    create_row,
    delete_row,
    get_row,
    list_rows,
    update_row,
)
from .workflows import persisted_workflow_catalog

#: Historical alias; both roads read the same resource registry.
RESOURCE_MODELS: dict[str, tuple[type[Any], tuple[str, ...]]] = {
    slug: (resource.model, resource.read_fields) for slug, resource in RESOURCES.items()
}


def _bolt_enabled() -> bool:
    return getattr(settings, "FUSION_BOLT_ENABLED", True)


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _workspace_id(user: Any) -> int | None:
    profile = getattr(user, "profile", None)
    return getattr(profile, "workspace_id", None)


def _workspace(user: Any):
    """Return the caller's Workspace instance (for FK-filtered catalogs)."""
    profile = getattr(user, "profile", None)
    return getattr(profile, "workspace", None)


async def _request_user(request: Any) -> Any:
    return getattr(request, "user", None) or getattr(request, "auth", None)


async def _request_body(request: Any) -> dict[str, Any]:
    """Read a Bolt JSON body into a plain dict across Bolt versions."""
    body = getattr(request, "json", {})
    if callable(body):
        body = body()
    import inspect

    if inspect.isawaitable(body):
        body = await body
    if hasattr(body, "items"):
        return dict(body.items())
    try:
        import msgspec

        return dict(msgspec.structs.asdict(body))
    except (ImportError, TypeError, AttributeError):
        return {}


async def _dashboard(workspace_id: int | None = None) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for key, resource in RESOURCES.items():
        try:
            queryset = resource.model.objects.all()
            if workspace_id is not None:
                queryset = queryset.filter(workspace_id=workspace_id)
            counts[key] = await queryset.acount()
        except (OperationalError, ProgrammingError):
            counts[key] = 0
    return {
        "counts": counts,
        "workflow_count": len(persisted_workflow_catalog(workspace_id=workspace_id)),
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
        return await _dashboard(workspace_id=_workspace_id(await _request_user(request)))

    @bolt.get("/workflows", **_protected)
    async def workflows(request: Any) -> dict[str, Any]:
        results = persisted_workflow_catalog(
            workspace_id=_workspace_id(await _request_user(request))
        )
        return {"results": results, "count": len(results)}

    @bolt.get("/integrations", **_protected)
    async def integrations(request: Any) -> dict[str, Any]:
        results = platform_catalog()
        return {"results": results, "count": len(results)}

    @bolt.get("/custom-fields", **_protected)
    async def custom_fields(request: Any) -> dict[str, Any]:
        results = custom_object_catalog(_workspace(await _request_user(request)))
        return {"results": results, "count": len(results)}

    @bolt.get("/revenue/trend", **_protected)
    async def revenue_trend(request: Any) -> dict[str, Any]:
        """Trailing-six-month recognized-revenue trend for the RevOps dashboard."""
        workspace_id = _workspace_id(await _request_user(request))
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

    def _register_collection(resource: str) -> None:
        """Register full tenant-scoped CRUD for one resource on the Bolt road."""
        config = RESOURCES[resource]
        model = config.model

        # Typed request/response bodies via msgspec; optional so the road still
        # works if the schema dependency is unavailable.
        try:
            struct = generate_msgspec_schema(
                model, name=f"{model.__name__}Schema", fields=list(config.read_fields)
            )
        except Exception:  # pragma: no cover - msgspec optional
            struct = None

        list_options = dict(_protected)
        detail_options = dict(_protected)
        if struct is not None:
            list_options["response_model"] = list[struct]
            detail_options["response_model"] = struct

        @bolt.get(f"/{resource}", **list_options)
        async def list_resource(request: Any) -> dict[str, Any]:
            results = list_rows(resource, _workspace_id(await _request_user(request)))
            return {"results": results, "count": len(results), "next": None, "previous": None}

        @bolt.post(f"/{resource}", **detail_options)
        async def create_resource(request: Any) -> Any:
            body = await _request_body(request)
            row, errors, _status = await sync_to_async(create_row)(
                resource, body, _workspace_id(await _request_user(request))
            )
            if errors:
                return {"detail": "Validation failed.", "errors": errors}
            return row

        @bolt.get(f"/{resource}/{{pk}}", **detail_options)
        async def retrieve_resource(request: Any, pk: Any) -> Any:
            row = await sync_to_async(get_row)(
                resource, pk, _workspace_id(await _request_user(request))
            )
            if row is None:
                return {"detail": "Not found."}
            return row

        @bolt.patch(f"/{resource}/{{pk}}", **detail_options)
        async def update_resource(request: Any, pk: Any) -> Any:
            body = await _request_body(request)
            row, errors, status = await sync_to_async(update_row)(
                resource, pk, body, _workspace_id(await _request_user(request))
            )
            if status == 404:
                return {"detail": "Not found."}
            if errors:
                return {"detail": "Validation failed.", "errors": errors}
            return row

        @bolt.delete(f"/{resource}/{{pk}}", status_code=204, auth=auth_backends, guards=_protected["guards"])
        async def delete_resource(request: Any, pk: Any) -> Any:
            ok = await sync_to_async(delete_row)(
                resource, pk, _workspace_id(await _request_user(request))
            )
            if not ok:
                return {"detail": "Not found."}
            return None

    for _resource in RESOURCES:
        _register_collection(_resource)


__all__ = ["RESOURCE_MODELS", "bolt"]
