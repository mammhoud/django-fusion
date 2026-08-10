"""FastAPI router for django-fusion task MCP tools.

Exposes the 8 task management tools (inspect, queues, history, retry,
trigger, stats, purge, workers) as FastAPI endpoints so the Kilo MCP
server can mount them alongside the designer and prompt catalog routers.

Usage from Kilo::

    from django_fusion.tasks.mcp_router import TaskMCPRouter
    app.include_router(TaskMCPRouter(), prefix="")
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

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


class TaskMCPRouter(APIRouter):
    """FastAPI router exposing django-fusion task MCP tools.

    Mounted by Kilo at ``/tasks/tools`` (tools list) and
    ``/tasks/call`` (JSON-RPC dispatch).  All handlers delegate to the
    django-fusion task system.
    """

    def __init__(self, *, prefix: str = ""):
        super().__init__(prefix=prefix, tags=["tasks-mcp"])
        self._register_routes()

    # -- route registration ------------------------------------

    def _register_routes(self):
        router = self

        @router.get("/tasks/tools")
        async def tools_list(_request: Request) -> JSONResponse:
            """List all available task MCP tools with their schemas."""
            return JSONResponse({
                "tools": [
                    {
                        "name": name,
                        "description": spec["description"],
                        "parameters": spec["parameters"],
                    }
                    for name, spec in MCP_TASK_TOOLS.items()
                ]
            })

        @router.post("/tasks/call")
        async def tools_call(request: Request) -> JSONResponse:
            """JSON-RPC endpoint for task operations."""
            try:
                body = await request.json()
            except Exception:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid JSON body"},
                )

            tool_name = body.get("params", {}).get("name")
            arguments = body.get("params", {}).get("arguments", {})

            handler = _HANDLERS.get(tool_name)
            if handler is None:
                return JSONResponse(
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
                return JSONResponse(
                    status_code=500,
                    content={"error": str(exc)},
                )

            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": result,
            })
