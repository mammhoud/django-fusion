"""Django views exposing MCP task tools. Served at ``/fusion/mcp/tasks/``.

Hardened surface (django-fusion-tasks-mcp-plan.md §6.4): the tools are
read/write task-management operations, so production exposure is gated behind
an explicit bearer token (``FUSION_MCP_TOKEN``), a staff session fallback, a
cache-backed rate limit, JSON-RPC body validation, and an audit log line per
call. In DEBUG with no token configured the surface stays reachable for local
development only.

Configuration::

    FUSION_MCP_TOKEN = "<shared-secret>"   # required outside DEBUG
    FUSION_MCP_RATE_LIMIT = "60/minute"    # optional (default 60/minute)

Clients send ``Authorization: Bearer <token>`` (see the plan's Claude Desktop
example).
"""
from __future__ import annotations

import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django_fusion.tasks.mcp_handlers import (
    handle_task_history,
    handle_task_inspect,
    handle_task_purge,
    handle_task_queues,
    handle_task_retry,
    handle_task_stats,
    handle_task_trigger,
    handle_task_workers,
)
from django_fusion.tasks.mcp_tools import MCP_TASK_TOOLS

logger = logging.getLogger("django_fusion.tasks.mcp")

_HANDLERS = {
    "task.inspect": handle_task_inspect,
    "task.queues": handle_task_queues,
    "task.history": handle_task_history,
    "task.retry": handle_task_retry,
    "task.trigger": handle_task_trigger,
    "task.stats": handle_task_stats,
    "task.purge": handle_task_purge,
    "task.workers": handle_task_workers,
}


def _configured_token() -> str:
    """Return the configured MCP bearer token (empty string when unset)."""
    return str(getattr(settings, "FUSION_MCP_TOKEN", "") or "")


def _client_key(request: HttpRequest) -> str:
    """A stable rate-limit key for the caller (token first, then IP)."""
    token = _bearer_token(request)
    if token:
        return f"mcp:token:{token}"
    ip = request.META.get("REMOTE_ADDR", "unknown")
    return f"mcp:ip:{ip}"


def _bearer_token(request: HttpRequest) -> str:
    header = request.META.get("HTTP_AUTHORIZATION", "") or ""
    if header.startswith("Bearer "):
        return header[len("Bearer ") :].strip()
    return ""


def _authorize(request: HttpRequest) -> JsonResponse | None:
    """Return an error response when the caller is not authorized, else None.

    Policy: an explicit ``FUSION_MCP_TOKEN`` is the only accepted credential in
    non-DEBUG environments; a staff session and DEBUG are dev fallbacks only.
    """
    token = _configured_token()
    if token:
        if _bearer_token(request) == token:
            return None
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user = getattr(request, "user", None)
    if getattr(user, "is_authenticated", False) and getattr(user, "is_staff", False):
        return None
    if getattr(settings, "DEBUG", False):
        return None
    return JsonResponse(
        {"error": "MCP access requires FUSION_MCP_TOKEN or a staff session"},
        status=401,
    )


def _rate_limit(request: HttpRequest) -> JsonResponse | None:
    """Cache-backed per-caller rate limit (default 60 calls/minute)."""
    try:
        limit = int(getattr(settings, "FUSION_MCP_RATE_LIMIT", 60))
    except (TypeError, ValueError):
        limit = 60
    if limit <= 0:
        return None

    key = _client_key(request)
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=60)
        count = 1
    if count > limit:
        return JsonResponse({"error": "Rate limit exceeded"}, status=429)
    return None


def _validate_body(body) -> dict | None:
    """Return a normalized JSON-RPC 2.0 ``tools/call`` body, or an error dict."""
    if not isinstance(body, dict):
        return {"error": "JSON-RPC body must be an object"}
    if body.get("jsonrpc") != "2.0":
        return {"error": "jsonrpc must be \"2.0\""}
    method = body.get("method")
    if method not in (None, "tools/call"):
        return {"error": f"Unsupported method: {method}"}
    params = body.get("params") or {}
    if not isinstance(params, dict):
        return {"error": "params must be an object"}
    tool_name = params.get("name")
    if not isinstance(tool_name, str) or not tool_name:
        return {"error": "params.name is required"}
    arguments = params.get("arguments", {})
    if not isinstance(arguments, dict):
        return {"error": "params.arguments must be an object"}
    return {"tool_name": tool_name, "arguments": arguments, "id": body.get("id")}


def mcp_tools_list(request: HttpRequest) -> JsonResponse:
    """List available MCP task tools (authenticated, read-only).

    Returns full tool definitions (name, description, parameters) so MCP
    clients can discover both the tool surface and its input schemas.
    """
    denied = _authorize(request)
    if denied is not None:
        return denied
    return JsonResponse({
        "tools": [
            {
                "name": name,
                "description": spec["description"],
                "inputSchema": spec["parameters"],
            }
            for name, spec in MCP_TASK_TOOLS.items()
        ]
    })


@csrf_exempt
def mcp_tools_call(request: HttpRequest) -> JsonResponse:
    """MCP JSON-RPC endpoint for task operations (authenticated + rate limited)."""
    denied = _authorize(request)
    if denied is not None:
        return denied
    limited = _rate_limit(request)
    if limited is not None:
        return limited

    try:
        raw = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    parsed = _validate_body(raw)
    if "error" in parsed:
        return JsonResponse(parsed, status=400)

    tool_name = parsed["tool_name"]
    arguments = parsed["arguments"]
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        return JsonResponse(
            {
                "error": f"Unknown tool: {tool_name}",
                "available": sorted(_HANDLERS.keys()),
            },
            status=404,
        )

    logger.info("mcp_tool_call tool=%r", tool_name)
    try:
        result = handler(**arguments)
    except Exception as exc:  # noqa: BLE001 - normalize handler failures to JSON-RPC
        logger.exception("Task MCP tool %r failed", tool_name)
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({"jsonrpc": "2.0", "id": parsed["id"], "result": result})
