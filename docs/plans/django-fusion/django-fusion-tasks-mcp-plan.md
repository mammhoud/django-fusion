# django-fusion — Unified Background Tasks & MCP Integration Plan

> **Status:** Planned
> **Owner:** django-fusion core team
> **Created:** 2026-08-10
> **Scope:** `libs/django-fusion/`, `projects/precis/`, `projects/landing-fusion/`, `projects/formints/`
> **Depends on:** django-fusion enhancement roadmap, worker consolidation, ceptor-ai MCP server
> **Companion plan:** [`django-fusion-llm-mcp-enhancement-plan.md`](django-fusion-llm-mcp-enhancement-plan.md) adds provider-neutral LLM routing, AI component workflows, caching, streaming, and governance on top of this task layer.

---

## 1. Executive Summary

The Structa Cloud monorepo currently runs a **hybrid Celery + Dramatiq** background-task stack with three per-site Celery workers, a shared Dramatiq worker, and a Celery Beat scheduler. The fusion product line (Precis LMS, Landing-Fusion) has **no background-task solution** — it removed `www.worker` from `INSTALLED_APPS` and relies on django-fusion's own task stack, which today is a thin `dispatch_job()` wrapper around django-rq.

This plan proposes:

1. **Replace Celery entirely** with Dramatiq as the sole task broker, completing the worker consolidation plan.
2. **Build a unified background-task API** in django-fusion (`django_fusion.tasks`) that abstracts the broker and provides task discovery, logging, retry, scheduling, and observability — working identically whether the backend is Dramatiq, django-rq, or in-process.
3. **Add MCP tools** to django-fusion for AI-driven task management: inspect queues, retry failed tasks, trigger tasks, view task history.
4. **Wire Precis LMS, Landing-Fusion, and Formint** to the unified API with project-owned task modules.

---

## 2. Current State Assessment

### 2.1 Existing Infrastructure

| Component | Location | Technology | Status |
|---|---|---|---|
| Shared Dramatiq worker | `projects/configs/tools/worker/` | Dramatiq + Redis | **Active** — email + content tasks |
| Shared Celery scheduler | `projects/configs/tools/worker/celery.py` | Celery Beat | **Active** — heartbeat + cleanup |
| Per-site Celery workers | `lms-worker`, `ctc-worker`, `vresume-worker` | Celery | **Active** — scheduled per-site |
| Worker consolidation plan | [`docs/plans/repository/worker-consolidation.md`](../repository/worker-consolidation.md) | Celery → shared | **Planned** — Phases 1-4 |
| django-fusion task log | `django_fusion.models.tasks.BackgroundTaskLog` | django-rq | **Exists** — thin wrapper |
| django-fusion dispatch | `django_fusion.services.jobs.dispatch_job` | django-rq | **Exists** — hardcoded to RQ |
| ceptor-ai MCP server | `libs/ceptor-ai/src/ceptor_ai/mcp_server.py` | FastAPI + MCP | **Active** — read-only metadata |
| Kilo MCP server | `applications/agents/mcp_server.py` | FastAPI | **Active** — introspection |

### 2.2 Gaps

| Gap | Impact |
|---|---|
| **No unified task API in django-fusion** | Each project hardcodes its broker (Dramatiq, Celery, django-rq). Migration between brokers requires rewriting every task. |
| **Fusion projects lack background tasks** | Precis and Landing-Fusion removed `www.worker` but have no replacement for email dispatch, content processing, or scheduled work. |
| **Celery is redundant** | The worker consolidation plan is incomplete. Per-site Celery workers duplicate the Dramatiq worker's function. |
| **`dispatch_job` hardcodes django-rq** | Cannot be used in Dramatiq/Celery deployments. The `BackgroundTaskLog` model is coupled to RQ's job ID schema. |
| **No MCP tooling for task management** | AI agents cannot inspect queues, retry failures, or trigger background work. |
| **Task observability is fragmented** | Celery uses its own result backend; Dramatiq uses a different middleware; RQ uses yet another. No unified dashboard. |
| **Email backend coupling** | `django_dramatiq_email` is project-specific. No django-fusion abstraction for async email backends. |

### 2.3 Duplicated Worker Code

The codebase has **three copies** of essentially the same worker package:

| Path | Role |
|---|---|
| `projects/www/worker/` | Legacy shared worker (used by CTC Research, LMS, VResume) |
| `projects/configs/management/workers/` | Management-context worker duplicate |
| `projects/configs/tools/worker/` | Tools-context worker duplicate |

All three contain identical `celery.py`, `email.py`, `content.py`, `tasks.py`, `modules.py`, and `decorators.py`. Only one should remain.

---

## 3. Architecture — Target State

