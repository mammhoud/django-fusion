# Shared — Shared Core & Workers

> **Related Names:** `shared`, `shared-worker`, `shared-scheduler`, `tasks`, `sentinel site`, `background tasks`, `Dramatiq`, `Celery`
> **Tags:** #project #shared #shared-core #worker #celery #dramatiq #tasks

**Canonical path:** `projects/www/`  
**Django site alias:** `shared` → resolves to `path: www` in `sites.yml`  
**Port:** 5080

---

## Overview

The `www/` directory (merged from former `projects/shared/` and `projects/www/`) is the **shared/core Django application code** used by all Structa Cloud websites. It serves double duty:

1. **Sentinel site** for the shared-task worker stack (`shared-worker` + `shared-scheduler`)
2. **Shared library** of task modules, CI utilities, and runtime helpers consumed by all tenant sites

Unlike per-site Django projects (ctc-research, lms, VResume), `www/` has no tenant-specific overrides — it's a site-agnostic configuration that can route tasks to **any** site's queue.

---

## Guide

### CLI Entry Point

```bash
# From projects/
python www/__main__.py check        # Django system check
python www/__main__.py migrate      # Apply migrations
python www/__main__.py shell        # Django shell
```

### Development

```bash
cd projects
make docker-up WEBSITE=www          # Run as Docker container
make check WEBSITE=www               # Django checks
```

### Task Worker Deployment

```bash
make deploy-tasks                    # Deploy shared-worker + shared-scheduler
make status-tasks                    # View worker status
make logs-tasks                      # View worker logs
```

---

## Code Map

| Path | Purpose | Customization |
|------|---------|:---:|
| `projects/www/__init__.py` | Package marker + sentinel docs | 🔴 not-customizable |
| `projects/www/settings.py` | Django settings for `www` sentinel site | ⚪ config-only |
| `projects/www/worker/__init__.py` | Exports: `configure_django_for_website`, `TASK_MODULES` | 🔴 not-customizable |
| `projects/www/worker/apps.py` | Django AppConfig — registers Dramatiq actors on `ready()` | 🔴 not-customizable |
| `projects/www/worker/celery.py` | Celery app bootstrap + beat scheduler | 🔴 not-customizable |
| `projects/www/worker/tasks.py` | Celery task definitions (heartbeat) | 🟢 customizable |
| `projects/www/worker/email.py` | Dramatiq email actors (templated + raw) | 🟢 customizable |
| `projects/www/worker/content.py` | Dramatiq content management actors | 🟢 customizable |
| `projects/www/worker/decorators.py` | Shared task decorators | 🔴 not-customizable |
| `projects/www/worker/runtime.py` | Runtime helpers (`configure_django_for_website`) | 🔴 not-customizable |
| `projects/www/worker/modules.py` | Task module registry (autodiscovery list) | 🟢 customizable |
| `projects/www/ci/utils.py` | CI/CD preflight utilities | 🟡 delegate |

---

## Remarks

| # | Note |
|---|------|
| ⚠️ | The sentinel site is registered in `sites.yml` with **aliases**: `shared`, `shared-worker`, `shared-scheduler`, `tasks`, `www`. Any of these can be used as `WEBSITE=` value. |
| ⚠️ | `www/settings.py` must NOT add `_SITE_APP_DIR` — doing so would block `www.core` and `www.worker` imports. |
| 💡 | The `www/` directory is bind-mounted into `shared-worker` and `shared-scheduler` containers, enabling hot-reload of task code without image rebuild. |
| 🔌 | To add a new task module: create the `.py` file → register in `modules.py` → add queue name to `docker-compose.tasks.yml`. |

---

## Customization Key

| Tag | Scope | What it means here |
|-----|-------|-------------------|
| 🟢 `customizable` | Task modules | Add/edit/remove tasks in `email.py`, `content.py`, `tasks.py`, `modules.py` |
| 🟡 `delegate` | CI utilities | Extend `ci/utils.py` by adding new helper functions consumed by deploy-preflight |
| 🔴 `not-customizable` | Core infra | `celery.py`, `apps.py`, `runtime.py`, `decorators.py` — framework core |
| ⚪ `config` | Settings | Configure via env vars: `DRAMATIQ_PROCESSES`, `DRAMATIQ_QUEUES`, `DB_NAME` |

---

## Related Documentation

| Resource | Path |
|----------|------|
| WWW configuration | [`configuration.md`](configuration.md) |
| WWW use cases | [`use-cases.md`](use-cases.md) |
| Shared methods | [`shared-methods.md`](shared-methods.md) |
| Infrastructure docs | [`../../infrastructure/worker-stack.md`](../../infrastructure/worker-stack.md) |
| Deployment guide | [`../../guides/04-deploy.md`](../../guides/04-deploy.md) |
| Backend environment | [`../../back-env/`](../../back-env/) |
| Site source | [GitHub](https://github.com/mammhoud/structa.cloud/tree/generic/projects/www) |
