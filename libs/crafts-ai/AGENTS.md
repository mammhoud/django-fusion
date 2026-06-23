# crafts-ai Agent Instructions

Scope: this file applies to `applications/libs/crafts-ai/`.

- Keep `crafts_ai` framework agnostic: do not import Django, Wagtail, Celery, or
  project website modules from this package.
- Do not wrap imports in `try`/`except`; use `importlib.util.find_spec` and
  `importlib.import_module` for optional dependencies.
- Put crafts-ai migration metadata under `crafts_ai` only when it is
  static or framework agnostic.
- Leave Django models, Wagtail blocks, middleware, snippets, and queue dispatch
  in `crafts-ai` until they have explicit non-Django adapters.
- Add tests for CLI output and migration classification whenever public metadata
  changes.
