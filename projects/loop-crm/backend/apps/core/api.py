"""Compatibility JSON endpoints for the Loop-CRM shell.

The canonical API is ``apps.core.bolt_api`` when django-bolt is installed.
These views keep the same resource contract available to older Django clients.
"""
from __future__ import annotations

import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.http import JsonResponse
from django_fusion.plugins.apis.auth import (
    FusionTokenError,
    TokenUserError,
    refresh_payload,
    user_token_payload,
    verify_request_user,
)

from apps.crm.custom_fields import custom_object_catalog
from apps.marketing.connectors import platform_catalog

from .bolt_api import RESOURCE_MODELS
from .realtime import safe_publish_workspace_event
from .resources import (
    bounded_int,
    count_rows,
    create_row,
    delete_row,
    get_row,
    list_rows,
    resolve_resource,
    update_row,
)
from .tenancy import current_workspace_id
from .workflows import persisted_workflow_catalog


def _json_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _body_json(request):
    try:
        return json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return None


def _saved_view_config(request, resource: str) -> dict | None:
    """Resolve ``?view=<pk>`` to the caller's saved view config (or None).

    The view must belong to this user, workspace, and resource; anything else
    is ignored so a foreign view id can never leak another member's filters.
    """
    view_pk = request.GET.get("view")
    if not view_pk:
        return None
    try:
        view_pk = int(view_pk)
    except (TypeError, ValueError):
        return None
    from .models import SavedView

    queryset = SavedView.objects.filter(pk=view_pk, user=request.user, resource=resource)
    workspace_id = current_workspace_id(request)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    view = queryset.first()
    return view.config if view is not None else None


@login_required
def resource_api(request, resource: str, pk: int | None = None):
    """Full tenant-scoped CRUD for a registered resource.

    GET (list) / POST (create) on the collection, and GET / PATCH / DELETE on
    the ``/<pk>/`` detail route. Every write is scoped to the caller's
    workspace and validated against the resource's write allowlist.
    """
    if resolve_resource(resource) is None:
        return JsonResponse({"detail": "Unknown resource."}, status=404)
    workspace_id = current_workspace_id(request)
    method = request.method

    if pk is None:
        if method == "GET":
            limit = bounded_int(request.GET.get("limit"), 100, 1, 200)
            offset = bounded_int(request.GET.get("offset"), 0, 0, 10**9)
            search = request.GET.get("search", "")
            view_config = _saved_view_config(request, resource)
            rows = list_rows(
                resource, workspace_id, limit=limit, offset=offset, search=search, view_config=view_config
            )
            total = count_rows(resource, workspace_id, search=search, view_config=view_config)
            return JsonResponse(
                {
                    "results": rows,
                    "count": total,
                    "next": offset + limit if offset + limit < total else None,
                    "previous": offset - limit if offset > 0 else None,
                }
            )
        if method == "POST":
            payload = _body_json(request)
            if payload is None:
                return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
            row, errors, status = create_row(resource, payload, workspace_id)
            if errors:
                return JsonResponse(errors, status=status)
            safe_publish_workspace_event(
                workspace_id, "resource.created", {"resource": resource, "row": row}
            )
            return JsonResponse(row, status=201)
        return JsonResponse({"detail": f"This endpoint does not accept {method}."}, status=405)

    if method == "GET":
        row = get_row(resource, pk, workspace_id)
        if row is None:
            return JsonResponse({"detail": "Not found."}, status=404)
        return JsonResponse(row)
    if method == "PATCH":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
        row, errors, status = update_row(resource, pk, payload, workspace_id)
        if status == 404:
            return JsonResponse({"detail": "Not found."}, status=404)
        if errors:
            return JsonResponse(errors, status=status)
        safe_publish_workspace_event(
            workspace_id, "resource.updated", {"resource": resource, "pk": pk, "row": row}
        )
        return JsonResponse(row)
    if method == "DELETE":
        if not delete_row(resource, pk, workspace_id):
            return JsonResponse({"detail": "Not found."}, status=404)
        safe_publish_workspace_event(
            workspace_id, "resource.deleted", {"resource": resource, "pk": pk}
        )
        return JsonResponse({"ok": True}, status=204)
    return JsonResponse({"detail": f"This endpoint does not accept {method}."}, status=405)


