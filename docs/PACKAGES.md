# Packages — Dependencies & Internal Libraries

This document covers the internal workspace packages, their APIs, and best practices for using them.

## Internal Packages (Editable Installs)

The workspace includes two internal packages installed as editable local sources:

| Package | Path | Import Name | Description |
|---|---|---|---|
| **django-fusion** | `libs/django-fusion/` | `django_fusion` | Django component system, analyzer, SCSS utilities |
| **ceptor-ai** | `libs/ceptor-ai/` | `ceptor_ai` | AI integration, chat, models, handlers |

Configured in `pyproject.toml`:

```toml
[tool.uv.sources]
django-fusion = { path = "libs/django-fusion", editable = true }
ceptor-ai = { path = "libs/ceptor-ai", editable = true }
```

## django-fusion

### Component System

The `django_fusion.comp` package provides a Django template component system:

```django
{% load components %}

{% comp "card" title="Hello" %}
  <p>Card content here</p>
{% endcomp %}
```

**Template tags** (registered as builtins):
- `{% comp "name" %}` — Render a component
- `{% slot "name" %}` — Define a slot inside a component
- `{% prop "name" %}` — Access a prop value
- `{% var "name" %}` — Define a template variable
- `{% css "path" %}` — Include component CSS
- `{% js "path" %}` — Include component JavaScript

### Analyzer (`django_fusion.analyzer`)

The analyzer app provides site analysis and monitoring:

```python
from django_fusion.analyzer.apps import AnalyzerAppConfig
```

**AppConfig**: `django_fusion.analyzer.apps.AnalyzerAppConfig`

**Tests location**: `libs/django-fusion/tests/analyzer/`

### Viewsets (`django_fusion.viewsets`)

Reusable Django REST/ViewSet patterns. See `DJANGO_OSOUL_VIEWSETS.md` for detailed API.

### CRUD Free Functions (`django_fusion.core.services.crud`)

Functional-style CRUD on Django models. The freestanding functions mirror
:class:`CRUDService` and :class:`BatchCRUDService`. New code should prefer
calling the functions directly — they compose well, don't require
instantiating a service, and skip the model-introspection overhead on the hot
path. The service classes remain as thin facades for backwards compatibility.

**Canonical imports**

```python
from django_fusion.core.services.crud import (
    # Bulk operations
    bulk_create, bulk_update, bulk_delete, upsert,
    # Single-row operations
    get_or_create, get_by_pk, get_one, update_one, delete_one,
    # Batch dispatch
    execute_batch,
    # Primary-key introspection
    get_pk_info, normalize_pk_kwargs, get_pk_value_from_data,
    PrimaryKeyInfo,
)
```

**Functions**

| Group | Function | Purpose |
|---|---|---|
| Bulk | `bulk_create(model, objects_data, batch_size=1000)` | Insert rows in batches; returns `(success, created_objs, message)` |
| Bulk | `bulk_update(model, objects, update_fields, batch_size=1000)` | Update rows with explicit field list; returns `(success, count, message)` |
| Bulk | `bulk_delete(model, identifiers, field=None)` | Delete rows whose `field` value matches; returns `(success, count, message)` |
| Bulk | `upsert(model, data, match_fields=None, update_fields=None)` | Update if `match_fields` matches, otherwise create; returns `(success, obj, message)` |
| Single-row | `get_or_create(model, defaults=None, **kwargs)` | `Model.objects.get_or_create` with `id` / `uuid` aliases; returns `(obj, created)` |
| Single-row | `get_by_pk(model, value)` | Look up one row by PK; returns `None` on miss |
| Single-row | `get_one(model, identifier=None, **kwargs)` | Alias for `get_first` (kept for historical imports) |
| Single-row | `get_first(model, identifier=None, **kwargs)` | `filter().first()` with PK aliases |
| Single-row | `update_one(model, identifier, data, **kwargs)` | Save a partial update to one row |
| Single-row | `delete_one(model, identifier, **kwargs)` | Delete one row by PK |
| Batch dispatch | `execute_batch(model, operations)` | Run a list of `create` / `update` / `delete` ops sequentially |
| PK introspection | `get_pk_info(model)` | Resolve PK name + type (`'id'` or `'uuid'`) |
| PK introspection | `normalize_pk_kwargs(model, kwargs)` | Map `id` / `uuid` aliases to the actual PK field |
| PK introspection | `get_pk_value_from_data(model, data)` | Extract the PK value from a data dict |

**Common usage**

```python
from django_fusion.core.services.crud import (
    bulk_create, get_first, upsert, delete_one,
)

# Bulk insert
ok, articles, msg = bulk_create(Article, [{"title": "a"}, {"title": "b"}])

# Fetch by primary key (PK alias 'id' or 'uuid' is auto-routed)
article = get_first(Article, id=42)

# Upsert
ok, article, msg = upsert(Article, {"title": "Hi", "id": 42}, match_fields=["id"])

# Delete
delete_one(Article, 42)
```

