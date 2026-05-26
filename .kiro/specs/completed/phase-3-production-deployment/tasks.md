# Tasks: Phase 3 — Production Deployment & Verification

## Overview

All tasks in this phase have been completed. The structa.cloud application has been built, deployed, and verified in production Docker containers.

---

- [x] 3.1 Fix structa.cloud Dockerfile — align with ctc-research pattern
  - Install venv/libs editable packages explicitly
  - Set `UV_PROJECT_ENVIRONMENT` and use `uv sync --frozen`
  - Copy rqworker-start script

- [x] 3.2 Fix structa.cloud entrypoint — add makemigrations, superuser, wagtail home, fixtures, cron
  - Add `makemigrations` + `migrate` steps
  - Add `collectstatic` step
  - Add superuser creation via `django_rseal.scripts.superuser`
  - Add Wagtail home page setup
  - Add fixture loading when `LOAD_FIXTURES=true`
  - Add cron for error reports

- [x] 3.3 Fix structa.cloud start script — correct ASGI module, clean args
  - Set ASGI module to `alliance.asgi:application`
  - Remove extraneous arguments

- [x] 3.4 Add rqworker-start script to structa.cloud compose/django/

- [x] 3.5 Add rqworker service to structa.cloud docker-compose.yml (already present)

- [x] 3.6 Build Docker images
  - Build structa.cloud Django image from `structa.cloud/compose/django/Dockerfile`
  - Build nginx media image
  - Confirm all images build without errors

- [x] 3.7 Start containers and verify health
  - Start postgres and redis infrastructure containers
  - Start website, website-media, website-worker containers
  - Confirm all containers reach Healthy_Status

- [x] 3.8 Run Django system checks inside container
  - Run `migrate --noinput` — zero unapplied migrations
  - Run `collectstatic --noinput` — all assets collected
  - Create superuser if not exists
  - Run `python manage.py check` — zero system check errors

- [x] 3.9 Run compilemessages for all locales
  - Execute `compilemessages` inside website container
  - Verify `.mo` files generated for all configured locales

- [x] 3.10 Verify health endpoints respond HTTP 200
  - `GET /health/` → HTTP 200
  - `GET /health/assets/` → HTTP 200
  - `GET /health/media/` → HTTP 200

- [x] 3.11 Verify admin panel accessible
  - `GET /admin/` → HTTP 200 or redirect to login

- [x] 3.12 Verify no tracebacks in logs
  - Confirm no Python tracebacks in any container log
  - Confirm no CRITICAL or ERROR level messages on startup

- [x] 3.13 Remove duplicated Wagtail settings — extracted to configs/base/wagtail.py

- [x] 3.14 Fix ROOT_URLCONF — core.urls → alliance.urls

- [x] 3.15 Fix WSGI/ASGI defaults — add alliance.* fallbacks
