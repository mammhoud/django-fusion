# Plan: Consolidated Task Worker as a First-Class Website Service

## Status

Draft — ready for review before implementation.

## Context

The monorepo currently keeps Celery tasks under `core/tasks/` and runs them through a single shared Docker container (`shared-worker` / `shared-scheduler`) defined in `applications/compose/docker-compose.tasks.yml`. Site context is passed into each task at call time via `configure_django_for_website(website)`.

This plan proposes moving the task package into `core/www/worker/`, exposing task management through website navigation, and making site configuration lazy/optional so the worker can serve multiple servers without a hard default site.

## Goals

1. **Single conceptual worker service** — keep one shared Celery worker/scheduler container.
2. **Move `core/tasks/` → `core/www/worker/`** — make the worker a real Django app under the shared `www` namespace.
3. **Website navigation for tasks** — add Django URLs/views so staff can inspect queues, active tasks, failed tasks, and retry failures.
4. **Multi-server / multi-config support** — route tasks and configuration based on the originating website/server, not a single env var.
5. **Optional website configs** — allow `configs.site` and `configs.settings.conf` to operate without an fully resolved active website at import time.

---

## 1. New File Layout

```text
core/www/worker/                    # was core/tasks/
├── __init__.py
├── apps.py                         # Django AppConfig: "www.worker"
├── celery.py                       # Celery app bootstrap (moved from core/tasks/celery.py)
├── runtime.py                      # configure_django_for_website, import_first
├── decorators.py                   # shared_task fallback
├── routing.py                      # NEW: dynamic task routes per site/server
├── email.py                        # shared email tasks
├── content.py                      # shared content/account tasks
├── django_rseal.py                 # legacy/optional RSEAL tasks
├── urls.py                         # NEW: task management URLs
├── views.py                        # NEW: task dashboard views
└── admin.py                        # NEW: optional TaskResult admin hooks

# Backward-compatibility shims (kept for one release)
core/tasks/__init__.py              # re-exports www.worker symbols
```

### Why `core/www/worker/`?

- `core/www/` is the canonical location for shared/core Django code.
- `core/www/core/` currently only holds CI utilities; it is not a Django app namespace. Placing the worker at `core/www/worker/` keeps it at the same level as future shared apps and avoids nesting it under an unrelated `core/` package. Consider renaming `core/www/core/` to `core/www/ci/` or moving it elsewhere to remove the naming collision.
- Treating the worker as a Django app lets it register URLs, admin, and signals like any other app.
- It keeps Celery task definitions co-located with the views that monitor them.

### Import path convention

The monorepo already adds `core/` to `sys.path` at runtime (see `configure_site_environment`). Therefore the app is referenced as `www.worker` in `INSTALLED_APPS` and Celery module paths, even though the filesystem path is `core/www/worker/`.

---

## 2. Import Path Migration Strategy

### 2.1 Python imports

Update all internal imports:

```python
# Old
from tasks.email import send_email_task
from tasks.runtime import configure_django_for_website

# New
from www.worker.email import send_email_task
from www.worker.runtime import configure_django_for_website
```

A global search/replace across `core/` and site apps is required.

### 2.2 Celery task names (critical)

Celery task names are derived from the module path by default. Moving the package would change queued task identities and break in-flight jobs. To avoid this, hard-code the current task names in decorators:

```python
# core/www/worker/email.py
from www.worker.decorators import shared_task

@shared_task(
    name="shared.email.send",            # keep current name
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_email_task(...):
    ...
```

Current task names (verify before migration): `shared.email.send`, `shared.email.bulk`, `shared.email.raw`, `shared.content.users_count`, `shared.content.welcome_email`. If these ever change, update both the decorators and any callers that reference task names by string.

All existing `@shared_task` definitions in `email.py`, `content.py`, etc. must receive an explicit `name=`.

### 2.3 Celery autodiscovery

Update `core/www/worker/celery.py`:

```python
TASK_IMPORTS = (
    "www.worker.email",
    "www.worker.content",
)

app.autodiscover_tasks(lambda: ["www.worker"])
```

Site-specific tasks living in `core/<site>/www/apps/<app>/tasks.py` are discovered only if the site package is on `PYTHONPATH` and listed in `INSTALLED_APPS`. Because the shared worker mounts all site directories, autodiscovery will find them as long as each site's Django apps are in `INSTALLED_APPS`. If a site is not mounted, its tasks are not discovered.

### 2.4 Backward-compatibility shim

Keep `core/tasks/` as a thin compatibility package for one release so third-party/site code has time to migrate. Delay imports inside functions to avoid circular imports at startup:

```python
# core/tasks/__init__.py
import warnings

def _warn():
    warnings.warn(
        "core.tasks is deprecated; import from www.worker instead.",
        DeprecationWarning,
        stacklevel=3,
    )

def __getattr__(name: str):
    _warn()
    import importlib
    mod = importlib.import_module("www.worker")
    return getattr(mod, name)
```

