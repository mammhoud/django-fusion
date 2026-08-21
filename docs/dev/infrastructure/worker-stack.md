# Shared Worker Stack

The active background runtime is **Dramatiq + APScheduler**. Celery, Celery
Beat, Django-Q, Django-RQ, and Temporal are not part of the active worker
stack.

## Architecture

```text
Product web services
  ├─ Precis Landing      backend/plugins/workers/
  ├─ Loop-CRM            backend/plugins/workers/
  └─ Formint Cloud       backend/plugins/workers/
          │
          └─ Redis (authenticated, common network)
                    │
          ┌─────────┴─────────┐
          │                   │
    shared-worker       shared-scheduler
    Dramatiq actors     APScheduler cron jobs
          │                   │
          └──── PostgreSQL ───┘
              shared audit DB
```

Precis/LMS remains an active product, but its product worker is deliberately
separate from the infrastructure-owned shared worker. Aggregate deploy/check
flows do not include LMS background services.

## Canonical code boundary

Every active product keeps background implementations under:

```text
projects/<product>/backend/plugins/workers/
```

`apps/tasks/` is retained only where it owns product-local `TaskExecution`
models and migrations. It is not a worker implementation directory.

Use the django-fusion API for portable tasks:

```python
from django_fusion.tasks import task


@task(queue="email", max_retries=3)
def send_notification(user_id: int):
    ...
```

The registry supports both explicit dotted modules and filesystem project
paths through `FUSION_TASK_MODULES` and `FUSION_TASK_PROJECT_PATHS`. A shared
worker can therefore load product task packages without selecting a product's
Django settings module or importing Precis/LMS task code.

## Compose deployment

The canonical stack is `application/docker-compose.tasks.yml`:

```bash
# The following command is read-only during validation; deployment is explicit.
docker compose -f application/docker-compose.tasks.yml config -q

# Start the shared stack after PostgreSQL and Redis are available.
DB_NAME=db_structa docker compose -f application/docker-compose.tasks.yml up -d
```

The worker command is:

```text
python manage.py rundramatiq --processes 2 --threads 4 \
  --queues shared,email,content,system,crm,marketing,finance,default
```

The scheduler command is:

```text
python -m django_fusion.tasks.scheduler
```

The shared stack uses the authenticated Redis broker URL in
`DRAMATIQ_BROKER_URL`. Product workers use the same broker contract with their
own database/site configuration.

## Scheduling

Scheduled tasks use a cron expression on `@task`:

```python
@task(queue="system", schedule="0 2 * * *")
def nightly_backup():
    ...
```

`django_fusion.tasks.scheduler` discovers registrations and runs them through
APScheduler. This replaces the old database-backed Celery Beat process.

## Product-specific workers

Precis/LMS has its own explicit worker and scheduler services in
`projects/precis/precis-main/docker-compose.yml` and discovers its local modules, including
`plugins.workers.campaign_tasks`. The old Temporal campaign management command
and `apps/domain/workflows/temporal/` package were removed; campaign onboarding
and batch processing are now regular Dramatiq actors.

To run the Precis worker locally:

```bash
cd projects/precis/precis-main
python backend/manage.py rundramatiq \
  --processes 2 --threads 4 --queues email,content,courses,campaigns,system,default
python backend/manage.py shell -c \
  'from plugins.workers import campaign_tasks; print("workers loaded")'
```

## Operational checks

```bash
make status-tasks
make logs-tasks

docker compose -f application/docker-compose.tasks.yml config -q
uv run pytest libs/django-fusion/tests/test_tasks.py \
  tests/websites/test_shared_tasks.py -q
```

Do not run migrations, fixture loads, volume resets, or production deployments
as a worker validation step. Confirm the target database and Redis credentials
before starting services on a shared host.

## Troubleshooting

| Symptom | Check |
|---|---|
| Worker starts with no actors | Verify `FUSION_TASK_PROJECT_PATHS`, mounted product backends, and `plugins/workers/__init__.py`. |
| Redis `NOAUTH` error | Verify `REDIS_PASSWORD` and the `DRAMATIQ_BROKER_URL` interpolation. |
| Scheduled jobs do not run | Inspect `shared-scheduler` logs and confirm APScheduler is installed. |
| LMS jobs appear in shared queues | Remove Precis from `FUSION_TASK_PROJECT_PATHS`; LMS is intentionally isolated. |
| Duplicate actor/module imports | Keep actor names unique and use the registry's explicit project-path discovery. |

## Source of truth

- `application/docker-compose.tasks.yml`
- `libs/django-fusion/src/django_fusion/tasks/`
- `projects/<product>/backend/plugins/workers/`
- `docs/plans/repository/active-monorepo-consolidation-2026-08-14.md`
