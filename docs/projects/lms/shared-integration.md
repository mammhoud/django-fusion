# Shared WWW — How Django Sites Use the Worker Stack

> All Django sites (CTC Research, LMS, Portfolio, Cypercloud) share the same background task infrastructure via `projects/www/worker/`.

---

## Architecture

```
Django Site (ctc-research / lms / portfolio / cypercloud)
    │
    │  Celery.send_task() / Dramatiq.send()
    ▼
┌─────────────────────────────────────────┐
│  shared-worker (Dramatiq)               │
│  shared-scheduler (Celery Beat)         │
│  ─────────────────────────────────────  │
│  Email dispatch     → email.py          │
│  Content management → content.py        │
│  Heartbeat          → tasks.py          │
│  Templated emails   → email.py          │
└─────────────────────────────────────────┘
    │
    ▼
  Redis (broker) → PostgreSQL (results)
```

---

## Task Modules

| Module | Tasks | Used By |
|--------|-------|---------|
| `email.py` | `send_templated_email`, `send_raw_email` | All Django sites |
| `content.py` | Content management actors | LMS, CTC Research |
| `tasks.py` | Heartbeat, health checks | All Django sites |

## How Sites Use the Worker

Each Django site queues tasks through the shared worker without any site-specific configuration:

```python
# Any site can dispatch tasks
from www.worker.email import send_templated_email

send_templated_email.send(
    template_name="enrollment_confirmation",
    context={"user": user, "course": course},
    recipient=user.email,
)
```

The worker routes tasks to the correct site's database via `configure_django_for_website()`:

```python
# modules.py — autodiscovery configures Django per-task
def configure_django_for_website(website_name: str):
    os.environ["WEBSITE"] = website_name
    django.setup()
```

## Registration

New task modules are registered in `projects/www/worker/modules.py`:

```python
TASK_MODULES = [
    "www.worker.email",
    "www.worker.content",
    "www.worker.tasks",
]
```

## Docker Configuration

```yaml
# docker-compose.tasks.yml
shared-worker:
  environment:
    - WEBSITE=shared
    - DB_NAME=db_ctc
  volumes:
    - ./www/worker:/app/www/worker  # Hot-reload task code
```

---

## Related

| Resource | Path |
|----------|------|
| LMS site docs | [`README.md`](README.md) |
| WWW shared core | [`../www/README.md`](../www/README.md) |
| Infrastructure | [`../../infrastructure/`](../../infrastructure/) |