### 3.1 Unified Task Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                     django_fusion.tasks                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ TaskRegistry  │  │ TaskBackend  │  │ BackgroundTaskLog      │ │
│  │ (discovery)   │  │ (abstraction)│  │ (audit trail)          │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
│         │                 │                       │              │
│         ▼                 ▼                       ▼              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Backend Adapters                           ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  ││
│  │  │ Dramatiq │  │ DjangoRQ │  │  InProc  │  │  (future:   │  ││
│  │  │ Adapter  │  │ Adapter  │  │ Adapter  │  │  Temporal)  │  ││
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   MCP Tool Layer                              ││
│  │  task.inspect  task.retry  task.trigger  task.history       ││
│  │  task.queues   task.stats  task.schedule  task.purge         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  Dramatiq Broker │          │  MCP Clients     │
│  (Redis/Rabbit)  │          │  (Claude, etc.)  │
└──────────────────┘          └──────────────────┘
```

### 3.2 Per-Project Task Discovery

Each project defines task modules that django-fusion discovers automatically:

```
projects/precis/backend/
├── apps/
│   ├── tasks/                    # ← Project task package
│   │   ├── __init__.py           # from django_fusion.tasks import registry
│   │   ├── email_tasks.py        # @task(queue="email")
│   │   ├── course_tasks.py       # @task(queue="courses")
│   │   ├── content_tasks.py      # @task(queue="content")
│   │   └── scheduled_tasks.py    # @task(schedule="0 */6 * * *")
│   └── ...
```

django-fusion's `TaskRegistry` scans `INSTALLED_APPS` for `tasks` subpackages and registers discovered tasks with the configured backend.

---

## 4. Phase 1 — Celery Removal & Dramatiq Unification

### 4.1 Goals

- Remove all Celery dependencies: `celery`, `django-celery-beat`, `django-celery-results`
- Consolidate to Dramatiq as the single task broker
- Use `django-dramatiq` + `apscheduler` (or Dramatiq's built-in scheduler) for periodic tasks
- Keep exactly one worker codebase (`projects/configs/worker/`)

### 4.2 Implementation Steps

| # | Step | Files affected |
|---|---|---|
| 1.1 | **Audit all Celery task consumers** — find every `@shared_task`, `celery.send_task()`, and `Celery()` app reference across all projects | `rg '@shared_task\|send_task\|from celery' projects/` |
| 1.2 | **Migrate Celery tasks to Dramatiq actors** — rewrite `heartbeat`, `cleanup`, and any per-site Celery tasks as `@dramatiq.actor` entries | `projects/configs/tools/worker/tasks.py` |
| 1.3 | **Replace Celery Beat with APScheduler** — port the schedule table (hourly heartbeat, daily cleanup, 6h sync_metrics) to APScheduler running inside the Dramatiq worker process | New: `projects/configs/worker/scheduler.py` |
| 1.4 | **Remove Celery from django-fusion** — delete the optional `sentry_sdk.integrations.celery` import, remove `CELERY_` settings references | `libs/django-fusion/src/django_fusion/plugins/debug_tools/sentry.py`, `projects/configs/Env/celery.yml` |
| 1.5 | **Remove per-site worker services** — comment out `lms-worker`, `ctc-worker`, `vresume-worker` from per-site `docker-compose.yml` files (Phase 4 of worker-consolidation) | Per-site compose files |
| 1.6 | **Consolidate worker code** — keep `projects/configs/tools/worker/` as the single source (already the active worker). Delete `projects/configs/management/workers/` (duplicate). Archive `projects/www/worker/` (legacy, superseded). Do NOT create a new path. | Worker packages |
| 1.7 | **Update `docker-compose.tasks.yml`** — single `shared-worker` (Dramatiq) + `shared-scheduler` (APScheduler) services | `applications/compose/docker-compose.tasks.yml` |
| 1.8 | **Update CI and deployment targets** — replace `celery -A` commands with `dramatiq` equivalents | Makefiles, CI workflows |
| 1.9 | **Remove `django-celery-beat` and `django-celery-results`** from dependencies | `pyproject.toml`, `uv.lock` |
| 1.10 | **Run full test suite** — verify no Celery imports remain, all scheduled tasks fire | `uv run pytest` |

### 4.3 Dramatiq Scheduler (APScheduler)

```python
# projects/configs/worker/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings

scheduler = BackgroundScheduler()

def register_scheduled_tasks():
    """Register periodic tasks from django-fusion task registry."""
    from django_fusion.tasks import task_registry

    for task_def in task_registry.scheduled_tasks():
        scheduler.add_job(
            task_def.func,
            trigger=CronTrigger.from_crontab(task_def.schedule),
            id=task_def.name,
            name=task_def.description,
            replace_existing=True,
        )

# Built-in schedules (replacing Celery Beat):
scheduler.add_job(heartbeat,  'interval', hours=1,   id='heartbeat')
scheduler.add_job(cleanup,    'cron',     hour=3,     id='cleanup')
scheduler.add_job(sync_metrics,'cron',    hour='*/6', id='sync_metrics')
```

---

## 5. Phase 2 — django-fusion Task API (`django_fusion.tasks`)

> **Implementation note:** Code blocks in this plan are proposed design
> sketches and acceptance examples. They are not evidence that the shown
> modules, settings, migrations, or task registrations are complete.

### 5.1 Module Structure

```
libs/django-fusion/src/django_fusion/tasks/
├── __init__.py          # Public API: task, task_registry, TaskBackend
├── registry.py          # TaskRegistry — discovery, registration, metadata
├── backends/
│   ├── __init__.py
│   ├── base.py          # AbstractTaskBackend
│   ├── dramatiq.py      # DramatiqBackend (default/production)
│   ├── rq.py            # RQBackend (compatibility)
│   └── inprocess.py     # InProcessBackend (testing/development)
├── decorators.py        # @task decorator — broker-agnostic
├── models.py            # BackgroundTaskLog (moved, enhanced)
├── scheduler.py         # APScheduler integration
├── mcp_tools.py         # MCP tool definitions for task operations
└── middleware.py         # Task middleware: logging, retry, metrics
```

### 5.2 Unified `@task` Decorator

```python
# django_fusion/tasks/decorators.py
from __future__ import annotations

import functools
from typing import Any, Callable, Optional
from django_fusion.tasks.registry import task_registry

class TaskOptions:
    """Broker-agnostic task configuration."""
    queue: str = "default"
    max_retries: int = 3
    min_backoff: int = 15_000      # ms
    max_backoff: int = 86_400_000  # ms (24h)
    time_limit: int = 1_800_000    # ms (30m)
    schedule: Optional[str] = None  # cron expression
    actor_name: Optional[str] = None
    bind: bool = False             # pass self/actor ref

def task(
    queue: str = "default",
    max_retries: int = 3,
    min_backoff: int = 15_000,
    max_backoff: int = 86_400_000,
    time_limit: int = 1_800_000,
    schedule: Optional[str] = None,
    actor_name: Optional[str] = None,
    bind: bool = False,
    **backend_kwargs: Any,
):
    """
    Register a function as a background task.

    This decorator is broker-agnostic — it registers with
    django-fusion's TaskRegistry, which routes to the configured
    backend (Dramatiq, RQ, or in-process for testing).

    Usage:
        @task(queue="email", max_retries=5)
        def send_welcome_email(user_id: int):
            ...
    """
    options = TaskOptions(
        queue=queue,
        max_retries=max_retries,
        min_backoff=min_backoff,
        max_backoff=max_backoff,
        time_limit=time_limit,
        schedule=schedule,
        actor_name=actor_name,
        bind=bind,
    )

    def decorator(func: Callable) -> Callable:
        task_registry.register(func, options, backend_kwargs)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

    # Attach .send() / .delay() to the wrapper
    wrapper.send = lambda *a, **kw: task_registry.send(wrapper, *a, **kw)
    wrapper.delay = wrapper.send  # alias for Celery compatibility
    wrapper._fusion_task = True   # marker for _lookup()
    wrapper.options = options
    return wrapper

    return decorator