Do not import `www.worker.celery` at module level in the shim; `celery.py` bootstraps Django and can create an import loop.

---

## 3. Website Navigation for Tasks

Add a lightweight task dashboard under `/worker/` (or `/admin/tasks/` if preferred). It should not require Flower.

### 3.1 URL design

```python
# core/www/worker/urls.py
from django.urls import path
from . import views

app_name = "worker"

urlpatterns = [
    path("status/", views.QueueStatusView.as_view(), name="status"),
    path("active/", views.ActiveTasksView.as_view(), name="active"),
    path("scheduled/", views.ScheduledTasksView.as_view(), name="scheduled"),
    path("failed/", views.FailedTasksView.as_view(), name="failed"),
    path("failed/<str:task_id>/retry/", views.RetryTaskView.as_view(), name="retry"),
]
```

Wire it into each site's URLconf under `/worker/`:

```python
# core/ctc-research/urls.py (and lms-demo, VResume)
from django.urls import path, include

urlpatterns = [
    ...
    path("worker/", include("www.worker.urls")),
]
```

### 3.2 View responsibilities

| View | Data source | Actions |
|------|-------------|---------|
| `QueueStatusView` | `app.control.inspect().active_queues()` | Show queue lengths, worker count |
| `ActiveTasksView` | `app.control.inspect().active()` | List running tasks per worker |
| `ScheduledTasksView` | `app.control.inspect().scheduled()` | List scheduled ETA tasks |
| `FailedTasksView` | `django_celery_results.models.TaskResult` | Filter by status=FAILURE |
| `RetryTaskView` | `TaskResult` + original task kwargs | Re-publish with `.apply_async()` |

**Security note for retry:** Re-publishing task kwargs can expose sensitive data. Restrict the retry view to staff/superusers and audit which tasks are retryable. Consider a blocklist for tasks that contain PII or credentials.

**Rate limiting:** Protect the retry endpoint from accidental or malicious abuse. Options:

- Django Ratelimit: `@ratelimit(key="user", rate="10/m")`
- Custom decorator throttling retries per task ID to once per minute
- Require POST + CSRF + staff permission for any retry action

**Prerequisite:** `django-celery-results` must be installed and added to `INSTALLED_APPS` along with `www.worker`. Verify in `pyproject.toml` and each site's settings.

### 3.3 Permission model

- Reuse the existing staff/superuser checks (`django.contrib.admin.views.decorators.staff_member_required`).
- Optionally add a custom permission `worker.view_task_dashboard`.

### 3.4 Template/HTMX

- Use shared templates under `core/assets/templates/`.
- Prefer HTMX for retry buttons and live queue refresh.

### 3.5 Menu / navigation integration

Add a "Task Worker" link to the staff navigation:

- **Admin sidebar:** extend the existing admin base template with a link to `/worker/status/`.
- **Header dropdown (staff only):** add a "Worker Dashboard" item under the user menu for users with `is_staff=True`.
- **Alternative:** mount the dashboard under `/admin/worker/` and link from the Django admin index.

Keep the dashboard URL consistent across all sites so staff muscle memory applies.

### 3.6 Testing the dashboard

- **Unit tests:** Mock `app.control.inspect()` in `tests/unit/worker/test_views.py` to assert queue status rendering without a live broker.
- **Retry flow tests:** Use `django_celery_results.models.TaskResult` fixtures to test the retry view; assert that `.apply_async()` is called with the stored kwargs.
- **Integration tests:** Start the shared worker in a test container, enqueue a test task, and verify it appears in the active tasks list.
- **Browser tests (optional):** Use the existing Selenium suite to log in as staff and navigate to `/worker/status/`.

---

## 4. Multi-Server / Multi-Config Support

### 4.1 Dynamic queues

Instead of one hard-coded `--queues` list, derive queues from configuration:

```python
# core/www/worker/celery.py
from configs.site import known_websites

DEFAULT_QUEUES = ["shared", "email", "default"]
SITE_QUEUES = list(known_websites())  # ctc-research, lms-demo, vresume, etc.
ALL_QUEUES = DEFAULT_QUEUES + SITE_QUEUES
```

The Docker Compose command becomes:

```yaml
command: >
  celery -A www.worker.celery:app worker
  --queues=${CELERY_QUEUES:-shared,email,default,ctc-research,lms-demo,vresume}
```

### 4.2 Per-site routing

Add `core/www/worker/routing.py`:

```python
from celery import Task
from configs.site import active_website_name

class SiteRouter:
    """Route tasks to site-specific queues when a website is provided."""

    def route(self, task: Task, args, kwargs, options, task_type=None):
        website = kwargs.get("website") or options.get("website")
        if website:
            return {"queue": f"site-{website}"}
        return None
```

