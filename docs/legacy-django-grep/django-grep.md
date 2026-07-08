# django-fusion Library Reference

**Location**: `libs/django-fusion/`
**Package**: `django_fusion`
**Purpose**: Generic Reusable Enhanced Pipelines — a utility library for Django/Wagtail projects providing components, pipelines, and MCP integration.

---

## Installation

```bash
# Via uv (workspace)
uv pip install -e ../libs/django-fusion

# Via pip
pip install django-fusion
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django_fusion.pipelines",
    "django_fusion.comp",
    # optional:
    "django_fusion.mcp_designer",
]
```

---

## Modules

### `django_fusion.comp` — Component System

Reusable Wagtail StreamField blocks and template tag integration.

**Key classes**:

| Class | File | Description |
|-------|------|-------------|
| `Component` | `comp/_init.py` | Base component with asset and binding support |
| `BaseBlock` | `comp/blocks/base.py` | Base StreamField block with context helpers |
| `BaseAdapter` | `comp/adapters/base.py` | Abstract adapter for request/response handling |
| `DjangoAdapter` | `comp/adapters/main.py` | Django HttpRequest adapter |
| `SimpleAdapter` | `comp/adapters/test.py` | Test adapter with configurable headers/params |

**Usage**:

```python
from wagtail.fields import StreamField
from django_fusion.comp.blocks import streamBlocks

class ContentPage(Page):
    body = StreamField(streamBlocks, use_json_field=True)
```

**Component API**:
- `get_asset(asset_filename)` — retrieve a component asset by filename
- `get_bound_component(node)` — bind component to a template block node
- `data_attribute_name` — HTML data attribute name for the component
- `id` — unique component identifier

---

### `django_fusion.pipelines` — Model Pipelines

Abstract base models and routing utilities.

**Base model `DefaultBase`** provides:
- `id` — UUID primary key
- `created_at` / `updated_at` — auto timestamps
- `created_by` / `updated_by` — audit user FKs
- `live` — boolean publish flag

**Usage**:

```python
from django_fusion.pipelines.models import DefaultBase

class MyModel(DefaultBase):
    title = models.CharField(max_length=255)
    # inherits UUID pk, timestamps, audit fields, live flag
```

---

### `django_fusion.mcp_designer` — MCP Server Integration

Model Context Protocol server for AI-assisted template and style editing.

**Capabilities**:
- Read/write Django templates safely
- Read/write SCSS/CSS style files
- Live preview generation via temporary dev server
- File patching with SEARCH/REPLACE blocks
- Webhook support for CI/CD

**Start the MCP server**:

```bash
mcp-django-server
```

---

### `django_fusion.contrib` — Utilities

Configuration and helper utilities.

- `conf.py` — unified settings management
- `helpers.py` — string manipulation, date formatting

---

## Configuration

```python
# settings.py
MCP_CREATE_BACKUPS = True
MCP_WEBHOOK_URL = None
MCP_TEMPLATE_EXTENSIONS = [".html"]
MCP_STYLE_EXTENSIONS = [".css", ".scss"]
MCP_EXTRA_TEMPLATE_DIRS = []
MCP_EXTRA_STATIC_DIRS = []
```

---

## Adapter Interface

All adapters implement `BaseAdapter`:

```python
class BaseAdapter:
    def request_headers(self) -> Mapping[str, str]: ...
    def request_params(self) -> Mapping[str, str]: ...
    def redirect_uri(self, response: Any) -> str | None: ...
    def set_redirect_uri(self, response: Any, uri: str) -> None: ...
```