```

### 5.3 Task Registry

```python
# django_fusion/tasks/registry.py
from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class TaskRegistration:
    func: Callable
    name: str
    module: str
    queue: str
    max_retries: int
    schedule: Optional[str]
    options: Dict[str, Any] = field(default_factory=dict)

class TaskRegistry:
    """
    Central registry for all background tasks across the project.

    Scans INSTALLED_APPS for ``tasks`` subpackages and registers
    tasks decorated with ``@task``. Provides the backend-independent
    ``.send()`` method.
    """

    def __init__(self):
        self._tasks: Dict[str, TaskRegistration] = {}
        self._backend = None
        self._discovered = False

    def configure(self, backend: TaskBackend):
        """Wire the registry to a concrete backend."""
        self._backend = backend

    def register(self, func: Callable, options: TaskOptions, backend_kwargs: dict):
        name = options.actor_name or f"{func.__module__}.{func.__name__}"
        self._tasks[name] = TaskRegistration(
            func=func,
            name=name,
            module=func.__module__,
            queue=options.queue,
            max_retries=options.max_retries,
            schedule=options.schedule,
            options={**backend_kwargs, "time_limit": options.time_limit,
                      "min_backoff": options.min_backoff,
                      "max_backoff": options.max_backoff},
        )

    def send(self, func: Callable, *args, **kwargs) -> Any:
        """Enqueue a task for background execution. Returns backend-specific message ID."""
        if self._backend is None:
            raise RuntimeError("TaskRegistry has no configured backend.")
        reg = self._lookup(func)
        return self._backend.enqueue(reg, args, kwargs)

    def scheduled_tasks(self) -> List[TaskRegistration]:
        return [t for t in self._tasks.values() if t.schedule]

    def autodiscover(self):
        """Scan INSTALLED_APPS for tasks subpackages."""
        if self._discovered:
            return
        from django.conf import settings
        for app in settings.INSTALLED_APPS:
            try:
                importlib.import_module(f"{app}.tasks")
            except ImportError:
                pass
        self._discovered = True

    def _lookup(self, func: Callable) -> TaskRegistration:
        # If the wrapper was decorated, it has _fusion_task marker.
        # Look up by the original function reference stored in the registry.
        for reg in self._tasks.values():
            if reg.func is func:
                return reg
            # Also match through the wrapper's original function
            if hasattr(func, '__wrapped__'):
                if reg.func is func.__wrapped__:
                    return reg
        # Fallback: search by module+name
        for reg in self._tasks.values():
            if reg.func.__module__ == getattr(func, '__module__', None) and \
               reg.func.__name__ == getattr(func, '__name__', None):
                return reg
        raise KeyError(f"Task not registered: {getattr(func, '__name__', func)}")

# Singleton
task_registry = TaskRegistry()
```

### 5.4 Dramatiq Backend

```python
# django_fusion/tasks/backends/dramatiq.py
from __future__ import annotations

import dramatiq
from typing import Any
from django_fusion.tasks.backends.base import AbstractTaskBackend
from django_fusion.tasks.registry import TaskRegistration

class DramatiqBackend(AbstractTaskBackend):
    """
    Dramatiq backend for django-fusion tasks.

    Wraps dramatiq.actor() around registered tasks so
    the Dramatiq worker discovers and executes them.
    """

    def __init__(self, broker_url: str = "redis://localhost:6379/1"):
        import dramatiq
        self.broker = dramatiq.get_broker() or self._setup_broker(broker_url)

    def _setup_broker(self, url: str):
        from dramatiq.brokers.redis import RedisBroker
        broker = RedisBroker(url=url)
        dramatiq.set_broker(broker)
        return broker

    def enqueue(self, reg: TaskRegistration, args: tuple, kwargs: dict) -> str:
        actor = self._get_or_create_actor(reg)
        message = actor.send(*args, **kwargs)
        return message.message_id

    def _get_or_create_actor(self, reg: TaskRegistration):
        actor_name = reg.name
        # Check if already registered via the broker's known actors
        try:
            from dramatiq import get_broker
            broker = get_broker()
            # Dramatiq broker maintains a mapping of known actors
            for actor in broker.get_declared_actors():
                if actor.actor_name == actor_name:
                    return actor
        except (AttributeError, ImportError):
            pass

        opts = reg.options
        actor = dramatiq.actor(
            actor_name=actor_name,
            queue_name=reg.queue,
            max_retries=opts.get("max_retries", 3),
            min_backoff=opts.get("min_backoff", 15000),
            max_backoff=opts.get("max_backoff", 86400000),
            time_limit=opts.get("time_limit", 1800000),
        )(self._wrap_with_logging(reg))

        return actor

    def _wrap_with_logging(self, reg: TaskRegistration):
        """Wrap the task function with BackgroundTaskLog tracking."""
        original = reg.func

        def tracked(*args, **kwargs):
            from django_fusion.models.tasks import BackgroundTaskLog
            import uuid

            log_entry = BackgroundTaskLog.objects.create(
                id=uuid.uuid4(),
                task_name=reg.name,
                queue_name=reg.queue,
                args=list(args),
                kwargs=kwargs,
                status="started",
            )

            try:
                result = original(*args, **kwargs)
                log_entry.status = "finished"
                log_entry.result = str(result)
                log_entry.save()
                return result
            except Exception as e:
                log_entry.status = "failed"
                log_entry.error_message = str(e)
                log_entry.save()
                raise

        tracked.__name__ = original.__name__
        tracked.__module__ = original.__module__
        return tracked
```

### 5.5 In-Process Backend (for Testing)

```python
# django_fusion/tasks/backends/inprocess.py
from django_fusion.tasks.backends.base import AbstractTaskBackend
from django_fusion.tasks.registry import TaskRegistration

class InProcessBackend(AbstractTaskBackend):
    """Runs tasks synchronously in the calling thread. For tests/dev."""

    def enqueue(self, reg: TaskRegistration, args: tuple, kwargs: dict) -> str:
        result = reg.func(*args, **kwargs)
        return "inprocess"
