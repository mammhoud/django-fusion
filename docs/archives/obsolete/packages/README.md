# Shared packages

The reusable Python packages live in `core/libs/` as editable submodules. They are
first-class libraries, not copies of site code:

| Package | Role | Framework boundary | Primary docs |
|---|---|---|---|
| [`django-fusion`](django-fusion/README.md) | Django/Wagtail components, routing, forms, and shared site primitives | Django-aware; keep site-specific behavior in adapters | [`README`](django-fusion/README.md), [`usage`](django-fusion/usage.md) |
| [`ceptor-ai`](https://github.com/mammhoud/ceptor-ai) | Standalone AI, orchestration, CLI, and optional MCP metadata service | `ceptor_ai` must not import Django or Wagtail | `core/libs/ceptor-ai/README.md`, [`AI start here`](../ai/START_HERE.md) |

Third-party library notes are under [`docs/libs/`](../libs/README.md). This page
covers the two maintained internal packages only.

## Install from this monorepo

Run from `/home/structa.cloud` (or the repository root):

```bash
uv pip install -e core/libs/django-fusion/
uv pip install -e core/libs/ceptor-ai/
# Add MCP dependencies only when the local HTTP app is needed:
uv pip install -e 'core/libs/ceptor-ai/[mcp]'
```

The submodules must be initialized first in a fresh checkout:

```bash
git submodule update --init --recursive
```

## Dependency direction

```text
site applications ──► django-fusion
site applications ──► ceptor-ai (only through an explicit integration boundary)
ceptor-ai ──────────► optional django-fusion discovery at runtime
```

`django-fusion` is the Django-aware foundation. `ceptor-ai` can be imported and
used for CLI/MCP metadata without Django being configured. Do not reverse these
boundaries by adding site models, settings, Wagtail, Celery, or database imports
to the pure-Python AI surface.

## AI and MCP quick checks

```bash
python -m ceptor_ai info
python -m ceptor_ai health
PYTHONPATH=core/libs/ceptor-ai/src \
  uvicorn ceptor_ai.mcp_server:app --host 127.0.0.1 --port 8002
curl http://127.0.0.1:8002/health
```

The Kilo configuration in `applications/kilo/config.json` uses the same command
and port. See [`docs/ai/mcp_reference.md`](../ai/mcp_reference.md) for endpoint
semantics, setup prompts, and troubleshooting.

## Choosing the right package

- Need `{% comp %}`, viewsets, forms/tables, or Wagtail integration? Use
  `django-fusion` and follow its canonical import paths.
- Need provider-agnostic AI helpers, orchestration, CLI metadata, or an optional
  local MCP app? Use `ceptor-ai`.
- Need site-specific behavior? Add a thin adapter in the site application and
  keep the reusable package generic.

## Validation

After a package change, run the narrowest package tests first:

```bash
cd core/libs/django-fusion && uv run pytest
cd core/libs/ceptor-ai && uv run pytest
```

When a package is consumed by a site, also run the relevant delegated checks from
`core/Makefile` and update both package docs and the AI attachment set when the
public surface changes.
