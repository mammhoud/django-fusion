"""Model Context Protocol (MCP) server integration.

Exposes ceptor-ai tools and context to MCP-compatible clients (e.g. Kiro, Claude).

Modules
-------
mcp.server      FastAPI/MCP server exposing ceptor-ai capabilities as MCP tools.

Usage::

    from ceptor_ai.mcp.server import create_mcp_app
    app = create_mcp_app()
"""
