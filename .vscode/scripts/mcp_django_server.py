#!/usr/bin/env python
"""
MCP Server for Django ORM access
"""
import os
import sys
import django

# Add your project to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from mcp.server import Server, NotificationOptions
import mcp.server.stdio
from mcp.types import TextContent
import asyncio

server = Server("django-orm")

@server.list_tools()
async def handle_list_tools():
    """List available Django ORM tools"""
    tools = [
        {
            "name": "django_query",
            "description": "Execute a Django ORM query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "model": {"type": "string", "description": "Django model name"},
                    "query": {"type": "string", "description": "ORM query to execute"}
                },
                "required": ["model", "query"]
            }
        },
        {
            "name": "django_list_models",
            "description": "List all available Django models",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]
    return tools

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, NotificationOptions())

if __name__ == "__main__":
    asyncio.run(main())
