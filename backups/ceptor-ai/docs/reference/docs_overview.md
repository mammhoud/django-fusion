# ceptor-ai to ceptor-ai migration notes

`ceptor-ai` is the target package for framework-agnostic AI and MCP code.  The
websites still use `ceptor-ai` for Django, Wagtail, middleware, model, and
job-dispatch runtime features.

## Import policy

Move to `ceptor_ai` only when the code has no Django, Wagtail, Celery, database,
or request/response dependency:

- `ceptor_ai.ai.*` → `ceptor_ai.ai.*`
- `ceptor_ai.mcp.*` → `ceptor_ai.mcp_server` or future `ceptor_ai.mcp.*`
- `ceptor_ai.workflows.orchestrator` → `ceptor_ai.orchestrator.*` (migrated; legacy path removed)

Keep in `ceptor_ai`:

- `ceptor_ai.blocks.*`
- `ceptor_ai.models.*`
- `ceptor_ai.middlewares.*`
- `ceptor_ai.services.infrastructure.jobs`

## Website usage

- CTC Research uses `ceptor-ai` for Wagtail blocks, models, snippets,
  processors, and middleware.
- LMS Demo uses the same shared Django package surface when matching plugins are
  enabled.
- VResume uses `ceptor-ai` in the accounts plugin for snippets, profile
  forms, privacy middleware, models, and Wagtail blocks.
- All websites can use `ceptor-ai` for AI tasks, prompts, MCP tooling, and
  static import migration planning.

## Commands

```bash
python -m ceptor_ai info
python -m ceptor_ai projects
python -m ceptor_ai rseal-plan applications
```

## Deprecated compatibility namespace

The legacy `ceptor_ai` top-level import path now exists only as a temporary
compatibility shim in `applications/libs/ceptor-ai/src/ceptor_ai/__init__.py`.
Do not add new code under that namespace; migrate imports to `ceptor_ai`
or another explicit `ceptor_ai` package.
