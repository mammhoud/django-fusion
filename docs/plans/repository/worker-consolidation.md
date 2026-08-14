# Worker Consolidation Plan

> **Lifecycle:** Superseded historical design — reviewed 2026-08-14
> **Current source of truth:** [`active-monorepo-consolidation-2026-08-14.md`](active-monorepo-consolidation-2026-08-14.md)

The original Celery/LMS-inclusive design below is retired. The implementation now
uses Dramatiq for asynchronous work and APScheduler for cron registration through
the django-fusion task API.

## Completed

- Removed Celery, Django-Q, RQ, Celery Beat, and Temporal worker runtime paths.
- Moved active product workers to each product's `backend/plugins/workers/`
  package; `apps/tasks/` remains only where it owns task-history models and
  migrations.
- Added filesystem and dotted-module discovery to
  `django_fusion.tasks.TaskRegistry`.
- Added a site-neutral `shared-worker` and `shared-scheduler` in
  `applications/docker-compose.tasks.yml`.
- Excluded Precis/LMS worker paths from the shared worker and from aggregate
  project deploy/check loops. Explicit Precis maintenance commands remain
  available.
- Migrated the former Precis Temporal campaign flow to
  `plugins.workers.campaign_tasks` Dramatiq actors.
- Replaced the old per-site worker scripts and compose commands with
  `python manage.py rundramatiq` and `python -m django_fusion.tasks.scheduler`.

## Current runtime contract

```text
HTTP product code
  -> django_fusion.tasks @task wrapper
  -> Redis (DRAMATIQ_BROKER_URL, database 1)
  -> shared-worker (Dramatiq actors)

APScheduler scheduler
  -> publishes scheduled actors to Redis
  -> shared-worker executes them
```

The shared worker receives active product backend paths through
`FUSION_TASK_PROJECT_PATHS`. It does not infer a tenant from the default Django
settings module and does not mount Precis/LMS task modules.

```bash
# Read-only Compose validation
Docker compose -f applications/docker-compose.tasks.yml config -q

# Start only after the database and Redis services are available
DB_NAME=db_structa docker compose -f applications/docker-compose.tasks.yml up -d
```

## Deprecated paths

| Retired item | Replacement |
|---|---|
| `celery -A ... worker` | `python manage.py rundramatiq` |
| Celery Beat | `python -m django_fusion.tasks.scheduler` |
| `applications/configs/*/worker` | Product `backend/plugins/workers` packages |
| `apps/tasks/*_tasks.py` implementations | `plugins/workers/*_tasks.py` |
| Precis Temporal campaign command | `plugins.workers.campaign_tasks` |
| Aggregate LMS queue | Explicit Precis maintenance only; never shared discovery |

This document is retained as migration evidence. Do not copy its former queue
commands or paths into new deployments. No production database, volume, or
service is modified by documentation updates.
