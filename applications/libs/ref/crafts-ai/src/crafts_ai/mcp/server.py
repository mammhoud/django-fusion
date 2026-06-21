"""Standalone MCP server — no Django required."""
import logging

logger = logging.getLogger(__name__)

class MCPServer:
    """Minimal MCP server wrapper."""
    def __init__(self, name: str = "craftsai-mcp", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._tools = {}

    def tool(self, name: str = None):
        """Decorator to register a tool."""
        def decorator(func):
            tool_name = name or func.__name__
            self._tools[tool_name] = func
            return func
        return decorator

    def list_tools(self) -> list:
        return list(self._tools.keys())

    def run(self, host: str = "localhost", port: int = 8765):
        logger.info(f"Starting {self.name} v{self.version} on {host}:{port}")
        logger.info(f"Registered tools: {self.list_tools()}")
