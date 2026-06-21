# crafts-ai to crafts-ai migration notes

`crafts-ai` is the target package for framework-agnostic AI and MCP code.  The
websites still use `crafts-ai` for Django, Wagtail, middleware, model, and
job-dispatch runtime features.

## Import policy

Move to `crafts_ai` only when the code has no Django, Wagtail, Celery, database,
or request/response dependency:

- `crafts_ai.rseal.ai.*` → `crafts_ai.ai.*`
- `crafts_ai.rseal.mcp.*` → `crafts_ai.mcp_server` or future `crafts_ai.mcp.*`
- `crafts_ai.rseal.workflows.orchestrator` → future `crafts_ai.orchestrator.*`

Keep in `crafts_ai.rseal`:

- `crafts_ai.rseal.blocks.*`
- `crafts_ai.rseal.models.*`
- `crafts_ai.rseal.pipelines.models.*`
- `crafts_ai.rseal.middlewares.*`
- `crafts_ai.rseal.services.infrastructure.jobs`

## Website usage

- CTC Research uses `crafts-ai` for Wagtail blocks, models, snippets,
  processors, and middleware.
- LMS Demo uses the same shared Django package surface when matching plugins are
  enabled.
- VResume uses `crafts-ai` in the accounts plugin for snippets, profile
  forms, privacy middleware, models, and Wagtail blocks.
- All websites can use `crafts-ai` for AI tasks, prompts, MCP tooling, and
  static import migration planning.

## Commands

```bash
python -m crafts_ai info
python -m crafts_ai projects
python -m crafts_ai rseal-plan applications
```

## Deprecated compatibility namespace

The legacy `django_rseal` top-level import path now exists only as a temporary
compatibility shim in `applications/libs/crafts-ai/src/django_rseal/__init__.py`.
Do not add new code under that namespace; migrate imports to `crafts_ai.rseal`
or another explicit `crafts_ai` package.
