# django-rseal to crafts-ai migration notes

`crafts-ai` is the target package for framework-agnostic AI and MCP code.  The
websites still use `django-rseal` for Django, Wagtail, middleware, model, and
job-dispatch runtime features.

## Import policy

Move to `crafts_ai` only when the code has no Django, Wagtail, Celery, database,
or request/response dependency:

- `django_rseal.ai.*` → `crafts_ai.ai.*`
- `django_rseal.mcp.*` → `crafts_ai.mcp_server` or future `crafts_ai.mcp.*`
- `django_rseal.workflows.orchestrator` → future `crafts_ai.orchestrator.*`

Keep in `django_rseal`:

- `django_rseal.blocks.*`
- `django_rseal.models.*`
- `django_rseal.pipelines.models.*`
- `django_rseal.middlewares.*`
- `django_rseal.services.infrastructure.jobs`

## Website usage

- CTC Research uses `django-rseal` for Wagtail blocks, models, snippets,
  processors, and middleware.
- LMS Demo uses the same shared Django package surface when matching plugins are
  enabled.
- VResume uses `django-rseal` in the accounts plugin for snippets, profile
  forms, privacy middleware, models, and Wagtail blocks.
- All websites can use `crafts-ai` for AI tasks, prompts, MCP tooling, and
  static import migration planning.

## Commands

```bash
python -m crafts_ai info
python -m crafts_ai projects
python -m crafts_ai rseal-plan applications
```
