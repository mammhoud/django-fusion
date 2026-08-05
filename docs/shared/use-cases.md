# 🎯 Shared — Use Cases

> How the shared `www/` Django core is used across all Structa Cloud sites and background workers.

---

## What WWW Provides

The `www/` directory at `projects/www/` is the **shared Django core** — code used by every site in the monorepo. It's not a standalone website but a reusable foundation.

| Component | Path | Purpose |
|-----------|------|---------|
| **Settings** | `projects/www/settings.py` | Sentinel site config for shared task workers |
| **Worker** | `projects/www/worker/` | Dramatiq + Celery task discovery |
| **Task Modules** | `projects/www/worker/modules.py` | Registered background task modules |
| **CI** | `projects/www/ci/` | Shared CI configuration |

---

## Use Case 1: Shared Background Worker

**Problem**: Every Django site needs background tasks (email, AI, sync). Running separate workers per site is wasteful.

**Solution**: One shared worker stack serves all sites.

```
┌────────────────────────────────────────────────┐
│          shared-worker (Dramatiq)               │
│          shared-scheduler (Celery Beat)          │
│                                                  │
│  Routes tasks per site via queue routing:        │
│    ctc-research queue  → ctc-research DB         │
│    lms queue           → lms DB                  │
│    portfolio queue     → portfolio DB            │
│    cypercloud queue    → cypercloud DB           │
└────────────────────────────────────────────────┘
```

### How It Works

```python
# projects/www/worker/modules.py
TASK_MODULES = [
    "ceptor_ai.tasks",                      # AI model tasks
    "ceptor_ai.workflows.tasks",            # Workflow automation
    "ceptor_ai.services.communication.tasks",  # Email/notifications
]
```

The worker autodiscovers these modules at startup. Each task includes queue routing so it hits the correct site's database.

### Deployment

```bash
make deploy-tasks           # Start shared-worker + shared-scheduler
make deploy-tasks TASKS_DB_NAME=db_lms  # Override default DB
```

---

## Use Case 2: Setting Up a New Django Site

**Problem**: Adding a new Django site requires boilerplate settings, URL config, site registration.

**Solution**: Clone from shared patterns — `www/settings.py` is the reference sentinel.

### Step-by-Step

```python
# projects/<new-site>/settings.py
# 1. Import shared settings
from configs.settings import *

# 2. Register the site
from configs.site import configure_site_environment
configure_site_environment("new-site", module="CMS", default_port=5080)

# 3. Add site-specific apps
LOCAL_APPS = ["new_site.pages", "new_site.plugins"]
INSTALLED_APPS += LOCAL_APPS
```

### What WWW Provides Automatically

| Component | How |
|-----------|-----|
| `INSTALLED_APPS` | django-fusion, Wagtail, allauth, ceptor-ai |
| `MIDDLEWARE` | Security, sessions, CSRF, auth, messages |
| `TEMPLATES` | Component tag builtins, shared template dirs |
| `DATABASES` | PostgreSQL (prod) or SQLite (dev) |
| `STATIC/MEDIA` | Shared staticfiles + Nginx media server |

---

## Use Case 3: Site-Agnostic Task Processing

**Problem**: The `ceptor_ai.tasks` module sends emails — but to which site's SMTP config?

**Solution**: The shared worker resolves per-site config at task execution time.

```python
# www/worker/__init__.py
# At task dispatch:
#   1. Read queue name → determine site
#   2. Load site-specific settings (email backend, API keys)
#   3. Execute task with correct site context
```

This lets one worker process:
- LMS enrollment confirmation emails
- Cypercloud AI response streaming
- Portfolio PDF generation
- CTC Research notification emails

All from a single `make deploy-tasks`.

---

## Use Case 4: Testing in Isolation

**Problem**: Testing `www.worker` modules requires a Django environment without a real site.

**Solution**: `www/settings.py` provides a minimal sentinel config for unit tests.

```python
# tests/unit/test_worker.py
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "www.settings"

import django
django.setup()

from www.worker.modules import TASK_MODULES
assert "ceptor_ai.tasks" in TASK_MODULES
```

---

## Use Case 5: CI Pipeline for Shared Code

**Problem**: Changes to `www/` affect all sites — need a fast CI gate.

**Solution**: The sentinel site loads with zero site-specific deps.

```bash
# Minimal CI check — no real DB, no Wagtail pages needed
python projects/www/__main__.py check  # Django system checks
python projects/www/__main__.py shell -c "from www.worker.modules import TASK_MODULES; print(TASK_MODULES)"
```

---

## When NOT to Use WWW

| Don't | Do Instead |
|-------|-----------|
| Add site-specific pages/models to `www/` | Add to `projects/<site>/www/` |
| Hardcode site-specific config in `www/settings.py` | Use Dynaconf per-site settings |
| Register site-specific tasks in `www/worker/` | Register in site's own `tasks.py` and route via queue |
| Mount `www/` as a standalone website | It's a library, not a deployable site |

---

## Related

| Topic | Path |
|-------|------|
| WWW configuration | [`configuration.md`](configuration.md) |
| Clone site guide | [`../../guides/06-clone-site.md`](../../guides/06-clone-site.md) |
| Backend env | [`../../back-env/`](../../back-env/) |
| django-fusion | [`../libs/django-fusion.md`](../libs/django-fusion.md) |
| POS configurations | [`../pos/configuration.md`](../pos/configuration.md) |
