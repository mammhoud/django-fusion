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
adopt new code without scrolling through tutorials. The full API reference for
each surface lives in **[packages.md](packages.md)**.

### Orchestrator (`ceptor-ai`)

```python
from ceptor_ai.orchestrator.operators import (
    OrchestratorState,
    scan_specs, load_specs,
    get_spec, get_specs_by_category, get_all_specs,
    get_tasks_by_category, get_tasks_by_status,
    filter_tasks, query_tasks,
    execute_task, execute_spec_tasks,
    get_spec_progress, get_category_summary, get_overall_summary,
    update_task_status,
    get_errors, get_warnings, get_error_summary,
    export_to_json, get_execution_history,
    get_format_compatibility_info, check_spec_format_compatibility,
)
from ceptor_ai.orchestrator.config import (
    OrchestratorConfig,
    load_from_file, load_from_env, load_from_args,
    validate_config, validate_warnings, validate_or_raise, format_summary,
)
```

Full reference: **[packages.md → Orchestrator Operators](packages.md#orchestrator-operators-ceptor_aiorchestrator)**

## Surface Map

| Surface | Module | Doc |
|---|---|---|
| Orchestrator operators | `ceptor_ai.orchestrator.operators` | [packages.md](packages.md#orchestrator-operators-ceptor_aiorchestrator) |
| Orchestrator config | `ceptor_ai.orchestrator.config` | [packages.md](packages.md#orchestrator-operators-ceptor_aiorchestrator) |
