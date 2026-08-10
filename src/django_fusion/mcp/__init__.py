"""django-fusion MCP integration package.

Provides FastAPI routers and prompt catalog utilities that any project
can mount into its own ASGI/FastAPI MCP server. The Kilo MCP server
(applications/agents/mcp_server.py) imports from here rather than
containing its own designer, info, and prompt logic.

Usage::

    from fastapi import FastAPI
    from django_fusion.mcp import FusionMCPRouter
    from django_fusion.plugins.designer.mcp_router import designer_router

    app = FastAPI()
    app.include_router(FusionMCPRouter(), prefix="")
    app.include_router(designer_router, prefix="")
"""

from __future__ import annotations

from django_fusion.mcp.fusion_router import FusionMCPRouter

__all__ = [
    "FusionMCPRouter",
    "list_prompt_metadata",
    "get_prompt",
]

# Lazy imports for optional prompt catalog
def __getattr__(name: str):
    if name == "list_prompt_metadata":
        from django_fusion.mcp.prompts import list_prompt_metadata

        return list_prompt_metadata
    if name == "get_prompt":
        from django_fusion.mcp.prompts import get_prompt

        return get_prompt
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
