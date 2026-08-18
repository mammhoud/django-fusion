"""django-bolt router for django-fusion task MCP tools.

Exposes the 8 task management tools (inspect, queues, history, retry,
trigger, stats, purge, workers) as django-bolt endpoints so the Kilo MCP
server can mount them alongside the designer and prompt catalog routers.

Register on a ``BoltAPI``::

    from django_bolt import BoltAPI
    from django_fusion.tasks.mcp_router import TaskMCPRouter

    api = TaskMCPRouter().api
"""

from __future__ import annotations

import json
import logging
from typing import Any

from django_bolt import BoltAPI
from django_bolt.responses import Response

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
from django_fusion.tasks.mcp_tools import MCP_TASK_TOOLS

logger = logging.getLogger(__name__)

_HANDLERS: dict[str, Any] = {
    "task.inspect": handle_task_inspect,
    "task.queues": handle_task_queues,
    "task.history": handle_task_history,
    "task.retry": handle_task_retry,
    "task.trigger": handle_task_trigger,
    "task.stats": handle_task_stats,
    "task.purge": handle_task_purge,
    "task.workers": handle_task_workers,
}


def _read_json_body(request: dict[str, Any]) -> dict[str, Any] | None:
    """Decode the raw request body into a JSON object, or ``None``."""
    raw = request.get("body", b"")
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", "replace")
    try:
        body = json.loads(raw) if raw else {}
    except (TypeError, ValueError):
        return None
    return body if isinstance(body, dict) else None


def register_task_routes(api: BoltAPI) -> None:
    """Register the django-fusion task MCP endpoints on *api*."""

    @api.get("/tasks/tools", tags=["tasks-mcp"])
    def tools_list() -> dict[str, Any]:
        """List all available task MCP tools with their schemas."""
        return {
            "tools": [
                {
                    "name": name,
                    "description": spec["description"],
                    "parameters": spec["parameters"],
                }
                for name, spec in MCP_TASK_TOOLS.items()
            ]
        }

    @api.post("/tasks/call", tags=["tasks-mcp"])
    def tools_call(request: dict[str, Any]) -> Any:
        """JSON-RPC endpoint for task operations."""
        body = _read_json_body(request)
        if body is None:
            return Response(status_code=400, content={"error": "Invalid JSON body"})

        tool_name = body.get("params", {}).get("name")
        arguments = body.get("params", {}).get("arguments", {})

        handler = _HANDLERS.get(tool_name)
        if handler is None:
            return Response(
                status_code=404,
                content={
                    "error": f"Unknown tool: {tool_name}",
                    "available": sorted(_HANDLERS.keys()),
                },
            )

        try:
            result = handler(**arguments)
        except Exception as exc:
            logger.exception("Task MCP tool %r failed", tool_name)
            return Response(status_code=500, content={"error": str(exc)})

        return {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": result,
        }


class TaskMCPRouter:
    """Builds a :class:`django_bolt.BoltAPI` exposing django-fusion task MCP tools."""

    def __init__(self, *, prefix: str = "", **kwargs: Any) -> None:
        self.api = BoltAPI(prefix=prefix, **kwargs)
        register_task_routes(self.api)

    @staticmethod
    def register(api: BoltAPI) -> None:
        """Register the task routes onto an existing BoltAPI."""
        register_task_routes(api)