def _dashboard_workspace_id(request):
    try:
        return request.user.profile.workspace_id
    except Exception:  # noqa: BLE001 - anonymous or profile-less requests stay unscoped
        return None


@login_required
def dashboard_api(request):
    if request.method != "GET":
        return JsonResponse({"detail": "This read endpoint accepts GET only."}, status=405)
    workspace_id = _dashboard_workspace_id(request)
    counts = {}
    for key, (model, _fields) in RESOURCE_MODELS.items():
        try:
            queryset = model.objects.filter(workspace_id=workspace_id) if workspace_id is not None else model.objects
            counts[key] = queryset.count()
        except (OperationalError, ProgrammingError):
            counts[key] = 0
    return JsonResponse({"data": {"counts": counts, "workflow_count": len(persisted_workflow_catalog(workspace_id=workspace_id))}})


def token_api(request):
    """Issue a compatibility JWT when the optional Bolt road is unavailable."""
    if request.method != "POST":
        return JsonResponse({"detail": "This token endpoint accepts POST only."}, status=405)
    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)

    if not getattr(request.user, "is_authenticated", False):
        return JsonResponse({"detail": "Sign in is required to issue a user token."}, status=401)
    requested_subject = str(payload.get("subject") or "").strip()
    if requested_subject and requested_subject != str(request.user.pk):
        return JsonResponse({"detail": "A token can only be issued for the current user."}, status=403)
    try:
        ttl = min(max(int(payload.get("ttl") or 3600), 60), 86_400)
        result = user_token_payload(request.user, ttl_seconds=ttl)
    except (FusionTokenError, TokenUserError, ValueError, TypeError) as exc:
        return JsonResponse({"detail": str(exc)}, status=503)
    return JsonResponse(result)


def current_user_api(request):
    """Verify a bearer token against the live Django user and role profile."""
    try:
        user = verify_request_user(request)
    except (FusionTokenError, TokenUserError) as exc:
        return JsonResponse({"detail": str(exc)}, status=401)
    profile = getattr(user, "profile", None)
    return JsonResponse(
        {
            "user": {
                "id": user.pk,
                "email": user.email,
                "name": user.get_full_name() or user.username,
                "role": getattr(profile, "role", "viewer"),
                "workspace_id": getattr(profile, "workspace_id", None),
                "is_staff": user.is_staff,
            }
        }
    )


def refresh_token_api(request):
    """Rotate a refresh token on the compatibility API road."""
    if request.method != "POST":
        return JsonResponse({"detail": "This refresh endpoint accepts POST only."}, status=405)
    try:
        payload = json.loads(request.body or "{}")
        result = refresh_payload(str(payload.get("refresh_token") or ""))
    except (TypeError, ValueError, FusionTokenError) as exc:
        return JsonResponse({"detail": str(exc)}, status=401)
    return JsonResponse(result)


@login_required
def workspace_current_api(request):
    """Expose the caller's workspace id so client islands can open the
    workspace-scoped WebSocket without hardcoding a tenant id.
    """
    return JsonResponse({"workspace_id": current_workspace_id(request)})


@login_required
def workflows_api(request):
    results = persisted_workflow_catalog(workspace_id=current_workspace_id(request))
    return JsonResponse({"results": results, "count": len(results)})


def integrations_api(request):
    return JsonResponse({"results": platform_catalog(), "count": len(platform_catalog())})


@login_required
def custom_fields_api(request):
    profile = getattr(request.user, "profile", None)
    workspace = getattr(profile, "workspace", None) if profile else None
    catalog = custom_object_catalog(workspace)
    return JsonResponse({"results": catalog, "count": len(catalog)})


def _custom_object_queryset(workspace_id, key: str | None = None):
    from apps.crm.models import CustomObjectDefinition

    queryset = CustomObjectDefinition.objects.filter(is_active=True)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    if key is not None:
        queryset = queryset.filter(key=key)
    return queryset