**Backwards-compatible service classes**

```python
# Works as before — thin facade over the free functions.
from django_fusion.core.services import CRUDService, BatchCRUDService

service = CRUDService(Article)
service.bulk_create([{"title": "Hi"}])
batch = BatchCRUDService(Article)
batch.execute_batch([{"type": "create", "data": {"title": "x"}}])
```

Use the service wrappers only when you need to preserve an existing
plugin / subclass override surface; prefer the bare functions for new code.

## ceptor-ai

### Model Integration

`ceptor_ai` provides AI model integration across all websites:

```python
# In settings.py
PROFILE_MODEL = "auth.User"  # Required ForeignKey target
```

### Key Requirements
- `PROFILE_MODEL` must be set before Django loads model classes
- Set in both `configs/base/auth.py` (base level) and each site's `settings.py`
- Defaults to `auth.User` (Django's built-in User model)

### App Configuration

```python
INSTALLED_APPS += ["ceptor_ai"]
```

## External Dependencies

### Core Framework

| Package | Version | Purpose |
|---|---|---|
| Django | >=4.2 | Web framework |
| Wagtail | >=7.4.2 | CMS |
| Gunicorn | — | WSGI server |
| Uvicorn | — | ASGI server |

### Authentication

| Package | Purpose |
|---|---|
| django-allauth | Authentication, social auth, MFA |
| fido2 | WebAuthn/FIDO2 support |

### Admin & UI

| Package | Purpose |
|---|---|
| django-unfold | Modern admin theme |
| django-heroicons | Heroicons template tags |
| django-htmx | HTMX integration |
| django-bird | UI components |
| django-colorfield | Color picker field |
| django-crispy-forms | Form rendering |
| django-webpack-loader | Webpack integration |
| django-tables2 | Data tables |

### Data & Storage

| Package | Purpose |
|---|---|
| psycopg / psycopg-binary | PostgreSQL driver |
| django-redis | Redis cache backend |
| django-storages | Cloud storage (S3) |
| django-embed-video | Video embedding |
| django-import-export | Data import/export |
| django-simple-history | Model history tracking |

### Task Queue

| Package | Purpose |
|---|---|
| celery[redis] | Distributed task queue |
| django-celery-beat | Periodic task scheduler |
| django-celery-results | Task result storage |
| django-rq | Redis Queue integration |

### Payments

| Package | Purpose |
|---|---|
| django-paypal | PayPal integration |
| stripe | Stripe payments |

### Monitoring & Logging

| Package | Purpose |
|---|---|
| sentry-sdk[django] | Error monitoring |
| django-structlog | Structured logging |
| django-debug-toolbar | Debug panel |
| django-silk | Request profiling |
| django-extensions | Dev utilities |

### Development Tools

| Package | Purpose |
|---|---|
| pytest + pytest-django | Testing |
| hypothesis | Property-based testing |
| bumpver | Version management |
| django-stubs | Type stubs |
| watchfiles | File watching |
| livereload | Browser reload |

## Installing Packages

```bash
# Add a new package
cd applications
uv add <package-name>

# Install all dependencies
uv sync

# Install with dev dependencies
uv sync --group dev

# Run a command in the uv environment
uv run <command>
```

## Package Best Practices

### Adding New Dependencies

1. **Check existing usage**: Search the codebase for similar functionality
2. **Use `uv add`**: Never manually edit `pyproject.toml` version strings
3. **Pin versions**: Only when a specific version is required for compatibility
4. **Document**: Add the package to this document with its purpose

### Internal Library Development

1. **Editable installs**: Both `django-fusion` and `ceptor-ai` use `editable = true`
2. **Tests alongside source**: Tests live in `libs/<package>/tests/`
3. **Import convention**: Use the public import name (`django_fusion`, `ceptor_ai`)
4. **Avoid circular imports**: Internal libs should not import from site-specific code

### Template Dependencies

Templates use the following pattern for optional dependencies:

```python
import importlib.util

if importlib.util.find_spec("heroicons") is not None:
    TEMPLATE_BUILTINS.append("heroicons.templatetags.heroicons")
```

This ensures templates work even when optional packages aren't installed.

## pyproject.toml Structure

```toml
[project]
name = "websites-workspace"
version = "1.0.3"
requires-python = ">=3.11"

[tool.uv.sources]      # Local editable packages
[tool.pytest.ini_options]  # Test configuration
[tool.bumpver]         # Version management
[tool.hatch.build]     # Build configuration
```

## See Also
- [websites.md](websites.md) — Website-specific package usage
- [environments.md](environments.md) — Environment configuration
- [templates.md](templates.md) — Template best practices