```

### 5.6 Enhanced `BackgroundTaskLog`

Move from `django_fusion.models.tasks` to `django_fusion.tasks.models` and enhance:

```python
# django_fusion/tasks/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class BackgroundTaskLog(models.Model):
    """Audit trail for every background task execution."""

    STATUS_CHOICES = [
        ("queued",    _("Queued")),
        ("started",   _("Started")),
        ("finished",  _("Finished")),
        ("failed",    _("Failed")),
        ("cancelled", _("Cancelled")),
        ("retrying",  _("Retrying")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=255, db_index=True)
    queue_name = models.CharField(max_length=100, default="default")
    backend = models.CharField(max_length=50, default="dramatiq")  # dramatiq | rq | inprocess

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")

    args = models.JSONField(default=list, blank=True)
    kwargs = models.JSONField(default=dict, blank=True)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    error_traceback = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)

    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_scheduled = models.BooleanField(default=False)

    # Site/app context
    site_id = models.IntegerField(null=True, blank=True, db_index=True)
    app_label = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        app_label = "django_fusion"
        verbose_name = _("Background Task Log")
        verbose_name_plural = _("Background Task Logs")
        ordering = ["-created_at"]
        db_table = "fusion_background_task_log"
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["task_name", "-created_at"]),
            models.Index(fields=["queue_name", "status"]),
        ]

    def __str__(self):
        return f"{self.task_name} [{self.status}] @ {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def duration(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
