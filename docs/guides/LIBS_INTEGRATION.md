# Internal libraries integration guide

This guide covers the maintained reusable packages in `core/libs/`. Both are
editable submodules and must be treated as first-class packages rather than
copied into a site.

## Package map and boundaries

```text
site applications ──► django-fusion
site applications ──► ceptor-ai (explicit integration boundary)
ceptor-ai ──────────► optional django-fusion discovery
```

| Package | Location | Responsibility | Do not put here |
|---|---|---|---|
| `django-fusion` | `core/libs/django-fusion/` | Django/Wagtail components, routing, forms/tables, viewsets, middleware, health checks | AI provider calls, site models, credentials |
| `ceptor-ai` | `core/libs/ceptor-ai/` | AI helpers, orchestration, CLI, and optional MCP metadata | Django/Wagtail/Celery/database imports in its standalone surface |

The package names and import names are intentionally different:

```text
distribution: django-fusion  → import: django_fusion
distribution: ceptor-ai      → import: ceptor_ai
```

## Installation

From `/home/structa.cloud`:

```bash
git submodule update --init --recursive
uv pip install -e core/libs/django-fusion/
uv pip install -e core/libs/ceptor-ai/
```

Install the optional MCP dependencies only for local MCP work:

```bash
uv pip install -e 'core/libs/ceptor-ai/[mcp]'
```

Do not document or introduce the historical `libs/` or `venv/libs/` paths in new
code. The canonical paths are always under `core/libs/`.

## django-fusion integration

Use django-fusion for reusable Django-aware infrastructure:

- `{% comp %}` components, props, slots, attributes, and fragment scoping
- `Site`, `Application`, `Viewset`, `ModelViewset`, and fragment routing
- forms/tables mixins and shared validators
- middleware, auth adapters, health checks, and Wagtail integration

Read the package's numbered docs for the public API:

- `core/libs/django-fusion/docs/01-getting-started.md`
- `core/libs/django-fusion/docs/04-component-tag.md`
- `core/libs/django-fusion/docs/05-routing.md`
- `core/libs/django-fusion/docs/09-health.md`
- `core/libs/django-fusion/docs/10-wagtail-integration.md`

Use canonical imports from the package docs. Keep site-specific behavior in a
thin wrapper or adapter inside `core/<site>/`, so the library remains reusable.
For a new component, first search shared templates and existing component
registrations before adding another implementation.

Example component usage:

```django
{% load fusion_tags %}
{% comp "components/button.html" label="Save" variant="primary" / %}
```

Example site adapter:

```python
from django_fusion.managers import GroupAccessControl


class SiteAccess:
    """Site policy wrapper; reusable permission logic stays in django-fusion."""

    @staticmethod
    def can_edit(user) -> bool:
        return GroupAccessControl.check_group_access(user, ["editors", "admins"])
```

## ceptor-ai integration

Use ceptor-ai for provider-agnostic AI helpers, orchestration, CLI metadata, and
an optional local MCP app. The package can be imported without Django settings.
Start with:

```bash
python -m ceptor_ai info
python -m ceptor_ai health
```

The optional MCP app is:

```bash
PYTHONPATH=core/libs/ceptor-ai/src \
  uvicorn ceptor_ai.mcp_server:app --host 127.0.0.1 --port 8002
```

Smoke-test it from another terminal:

```bash
curl --fail http://127.0.0.1:8002/health
curl --fail http://127.0.0.1:8002/features
curl --fail http://127.0.0.1:8002/file-structure
```

MCP is metadata-only today. Keep it loopback-only and do not add shell
execution, file writes, database mutations, or secrets to responses. The full
setup prompt and endpoint contract are in [`docs/ai/mcp_reference.md`](../ai/mcp_reference.md).

### Django boundary

A site may adapt ceptor-ai in an explicit Django integration module, but the
standalone `ceptor_ai` package must not import Django, Wagtail, Celery, settings,
or site modules. Optional package detection must remain lazy:

```python
from importlib import import_module, util


def optional_module(name: str):
    if util.find_spec(name) is None:
        return None
    return import_module(name)
```

Do not add `ceptor_ai` to `INSTALLED_APPS` unless the package's current README
explicitly documents a Django app surface for that release. The CLI and MCP
metadata workflow does not require Django configuration.

## AI-assisted change workflow

Use this prompt when asking an agent to change either package:

> Read the root and nested `AGENTS.md` files, identify whether the target is
> `core/libs/django-fusion` or `core/libs/ceptor-ai`, and inspect the package
> README, `PROMPTS.md`, and relevant numbered docs before editing. Preserve the
> package boundary and canonical import paths. For MCP work, use
> `ceptor_ai.mcp_server:app` on `127.0.0.1:8002`, verify `/health` and
> `/features`, and do not expose secrets or add mutations. Report the narrowest
> package test and any site checks needed before making changes.

The package prompt references are:

- `core/libs/django-fusion/PROMPTS.md` (`DF-*` docs)
- `core/libs/ceptor-ai/PROMPTS.md` (`CA-*` docs)
- `applications/kilo/commands/ceptor-ai.md` (Kilo workflow)

## Testing and release checklist

### django-fusion

```bash
cd core/libs/django-fusion
uv run pytest
```

### ceptor-ai

```bash
cd core/libs/ceptor-ai
uv run pytest
uv run pytest tests/test_mcp_metadata.py
```

For a package change consumed by a site, run the narrowest delegated check from
`core/Makefile` for that site. Before release or submodule updates:

1. Update the package changelog and relevant numbered docs.
2. Update `PROMPTS.md` when an AI task or public workflow changes.
3. Update `docs/ai/latest_features.md` and `docs/ai/mcp_reference.md` for MCP
   surface changes.
4. Commit the library repository, then update the parent submodule pointer.
5. Record the tested commit in the parent change description.

## Related references

- [`docs/packages/README.md`](../packages/README.md)
- [`docs/libs/README.md`](../libs/README.md)
- [`docs/ai/START_HERE.md`](../ai/START_HERE.md)
- [`docs/ai/mcp_reference.md`](../ai/mcp_reference.md)
- [`AGENTS.md`](../../AGENTS.md)
