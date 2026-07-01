# Packages — Dependencies & Internal Libraries

This document covers the internal workspace packages, their APIs, and best practices for using them.

## Internal Packages (Editable Installs)

The workspace includes two internal packages installed as editable local sources:

| Package | Path | Import Name | Description |
|---|---|---|---|
| **django-osoul** | `libs/django-osoul/` | `django_osoul` | Django component system, analyzer, SCSS utilities |
| **ceptor-ai** | `libs/ceptor-ai/` | `ceptor_ai` | AI integration, chat, models, handlers |

Configured in `pyproject.toml`:

```toml
[tool.uv.sources]
django-osoul = { path = "libs/django-osoul", editable = true }
ceptor-ai = { path = "libs/ceptor-ai", editable = true }
```

## django-osoul

### Component System

The `django_osoul.comp` package provides a Django template component system:

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

### Analyzer (`django_osoul.analyzer`)

The analyzer app provides site analysis and monitoring:

```python
from django_osoul.analyzer.apps import AnalyzerAppConfig
```

**AppConfig**: `django_osoul.analyzer.apps.AnalyzerAppConfig`

**Tests location**: `libs/django-osoul/tests/analyzer/`

### Viewsets (`django_osoul.viewsets`)

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

### Orchestrator Operators (`ceptor_ai.orchestrator`)

Functional-style orchestrator. Everything lives in the
`ceptor_ai.orchestrator.operators` module: a single :class:`OrchestratorState`
holds the cross-cutting mutable state, and the rest of the surface is bare
functions — no god-classes, no inheritance, no fixtures needed. Pair with
`ceptor_ai.orchestrator.progress` and `ceptor_ai.orchestrator.tracker` for the
state-tracking helpers used internally by the operators; pair with
`ceptor_ai.orchestrator.config` for the `OrchestratorConfig` container and its
loader operators (no more `ConfigLoader` god-class).

**Canonical imports**

```python
from ceptor_ai.orchestrator.operators import (
    OrchestratorState,
    # Scan / load
    scan_specs, load_specs,
    # Queries
    get_spec, get_specs_by_category, get_all_specs,
    get_tasks_by_category, get_tasks_by_status,
    filter_tasks, query_tasks,
    # Execution
    execute_task, execute_spec_tasks,
    # Progress / errors / export / format
    get_spec_progress, get_category_summary, get_overall_summary,
    update_task_status,
    get_errors, get_warnings, get_error_summary,
    export_to_json, get_execution_history,
    get_format_compatibility_info, check_spec_format_compatibility,
)
```

**Operators**

| Group | Function | Purpose |
|---|---|---|
| Scan / load | `scan_specs(state, base_path=None)` | Walk a spec tree and report counts per category |
| Scan / load | `load_specs(state, base_path=None)` | Scan + parse every spec on disk; populate `state.specs` / `state.tasks` |
| Queries | `get_spec(state, category, spec_name)` | Look up a single :class:`Spec` by path |
| Queries | `get_specs_by_category(state, category)` | List every :class:`Spec` under a category |
| Queries | `get_all_specs(state)` | Flattened list of every loaded spec |
| Queries | `get_tasks_by_category(state, category)` | Tasks belonging to a category |
| Queries | `get_tasks_by_status(state, status)` | Tasks currently in a given :class:`TaskStatus` |
| Queries | `filter_tasks(state, criteria)` | Free-form criteria filter (delegates to `tracker`) |
| Queries | `query_tasks(state, criteria)` | Delegates filter to `TaskQuery.find_by_criteria` |
| Execution | `execute_task(state, task_id)` | Run one task by id |
| Execution | `execute_spec_tasks(state, category, spec_name)` | Run every task in a spec |
| Progress | `get_spec_progress(state, category, spec_name)` | Per-spec progress report |
| Progress | `get_category_summary(state, category)` | Per-category progress summary |
| Progress | `get_overall_summary(state)` | Aggregated summary across all specs |
| Progress | `update_task_status(state, task_id, new_status)` | Update one task's :class:`TaskStatus` |
| Errors | `get_errors(state)` / `get_warnings(state)` | Lists recorded by the state's error handler |
| Errors | `get_error_summary(state)` | Aggregated error counts |
| Export | `export_to_json(state, file_path)` | Dump specs + summary to a JSON file |
| Execution | `get_execution_history(state, task_id)` | Past runs for one task |
| Format | `get_format_compatibility_info(state)` | Compatibility layer metadata |
| Format | `check_spec_format_compatibility(state, spec_path)` | Validate a single spec file's format |

**State**

:class:`OrchestratorState` is a `dataclass` that owns the `scanner`, `parser`,
`executor`, `PBT executor`, `management-script runner`, `error handler`,
`recovery manager`, `compatibility layer`, and the in-memory `specs` / `tasks`
/ `status_history` collections. Construct one with a populated
:class:`OrchestratorConfig`:

```python
from ceptor_ai.orchestrator.config import OrchestratorConfig
from ceptor_ai.orchestrator.operators import OrchestratorState, load_specs

state = OrchestratorState(config=OrchestratorConfig(base_path=".kiro/specs"))
result = load_specs(state)
# {
#     "success": True,
#     "loaded": int,
#     "failed": int,
#     "total": int,
# }
```

**Companion modules**

- `ceptor_ai.orchestrator.progress` — `spec_progress_report`, `category_summary`, `overall_summary`
- `ceptor_ai.orchestrator.tracker` — task lookup / status update helpers (`get_task_by_id`, `update_task_status`, `filter_tasks`, …)
- `ceptor_ai.orchestrator.config` — module-level loader operators: `load_from_file`, `load_from_env`, `load_from_args`, `validate_config`, `validate_warnings`, `validate_or_raise`, `format_summary`

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

1. **Editable installs**: Both `django-osoul` and `ceptor-ai` use `editable = true`
2. **Tests alongside source**: Tests live in `libs/<package>/tests/`
3. **Import convention**: Use the public import name (`django_osoul`, `ceptor_ai`)
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
