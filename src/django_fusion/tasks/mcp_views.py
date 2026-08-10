"""Django views exposing MCP task tools.  Served at /fusion/mcp/tasks/."""

from __future__ import annotations

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django_fusion.tasks.mcp_tools import MCP_TASK_TOOLS
from django_fusion.tasks.mcp_handlers import (
    handle_task_inspect,
    handle_task_queues,
    handle_task_history,
    handle_task_retry,
    handle_task_trigger,
    handle_task_stats,
    handle_task_purge,
    handle_task_workers,
)

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


def mcp_tools_list(request):
    """List available MCP task tools."""
    return JsonResponse({"tools": list(MCP_TASK_TOOLS.keys())})


@csrf_exempt
def mcp_tools_call(request):
    """MCP JSON-RPC endpoint for task operations."""
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON body"}, status=400
        )

    tool_name = body.get("params", {}).get("name")
    arguments = body.get("params", {}).get("arguments", {})

    handler = _HANDLERS.get(tool_name)
    if not handler:
        return JsonResponse(
            {
                "error": f"Unknown tool: {tool_name}",
                "available": sorted(_HANDLERS.keys()),
            },
            status=404,
        )

    try:
        result = handler(**arguments)
        return JsonResponse(
            {"jsonrpc": "2.0", "id": body.get("id"), "result": result}
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
