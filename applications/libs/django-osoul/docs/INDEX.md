# Structa Cloud — Documentation Index

Master index for all Structa Cloud project documentation.

## Core Documentation

| Document | Description |
|---|---|
| [websites.md](websites.md) | Website config, modules, ports, LOCAL_APPS, UNFOLD sidebar, CELERY_BEAT schedules |
| [environments.md](environments.md) | Environment types (development, demo, production), dynaconf, and settings |
| [packages.md](packages.md) | Internal packages (`django-osoul`, `ceptor-ai`), dependencies, and best practices |
| [templates.md](templates.md) | Template organization, inheritance, HTMX fragments, and usage patterns |

## Architecture

- **Workspace root**: `applications/` — shared Django workspace
- **Site modules**: `ctc-research/`, `lms-demo/`, `VResume/` — per-website application code
- **Shared configs**: `configs/` — base settings, site config, and environment management
- **Shared templates**: `assets/templates/` — cross-site template library
- **Internal libraries**: `libs/django-osoul/`, `libs/ceptor-ai/` — editable workspace packages

## Quick Reference

### Websites

| Website | Directory | Module | Port | Site ID |
|---|---|---|---|---|
| CTC Research | `ctc-research/` | LMS | 5070 | 1 |
| LMS Demo | `lms-demo/` | LMS | 5071 | 2 |
| VResume | `VResume/` | CMS | 5072 | 3 |

### Running Commands

```bash
# Django checks
cd applications && uv run ctc-research check
cd applications && uv run lms-demo check
cd applications && uv run vresume check

# Via Makefile
make check WEBSITE=ctc
make check WEBSITE=structa
make check WEBSITE=vresume

# Run dev server
make run-dev WEBSITE=ctc     # port 5070
make run-dev WEBSITE=structa  # port 5071
make run-dev WEBSITE=vresume  # port 5072

# Run tests
uv run pytest
```

### Key Files

| File | Purpose |
|---|---|
| `applications/manage.py` | Unified Django management CLI with multi-site support |
| `applications/configs/site.py` | Site environment configuration and resolution |
| `applications/configs/settings/__init__.py` | Entry point for shared settings |
| `applications/configs/base/__init__.py` | Imports all base config modules |
| `applications/configs/base/apps.py` | Shared Django app registry |
| `applications/Makefile` | Build, deploy, and development commands |
| `applications/pyproject.toml` | Package metadata and `uv` dependencies |

## Canonical Imports

One canonical-imports block per public surface, kept short so consumers can
adopt new code without scrolling through tutorials. The full API reference
for each surface lives in **[packages.md](packages.md)**.

### CRUD (`django-osoul`)

```python
from django_osoul.core.services.crud import (
    # Bulk
    bulk_create, bulk_update, bulk_delete, upsert,
    # Single-row
    get_or_create, get_by_pk, get_one, update_one, delete_one,
    # Batch dispatch
    execute_batch,
    # Primary-key introspection
    get_pk_info, normalize_pk_kwargs, get_pk_value_from_data,
    PrimaryKeyInfo,
)
```

Full reference: **[packages.md → CRUD Free Functions](packages.md#crud-free-functions-django_osoulcoreservicescrud)**

## Surface Map

| Surface | Module | Doc |
|---|---|---|
| CRUD free functions | `django_osoul.core.services.crud` | [packages.md](packages.md#crud-free-functions-django_osoulcoreservicescrud) |
| Component system | `django_osoul.comp` | [packages.md](packages.md#component-system) |
| Analyzer | `django_osoul.analyzer` | [packages.md](packages.md#analyzer-django_osoulanalyzer) |