def _custom_definition_payload(definition) -> dict:
    return {
        "id": definition.pk,
        "key": definition.key,
        "name": definition.name,
        "icon": definition.icon,
        "fields": definition.fields,
        "record_count": definition.records.count(),
    }


@login_required
def custom_objects_api(request):
    """List/create workspace custom-object definitions."""
    from django.core.exceptions import ValidationError

    from apps.crm.custom_objects import validate_definition_fields
    from apps.crm.models import CustomObjectDefinition

    workspace_id = current_workspace_id(request)
    if request.method == "GET":
        definitions = _custom_object_queryset(workspace_id).order_by("name")
        results = [_custom_definition_payload(d) for d in definitions]
        return JsonResponse({"results": results, "count": len(results)})
    if request.method == "POST":
        if workspace_id is None:
            return JsonResponse({"detail": "A workspace is required."}, status=403)
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
        name = str(payload.get("name") or "").strip()
        key = str(payload.get("key") or "").strip().lower()
        if not name or not key:
            return JsonResponse({"detail": "name and key are required."}, status=400)
        try:
            fields = validate_definition_fields(payload.get("fields") or [])
        except ValidationError as exc:
            return JsonResponse({"fields": exc.messages}, status=400)
        try:
            definition = CustomObjectDefinition.objects.create(
                workspace_id=workspace_id,
                name=name,
                key=key,
                icon=str(payload.get("icon") or "dataset"),
                fields=fields,
                created_by=request.user,
            )
        except Exception as exc:  # noqa: BLE001 - normalize uniqueness/DB errors
            return JsonResponse({"__all__": str(exc)}, status=400)
        safe_publish_workspace_event(
            workspace_id, "resource.created", {"resource": "custom_objects", "pk": definition.pk}
        )
        return JsonResponse(_custom_definition_payload(definition), status=201)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


def _get_definition_or_404(workspace_id, key: str):
    from django.shortcuts import get_object_or_404

    queryset = _custom_object_queryset(workspace_id, key=key)
    return get_object_or_404(queryset, key=key)


@login_required
def custom_object_records_api(request, key: str):
    """List/create rows for one workspace custom-object definition."""
    from django.core.exceptions import ValidationError

    from apps.crm.custom_objects import validate_record_data
    from apps.crm.models import CustomObjectRecord

    workspace_id = current_workspace_id(request)
    definition = _get_definition_or_404(workspace_id, key)
    if request.method == "GET":
        records = definition.records.all()
        if workspace_id is not None:
            records = records.filter(workspace_id=workspace_id)
        rows = list(
            records.order_by("-updated_at").values("id", "data", "updated_at", "created_by__username")
        )
        for row in rows:
            if row["updated_at"]:
                row["updated_at"] = row["updated_at"].isoformat()
        return JsonResponse({"results": rows, "count": len(rows)})
    if request.method == "POST":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
        try:
            data = validate_record_data(definition, payload.get("data"))
        except ValidationError as exc:
            return JsonResponse(exc.message_dict if hasattr(exc, "message_dict") else {"data": exc.messages}, status=400)
        record = CustomObjectRecord.objects.create(
            workspace_id=workspace_id,
            definition=definition,
            data=data,
            created_by=request.user,
        )
        safe_publish_workspace_event(
            workspace_id, "resource.created", {"resource": "custom_object_records", "pk": record.pk}
        )
        return JsonResponse({"id": record.pk, "data": record.data}, status=201)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


