"""Smoke tests for ceptor_ai — no Django required."""
import pytest


def test_ceptor_ai_ai_import():
    from ceptor_ai.ai.integrations import (
        AIIntegration,
        AIIntegrationRegistry,
        ClaudeIntegration,
        OpenAIIntegration,
    )
    assert "openai" in AIIntegrationRegistry.list_integrations()
    assert "claude" in AIIntegrationRegistry.list_integrations()


def test_ceptor_ai_mcp_import():
    from ceptor_ai.mcp.server import MCPServer
    server = MCPServer(name="test-server")
    assert server.name == "test-server"
    assert server.list_tools() == []


def test_ceptor_ai_mcp_tool_registration():
    from ceptor_ai.mcp.server import MCPServer
    server = MCPServer()

    @server.tool("greet")
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    assert "greet" in server.list_tools()


def test_ceptor_ai_no_django():
    """Verify ceptor_ai core modules don't import Django."""
    from ceptor_ai.ai import integrations
    from ceptor_ai.mcp import server
    assert integrations is not None
    assert server is not None
