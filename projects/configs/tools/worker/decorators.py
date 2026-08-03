"""Optional Celery decorators used by the shared task package.

Provides a drop-in ``shared_task`` decorator that gracefully falls back to
a no-op when Celery is not installed. This allows the ``www.worker.tasks``
module to define Celery tasks without creating a hard dependency on Celery
— Dramatiq-only deployments (the default) can ignore the Celery decorator
entirely while Celery-based deployments (e.g. ``shared-scheduler``) use the
real Celery implementation.

The fallback behavior:
- ``@shared_task`` with no arguments returns the decorated function unchanged.
- ``@shared_task(queue="...", ...)`` with arguments still returns the function
  unchanged when Celery is absent.
- ``shared_task(func)`` used as a bare decorator returns ``func`` directly.
"""

from __future__ import annotations

import importlib
import importlib.util
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def shared_task(*dargs: Any, **dkwargs: Any):
    """Decorate a function as a Celery shared task, or fall back to no-op.

    Uses ``importlib.util.find_spec("celery")`` to detect Celery at runtime
    rather than at import time, so the module can be safely imported even
    when Celery is not installed.

    Can be used as:

    **Bare decorator (no arguments)**
    .. code-block:: python

        @shared_task
        def my_task():
            ...

    **Decorator with arguments**
    .. code-block:: python

        @shared_task(queue="my-queue", bind=True)
        def my_task(self):
            ...

    Args:
        *dargs: Positional arguments forwarded to Celery's
            ``shared_task`` when Celery is available.
            If a single callable is passed as the only positional
            argument with no keyword arguments, it's treated as a
            bare decorator invocation (``shared_task(func)``).
        **dkwargs: Keyword arguments forwarded to Celery's
            ``shared_task`` (e.g. ``queue``, ``bind``, ``max_retries``).

    Returns:
        A Celery ``Task`` instance when Celery is installed,
        otherwise the original function unchanged.
    """
    if importlib.util.find_spec("celery") is not None:
        celery_module = importlib.import_module("celery")
        return celery_module.shared_task(*dargs, **dkwargs)

    def decorator(func: F) -> F:
        return func

    if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
        return dargs[0]
    return decorator
