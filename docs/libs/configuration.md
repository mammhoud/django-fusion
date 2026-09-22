# Libs — Configuration & Usage

> **django-fusion:** Component system, routing, viewsets  
> **ceptor-ai:** AI assistant, MCP server, chat client

---

## django-fusion

### Installation

```bash
uv pip install -e libs/django-fusion/
```

### Key Import Paths

```python
# Routing
from django_fusion.comp.routes import Viewset, Site, Application, route

# Generic CBVs
from django_fusion.comp.generic import CreateModelView, ListModelView

# Component template tag
{% comp "contact.sections.form" block=block / %}
```

### Configuration

```python
INSTALLED_APPS = [
    "django_fusion",
]

TEMPLATES = [{
    "DIRS": [BASE_DIR / "templates"],
    "OPTIONS": {
        "loaders": [
            "django_fusion.comp.loaders.ComponentLoader",
        ],
    },
}]
```

---

## ceptor-ai

### Installation

```bash
uv pip install -e libs/ceptor-ai/
```

### Chat Client

```python
from ceptor_ai.chat.client import CeptorClient

client = CeptorClient(backend="openai", model="gpt-4o")
response = client.chat("Generate a Django view for...")
```

### MCP Server

```python
from ceptor_ai.mcp import MCPServer

server = MCPServer()
server.register_tool("search_codebase", search_handler)
server.serve()
```

---

## Related

| Resource | Path |
|----------|------|
| Libs README | [`README.md`](README.md) |
| django-fusion guide | [`django-fusion.md`](django-fusion.md) |
| AI & Agents | [`../../ai/`](../../ai/) |
