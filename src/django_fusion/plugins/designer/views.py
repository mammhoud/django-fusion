"""Authenticated JSON-RPC adapter for the django-fusion designer."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django_fusion.plugins.designer import (
    designer_component_catalog,
    designer_webapp_enhancement_plan,
    designer_website_audit,
    designer_form_scaffold,
    designer_preview,
    designer_table_scaffold,
    designer_validate,
    designer_wagtail_field,
)
from django_fusion.plugins.designer.tools import MCP_DESIGNER_TOOLS

_HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "designer.component_catalog": designer_component_catalog,
    "designer.website_audit": designer_website_audit,
    "designer.webapp_enhancement_plan": designer_webapp_enhancement_plan,
    "designer.wagtail_field": designer_wagtail_field,
    "designer.form_scaffold": designer_form_scaffold,
    "designer.table_scaffold": designer_table_scaffold,
    "designer.validate": designer_validate,
    "designer.preview": designer_preview,
}


def _is_allowed(request) -> bool:
    """Allow staff users; anonymous mode is DEBUG-only and localhost-only."""
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
    if not getattr(settings, "DEBUG", False) or not getattr(settings, "FUSION_DESIGNER_ALLOW_ANONYMOUS", False):
        return False
    remote_addr = request.META.get("REMOTE_ADDR", "")
    return remote_addr in {"127.0.0.1", "::1", "localhost"}


def _error(message: str, status: int, *, request_id: Any = None) -> JsonResponse:
    return JsonResponse({"jsonrpc": "2.0", "id": request_id, "error": {"message": message}}, status=status)


@require_POST
def designer_tools_list(request):
    """Handle the standard MCP ``tools/list`` JSON-RPC request."""
    request_id = None
    if not _is_allowed(request):
        return _error("Designer access requires a staff or superuser account", 403)
    try:
        body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            return _error("JSON-RPC body must be an object", 400)
        request_id = body.get("id")
        if body.get("jsonrpc") != "2.0" or body.get("method") != "tools/list":
            return _error("method must be tools/list and jsonrpc must be '2.0'", 400, request_id=request_id)
    except (AttributeError, UnicodeDecodeError, json.JSONDecodeError):
        return _error("Invalid JSON-RPC body", 400, request_id=request_id)
    tools = [{"name": name, **tool} for name, tool in MCP_DESIGNER_TOOLS.items()]
    return JsonResponse({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}})


@require_POST
def designer_tools_call(request):
    """Call one safe, authenticated designer tool."""
    request_id = None
    if not _is_allowed(request):
        return _error("Designer access requires a staff or superuser account", 403)
    try:
        body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            return _error("JSON-RPC body must be an object", 400, request_id=request_id)
        request_id = body.get("id")
        if body.get("jsonrpc") != "2.0":
            return _error("jsonrpc must be '2.0'", 400, request_id=request_id)
        if body.get("method") != "tools/call":
            return _error("method must be tools/call", 400, request_id=request_id)
        params = body.get("params", {})
        if not isinstance(params, dict):
            return _error("params must be an object", 400, request_id=request_id)
        name = params.get("name")
        arguments = params.get("arguments", {})
    except (AttributeError, UnicodeDecodeError, json.JSONDecodeError):
        return _error("Invalid JSON-RPC body", 400, request_id=request_id)
    if not isinstance(arguments, dict):
        return _error("arguments must be an object", 400, request_id=request_id)
    handler = _HANDLERS.get(name)
    if handler is None:
        return _error(f"Unknown designer tool: {name}", 404, request_id=request_id)
    try:
        result = handler(**arguments)
    except (TypeError, ValueError) as exc:
        return _error(str(exc), 400, request_id=request_id)
    except Exception:
        return _error("Designer tool failed", 500, request_id=request_id)
    return JsonResponse({"jsonrpc": "2.0", "id": request_id, "result": result})
