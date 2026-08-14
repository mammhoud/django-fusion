"""Compatibility JSON endpoints for the Loop-CRM shell.

The canonical API is ``apps.core.bolt_api`` when django-bolt is installed.
These views keep the same resource contract available to older Django clients.
"""
from __future__ import annotations

import json
from decimal import Decimal

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
from .workflows import persisted_workflow_catalog


def _json_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def resource_api(request, resource: str):
    if request.method != "GET":
        return JsonResponse({"detail": "This read endpoint accepts GET only."}, status=405)
    model_config = RESOURCE_MODELS.get(resource)
    if model_config is None:
        return JsonResponse({"detail": "Unknown resource."}, status=404)
    model, fields = model_config
    try:
        rows = list(model.objects.values(*fields)[:100])
    except (OperationalError, ProgrammingError):
        rows = []
    return JsonResponse(
        {"results": [{key: _json_value(value) for key, value in row.items()} for row in rows], "count": len(rows), "next": None, "previous": None}
    )


def _dashboard_workspace_id(request):
    try:
        return request.user.profile.workspace_id
    except Exception:  # noqa: BLE001 - anonymous or profile-less requests stay unscoped
        return None


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
    return JsonResponse({"data": {"counts": counts, "workflow_count": len(persisted_workflow_catalog())}})


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


def workflows_api(request):
    results = persisted_workflow_catalog()
    return JsonResponse({"results": results, "count": len(results)})


def integrations_api(request):
    return JsonResponse({"results": platform_catalog(), "count": len(platform_catalog())})


def custom_fields_api(request):
    profile = getattr(request.user, "profile", None)
    workspace = getattr(profile, "workspace", None) if profile else None
    catalog = custom_object_catalog(workspace)
    return JsonResponse({"results": catalog, "count": len(catalog)})
