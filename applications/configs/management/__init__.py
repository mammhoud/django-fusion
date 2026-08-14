"""Shared/core worker, CI, and settings for the application stack.

This package (formerly `projects/www/`) provides the shared worker and CI
infrastructure used across all Structa Cloud sites:
  - plugins/workers: Dramatiq actors and email sending
                     (runs globally via the shared-task stack)
  - tools.ci:      CI/CD utility modules for preflight checks and validation
  - tools.settings.py: Django settings for the sentinel `www` site used by
                 shared-worker / shared-scheduler

Registered in `projects/cli.py:SITES` so shared-worker / shared-scheduler can
declare `WEBSITE=shared` (resolved via aliases) and boot without impersonating
any per-site tenant (ctc-research / lms / VResume / lms-fusion / cms-fusion).
The actual Django settings live at `projects/tools/settings.py`.

DEV-TIME ONLY:
Production workers run with PROJECT_PATH=ctc-research baked at build time
(override-able via `TASKS_PROJECT_PATH=tools` build arg). Under the default
PROJECT_PATH=ctc-research, `projects/tools/settings.py` is only loaded by
ad-hoc CLI runs (`python projects/tools/__main__.py check`, unit tests,
dev tooling). Setting TASKS_PROJECT_PATH=tools bakes tools/ contents into
/app/www/ (the Docker image path is `/app/www/` regardless of source dir).
"""
