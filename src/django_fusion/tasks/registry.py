"""Task registry — discovery, registration, metadata."""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TaskRegistration:
    """Metadata for a registered background task."""

    func: Callable
    name: str
    module: str
    queue: str
    max_retries: int
    schedule: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)


class TaskRegistry:
    """Central registry for all background tasks across the project.

    Scans INSTALLED_APPS for ``tasks`` subpackages and registers
    tasks decorated with ``@task``. Provides a backend-independent
    ``.send()`` method.
    """

    def __init__(self):
        self._tasks: Dict[str, TaskRegistration] = {}
        self._backend = None
        self._discovered = False

    # ── configuration ──────────────────────────────────────────

    def configure(self, backend):
        """Wire the registry to a concrete backend.

        Args:
            backend: An :class:`AbstractTaskBackend` instance.
        """
        self._backend = backend

    @property
    def backend(self):
        return self._backend

    # ── registration ───────────────────────────────────────────

    def register(
        self,
        func: Callable,
        options,
        backend_kwargs: Optional[dict] = None,
    ):
        """Register a task function.

        Args:
            func: The decorated callable.
            options: A :class:`TaskOptions` instance.
            backend_kwargs: Extra kwargs forwarded to the backend.
        """
        if backend_kwargs is None:
            backend_kwargs = {}
        name = options.actor_name or f"{func.__module__}.{func.__name__}"
        merged = {
            "time_limit": options.time_limit,
            "min_backoff": options.min_backoff,
            "max_backoff": options.max_backoff,
            **backend_kwargs,
        }
        self._tasks[name] = TaskRegistration(
            func=func,
            name=name,
            module=func.__module__,
            queue=options.queue,
            max_retries=options.max_retries,
            schedule=options.schedule,
            options=merged,
        )

    # ── dispatch ───────────────────────────────────────────────

    def send(self, func: Callable, *args, **kwargs) -> Any:
        """Enqueue a registered task for background execution.

        Returns:
            Backend-specific message / job identifier.
        """
        if self._backend is None:
            raise RuntimeError(
                "TaskRegistry has no configured backend. "
                "Call task_registry.configure(backend) during app startup."
            )
        reg = self._lookup(func)
        return self._backend.enqueue(reg, args, kwargs)

    def run(self, func: Callable, *args, **kwargs) -> Any:
        """Run a registered task synchronously (for testing)."""
        reg = self._lookup(func)
        return reg.func(*args, **kwargs)

    # ── query ──────────────────────────────────────────────────

    def scheduled_tasks(self) -> List[TaskRegistration]:
        return [t for t in self._tasks.values() if t.schedule]

    def get(self, name: str) -> Optional[TaskRegistration]:
        return self._tasks.get(name)

    def list_tasks(self) -> List[str]:
        return sorted(self._tasks.keys())

    def task_count(self) -> int:
        return len(self._tasks)

    # ── discovery ──────────────────────────────────────────────

    def autodiscover(self):
        """Scan INSTALLED_APPS for ``tasks`` subpackages and import them.

        Each app's ``tasks`` package should import and decorate its
        task functions so they register themselves.
        """
        if self._discovered:
            return
        try:
            from django.conf import settings
        except Exception:
            self._discovered = True
            return

        for app in settings.INSTALLED_APPS:
            try:
                importlib.import_module(f"{app}.tasks")
            except ImportError:
                pass
        self._discovered = True

    # ── internal ───────────────────────────────────────────────

    def _lookup(self, func: Callable) -> TaskRegistration:
        # Direct match
        for reg in self._tasks.values():
            if reg.func is func:
                return reg
        # Unwrapped match
        for reg in self._tasks.values():
            if hasattr(func, "__wrapped__") and reg.func is func.__wrapped__:
                return reg
        # Module + name fallback
        for reg in self._tasks.values():
            if (
                reg.func.__module__ == getattr(func, "__module__", None)
                and reg.func.__name__ == getattr(func, "__name__", None)
            ):
                return reg
        raise KeyError(
            f"Task not registered: {getattr(func, '__name__', func)}. "
            f"Registered tasks: {sorted(self._tasks.keys())}"
        )


# Singleton
task_registry = TaskRegistry()
