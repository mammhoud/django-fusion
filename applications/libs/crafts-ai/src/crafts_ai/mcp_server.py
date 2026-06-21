"""Optional FastAPI MCP integration points for crafts-ai."""

from __future__ import annotations

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover - optional runtime dependency
    FastAPI = None  # type: ignore[assignment]

from .cli import package_info

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
