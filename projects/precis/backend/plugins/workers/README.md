# `plugins.workers` — Dramatiq workers

All active background work is registered through `django_fusion.tasks` and
runs on the shared Redis-backed Dramatiq broker. Celery, Celery Beat, Django-Q,
and Django-RQ are not runtime dependencies.

## Layout

- `apps.py` — shared infrastructure `AppConfig`.
- `heartbeat.py` — scheduled scheduler heartbeat.
- `shared_email.py` / `shared_content.py` — site-neutral infrastructure actors.
- `email_tasks.py`, `content_tasks.py`, `course_tasks.py` — Precis product jobs.
- `legacy_email_tasks.py` — migrated Precis email queue jobs.
- `campaign_tasks.py` — Dramatiq replacement for the retired Temporal campaign worker.
- `runtime.py` — per-site Django import helpers.
- `modules.py` — shared infrastructure module list.

Other active products use the same package boundary:

```text
projects/<product>/backend/plugins/workers/*.py
```

The shared worker discovers product modules from `FUSION_TASK_PROJECT_PATHS`.
Each package may expose `TASK_MODULES` from `plugins.workers.__init__`.

## Run

```bash
python manage.py rundramatiq --processes 2 --threads 4 --queues shared,email,content,system,crm,marketing,finance,default
python -m django_fusion.tasks.scheduler
```

Scheduled jobs use `@task(schedule="minute hour day month weekday")`; the
APScheduler process replaces the old Celery Beat database scheduler.
