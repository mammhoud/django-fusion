# Shared configuration tools

Worker implementations are maintained in the product package
`projects/precis/backend/plugins/workers/`. The infrastructure stack is
Dramatiq-only and schedules periodic jobs with APScheduler.

```bash
python manage.py rundramatiq --processes 2 --threads 4 --queues shared,email,content,system,crm,marketing,finance,default
python -m django_fusion.tasks.scheduler
```
