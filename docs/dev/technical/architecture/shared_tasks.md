# Shared Background Task Architecture

The monorepo uses one broker-neutral task API from `django-fusion` and Dramatiq
for production execution. HTTP servers remain product-specific; the shared
worker consumes only explicitly configured active product task packages.

## Runtime roles

| Layer | Location | Responsibility |
|---|---|---|
| Product servers | `projects/precis/precis-landing/`, `projects/loop-crm/`, `projects/formints/` | HTTP, settings, product models, task producers |
| Task API | `libs/django-fusion/src/django_fusion/tasks/` | `@task`, registry, audit logging, backend abstraction |
| Product workers | `<product>/backend/plugins/workers/` | Dramatiq actors owned by each product |
| Shared worker | `applications/docker-compose.tasks.yml` | Loads configured product paths and executes actors |
| Shared scheduler | `django_fusion.tasks.scheduler` | Publishes cron tasks to the Dramatiq broker |
| Broker | Redis database 1 | `DRAMATIQ_BROKER_URL` transport |

Precis/LMS task modules are deliberately excluded from the shared worker. They
remain available only through explicit product maintenance configuration.

## Task package contract

Every active product exposes a `plugins/workers` package with a `TASK_MODULES`
 tuple/list:

```text
backend/
├── apps/tasks/                 # optional TaskExecution model boundary
└── plugins/workers/
    ├── __init__.py             # TASK_MODULES
    └── *_tasks.py              # @task-decorated actors
```

Actors use the django-fusion API:

```python
from django_fusion.tasks import task

@task(queue="email", max_retries=3)
def send_welcome_email(user_id: int) -> None:
    ...
```

Callers enqueue with `.send(...)`. The legacy `.delay(...)` attribute is only a
small source-compatibility alias implemented by django-fusion; it does not
import or require Celery.

## Discovery and site context

The shared worker receives product backend directories through
`FUSION_TASK_PROJECT_PATHS` and may receive dotted modules through
`FUSION_TASK_MODULES`. `TaskRegistry` adds each project path to the import path,
loads its `plugins.workers` package and imports its declared child modules.

Site-specific actors should carry a serializable `website` or `site` argument
when they access product data. The worker records the site key in the shared
task audit record and does not select a product by a global default.

## Compose runtime

```bash
docker compose -f applications/docker-compose.tasks.yml config -q
DB_NAME=db_structa docker compose -f applications/docker-compose.tasks.yml up -d
```

The worker command is:

```bash
python manage.py rundramatiq \
  --processes 2 --threads 4 \
  --queues shared,email,content,system,crm,marketing,finance,default
```

The scheduler command is:

```bash
python -m django_fusion.tasks.scheduler
```

The scheduler publishes scheduled actors to Redis; it does not execute product
functions in the scheduler process. The Dramatiq worker remains the only active
consumer.

## Retired runtimes

Celery, Celery Beat, Django-Q, Django-RQ, and Temporal worker entrypoints are
not part of the active runtime. Their old settings, commands, and duplicate
worker packages have been removed. Superseded plans remain historical evidence
only and must not be used as deployment instructions.

## Operational checks

- `docker compose ... config -q` validates interpolation without starting services.
- `uv run pytest libs/django-fusion/tests/test_tasks.py tests/unit/tasks tests/websites/test_shared_tasks.py -q`
  covers registry discovery, delayed publishing, worker paths, and LMS exclusion.
- If no actors appear, verify mounted product paths and each package's
  `TASK_MODULES` before changing queues.
- If Redis reports `NOAUTH`, verify `REDIS_PASSWORD` interpolation in
  `DRAMATIQ_BROKER_URL`.
