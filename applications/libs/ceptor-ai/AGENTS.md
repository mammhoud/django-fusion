# ceptor-ai Agent Instructions

Scope: this file applies to `applications/libs/ceptor-ai/`.

- Keep `ceptor_ai` framework agnostic: do not import Django, Wagtail, Celery, or
  project website modules from this package.
- Do not wrap imports in `try`/`except`; use `importlib.util.find_spec` and
  `importlib.import_module` for optional dependencies.
- Put ceptor-ai migration metadata under `ceptor_ai` only when it is
  static or framework agnostic.
- Leave Django models, Wagtail blocks, middleware, snippets, and queue dispatch
  in `ceptor-ai` until they have explicit non-Django adapters.
- Add tests for CLI output and migration classification whenever public metadata
  changes.