```

---

## 6. Phase 3 — MCP Tool Integration

### 6.1 Goals

Expose task management as MCP tools so AI agents (Claude, Syntara, Freebuff) can:

- Inspect queue status and lengths
- View task history and failures
- Retry failed tasks
- Trigger tasks manually
- Purge stale queues
- Check worker health

### 6.2 MCP Tools Specification

```python
# django_fusion/tasks/mcp_tools.py
"""
MCP tool definitions for background task operations.

These are registered with ceptor-ai's MCP server and exposed
to AI agents via the Model Context Protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

# ── Tool Definitions ──────────────────────────────────────────────

MCP_TASK_TOOLS = {
    "task.inspect": {
        "description": "Inspect a task by its ID or name. Returns current status, logs, retry count.",
        "parameters": {
            "task_id": {"type": "string", "description": "UUID of the task log entry"},
            "task_name": {"type": "string", "description": "Registered task name (alternative to task_id)"},
        },
    },
    "task.queues": {
        "description": "List all task queues with message counts and consumer status.",
        "parameters": {},
    },
    "task.history": {
        "description": "Query task execution history with filtering by status, queue, date range.",
        "parameters": {
            "status": {"type": "string", "enum": ["queued", "started", "finished", "failed", "cancelled", "retrying"]},
            "queue": {"type": "string"},
            "task_name": {"type": "string"},
            "since": {"type": "string", "description": "ISO-8601 datetime"},
            "limit": {"type": "integer", "default": 20},
        },
    },
    "task.retry": {
        "description": "Re-enqueue a failed task with the same arguments.",
        "parameters": {
            "task_id": {"type": "string", "description": "UUID of the failed task log entry"},
        },
    },
    "task.trigger": {
        "description": "Manually trigger a registered task by name with arguments.",
        "parameters": {
            "task_name": {"type": "string", "description": "Registered task name (e.g., 'precis.email.send_welcome')"},
            "args": {"type": "array", "default": []},
            "kwargs": {"type": "object", "default": {}},
        },
    },
    "task.stats": {
        "description": "Aggregate statistics: counts by status, queue throughput, failure rates.",
        "parameters": {
            "period": {"type": "string", "enum": ["1h", "24h", "7d"], "default": "24h"},
        },
    },
    "task.purge": {
        "description": "Purge stale completed/failed task logs older than N days.",
        "parameters": {
            "older_than_days": {"type": "integer", "default": 30},
            "status": {"type": "string", "enum": ["finished", "failed"], "default": "finished"},
        },
    },
    "task.workers": {
        "description": "Check Dramatiq worker health, process counts, and consumer status.",
        "parameters": {},
    },
}
```

### 6.3 MCP Handlers Implementation

```python
# django_fusion/tasks/mcp_handlers.py

from django.db.models import Count, Min, Q, Avg, F
from django.utils import timezone
from datetime import timedelta
from .models import BackgroundTaskLog
from .registry import task_registry


def handle_task_inspect(task_id=None, task_name=None):
    """Handler for task.inspect MCP tool."""
    if task_id:
        log = BackgroundTaskLog.objects.filter(id=task_id).first()
    elif task_name:
        log = BackgroundTaskLog.objects.filter(task_name=task_name).order_by("-created_at").first()
    else:
        return {"error": "Provide task_id or task_name"}

    if not log:
        return {"error": "Task not found"}

    return {
        "task_id": str(log.id),
        "task_name": log.task_name,
        "status": log.status,
        "queue": log.queue_name,
        "retry_count": log.retry_count,
        "created_at": log.created_at.isoformat(),
        "started_at": log.started_at.isoformat() if log.started_at else None,
        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        "duration_seconds": log.duration,
        "error": log.error_message[:500] if log.error_message else None,
    }


def handle_task_queues():
    """Handler for task.queues MCP tool."""
    # Per-queue counts of pending tasks
    queue_counts = (
        BackgroundTaskLog.objects
        .filter(status__in=["queued", "started", "retrying"])
        .values("queue_name")
        .annotate(count=Count("id"), oldest=Min("created_at"))
        .order_by("-count")
    )

    return {
        "queues": [
            {
                "name": q["queue_name"],
                "pending": q["count"],
                "oldest_pending": q["oldest"].isoformat() if q["oldest"] else None,
            }
            for q in queue_counts
        ],
        "total_pending": sum(q["count"] for q in queue_counts),
    }


def handle_task_history(status=None, queue=None, task_name=None, since=None, limit=20):
    """Handler for task.history MCP tool."""
    qs = BackgroundTaskLog.objects.all()

    if status:
        qs = qs.filter(status=status)
    if queue:
        qs = qs.filter(queue_name=queue)
    if task_name:
        qs = qs.filter(task_name__icontains=task_name)
    if since:
        qs = qs.filter(created_at__gte=since)

    logs = qs[:limit]

    return {
        "count": len(logs),
        "total_matching": qs.count(),
        "tasks": [
            {
                "id": str(log.id),
                "name": log.task_name,
                "status": log.status,
                "queue": log.queue_name,
                "created": log.created_at.isoformat(),
                "duration": log.duration,
                "error": log.error_message[:200] if log.error_message else None,
            }
            for log in logs
        ],
    }


def handle_task_retry(task_id):
    """Handler for task.retry MCP tool."""
    log = BackgroundTaskLog.objects.filter(id=task_id, status="failed").first()
    if not log:
        return {"error": "Task not found or not in failed state"}

    # Re-enqueue with same args
    reg = task_registry._tasks.get(log.task_name)
    if not reg:
        return {"error": f"Task '{log.task_name}' is not registered"}

    task_id = task_registry.send(reg.func, *log.args, **log.kwargs)
    return {"status": "re-queued", "new_task_id": task_id}


def handle_task_trigger(task_name, args=None, kwargs=None):
    """Handler for task.trigger MCP tool."""
    reg = task_registry._tasks.get(task_name)
    if not reg:
        available = list(task_registry._tasks.keys())
        return {"error": f"Task '{task_name}' not found", "available_tasks": available[:20]}

    task_id = task_registry.send(reg.func, *(args or []), **(kwargs or {}))
    return {"status": "triggered", "task_id": task_id}


def handle_task_stats(period="24h"):
    """Handler for task.stats MCP tool."""
    deltas = {"1h": timedelta(hours=1), "24h": timedelta(hours=24), "7d": timedelta(days=7)}
    since = timezone.now() - deltas.get(period, timedelta(hours=24))

    qs = BackgroundTaskLog.objects.filter(created_at__gte=since)

    return {
        "period": period,
        "total": qs.count(),
        "by_status": {
            row["status"]: row["count"]
            for row in qs.values("status").annotate(count=Count("id"))
        },
        "failure_rate": round(
            qs.filter(status="failed").count() / max(qs.count(), 1) * 100, 1
        ),
        "avg_duration_seconds": qs.exclude(completed_at=None)
            .aggregate(avg=models.Avg(models.F("completed_at") - models.F("started_at")))["avg"],
    }


def handle_task_purge(older_than_days=30, status="finished"):
    """Handler for task.purge MCP tool."""
    since = timezone.now() - timedelta(days=older_than_days)
    deleted, _ = BackgroundTaskLog.objects.filter(
        status=status, created_at__lt=since
    ).delete()
    return {"deleted_count": deleted, "older_than_days": older_than_days, "status": status}


def handle_task_workers():
    """Handler for task.workers MCP tool."""
    try:
        from dramatiq import get_broker
        broker = get_broker()
        return {
            "broker_type": type(broker).__name__,
            "backend": "dramatiq",
        }
    except Exception as e:
        return {"error": str(e)}
```

### 6.4 MCP Server Registration

**⚠️ Boundary and production gate:** django-fusion MCP tools must NOT be registered into `ceptor-ai`'s MCP server. ceptor-ai explicitly avoids Django imports (see `applications/agents/commands/ceptor-ai.md`). Instead, django-fusion serves its own MCP endpoint at `/fusion/mcp/` within the Django application. The current Django view surface is an implementation scaffold: production exposure is blocked until authentication, authorization, rate limiting, request validation, audit logging, and transport/client compatibility are verified.

```python
# django_fusion/tasks/mcp_views.py
"""Django views exposing MCP task tools. Served at /fusion/mcp/tasks/."""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .mcp_handlers import (
    handle_task_inspect, handle_task_queues, handle_task_history,
    handle_task_retry, handle_task_trigger, handle_task_stats,
    handle_task_purge, handle_task_workers,
)
from .mcp_tools import MCP_TASK_TOOLS

_HANDLERS = {
    "task.inspect": handle_task_inspect,
    "task.queues":   handle_task_queues,
    "task.history":  handle_task_history,
    "task.retry":    handle_task_retry,
    "task.trigger":  handle_task_trigger,
    "task.stats":    handle_task_stats,
    "task.purge":    handle_task_purge,
    "task.workers":  handle_task_workers,
}

@csrf_exempt
@require_POST
def mcp_tools_call(request):
    """MCP JSON-RPC endpoint for task operations."""
    try:
        body = json.loads(request.body)
        tool_name = body.get("params", {}).get("name")
        arguments = body.get("params", {}).get("arguments", {})

        handler = _HANDLERS.get(tool_name)
        if not handler:
            return JsonResponse({"error": f"Unknown tool: {tool_name}"}, status=404)

        result = handler(**arguments)
        return JsonResponse({"jsonrpc": "2.0", "id": body.get("id"), "result": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def mcp_tools_list(request):
    """List available MCP task tools."""
    return JsonResponse({"tools": MCP_TASK_TOOLS})
```

```python
# urls.py — in django_fusion or project urls
from django.urls import path
from django_fusion.tasks.mcp_views import mcp_tools_call, mcp_tools_list

urlpatterns = [
    path("fusion/mcp/tools/list/", mcp_tools_list, name="mcp-tools-list"),
    path("fusion/mcp/tools/call/", mcp_tools_call, name="mcp-tools-call"),
]
```

---

## 7. Phase 4 — Project-Level Integration

### 7.1 Precis LMS (`projects/precis/backend/`)

> **Note:** Import paths below are illustrative. During implementation, validate
> against the actual app structure at `projects/precis/backend/apps/` (e.g., LMS
> models may be at `apps.pages.lms.models`, `apps.plugins.lms`, or similar).

```python
# settings.py
# ── django-fusion Tasks Configuration ─────────────────────────
FUSION_TASKS = {
    "BACKEND": "django_fusion.tasks.backends.dramatiq.DramatiqBackend",
    "BROKER_URL": "redis://localhost:6379/1",
    "TASK_ALWAYS_EAGER": False,   # Run async in production
    "LOG_ALL_TASKS": True,
    "LOG_RETENTION_DAYS": 30,
}

INSTALLED_APPS = [
    # ...
    "django_fusion.tasks",  # registers BackgroundTaskLog, provides @task
]
```

```python
# apps/tasks/__init__.py
from django_fusion.tasks import task_registry
task_registry.autodiscover()
```

```python
# apps/tasks/email_tasks.py
from django_fusion.tasks import task

@task(queue="email", max_retries=5, min_backoff=30_000)
def send_enrollment_confirmation(enrollment_id: int):
    """Send welcome email + course access instructions."""
    from apps.lms.models import Enrollment
    enrollment = Enrollment.objects.select_related("student", "course").get(id=enrollment_id)
    # ... compose and send email

@task(queue="email", max_retries=5)
def send_certificate(certificate_id: int):
    """Generate and email a course completion certificate."""
    from apps.lms.models import Certificate
    cert = Certificate.objects.get(id=certificate_id)
    # ... render PDF, attach, send

@task(queue="email", max_retries=3)
def send_password_reset(user_id: int):
    """Send password reset email."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    # ... send reset link
