# projects/www — Shared Core Application Code

The `www/` directory (merged from the former `projects/shared/` and `projects/www/`) contains all shared/core Django application code used by the Structa Cloud monorepo. It serves as the **sentinel site** for the shared-task worker stack (shared-worker + shared-scheduler) running Celery + Dramatiq across all tenant websites.

---

## 📁 Project Tree

```
www/
├── __init__.py              # Package marker; docs about the merged sentinel site
├── __main__.py              # CLI entry point: `python www/__main__.py check`
├── settings.py              # Django settings for the sentinel `www` site
├── README.md                # This file
│
├── ci/                      # CI/CD preflight and validation utilities
│   ├── __init__.py
│   └── utils.py             # Shared CI helpers used by deploy-preflight actions
│
└── worker/                  # Background task processing (Celery + Dramatiq)
    ├── __init__.py           # Exports: configure_django_for_website, TASK_MODULES
    ├── apps.py               # Django AppConfig — registers Dramatiq actors on ready()
    ├── celery.py             # Celery application config for www.worker
    ├── content.py            # Dramatiq actors for shared content (user counts, welcome)
    ├── decorators.py         # Custom task decorators (shared_task, fallback no-ops)
    ├── email.py              # Dramatiq actors for email sending (templated + raw)
    ├── modules.py            # Task module registry (autodiscovery list)
    ├── runtime.py            # Runtime helpers (configure_django_for_website, import_first)
    └── tasks.py              # Celery task definitions (heartbeat, shared ops)
```

---

## 🎯 Use Cases

### 1. Sentinel Site for Task Workers

The `www` site is registered in `sites.yml` as `shared` (with aliases including `shared`, `shared-worker`, `shared-scheduler`, `tasks`, `www`). When the shared-task stack boots:

```yaml
# docker-compose.tasks.yml sets:
DJANGO_SITE=shared    # resolves via alias → site config → path: www
WEBSITE=shared
```

The `www/settings.py` is loaded as the Django settings module, which configures the environment without any tenant-specific overrides. This allows the shared-worker to route tasks to **any** site's queue without impersonating that site.

### 2. Background Task Processing

| Task Module | Technology | Purpose |
|-------------|-----------|---------|
| `www/worker/email.py` | Dramatiq | Send templated/raw emails for any site |
| `www/worker/content.py` | Dramatiq | Content management tasks (user counts, welcome) |
| `www/worker/tasks.py` | Celery | Heartbeat monitoring, shared operations |
| `www/worker/celery.py` | Celery | Celery app bootstrap (beat scheduler, autodiscovery) |

### 3. CI/CD Preflight Validation

`www/ci/utils.py` provides shared helper functions used by the deploy-preflight GitHub Action and local `make deploy-preflight` commands.

---

## 🔧 Key Files Documentation

### `settings.py` — Django Configuration for Sentinel Site

```python
# Configures sys.path so that:
#   - projects/ is at sys.path[0]
#   - projects/www/ is also on sys.path
# Then imports from configs.settings (shared Django settings)
# and overrides WEBSITE_NAME = "www"
```

**Key differences from per-site settings.py:**
- No `_SITE_APP_DIR = _SITE_DIR / "www"` — adding this would block `www.core` and `www.worker` imports
- No `LOCAL_APPS` appended — the `www.worker` app is registered globally in `configs/base/apps.py`

**Runtime resolution:**
- Dev: `python projects/www/__main__.py check` → loads `www/settings.py`
- Docker (default): `PROJECT_PATH=fusion-cms` → loads `fusion-cms/settings.py`
- Docker (tasks override): `TASKS_PROJECT_PATH=www` → loads `www/settings.py`

### `__main__.py` — CLI Entry Point

Provides per-site command routing through `cli.py:SiteCLI` infrastructure:

```bash
python projects/www/__main__.py check     # Django system check
python projects/www/__main__.py migrate   # Apply migrations
python projects/www/__main__.py shell     # Django shell
```

### `worker/celery.py` — Celery Application

Configures the Celery app for the shared-task stack:

```python
app = Celery("www.worker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```

Used by `shared-scheduler` container running:
```bash
celery -A www.worker.celery:app beat
```

### `worker/email.py` — Dramatiq Email Actors

Handles email sending across all websites:

```python
@dramatiq.actor(queue_name="email")
def send_templated_email(to_email, subject, template_name, context):
    """Render and send a Django template email."""
```

### `worker/tasks.py` — Celery Tasks

Defines shared Celery tasks:

```python
@shared_task(queue="shared")
def heartbeat():
    """Periodic task to verify the worker is alive and healthy."""
```

---

## 🐳 Docker Integration

The `www/` directory is bind-mounted into shared-worker and shared-scheduler containers:

```yaml
# From docker-compose.tasks.yml:
volumes:
  - ../../projects/www:/app/www:z
```

This allows hot-reloading task code without rebuilding the image.

---

## 🔗 Related

| Path | Description |
|------|-------------|
| `projects/configs/Env/sites.yml` | Site registration with `path: www` |
| `projects/cli.py` | Site resolution and CLI infrastructure |
| `applications/compose/docker-compose.tasks.yml` | Shared-worker + shared-scheduler compose |
| `docs/infrastructure/` | Deployment and infrastructure docs |
