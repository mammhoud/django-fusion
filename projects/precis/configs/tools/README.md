# Shared configuration tools

The background worker implementation was moved to the canonical
`projects/precis/precis-lms/backend/plugins/workers/` package. It is Dramatiq-only and
uses django-fusion's `@task` registry.

```bash
python manage.py rundramatiq --processes 2 --threads 4 --queues shared,email,content,system,crm,marketing,finance,default
python -m django_fusion.tasks.scheduler
```

The shared infrastructure actors are `heartbeat.py`, `shared_email.py`, and
`shared_content.py`. Product-specific modules are loaded from
`FUSION_TASK_PROJECT_PATHS` and each product's `plugins/workers/__init__.py`.
