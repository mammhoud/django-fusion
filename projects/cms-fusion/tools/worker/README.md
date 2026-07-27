# www/worker — Background Task Processing (Celery + Dramatiq)

The `worker/` package provides all background task processing for the Structa Cloud monorepo, running across all tenant websites (ctc-research, lms, VResume) through the shared-task stack.

---

## 📁 Directory Structure

```
worker/
├── __init__.py    # Exports: configure_django_for_website, import_first, TASK_MODULES
├── apps.py        # Django AppConfig — registers Dramatiq actors on app ready()
├── celery.py      # Celery application configuration
├── content.py     # Dramatiq actors for shared content operations
├── decorators.py  # Custom task decorators with Celery fallbacks
├── email.py       # Dramatiq actors for email sending (templated + raw)
├── modules.py     # Task module registry for autodiscovery
├── runtime.py     # Runtime helpers (Django config, module import)
├── tasks.py       # Celery task definitions (heartbeat, shared ops)
└── README.md      # This file
```

---

## 🎯 Use Cases

### Email Sending (`email.py`)
- Send templated emails using Django templates across any site
- Send raw emails with pre-rendered HTML
- Queue: `email`

### Content Management (`content.py`)
- Welcome email dispatch for new users
- User count queries across sites
- Queue: `default`

### Health Monitoring (`tasks.py`)
- Celery heartbeat task to verify worker health
- Shared operational tasks
- Queue: `shared`

---

## 📄 File Documentation

### `celery.py` — Celery App Bootstrap
```python
app = Celery("www.worker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```
Used by `shared-scheduler` container: `celery -A www.worker.celery:app beat`

### `email.py` — Dramatiq Email Actors
```python
@dramatiq.actor(queue_name="email", max_retries=3)
def send_templated_email(to_email, subject, template_name, context):
    """Render a Django template and send via configured email backend."""
    
@dramatiq.actor(queue_name="email", max_retries=3)
def send_raw_email(to_email, subject, html_body):
    """Send pre-rendered email without template lookup."""
```

### `tasks.py` — Celery Task Definitions
```python
@shared_task(queue="shared", bind=True)
def heartbeat():
    """Periodic health check — verifies worker is alive and processing tasks."""
```

### `runtime.py` — Runtime Helpers
- `configure_django_for_website(site_name)` — Sets up Django settings for a specific tenant
- `import_first(*module_names)` — Tries importing modules in order, returns first success

### `modules.py` — Task Module Registry
Lists all task modules for Dramatiq autodiscovery:
```python
TASK_MODULES = [
    "www.worker.email",
    "www.worker.content",
    "www.worker.tasks",
]
```

### `apps.py` — Django AppConfig
```python
class WorkerConfig(AppConfig):
    name = "www.worker"
    
    def ready(self):
        import www.worker.email  # noqa — registers Dramatiq actors
        import www.worker.content  # noqa
```

---

## 🔗 Related
- `applications/compose/docker-compose.tasks.yml` — Shared-worker + scheduler compose
- `projects/www/settings.py` — Sentinel site settings
- `docs/infrastructure/deployment.md` — Deployment guide
