"""FastAPI endpoints for project-local MCP helpers.

Run with the crafts-ai source package on the import path, for example:

    PYTHONPATH=applications/libs/crafts-ai/src uvicorn mcp_server:app \
        --app-dir .kilo --host 127.0.0.1 --port 8002
"""

from __future__ import annotations

from io import StringIO
from typing import Any

from django.core.management import call_command
from fastapi import FastAPI

from crafts_ai.cli import package_info

app = FastAPI(title="Structa Cloud MCP")


@app.get("/health")
async def health() -> dict[str, str]:
    """Return a lightweight health response for the MCP server."""
    return {"status": "ok"}


@app.get("/crafts-ai/info")
async def crafts_ai_info() -> dict[str, str | bool]:
    """Return framework-agnostic crafts-ai package metadata."""
    return package_info()


@app.get("/migrations/status")
async def migration_status() -> dict[str, Any]:
    """Return Django migration status from the configured project."""
    out = StringIO()
    call_command("showmigrations", stdout=out)
    output = out.getvalue()
    return {"raw": output}