@login_required
def custom_object_record_detail_api(request, key: str, pk: int):
    """GET/PATCH/DELETE one custom-object row, tenant-scoped."""
    from django.core.exceptions import ValidationError

    from apps.crm.custom_objects import validate_record_data
    from apps.crm.models import CustomObjectRecord

    workspace_id = current_workspace_id(request)
    definition = _get_definition_or_404(workspace_id, key)
    queryset = CustomObjectRecord.objects.filter(definition=definition)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    record = queryset.filter(pk=pk).first()
    if record is None:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "GET":
        return JsonResponse({"id": record.pk, "data": record.data})
    if request.method == "PATCH":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
        merged = {**(record.data or {}), **(payload.get("data") or {})}
        try:
            record.data = validate_record_data(definition, merged)
        except ValidationError as exc:
            return JsonResponse(exc.message_dict if hasattr(exc, "message_dict") else {"data": exc.messages}, status=400)
        record.save(update_fields=["data", "updated_at"])
        safe_publish_workspace_event(
            workspace_id, "resource.updated", {"resource": "custom_object_records", "pk": record.pk}
        )
        return JsonResponse({"id": record.pk, "data": record.data})
    if request.method == "DELETE":
        record.delete()
        safe_publish_workspace_event(
            workspace_id, "resource.deleted", {"resource": "custom_object_records", "pk": pk}
        )
        return JsonResponse({"ok": True}, status=204)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


def _saved_view_payload(view) -> dict:
    return {
        "id": view.pk,
        "resource": view.resource,
        "name": view.name,
        "view_type": view.view_type,
        "config": view.config,
        "is_default": view.is_default,
    }


@login_required
def saved_views_api(request):
    """List/create the caller's saved views (member- and workspace-scoped)."""
    from .models import SavedView

    workspace_id = current_workspace_id(request)
    if request.method == "GET":
        queryset = SavedView.objects.filter(user=request.user)
        if workspace_id is not None:
            queryset = queryset.filter(workspace_id=workspace_id)
        results = [_saved_view_payload(v) for v in queryset.order_by("resource", "name")]
        return JsonResponse({"results": results, "count": len(results)})
    if request.method == "POST":
        if workspace_id is None:
            return JsonResponse({"detail": "A workspace is required."}, status=403)
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
        name = str(payload.get("name") or "").strip()
        resource = str(payload.get("resource") or "").strip()
        if not name or not resource:
            return JsonResponse({"detail": "name and resource are required."}, status=400)
        if resolve_resource(resource) is None:
            return JsonResponse({"detail": "Unknown resource."}, status=404)
        config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
        view_type = payload.get("view_type") if payload.get("view_type") in {"list", "kanban"} else "list"
        view, created = SavedView.objects.update_or_create(
            workspace_id=workspace_id,
            user=request.user,
            resource=resource,
            name=name,
            defaults={
                "view_type": view_type,
                "config": config,
                "is_default": bool(payload.get("is_default")),
            },
        )
        safe_publish_workspace_event(
            workspace_id,
            "resource.created" if created else "resource.updated",
            {"resource": "saved_views", "pk": view.pk},
        )
        return JsonResponse(_saved_view_payload(view), status=201 if created else 200)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)


@login_required
def saved_view_detail_api(request, pk: int):
    """GET/PATCH/DELETE one of the caller's saved views."""
    from .models import SavedView

    workspace_id = current_workspace_id(request)
    queryset = SavedView.objects.filter(user=request.user)
    if workspace_id is not None:
        queryset = queryset.filter(workspace_id=workspace_id)
    view = queryset.filter(pk=pk).first()
    if view is None:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "GET":
        return JsonResponse(_saved_view_payload(view))
    if request.method == "PATCH":
        payload = _body_json(request)
        if payload is None:
            return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
        if "config" in payload and isinstance(payload["config"], dict):
            view.config = payload["config"]
        if "view_type" in payload and payload["view_type"] in {"list", "kanban"}:
            view.view_type = payload["view_type"]
        if "is_default" in payload:
            view.is_default = bool(payload["is_default"])
        if "name" in payload and str(payload["name"]).strip():
            view.name = str(payload["name"]).strip()
        view.save(update_fields=["config", "view_type", "is_default", "name", "updated_at"])
        safe_publish_workspace_event(
            workspace_id, "resource.updated", {"resource": "saved_views", "pk": view.pk}
        )
        return JsonResponse(_saved_view_payload(view))
    if request.method == "DELETE":
        view.delete()
        safe_publish_workspace_event(
            workspace_id, "resource.deleted", {"resource": "saved_views", "pk": pk}
        )
        return JsonResponse({"ok": True}, status=204)
    return JsonResponse({"detail": f"This endpoint does not accept {request.method}."}, status=405)
