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
