# Sentinel `shared` site package.
#
# Registered in `core/configs/settings/ENV/sites.yml` and `core/cli.py:SITES`
# so shared-worker / shared-scheduler can declare `WEBSITE=shared` and boot
# without impersonating any per-site tenant (ctc-research / lms-demo / VResume).
# The actual Django settings live at `core/shared/settings.py`; this file is
# just the package marker.
#
# DEV-TIME ONLY:
# Production workers run with PROJECT_PATH=ctc-research baked at build time
# (override-able via `TASKS_PROJECT_PATH=shared` build arg — when set, the
# image bake itself flips and this file's settings actually become the
# runtime settings) and DJANGO_SETTINGS_MODULE=settings defaulting to
# the baked site's settings. Under the default PROJECT_PATH=ctc-research,
# `core/shared/settings.py` is therefore only loaded by ad-hoc CLI runs
# (`python core/shared/__main__.py check`, unit tests, dev tooling).
# Setting TASKS_PROJECT_PATH=shared IS the runtime wiring: the
# Dockerfile's `COPY core/${PROJECT_PATH}` step bakes shared/ contents
# into /app/shared/, which the runtime loads as the default `settings`
# module (DJANGO_SETTINGS_MODULE=settings resolves to
# /app/shared/settings.py when /app/shared/ is on sys.path).
