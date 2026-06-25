"""Smoke tests for craftsai — no Django required."""
import pytest


def test_craftsai_ai_import():
    from crafts_ai.ai.integrations import (
        AIIntegration,
        AIIntegrationRegistry,
        ClaudeIntegration,
        OpenAIIntegration,
    )
    assert "openai" in AIIntegrationRegistry.list_integrations()
    assert "claude" in AIIntegrationRegistry.list_integrations()


def test_craftsai_mcp_import():
    from crafts_ai.mcp.server import MCPServer
    server = MCPServer(name="test-server")
    assert server.name == "test-server"
    assert server.list_tools() == []


def test_craftsai_mcp_tool_registration():
    from crafts_ai.mcp.server import MCPServer
    server = MCPServer()

    @server.tool("greet")
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    assert "greet" in server.list_tools()


def test_craftsai_no_django():
    """Verify craftsai core modules don't import Django."""
    from crafts_ai.ai import integrations
    from crafts_ai.mcp import server
    assert integrations is not None
    assert server is not None
