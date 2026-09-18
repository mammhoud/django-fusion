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
from apps.finance.services import revenue_trend_results, trend_aggregates
from apps.marketing.connectors import platform_catalog

from .realtime import safe_apublish_workspace_event
from .resource_tables import resource_table
from .resources import (
    RESOURCES,
    bounded_int,
    count_rows,
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


def _request_query(request: Any) -> dict[str, Any]:
    """Read Bolt query params tolerantly across versions (dict/QueryDict)."""
    query = getattr(request, "query_params", None)
    if query is None:
        query = getattr(request, "GET", {})
    try:
        items = dict(query)
    except Exception:  # noqa: BLE001 - a missing query object means defaults
        return {}
    return {
        key: (value[0] if isinstance(value, (list, tuple)) else value)
        for key, value in items.items()
    }


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
        from django_bolt.openapi.spec import Tag

        bolt.openapi_config.description = (
            "Canonical tenant-scoped JSON API for Loop-CRM. Every resource "
            "road is workspace-scoped to the authenticated user and accepts "
            "``limit``/``offset``/``search`` on collection GETs; ``count`` is "
            "the filtered total and ``next``/``previous`` are offsets."
        )
        bolt.openapi_config.tags = [
            Tag(
                name=resource.label or slug.replace("_", " ").title(),
                description=resource.description or None,
            )
            for slug, resource in RESOURCES.items()
        ]


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

        @bolt.get("/health", tags=["System"], summary="Health check", **_public)
        async def health(request: Any) -> dict[str, str]:
            """Public liveness endpoint for the Bolt API."""
            return {"status": "ok", "service": "loop-crm-bolt"}

    token_config = getattr(bolt, "fusion_token_config", None)
    # Token issuance is bound to the authenticated Django user; arbitrary
    # subject/device tokens are intentionally not available on Loop-CRM.
    mount_token_endpoint(bolt, config=token_config, user_required=True)
    mount_refresh_endpoint(bolt, config=token_config)

    @bolt.get(
        "/tables/{resource}",
        tags=["System"],
        summary="Resource table",
        description=(
            "Schema-aware fusion table projection for one resource: headers "
            "carry type metadata (text/money/date/pill/link) and rows are "
            "formatted cell lists aligned to the headers. Workspace-scoped."
        ),
        **_protected,
    )
    async def resource_table_view(request: Any, resource: str) -> dict[str, Any] | Any:
        if resource not in RESOURCES:
            return {"detail": "Unknown resource."}
        queryset = RESOURCES[resource].model.objects.all()
        workspace_id = _workspace_id(await _request_user(request))
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        return await sync_to_async(resource_table)(queryset, resource)

    @bolt.get(
        "/dashboard",
        tags=["System"],
        summary="Workspace dashboard",
        description="Row counts for every resource plus the persisted workflow total.",
        **_protected,
    )
    async def dashboard(request: Any) -> dict[str, Any]:
        return await _dashboard(workspace_id=_workspace_id(await _request_user(request)))

    @bolt.get(
        "/workflows",
        tags=["Automation"],
        summary="List workflows",
        description="Persisted no-code workflow catalog for the caller's workspace.",
        **_protected,
    )
    async def workflows(request: Any) -> dict[str, Any]:
        results = persisted_workflow_catalog(
            workspace_id=_workspace_id(await _request_user(request))
        )
        return {"results": results, "count": len(results)}

    @bolt.get(
        "/integrations",
        tags=["Automation"],
        summary="List social platform connectors",
        description="Catalog of publish adapters and their OAuth/connect capabilities.",
        **_protected,
    )
    async def integrations(request: Any) -> dict[str, Any]:
        results = platform_catalog()
        return {"results": results, "count": len(results)}

    @bolt.get(
        "/custom-fields",
        tags=["Automation"],
        summary="List custom object definitions",
        description="Workspace-scoped runtime schema catalog for custom objects.",
        **_protected,
    )
    async def custom_fields(request: Any) -> dict[str, Any]:
        results = custom_object_catalog(_workspace(await _request_user(request)))
        return {"results": results, "count": len(results)}

    @bolt.get(
        "/revenue/trend",
        tags=["Revenue"],
        summary="Revenue trend",
        description="Trailing-six-month recognized-revenue trend for the RevOps dashboard.",
        **_protected,
    )
    async def revenue_trend(request: Any) -> dict[str, Any]:
        workspace_id = _workspace_id(await _request_user(request))
        queryset = RevenueEvent.objects.all()
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        rows: list[dict[str, Any]] = []
        try:
            queryset = (
                queryset.annotate(month=TruncMonth("recognized_on"))
                .values("month")
                .annotate(**trend_aggregates())
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
        tag = config.label or resource.replace("_", " ").title()
        singular = config.singular or tag.rstrip("s").lower()
        description = config.description or f"{tag} resource."

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

        @bolt.get(
            f"/{resource}",
            tags=[tag],
            summary=f"List {tag.lower()}",
            description=(
                f"{description} Supports ``limit``/``offset``/``search``; "
                "``count`` is the filtered total and ``next``/``previous`` are offsets."
            ),
            **list_options,
        )
        async def list_resource(request: Any) -> dict[str, Any]:
            query = _request_query(request)
            limit = bounded_int(query.get("limit"), 100, 1, 200)
            offset = bounded_int(query.get("offset"), 0, 0, 10**9)
            search = str(query.get("search") or "")
            workspace_id = _workspace_id(await _request_user(request))
            results = await sync_to_async(list_rows)(
                resource, workspace_id, limit=limit, offset=offset, search=search
            )
            total = await sync_to_async(count_rows)(resource, workspace_id, search=search)
            return {
                "results": results,
                "count": total,
                "next": offset + limit if offset + limit < total else None,
                "previous": offset - limit if offset > 0 else None,
            }

        @bolt.post(
            f"/{resource}",
            tags=[tag],
            summary=f"Create {singular}",
            description=f"{description} Required fields: {', '.join(config.required_fields) or 'none'}.",
            **detail_options,
        )
        async def create_resource(request: Any) -> Any:
            body = await _request_body(request)
            workspace_id = _workspace_id(await _request_user(request))
            row, errors, _status = await sync_to_async(create_row)(resource, body, workspace_id)
            if errors:
                return {"detail": "Validation failed.", "errors": errors}
            await safe_apublish_workspace_event(
                workspace_id, "resource.created", {"resource": resource, "row": row}
            )
            return row

        @bolt.get(
            f"/{resource}/{{pk}}",
            tags=[tag],
            summary=f"Retrieve {singular}",
            description=f"{description} Scoped to the caller's workspace.",
            **detail_options,
        )
        async def retrieve_resource(request: Any, pk: Any) -> Any:
            row = await sync_to_async(get_row)(
                resource, pk, _workspace_id(await _request_user(request))
            )
            if row is None:
                return {"detail": "Not found."}
            return row

        @bolt.patch(
            f"/{resource}/{{pk}}",
            tags=[tag],
            summary=f"Update {singular}",
            description=f"{description} Partial update scoped to the caller's workspace.",
            **detail_options,
        )
        async def update_resource(request: Any, pk: Any) -> Any:
            body = await _request_body(request)
            workspace_id = _workspace_id(await _request_user(request))
            row, errors, status = await sync_to_async(update_row)(resource, pk, body, workspace_id)
            if status == 404:
                return {"detail": "Not found."}
            if errors:
                return {"detail": "Validation failed.", "errors": errors}
            await safe_apublish_workspace_event(
                workspace_id, "resource.updated", {"resource": resource, "pk": pk, "row": row}
            )
            return row

        @bolt.delete(
            f"/{resource}/{{pk}}",
            tags=[tag],
            summary=f"Delete {singular}",
            description=f"{description} Scoped to the caller's workspace.",
            status_code=204,
            auth=auth_backends,
            guards=_protected["guards"],
        )
        async def delete_resource(request: Any, pk: Any) -> Any:
            workspace_id = _workspace_id(await _request_user(request))
            ok = await sync_to_async(delete_row)(resource, pk, workspace_id)
            if not ok:
                return {"detail": "Not found."}
            await safe_apublish_workspace_event(
                workspace_id, "resource.deleted", {"resource": resource, "pk": pk}
            )
            return None

    for _resource in RESOURCES:
        _register_collection(_resource)


__all__ = ["RESOURCE_MODELS", "bolt"]
