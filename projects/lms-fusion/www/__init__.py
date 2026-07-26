"""Shared/core Django code used by the application stack.

The `www` site (merged from `projects/shared/` and `projects/www/`) provides:
  - www.worker:  Celery task definitions, Dramatiq actors, email sending
                 (runs globally across all sites via the shared-task stack)
  - www.ci:      CI/CD utility modules for preflight checks and validation
  - www.settings.py: Django settings for the sentinel `www` site used by
                 shared-worker / shared-scheduler

Registered in `projects/configs/settings/ENV/sites.yml` and `projects/cli.py:SITES`
so shared-worker / shared-scheduler can declare `WEBSITE=shared` (resolved via
aliases) and boot without impersonating any per-site tenant (ctc-research / lms
/ VResume). The actual Django settings live at `projects/www/settings.py`.

DEV-TIME ONLY:
Production workers run with PROJECT_PATH=ctc-research baked at build time
(override-able via `TASKS_PROJECT_PATH=www` build arg — when set, the
image bake itself flips and this file's settings actually become the
runtime settings) and DJANGO_SETTINGS_MODULE=settings defaulting to
the baked site's settings. Under the default PROJECT_PATH=ctc-research,
`projects/www/settings.py` is therefore only loaded by ad-hoc CLI runs
(`python projects/www/__main__.py check`, unit tests, dev tooling).
Setting TASKS_PROJECT_PATH=www IS the runtime wiring: the
Dockerfile's `COPY projects/${PROJECT_PATH}` step bakes www/ contents
into /app/www/, which the runtime loads as the default `settings`
module (DJANGO_SETTINGS_MODULE=settings resolves to
/app/www/settings.py when /app/www/ is on sys.path).
"""
