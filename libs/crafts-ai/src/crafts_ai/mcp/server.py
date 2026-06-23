"""MCP tools for Structa component analysis and secure config inspection."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

COMP_RE = re.compile(r"{%\s*comp\s+['\"]?([^'\"\s%]+)")
FIELD_RE = re.compile(r"{{\s*([A-Za-z_][\w.]*)")
SENSITIVE = ("SECRET", "TOKEN", "PASSWORD", "KEY", "DATABASE_URL")

class MCPServer:
    def __init__(self, name: str = "craftsai-mcp", version: str = "1.0.0"):
        self.name = name; self.version = version; self._tools = {}
    def tool(self, name: str | None = None):
        def decorator(func):
            self._tools[name or func.__name__] = func; return func
        return decorator
    def list_tools(self) -> list[str]:
        return list(self._tools)
    def call_tool(self, name: str, **kwargs: Any) -> Any:
        return self._tools[name](**kwargs)
    def run(self, host: str = "localhost", port: int = 8765):
        print(json.dumps({"name": self.name, "version": self.version, "tools": self.list_tools()}))

def _templates(root: Path) -> list[Path]:
    return sorted(set(root.glob("**/assets/templates/**/*.html")) | set(root.glob("**/theme/**/*.html")))

def theme_analyzer(root: str = ".") -> dict[str, Any]:
    base = Path(root).resolve(); components = {}
    for path in _templates(base):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(base).as_posix()
        components[rel] = {"comp_tags": COMP_RE.findall(text), "fields": sorted(set(FIELD_RE.findall(text)))}
    return {"root": str(base), "components": components}

def component_mapper(root: str = ".", central: str = "applications/ctc-research") -> dict[str, Any]:
    base = Path(root).resolve(); central_base = (base / central).resolve() if not Path(central).is_absolute() else Path(central)
    central_names = {p.name: p.relative_to(central_base).as_posix() for p in _templates(central_base)}
    suggestions = {}
    for path in _templates(base):
        if central_base in path.parents: continue
        if path.name in central_names:
            suggestions[path.relative_to(base).as_posix()] = central_names[path.name]
    return {"central": str(central_base), "suggestions": suggestions}

def config_inspector(prefix: str | None = None) -> dict[str, str]:
    data = {}
    for key, value in os.environ.items():
        if prefix and not key.startswith(prefix): continue
        data[key] = "***redacted***" if any(flag in key.upper() for flag in SENSITIVE) else value
    return dict(sorted(data.items()))

def load_agent_configs(root: str = ".") -> dict[str, Any]:
    configs = {}
    for path in (Path(root) / ".kilo" / "agent").glob("*.json"):
        configs[path.name] = json.loads(path.read_text(encoding="utf-8"))
    return configs

server = MCPServer()
server.tool("theme_analyzer")(theme_analyzer)
server.tool("component_mapper")(component_mapper)
server.tool("config_inspector")(config_inspector)
server.tool("load_agent_configs")(load_agent_configs)
