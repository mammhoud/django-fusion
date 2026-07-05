# Unused and Duplicate Files Plan

Last updated: 2026-05-30

## Goal

Reduce duplicated website-local code without breaking imports that still point to legacy namespaces.

## Current high-risk duplicates

- `www/core/handlers/**` duplicates large parts of `plugins/accounts/**`.
- `www/apps/**` duplicates large parts of `plugins/accounts/**` and legacy `apps.*` imports.
- Site-local `node_modules/` directories should stay untracked and should not be copied into images; the Docker build already ignores `**/node_modules`.
- Generated runtime folders (`logs/`, `assets/staticfiles/`, `assets/bundles/`, caches) should remain untracked and mounted or rebuilt.

## Safe removal sequence

1. Keep `www.core` installed only for management commands such as `setup_wagtail_home`.
2. Do not install `www.apps`, `plugins.accounts`, `plugins.profile`, `plugins.products`, `plugins.lms`, or `plugins.blog` until package imports are updated away from removed `django_fusion.core.*` and `crafts_ai.http.*` paths.
3. Move actively used URL/view code to `plugins.*` or shared packages first.
4. Add import-compatibility tests before removing any legacy module.
5. Delete duplicate modules in small batches and run:
   - `uv run python manage.py --site ctc-research check`
   - `uv run python manage.py --site lms-demo check`
   - `uv run pytest tests/unit/test_notification_headers.py tests/unit/tasks/test_runtime_imports.py`

## Import modernization targets

- Replace `django_fusion.core.models` with current `django_fusion.models` exports where available.
- Replace `django_fusion.core.managers` with current `django_fusion.managers` exports where available.
- Replace `django_fusion.core.services` with current `django_fusion.services` exports where available.
- Replace `crafts_ai.http.*` imports with the current `crafts_ai.workflows.*`, `crafts_ai.services.*`, or package-documented paths.
- Keep `django_fusion` limited to tests and health/debug URLs.