Register it in `celery.py`:

```python
from www.worker.routing import SiteRouter

app.conf.task_routes = (SiteRouter().route,)
```

### 4.3 Per-server config overrides

Allow each site to override worker behavior via `core/configs/settings/ENV/celery.yml` or per-site `.env`:

```yaml
celery:
  worker:
    concurrency: 4
    prefetch_multiplier: 2
    queues:
      - shared
      - email
      - ctc-research
```

`MainSettings.get("celery.worker.concurrency", default=2)` can feed into the compose command via env vars.

### 4.4 Multi-server scope

"More than one server" in this plan means:

1. **Multiple logical sites on one physical worker** — already supported by mounting all site directories and routing by `website` task argument.
2. **Multiple worker containers behind the same broker** — scale `shared-worker` horizontally by running more containers with the same `--queues` list. They share the same Redis/Postgres backend and split work naturally.
3. **Remote / dedicated workers per site** — if a site ever needs its own worker, deploy a second compose stack that mounts only that site's directory and listens only to that site's queue. The routing and queue naming stay the same; only the compose service definition differs.

The plan does **not** cover cross-region broker replication or Celery workers running on separate Kubernetes clusters. Those require a separate networking/broker plan.

---

## 5. Optional Website Configuration

### 5.1 Problem

`core/configs/settings/conf.py` currently calls `active_website_name()` and `active_site_dir()` at import time and inside `__init__`. This forces a default site even when the worker is meant to be site-agnostic.

### 5.2 Changes

1. **Remove global eager resolution** in `conf.py`:

   ```python
   # Before
   SITE_DIR = active_site_dir()

   # After
   @functools.lru_cache(maxsize=1)
   def get_site_dir() -> Path:
       return active_site_dir()
   ```

