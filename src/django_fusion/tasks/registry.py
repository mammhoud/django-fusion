"""Task registry — discovery, registration, metadata."""

from __future__ import annotations

import importlib
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
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

    Scans configured ``plugins/workers`` packages and Django app ``tasks``
    compatibility modules, then registers
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
            "max_retries": options.max_retries,
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

        ``_fusion_options`` is reserved for broker options such as Dramatiq's
        millisecond ``delay``. It is removed before the task function receives
        its serialized arguments.
        """
        if self._backend is None:
            raise RuntimeError(
                "TaskRegistry has no configured backend. "
                "Call task_registry.configure(backend) during app startup."
            )
        reg = self._lookup(func)
        broker_options = kwargs.pop("_fusion_options", None) or {}
        return self._backend.enqueue(reg, args, kwargs, options=broker_options)

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

    def autodiscover(
        self,
        project_paths: Optional[list[str]] = None,
        modules: Optional[list[str]] = None,
    ) -> list[str]:
        """Import task packages from Django apps and configured project paths.

        ``FUSION_TASK_PROJECT_PATHS`` makes one shared worker independent of a
        product's settings package. Each entry may be a filesystem path to a
        project/backend directory (or directly to a ``plugins/workers``
        package), while ``FUSION_TASK_MODULES`` accepts dotted packages. This
        is useful
        for infrastructure workers that must load active applications without
        importing a retired product's task tree.

        Returns the successfully imported module names. Import errors are
        logged and skipped so one optional product cannot prevent the worker
        from serving the remaining task packages.
        """
        if self._discovered:
            return []

        discovered: list[str] = []
        configured_paths = project_paths or self._setting_list(
            "FUSION_TASK_PROJECT_PATHS"
        )
        configured_modules = modules or self._setting_list("FUSION_TASK_MODULES")

        for project_path in configured_paths:
            module_name = self._import_project_path(project_path)
            if module_name:
                discovered.append(module_name)

        for module_name in configured_modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                logger.warning("Could not import configured task module %r", module_name)
            else:
                discovered.append(module_name)

        try:
            from django.conf import settings
            installed_apps = settings.INSTALLED_APPS
        except Exception:
            installed_apps = ()

        for app in installed_apps:
            try:
                importlib.import_module(f"{app}.tasks")
            except ImportError:
                pass
            else:
                discovered.append(f"{app}.tasks")

        self._discovered = True
        backend = self._backend
        register_tasks = getattr(backend, "register_tasks", None)
        if callable(register_tasks):
            register_tasks(self)
        return discovered

    @staticmethod
    def _setting_list(name: str) -> list[str]:
        """Read a list setting from Django or a comma-separated environment variable."""
        try:
            from django.conf import settings
            value = getattr(settings, name, None)
        except Exception:
            value = None
        if value is None:
            value = os.getenv(name, "")
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [str(item) for item in value or []]

    def _import_project_path(self, raw_path: str) -> str | None:
        """Import a ``plugins.workers`` package rooted at a project path."""
        path = Path(raw_path).expanduser()
        if not path.exists():
            logger.warning("Configured task project path does not exist: %s", path)
            return None

        worker_dir = path
        if path.name not in {"workers", "tasks"}:
            candidates = (
                path / "plugins" / "workers",
                path / "backend" / "plugins" / "workers",
                path / "apps" / "tasks",
                path / "backend" / "apps" / "tasks",
                path / "tasks",
            )
            worker_dir = next(
                (candidate for candidate in candidates if candidate.is_dir()),
                path,
            )
        if worker_dir.name not in {"workers", "tasks"} or not worker_dir.is_dir():
            logger.warning("No worker package found below configured path: %s", path)
            return None

        package_root = worker_dir.parent.parent
        package_root_text = str(package_root)
        if package_root_text not in sys.path:
            sys.path.insert(0, package_root_text)
        module_name = f"{worker_dir.parent.name}.{worker_dir.name}"

        # Every product intentionally uses the same package contract
        # (``plugins.workers``). Before importing the next filesystem package,
        # clear only the colliding product namespaces so importlib resolves the
        # requested path rather than the first product already cached in
        # ``sys.modules``. The decorated functions retain their canonical
        # module names, so producers and the shared worker use identical actor
        # names.
        existing = sys.modules.get(module_name)
        existing_file = getattr(existing, "__file__", "") if existing else ""
        if existing_file and not Path(existing_file).resolve().is_relative_to(
            package_root.resolve()
        ):
            for cached_name in tuple(sys.modules):
                if cached_name == "plugins" or cached_name.startswith("plugins."):
                    del sys.modules[cached_name]
                elif cached_name == "apps" or cached_name.startswith("apps."):
                    del sys.modules[cached_name]

        try:
            package = importlib.import_module(module_name)
        except ImportError:
            logger.warning("Could not import configured worker package %r", module_name)
            return None

        # A workers package may expose a tuple/list of concrete modules. This
        # keeps one filesystem path sufficient for a shared worker while still
        # allowing each product to split actors by domain.
        for child_module in getattr(package, "TASK_MODULES", ()):
            try:
                importlib.import_module(child_module)
            except ImportError:
                logger.warning("Could not import configured worker module %r", child_module)
        return module_name

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
