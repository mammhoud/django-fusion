"""
django_fusion.tasks — Unified background-task API.

Provides broker-agnostic task registration, backends (Dramatiq, RQ, in-process),
MCP tooling for AI-driven task management, and an async email backend.

Usage::

    from django_fusion.tasks import task, task_registry

    @task(queue="email", max_retries=5)
    def send_welcome_email(user_id: int):
        ...

    send_welcome_email.send(user_id=42)

Auto-configuration::

    # settings.py
    FUSION_TASKS = {
        "BACKEND": "django_fusion.tasks.backends.dramatiq.DramatiqBackend",
        "BROKER_URL": "redis://localhost:6379/1",
        "TASK_ALWAYS_EAGER": False,
        "LOG_ALL_TASKS": True,
    }

The backend is wired during Django's ``AppConfig.ready()``.
"""

import os

from django_fusion.tasks.backends.base import AbstractTaskBackend
from django_fusion.tasks.backends.inprocess import InProcessBackend
from django_fusion.tasks.decorators import TaskOptions, task
from django_fusion.tasks.registry import TaskRegistration, TaskRegistry, task_registry

__all__ = [
    "task",
    "TaskOptions",
    "TaskRegistry",
    "TaskRegistration",
    "task_registry",
    "AbstractTaskBackend",
    "InProcessBackend",
]


# Register the scheduled task-history sync.  Imported here so
# ``task_registry.autodiscover()`` (which imports ``django_fusion.tasks``) also
# registers the periodic ``sync_task_history`` job.
from django_fusion.tasks.sync import sync_task_history  # noqa: E402, F401

__all__.append("sync_task_history")


def _configure_from_settings():
    """Wire the task_registry backend from ``FUSION_TASKS`` Django setting.

    Called during :meth:`AppConfig.ready()`.  Falls back to
    :class:`InProcessBackend` when no backend is configured (safe for
    tests and development).
    """
    if task_registry.backend is not None:
        return  # already configured

    from importlib import import_module

    try:
        from django.conf import settings
        fusion_tasks = getattr(settings, "FUSION_TASKS", None) or {}
    except Exception:
        fusion_tasks = {}

    backend_path = fusion_tasks.get(
        "BACKEND",
        "django_fusion.tasks.backends.dramatiq.DramatiqBackend",
    )
    broker_url = (
        fusion_tasks.get("BROKER_URL")
        or os.getenv("DRAMATIQ_BROKER_URL")
        or os.getenv("REDIS_URL")
        or "redis://localhost:6379/1"
    )

    try:
        module_name, class_name = backend_path.rsplit(".", 1)
        module = import_module(module_name)
        backend_cls = getattr(module, class_name)
    except Exception:
        task_registry.configure(InProcessBackend())
        return

    try:
        if "InProcess" in class_name:
            backend = backend_cls()
        else:
            backend = backend_cls(broker_url=broker_url)
        task_registry.configure(backend)
    except Exception:
        task_registry.configure(InProcessBackend())