```

```python
# apps/tasks/course_tasks.py
from django_fusion.tasks import task

@task(queue="courses", max_retries=2, time_limit=600_000)  # 10 min
def generate_course_progress_report(course_id: int, instructor_id: int):
    """Generate a CSV progress report for an instructor."""
    ...

@task(queue="courses", schedule="0 */6 * * *")  # Every 6 hours
def sync_course_completion_rates():
    """Update cached completion percentages for all active courses."""
    ...

@task(queue="courses", schedule="0 9 * * 1")  # Monday 9 AM
def send_weekly_learning_digest():
    """Send weekly digest emails to all enrolled students."""
    ...
```

```python
# apps/tasks/content_tasks.py
from django_fusion.tasks import task

@task(queue="content", max_retries=3)
def process_uploaded_video(video_id: int):
    """Transcode and thumbnail a newly uploaded course video."""
    ...

@task(queue="content", max_retries=3)
def generate_ai_course_description(course_id: int):
    """Use LLM to generate SEO-optimized course description."""
    ...
```

### 7.2 Landing-Fusion (`projects/landing-fusion/`)

```python
# apps/tasks/email_tasks.py
from django_fusion.tasks import task

@task(queue="email", max_retries=5)
def send_newsletter(campaign_id: int):
    """Send a newsletter campaign to all subscribers."""
    ...

@task(queue="email", max_retries=3)
def send_contact_form_notification(contact_id: int):
    """Notify admin of new contact form submission."""
    ...

@task(queue="email", schedule="0 8 * * 1")  # Monday 8 AM
def send_weekly_site_stats():
    """Email site analytics summary to admins."""
    ...
```

```python
# apps/tasks/content_tasks.py
from django_fusion.tasks import task

@task(queue="content", max_retries=3)
def warm_page_cache(page_id: int):
    """Pre-render and cache a Wagtail page."""
    ...

@task(queue="content", max_retries=2)
def generate_blog_preview_images(post_id: int):
    """Generate social-media preview images for a blog post."""
    ...
```

### 7.3 Formint POS (`projects/formints/`)

```python
# apps/tasks/sync_tasks.py
from django_fusion.tasks import task

@task(queue="sync", max_retries=10, min_backoff=5_000, max_backoff=300_000)
def push_branch_data(branch_id: int, since_version: int):
    """Push pending DataToken changes to a branch."""
    ...

@task(queue="sync", max_retries=5)
def pull_branch_data(branch_id: int):
    """Pull latest changes from a branch."""
    ...

@task(queue="sync", schedule="*/5 * * * *")  # Every 5 minutes
def run_branch_sync_scheduler():
    """Check all branches for pending sync work."""
    ...
```

```python
# apps/tasks/report_tasks.py
from django_fusion.tasks import task

@task(queue="reports", max_retries=2, time_limit=1_200_000)  # 20 min
def generate_daily_sales_report(branch_id: int, date_str: str):
    """Generate EOD sales report PDF."""
    ...

@task(queue="reports", schedule="0 1 * * *")  # 1 AM daily
def generate_all_branch_reports():
    """Generate EOD reports for all active branches."""
    ...
```

---

## 8. Phase 5 — Async Email Backend

### 8.1 django-fusion Async Email Backend

Replace the project-level `django_dramatiq_email` with a django-fusion email backend:

```python
# django_fusion/tasks/email_backend.py
"""
Async email backend for django-fusion.

Usage in settings.py:
    EMAIL_BACKEND = "django_fusion.tasks.email_backend.AsyncEmailBackend"
"""

from django.core.mail.backends.base import BaseEmailBackend
from django_fusion.tasks.registry import task_registry


