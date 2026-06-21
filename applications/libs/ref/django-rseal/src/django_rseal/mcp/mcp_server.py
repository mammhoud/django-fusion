import asyncio
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import mcp.server.stdio
import mcp.types as types
import requests
from django.conf import settings
from mcp.server import Server
from mcp.server.models import InitializationOptions

from .signals import file_written
from .utils import get_all_static_dirs, get_all_template_dirs, validate_scss


class DjangoMCPServer:
    def __init__(self):
        self.server = Server("django-mcp-designer")
        self.setup_tools()

    def setup_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                types.Tool(name="list_templates", description="List all template files", inputSchema={"type": "object"}),
                types.Tool(name="read_template", description="Read a template file", inputSchema={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}},
                    "required": ["filepath"]
                }),
                types.Tool(name="write_template", description="Write a template file", inputSchema={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}},
                    "required": ["filepath", "content"]
                }),
                types.Tool(name="list_styles", description="List all style files", inputSchema={"type": "object"}),
                types.Tool(name="read_style", description="Read a style file", inputSchema={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}},
                    "required": ["filepath"]
                }),
                types.Tool(name="write_style", description="Write a style file", inputSchema={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}},
                    "required": ["filepath", "content"]
                }),
                types.Tool(
                    name="patch_file",
                    description="Safely patch a file using SEARCH/REPLACE blocks. Replace 'search' block exactly matching the file content with the 'replace' block.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string"},
                            "search": {"type": "string"},
                            "replace": {"type": "string"}
                        },
                        "required": ["filepath", "search", "replace"]
                    }
                ),
                types.Tool(
                    name="update_component_style",
                    description="High-level tool to update a component's style. Driven by conversational design workflow. If style_property or style_value are missing, you should elicit them from the user.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component_name": {"type": "string", "description": "Name of the component"},
                            "style_property": {"type": "string", "description": "CSS property to change (e.g., padding, color)"},
                            "style_value": {"type": "string", "description": "New value for the CSS property"}
                        },
                        "required": ["component_name", "style_property", "style_value"]
                    }
                ),
                types.Tool(name="preview_changes", description="Preview changes in a temporary server", inputSchema={
                    "type": "object",
                    "properties": {"changed_files": {"type": "array", "items": {"type": "string"}}},
                    "required": ["changed_files"]
                }),
            ]

        @self.server.list_prompts()
        async def list_prompts() -> list[types.Prompt]:
            return [
                types.Prompt(
                    name="update-component-style",
                    description="Conversational design workflow to update the style of a Django component.",
                    arguments=[
                        types.PromptArgument(
                            name="component_name",
                            description="Name of the component to update",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="refactor-component",
                    description="Refactor a component's structure.",
                    arguments=[
                        types.PromptArgument(
                            name="component_name",
                            description="Name of the component to refactor",
                            required=True
                        )
                    ]
                )
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
            if name == "update-component-style":
                component = (arguments or {}).get("component_name", "a specific component")
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"I would like to update the style of {component}. Please use 'list_styles' or resources to find the context, then formulate CSS/HTML changes, and finally ask for missing details (elicitation) before applying changes with 'patch_file'. Do you have any specific color or size changes in mind?"
                            )
                        )
                    ]
                )
            elif name == "refactor-component":
                component = (arguments or {}).get("component_name", "the component")
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"Please refactor the HTML structure for {component}. Use 'read_template' to check its current layout, then 'patch_file' to rewrite it."
                            )
                        )
                    ]
                )
            raise ValueError(f"Unknown prompt: {name}")

        @self.server.list_resources()
        async def list_resources() -> list[types.Resource]:
            return []

        @self.server.list_resource_templates()
        async def list_resource_templates() -> list[types.ResourceTemplate]:
            return [
                types.ResourceTemplate(
                    uriTemplate="file://{filepath}",
                    name="Project File",
                    description="Any file in the project (access via file://)",
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            if uri.startswith("file://"):
                filepath = uri[len("file://"):]
                full = Path(settings.BASE_DIR) / filepath
                if not full.exists():
                    full = Path(filepath)
                if full.exists():
                    return full.read_text(encoding='utf-8')
                raise ValueError(f"Resource not found: {uri}")
            raise ValueError(f"Unsupported URI scheme: {uri}")

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            try:
                if name == "list_templates":
                    files = self._find_templates()
                    return [types.TextContent(type="text", text="\n".join(files))]
                elif name == "read_template":
                    return self._read_file(arguments["filepath"])
                elif name == "write_template":
                    return self._write_file(arguments["filepath"], arguments["content"], is_template=True)
                elif name == "list_styles":
                    files = self._find_styles()
                    return [types.TextContent(type="text", text="\n".join(files))]
                elif name == "read_style":
                    return self._read_file(arguments["filepath"])
                elif name == "write_style":
                    return self._write_file(arguments["filepath"], arguments["content"], is_style=True)
                elif name == "patch_file":
                    return self._patch_file(arguments["filepath"], arguments["search"], arguments["replace"])
                elif name == "update_component_style":
                    comp = arguments["component_name"]
                    prop = arguments["style_property"]
                    val = arguments["style_value"]
                    return [types.TextContent(type="text", text=f"Gathering context for {comp}. Now please use 'patch_file' to apply '{prop}: {val}' to the relevant CSS file.")]
                elif name == "preview_changes":
                    return await self._preview_changes(arguments.get("changed_files", []))
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    def _find_templates(self):
        """Return list of all template files (relative to project root)."""
        templates = []
        exts = getattr(settings, 'MCP_TEMPLATE_EXTENSIONS', ['.html'])
        base_dir = Path(settings.BASE_DIR)
        for template_dir in get_all_template_dirs():
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in exts):
                        full = Path(root) / file
                        try:
                            rel = full.relative_to(base_dir)
                            templates.append(str(rel))
                        except ValueError:
                            templates.append(str(full))
        return sorted(list(set(templates)))

    def _find_styles(self):
        """Return list of all style files."""
        styles = []
        exts = getattr(settings, 'MCP_STYLE_EXTENSIONS', ['.css', '.scss'])
        base_dir = Path(settings.BASE_DIR)
        for static_dir in get_all_static_dirs():
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in exts):
                        full = Path(root) / file
                        try:
                            rel = full.relative_to(base_dir)
                            styles.append(str(rel))
                        except ValueError:
                            styles.append(str(full))
        return sorted(list(set(styles)))

    def _read_file(self, rel_path):
        full = Path(settings.BASE_DIR) / rel_path
        if not full.exists():
            full = Path(rel_path)
        if not full.exists():
            raise ValueError(f"File not found: {rel_path}")
        content = full.read_text(encoding='utf-8')
        return [types.TextContent(type="text", text=content)]

    def _write_file(self, rel_path, new_content, is_template=False, is_style=False):
        full = Path(settings.BASE_DIR) / rel_path
        if not full.exists():
            full = Path(rel_path)
        if not full.exists():
            raise ValueError(f"File not found: {rel_path}")

        # Backup
        if getattr(settings, 'MCP_CREATE_BACKUPS', True):
            backup = full.with_suffix(full.suffix + '.bak')
            shutil.copy(full, backup)

        # Validate SCSS if needed
        if is_style and full.suffix == '.scss':
            validate_scss(new_content)

        # Write
        full.write_text(new_content, encoding='utf-8')

        # Send signal
        file_written.send(sender=self.__class__, filepath=str(rel_path), content=new_content)

        # Optional webhook
        webhook_url = getattr(settings, 'MCP_WEBHOOK_URL', None)
        if webhook_url:
            self._send_webhook(rel_path, new_content)

        backup_msg = f" (backup at {backup})" if getattr(settings, 'MCP_CREATE_BACKUPS', True) else ""
        return [types.TextContent(type="text", text=f"Changes written to {rel_path}{backup_msg}")]

    def _patch_file(self, rel_path, search, replace):
        full = Path(settings.BASE_DIR) / rel_path
        if not full.exists():
            full = Path(rel_path)
        if not full.exists():
            raise ValueError(f"File not found: {rel_path}")

        file_content = full.read_text(encoding='utf-8')
        if search not in file_content:
            return [types.TextContent(type="text", text="Error: Exact search block not found in file. Make sure it matches perfectly.")]

        # Backup
        if getattr(settings, 'MCP_CREATE_BACKUPS', True):
            backup = full.with_suffix(full.suffix + '.bak')
            import shutil
            shutil.copy(full, backup)

        new_content = file_content.replace(search, replace, 1)
        full.write_text(new_content, encoding='utf-8')

        return [types.TextContent(type="text", text=f"File {rel_path} successfully patched.")]

    async def _preview_changes(self, changed_files):
        port = 8082
        cmd = [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}"]

        try:
            process = subprocess.Popen(
                cmd,
                cwd=settings.BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            await asyncio.sleep(3)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                return [types.TextContent(type="text", text=f"Failed to start preview server: {stderr}")]

            url = f"http://127.0.0.1:{port}"
            return [types.TextContent(type="text", text=f"Preview started at {url}. (Note: direct changes applied)")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error starting preview: {str(e)}")]

    def _send_webhook(self, rel_path, content):
        def send():
            try:
                requests.post(settings.MCP_WEBHOOK_URL, json={'file': str(rel_path), 'content': content}, timeout=5)
            except Exception:
                pass
        threading.Thread(target=send, daemon=True).start()

    async def run(self):
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="django-mcp-designer",
                    server_version="0.1.0",
                    capabilities=types.ServerCapabilities(
                        tools=types.ToolsCapability(listChanged=True),
                        prompts=types.PromptsCapability(listChanged=True),
                        resources=types.ResourcesCapability(listChanged=True, subscribe=False)
                    )
                ),
            )


def main():
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    django.setup()

    server = DjangoMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
