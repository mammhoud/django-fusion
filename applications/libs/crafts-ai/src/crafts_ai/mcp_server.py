"""Optional FastAPI MCP integration points for crafts-ai."""

from __future__ import annotations

from importlib import import_module, util
from typing import Any

from .cli import package_info

MCP_FEATURES: tuple[dict[str, str], ...] = (
    {
        "name": "health",
        "path": "/health",
        "summary": "Lightweight readiness response for local MCP clients.",
    },
    {
        "name": "package_info",
        "path": "/info",
        "summary": "Package metadata shared with CLI and documentation workflows.",
    },
    {
        "name": "latest_features",
        "path": "/features",
        "summary": "Current AI/customizer/MCP feature inventory for docs and agents.",
    },
    {
        "name": "file_structure",
        "path": "/file-structure",
        "summary": "Canonical package and documentation paths agents should inspect.",
    },
)

MCP_FILE_STRUCTURE: dict[str, tuple[str, ...]] = {
    "package": (
        "applications/libs/crafts-ai/src/crafts_ai/",
        "applications/libs/crafts-ai/src/crafts_ai/customizer/",
        "applications/libs/crafts-ai/src/crafts_ai/mcp_server.py",
    ),
    "docs": (
        "applications/libs/crafts-ai/docs/agents.md",
        "docs/ai/START_HERE.md",
        "docs/ai/latest_features.md",
        "docs/ai/mcp_reference.md",
    ),
    "kilo": (
        ".kilo/config.json",
        ".kilo/commands/",
        ".kilo/skills/",
    ),
}


def latest_features() -> dict[str, Any]:
    """Return framework-agnostic MCP feature metadata for docs and agents."""
    return {
        "package": "crafts-ai",
        "features": list(MCP_FEATURES),
        "file_structure": {
            key: list(paths) for key, paths in MCP_FILE_STRUCTURE.items()
        },
    }


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

    @app.get("/features")
    async def features() -> dict[str, Any]:
        """Return current crafts-ai feature metadata for MCP clients."""
        return latest_features()

    @app.get("/file-structure")
    async def file_structure() -> dict[str, list[str]]:
        """Return canonical package, docs, and Kilo file locations."""
        return {key: list(paths) for key, paths in MCP_FILE_STRUCTURE.items()}
else:
    app = None
