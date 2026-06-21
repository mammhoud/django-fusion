"""Optional FastAPI MCP integration points for crafts-ai."""

from __future__ import annotations

from importlib import import_module, util
from typing import Any

from .cli import package_info

FastAPI: Any = None
if util.find_spec("fastapi") is not None:
    FastAPI = import_module("fastapi").FastAPI

if FastAPI is not None:
    app = FastAPI(title="crafts-ai MCP")

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Return a health response for Kilo MCP checks."""
        return {"status": "ok", "package": "crafts-ai"}

    @app.get("/info")
    async def info() -> dict[str, str | bool]:
        """Return package metadata for MCP clients."""
        return package_info()
else:
    app = None
