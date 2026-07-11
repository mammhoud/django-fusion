# Structa Cloud — Documentation Index

Master index for all Structa Cloud project documentation.

## Core Documentation

| Document | Description |
|---|---|
| [websites.md](websites.md) | Website config, modules, ports, LOCAL_APPS, UNFOLD sidebar, CELERY_BEAT schedules |
| [environments.md](environments.md) | Environment types (development, demo, production), dynaconf, and settings |
| [packages.md](packages.md) | Internal packages (`django-fusion`, `ceptor-ai`), dependencies, and best practices |
| [templates.md](templates.md) | Template organization, inheritance, HTMX fragments, and usage patterns |
| [../CHANGELOG.md](../CHANGELOG.md) | Full change history for the workspace |

## Architecture

- **Workspace root**: `core/` — shared Django workspace
- **Site modules**: `ctc-research/`, `lms-demo/`, `VResume/` — per-website application code
- **Shared configs**: `configs/` — base settings, site config, and environment management
- **Shared templates**: `assets/templates/` — cross-site template library
- **Internal libraries**: `libs/django-fusion/`, `libs/ceptor-ai/` — editable workspace packages

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
| `core/manage.py` | Unified Django management CLI with multi-site support |
| `core/configs/site.py` | Site environment configuration and resolution |
| `core/configs/settings/__init__.py` | Entry point for shared settings |
| `core/configs/base/__init__.py` | Imports all base config modules |
| `core/configs/base/apps.py` | Shared Django app registry |
| `core/Makefile` | Build, deploy, and development commands |
| `core/pyproject.toml` | Package metadata and `uv` dependencies |
