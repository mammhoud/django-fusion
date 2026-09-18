# Shared management configuration

The shared worker runtime is owned by `projects/structa.cloud/backend/plugins/workers/`.
Dramatiq consumes all queues and APScheduler runs `@task(schedule=...)` jobs.
There is no Celery app or Celery Beat process in the active stack.

```bash
python manage.py rundramatiq --processes 2 --threads 4 --queues shared,email,content,system,crm,marketing,finance,default
python -m django_fusion.tasks.scheduler
```

Use `FUSION_TASK_PROJECT_PATHS` to load product `plugins/workers` packages
without importing retired product task trees.