class AsyncEmailBackend(BaseEmailBackend):
    """
    Email backend that enqueues all messages as background tasks.

    Configure with:
        FUSION_EMAIL_TASK_QUEUE = "email"   # default
        FUSION_EMAIL_MAX_RETRIES = 5        # default
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        from django.conf import settings
        self.queue = getattr(settings, "FUSION_EMAIL_TASK_QUEUE", "email")
        self.max_retries = getattr(settings, "FUSION_EMAIL_MAX_RETRIES", 5)
        self.real_backend = getattr(
            settings, "FUSION_REAL_EMAIL_BACKEND",
            "django.core.mail.backends.smtp.EmailBackend"
        )

    def send_messages(self, email_messages):
        """Enqueue each message as a background task."""
        task_ids = []
        for message in email_messages:
            task_id = _send_email_task.send(
                subject=message.subject,
                body=message.body,
                from_email=message.from_email,
                recipient_list=message.recipients(),
                html_message=getattr(message, "alternatives", None),
            )
            task_ids.append(task_id)
        return len(task_ids)


@task(queue="email", max_retries=5, actor_name="fusion.email.send")
def _send_email_task(subject, body, from_email, recipient_list, html_message=None):
    """Background worker that sends email via the real SMTP backend."""
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    from django.core.mail import get_connection

    connection = get_connection(backend=settings.FUSION_REAL_EMAIL_BACKEND)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=recipient_list,
        connection=connection,
    )
    if html_message:
        for alt_content, alt_type in html_message:
            msg.attach_alternative(alt_content, alt_type)
    msg.send()
```

---

## 9. Configuration Reference

### 9.1 django-fusion Settings

```python
# settings.py — all projects

# ── Task Broker ────────────────────────────────────────────────
FUSION_TASKS = {
    # Backend class path
    "BACKEND": "django_fusion.tasks.backends.dramatiq.DramatiqBackend",

    # Broker connection
    "BROKER_URL": "redis://localhost:6379/1",

    # Testing override — runs tasks synchronously
    "TASK_ALWAYS_EAGER": False,

    # Task logging
    "LOG_ALL_TASKS": True,
    "LOG_RETENTION_DAYS": 30,
    "LOG_ANONYMIZE_ARGS": True,  # Mask sensitive arguments in logs

    # Retry defaults
    "DEFAULT_MAX_RETRIES": 3,
    "DEFAULT_MIN_BACKOFF": 15_000,   # milliseconds
    "DEFAULT_MAX_BACKOFF": 86_400_000,

    # Time limits
    "DEFAULT_TIME_LIMIT": 1_800_000,  # 30 minutes

    # Scheduled tasks
    "SCHEDULER_ENABLED": True,
    "SCHEDULER_TIMEZONE": "UTC",
}

# ── Async Email ────────────────────────────────────────────────
EMAIL_BACKEND = "django_fusion.tasks.email_backend.AsyncEmailBackend"
FUSION_REAL_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
FUSION_EMAIL_TASK_QUEUE = "email"
FUSION_EMAIL_MAX_RETRIES = 5
```

### 9.2 Per-Project Overrides

```python
# projects/precis/backend/settings.py
FUSION_TASKS["DEFAULT_MAX_RETRIES"] = 5       # Courses are important
FUSION_TASKS["LOG_RETENTION_DAYS"] = 90        # Keep course history longer

# projects/landing-fusion/backend/settings.py
FUSION_TASKS["LOG_RETENTION_DAYS"] = 14        # Marketing tasks don't need long retention

# projects/formints/formint/settings.py
FUSION_TASKS["DEFAULT_MAX_RETRIES"] = 10       # Sync tasks need aggressive retry
FUSION_TASKS["DEFAULT_MIN_BACKOFF"] = 5_000    # Faster retry for sync
```

### 9.3 Docker Configuration (Post-Celery)

```yaml
# applications/compose/docker-compose.tasks.yml
services:
  shared-worker:
    image: structa-cloud-worker:latest
    container_name: shared-worker
    restart: unless-stopped
    command: python -m django_fusion.tasks.worker
    environment:
      DJANGO_SETTINGS_MODULE: settings
      FUSION_TASK_BACKEND: dramatiq
      DRAMATIQ_BROKER_URL: redis://default-redis:6379/1
    volumes:
      - ../../projects:/app/projects:ro
      - ../../libs:/app/libs:ro
    networks:
      - structa-network

  shared-scheduler:
    image: structa-cloud-worker:latest
    container_name: shared-scheduler
    restart: unless-stopped
    command: python -m django_fusion.tasks.scheduler
    environment:
      DJANGO_SETTINGS_MODULE: settings
    volumes:
      - ../../projects:/app/projects:ro
      - ../../libs:/app/libs:ro
    networks:
      - structa-network
```

---

## 10. MCP Client Integration

### 10.1 Claude Desktop Configuration

Task MCP tools are served from django-fusion at `/fusion/mcp/tools/`, NOT from ceptor-ai (which avoids Django imports). Configure an HTTP MCP transport in Claude Desktop:

```json
{
  "mcpServers": {
    "structa-tasks": {
      "type": "http",
      "url": "http://localhost:8000/fusion/mcp/tools/",
      "headers": {
        "Authorization": "Bearer ${FUSION_MCP_TOKEN}"
      }
    }
  }
}
```

### 10.2 Example MCP Interactions

```
Agent:  "Show me all failed email tasks from the last hour."

→ POST /mcp/tools/call
  tool: task.history
  args: { "status": "failed", "queue": "email", "since": "2026-08-10T14:00:00Z" }

← [
    { "id": "a1b2...", "name": "precis.email.send_enrollment_confirmation",
      "status": "failed", "error": "SMTP connection timeout to smtp.example.com:587" },
    ...
  ]

Agent:  "Retry those failed email tasks."

→ POST /mcp/tools/call
  tool: task.retry
  args: { "task_id": "a1b2..." }

← { "status": "re-queued", "new_task_id": "c3d4..." }
```

---

## 11. Migration Path

### 11.1 Backward Compatibility

- The existing `django_fusion.services.jobs.dispatch_job` remains functional but is **deprecated** in favor of `@task`. Add a `DeprecationWarning` on first call per process.
- Existing Dramatiq actors in `projects/configs/tools/worker/` continue working — they're just Dramatiq actors with no django-fusion wrapper.
- **`BackgroundTaskLog` migration**: The existing table `grep_background_task_log` (app_label=`"shared"`) is migrated to `fusion_background_task_log` (app_label=`"django_fusion"`). Use Django's `SeparateDatabaseAndState` in a two-step migration:
  1. **Step 1**: Create new table `fusion_background_task_log` alongside the old one. Copy all data.
  2. **Step 2**: Drop old `grep_background_task_log` table. Remove old model.
- Projects using `django_dramatiq_email` (LMS, CTC Research) migrate to `EMAIL_BACKEND = "django_fusion.tasks.email_backend.AsyncEmailBackend"`. The `django_dramatiq_email` package is removed from dependencies after migration.
- The `@task` `.send()` returns the backend's native message type (e.g., Dramatiq `Message` object) — use `.send().message_id` for the string ID. This is documented in the decorator's docstring.

### 11.2 Incremental Rollout

| Step | Scope | Risk |
|---|---|---|
| 1. **Add `django_fusion.tasks` without removing Celery** | django-fusion package only | None — new code, no consumers |
| 2. **Add MCP tools** | django-fusion + ceptor-ai | None — read-only tools |
| 3. **Wire Precis LMS tasks** | `projects/precis/` | Low — no existing tasks to break |
| 4. **Wire Landing-Fusion tasks** | `projects/landing-fusion/` | Low — no existing tasks to break |
| 5. **Wire Formint tasks** | `projects/formints/` | Medium — existing sync tasks need migration |
| 6. **Migrate shared worker tasks** | `projects/configs/` | Medium — existing Celery tasks → Dramatiq |
| 7. **Remove Celery** | All projects | Medium — requires Docker/CI updates |
| 8. **Enable scheduler** | All projects | Low — APScheduler replaces Celery Beat |

---

## 12. Testing Strategy

### 12.1 django-fusion Task Tests

```python
# libs/django-fusion/tests/test_tasks.py

class TestTaskDecorator:
    def test_task_registers_with_registry(self):
        @task(queue="test")
        def my_task():
            pass
        assert "test_module.my_task" in task_registry._tasks

    def test_task_send_enqueues_to_backend(self):
        backend = InProcessBackend()
        task_registry.configure(backend)

        results = []
        @task(queue="test")
        def add_to_results(x):
            results.append(x)

        add_to_results.send(42)
        assert results == [42]

    def test_task_schedule_parsed(self):
        @task(schedule="0 */6 * * *")
        def periodic():
            pass
        assert task_registry._tasks["test_module.periodic"].schedule == "0 */6 * * *"


class TestBackgroundTaskLog:
    def test_log_created_on_send(self):
        ...

    def test_log_updated_on_completion(self):
        ...

    def test_log_captures_error(self):
        ...


class TestDramatiqBackend:
    def test_enqueue_creates_actor(self):
        ...

    def test_retry_on_failure(self):
        ...


class TestMCPHandlers:
    def test_inspect_returns_task_details(self):
        ...

    def test_history_filters_by_status(self):
        ...

    def test_retry_requeues_failed_task(self):
        ...

    def test_stats_computes_failure_rate(self):
        ...

    def test_purge_deletes_old_logs(self):
        ...
```

### 12.2 Project-Level Tests

```python
# projects/precis/backend/apps/tasks/tests/test_email_tasks.py

class TestEmailTasks:
    def test_send_enrollment_confirmation_enqueued(self):
        enrollment = EnrollmentFactory()
        task_id = send_enrollment_confirmation.send(enrollment.id)
        log = BackgroundTaskLog.objects.get(id=task_id)
        assert log.status in ("queued", "started", "finished")
        assert log.task_name == "precis.email.send_enrollment_confirmation"

    def test_send_certificate_generates_pdf(self):
        ...


class TestScheduledTasks:
    def test_weekly_digest_schedule_registered(self):
        reg = task_registry._tasks["precis.course.send_weekly_learning_digest"]
        assert reg.schedule == "0 9 * * 1"
```

---

## 13. Observability

### 13.1 Metrics

```python
# django_fusion/tasks/middleware.py

class TaskMetricsMiddleware:
    """Records Prometheus-compatible metrics for task execution."""

    def before_enqueue(self, task_name, queue):
        metrics.TASK_ENQUEUED.labels(task=task_name, queue=queue).inc()

    def after_completion(self, task_name, duration_ms, status):
        metrics.TASK_COMPLETED.labels(task=task_name, status=status).inc()
        metrics.TASK_DURATION.labels(task=task_name).observe(duration_ms)

    def on_failure(self, task_name, queue, error_type):
        metrics.TASK_FAILED.labels(task=task_name, queue=queue, error=error_type).inc()
        metrics.TASK_RETRY_COUNT.labels(task=task_name).inc()
```

### 13.2 Django Admin Dashboard

```python
# django_fusion/tasks/admin.py

@admin.register(BackgroundTaskLog)
class BackgroundTaskLogAdmin(admin.ModelAdmin):
    list_display = ["task_name", "status", "queue_name", "created_at", "duration_display"]
    list_filter = ["status", "queue_name", "task_name"]
    search_fields = ["task_name", "error_message"]
    readonly_fields = ["id", "task_name", "created_at", "started_at",
                        "completed_at", "retry_count", "error_message"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    def duration_display(self, obj):
        if obj.duration:
            return f"{obj.duration:.1f}s"
        return "—"
    duration_display.short_description = "Duration"

    actions = ["retry_selected", "cancel_selected"]

    def retry_selected(self, request, queryset):
        for log in queryset.filter(status="failed"):
            task_registry.send(log.task_name, *log.args, **log.kwargs)
        self.message_user(request, f"Re-queued {queryset.count()} tasks.")
```

---

## 14. Success Criteria

- [ ] **No Celery imports** remain in any project source (excluding CI migration scripts)
- [ ] `django_fusion.tasks` provides a `@task` decorator that works identically with Dramatiq and in-process backends
- [ ] All existing email, content, heartbeat, and cleanup tasks have been migrated to `@task`
- [ ] `BackgroundTaskLog` records every task execution with status, duration, and error details
- [ ] MCP tools (`task.inspect`, `task.queues`, `task.history`, `task.retry`, `task.trigger`, `task.stats`, `task.purge`, `task.workers`) return correct results
- [ ] Precis LMS has task modules for email, courses, content
- [ ] Landing-Fusion has task modules for email, content
- [ ] Formint has task modules for sync, reports
- [ ] APScheduler replaces Celery Beat for all scheduled work
- [ ] `docker-compose.tasks.yml` deploys a single `shared-worker` + `shared-scheduler`
- [ ] django-fusion task test suite passes (≥90% coverage on new code)
- [ ] Per-project task test suites pass
- [ ] Worker consolidation plan (Phases 1-4) is complete

---

## 15. Related Plans

| Plan | Path |
|---|---|
| Worker Consolidation | [`../repository/worker-consolidation.md`](../repository/worker-consolidation.md) |
| django-fusion POS Enhancements | [`django-fusion-enhancements.md`](django-fusion-enhancements.md) |
| Fusion Assets & Templates Cleanup | [`fusion-assets-templates-cleanup.md`](fusion-assets-templates-cleanup.md) |
| Codebase Audit & Migration | [`../CODEBASE_AUDIT_AND_MIGRATION_PLAN.md`](../CODEBASE_AUDIT_AND_MIGRATION_PLAN.md) |
| Feature Roadmap | [`../../features/feature-roadmap.md`](../../features/feature-roadmap.md) |
| Document Lifecycle | [`../document-lifecycle.md`](../document-lifecycle.md) |
| Canonical Plan Registry | [`../README.md`](../README.md) |
| Recommendations | [`../../recommendations.md`](../../recommendations.md) |
| LLM & AI MCP Enhancement | [`django-fusion-llm-mcp-enhancement-plan.md`](django-fusion-llm-mcp-enhancement-plan.md) |

---

*This plan is a living document. Update status and progress tracking as phases are completed.*
