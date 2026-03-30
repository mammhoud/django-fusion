# 🤖 Model Context Protocol (MCP) in AllianceCore

## Overview

AllianceCore is designed to be fully integrated with AI-driven development workflows using the **Model Context Protocol (MCP)**. MCP allows AI agents (like Claude or Antigravity) to act as a "junior developer" with direct access to your Django environment.

## 🛠️ Usage with Django Grep

The `django-grep` plugin provides the underlying server that implements the MCP tools. It is installed as a source clone at `/libs/django-grep` (see [INSTALL.md](../INSTALL.md#3-set-up-django-grep-source-clone)).

### Available Tools

| Tool | Description |
|---|---|
| `search_code` | Fast regex search across the entire project |
| `design_component` | Create new Wagtail blocks and templates autonomously |
| `inspect_schema` | Visualize database relationships and model definitions |
| `debug_logs` | Access and analyze application logs in real-time |

## 🔌 How to Integrate

To enable AI agents to work on this project:

1. Ensure `django_grep.mcp_designer` is in `INSTALLED_APPS`.
2. Configure your AI IDE (e.g., Cursor, Windsurf) or Agent to point to the `mcp_django_server.py` entry point.
3. Use the following prompt to prime the AI:
   > "You are an expert Django/Wagtail developer. Use the MCP tools provided by django-grep to explore the AllianceCore codebase and help me build new features."

## 📍 Integration Points

- **Core:** The core project provides the settings and structure for MCP discovery.
- **Plugins:** Each plugin (Blog, Handlers) contains its own logic that the AI can discover and extend.
- **LMS:** When the LMS module is active, AI agents will automatically scan its models and offer LMS-specific tools.

## ⚙️ Settings

Add the following to `INSTALLED_APPS` in your settings:

```python
INSTALLED_APPS = [
    # ...
    "django_grep",
    "django_grep.mcp_designer",
    # ...
]
```

Django Grep is installed from source — see the `pyproject.toml` source override:

```toml
[tool.uv.sources]
django-grep = { path = "/libs/django-grep", editable = true }
```

## Further Reading

- [Installation Guide](../INSTALL.md)
- [Settings Reference](../config/settings.md)