2. **Make `MainSettings` site fields lazy** (adjust for the project's Pydantic version; the example below is Pydantic v2):

   ```python
   class MainSettings(BaseSettings):
       WEBSITE_NAME: str = Field(default="", description="Active website name")
       WEBSITE_DIR: str = Field(default="", description="Active website directory")

       def model_post_init(self, __context):
           super().model_post_init(__context)
           if not self.WEBSITE_NAME:
               object.__setattr__(self, "WEBSITE_NAME", active_website_name())
           if not self.WEBSITE_DIR:
               object.__setattr__(self, "WEBSITE_DIR", str(active_site_dir()))
   ```

   For Pydantic v1, override `__init__` instead of `model_post_init`. Audit the project for the installed version before implementing.

3. **Delay site bootstrap in Celery**:

   ```python
   # core/www/worker/celery.py
   from celery.signals import worker_process_init

   @worker_process_init.connect
   def init_worker_process(**kwargs):
       # Only configure a default site if one is explicitly requested;
       # otherwise tasks will call configure_django_for_website(website)
       # on a per-task basis.
       if os.getenv("DJANGO_SITE"):
           _configure_default_site()
   ```

4. **Allow `configure_site_environment` to be a no-op** when `website=None`:

   ```python
   def configure_site_environment(website: str | None = None, ...):
       if website is None:
           return
       ...
   ```

5. **Make site config file optional**:

   If `core/configs/settings/ENV/sites.yml` is missing, `site_configs()` already returns an empty dict. Ensure callers handle the case gracefully:

   ```python
   def active_website_name(default: str = "structa.cloud") -> str | None:
       ...
       if not known_websites():
           return None  # or return default
   ```

   When no site is selected, `MainSettings` should leave `WEBSITE_NAME` and `WEBSITE_DIR` as empty strings rather than raising.

   **Environment variable migration:** After lazy config is implemented, `DJANGO_SITE` is no longer required for the shared worker. Keep it only for:

   - Web containers that serve a single site.
   - Legacy scripts that have not yet adopted `configure_django_for_website(website)`.
   - Local development when you want to default to a specific site.

   **Concrete API example:** Allow callers to opt out of website resolution entirely:

   ```python
   # Site-agnostic worker / CLI tools
   settings = MainSettings(website_name=None)
   assert settings.WEBSITE_NAME == ""  # no site resolved

   # Explicit website selection
   settings = MainSettings(website_name="lms-demo")
   assert settings.WEBSITE_NAME == "lms-demo"
   ```

### 5.3 `apps.py` for the Django app

```python
# core/www/worker/apps.py
from django.apps import AppConfig

class WorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "www.worker"
    label = "worker"
    verbose_name = "Task Worker"
```

### 5.4 Settings files to update

Add `www.worker` to `INSTALLED_APPS` in each site's settings module:

```python
# core/ctc-research/settings.py, core/lms-demo/settings.py, core/VResume/settings.py
INSTALLED_APPS = [
    ...
    "www.worker",
    "django_celery_results",
]
```

No changes to `manage.py`, `wsgi.py`, or `asgi.py` are required unless they import from `tasks` directly; update those imports to `www.worker`.

### 5.5 Dockerfile / image considerations

Verify that `core/compose/Dockerfile` copies the entire `core/` tree (or at least `core/www/worker/`, `core/configs/`, and site directories) into the image. If the Dockerfile copies only selected paths, add:

```dockerfile
COPY core/www/worker /app/core/www/worker
```

Ensure the container's `PYTHONPATH` includes `/app/core` so `www.worker` is importable.

---

## 6. Docker / Compose Changes

### 6.1 Update `applications/compose/docker-compose.tasks.yml`

Change the Celery command module:

```yaml
services:
  shared-worker:
    command: >
      celery -A www.worker.celery:app worker
      --loglevel=${CELERY_LOG_LEVEL:-info}
      --queues=${CELERY_QUEUES:-shared,email,default,ctc-research,lms-demo,vresume}
      ...

  shared-scheduler:
    command: >
      celery -A www.worker.celery:app beat
      ...
```

### 6.2 Update `applications/compose/Makefile`

No major changes; `tasks-up` / `tasks-down` remain the operator-facing targets.

---

## 7. Migration Steps

1. **Pin task names** — add explicit `name=` to every `@shared_task` in `core/tasks/`.
2. **Move files** — `core/tasks/` → `core/www/worker/`.
3. **Update imports** — global replace `from tasks.` → `from www.worker.`.
4. **Add shims** — create `core/tasks/__init__.py` re-exports.
5. **Update Celery bootstrap** — point `celery -A` to `www.worker.celery:app`.
6. **Register Django app** — add `www.worker` to `INSTALLED_APPS` in each site's settings.
7. **Add URLs/views** — create `core/www/worker/urls.py` and `views.py`; include in each site's `urls.py`.
8. **Make config lazy** — refactor `conf.py` and `site.py` to avoid import-time site resolution.
9. **Update compose** — change command module in `docker-compose.tasks.yml`.
10. **Update Dockerfile** — ensure `core/www/worker/` is copied into the shared worker image.
11. **Update Makefiles** — audit `core/Makefile`, site Makefiles, and root `Makefile` for references to `tasks.celery` or `core/tasks/`.
12. **Update tests** — move/adjust `tests/unit/tasks/` to import from `www.worker`.
13. **Validate** — run:
    - `docker compose -f applications/compose/docker-compose.tasks.yml config -q`
    - `make deploy-preflight`
    - Unit tests under `tests/unit/tasks/`
14. **Remove shims** — delete `core/tasks/` in a follow-up release.

### Priority / timeline

| Phase | Steps | Blocker? |
|-------|-------|----------|
| 1 — Prep | Pin task names, add shims | Yes — must happen before move |
| 2 — Move | Move files, update imports, update Celery command | Yes |
| 3 — Integrate | Add URLs/views, register app, menu links | No — can ship after move |
| 4 — Harden | Lazy config, optional site config, rate limiting | No — can ship after move |
| 5 — Cleanup | Remove shims, retire `core/tasks/` | No — do after Phase 2 is stable |

### Rollback strategy

If in-flight tasks fail after the move because task names were not pinned correctly:

1. Revert `docker-compose.tasks.yml` to the previous command module (`tasks.celery:app`).
2. Restore the old `core/tasks/` package from git.
3. Restart the worker container.
4. Re-queue any failed tasks manually.

To avoid this, pin task names and deploy the shim **before** moving the files.

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| In-flight Celery tasks break because task names change | Hard-code `name=` in every decorator before moving files |
| Import loops between `www.worker` and `configs.site` | Keep runtime helpers minimal; avoid importing models at module level |
| Site-agnostic worker fails to bootstrap Django | Only call `_configure_default_site()` when `DJANGO_SITE` is set; otherwise tasks self-configure |
| Staff dashboard exposes sensitive task data | Require `staff_member_required` or custom permission |
| Lazy config breaks code expecting eager `settings.WEBSITE_NAME` | Add `model_post_init` fallback; audit `.dict()` / JSON serialization |

---

## 9. Follow-up Work

- Add Flower as an optional overlay for advanced inspection.
- Implement task result retention policy via `django-celery-results` settings.
- Add per-site queue autoscaling rules in compose.

---

## 10. Decision Log

| Decision | Rationale |
|----------|-----------|
| Keep `core/tasks/` as a shim | Avoids breaking third-party/site imports during transition |
| Hard-code legacy Celery task names | Prevents queued task loss when module path changes |
| Use `www.worker` instead of `worker` | Follows existing `core/www/` convention for shared Django apps |
| Lazy site config | Required for a truly shared, site-agnostic worker container |
