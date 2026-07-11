"""Optional Celery decorators used by the shared task package."""

from __future__ import annotations

import importlib
import importlib.util
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def shared_task(*dargs: Any, **dkwargs: Any):
    """Return Celery's shared_task when installed, otherwise a no-op decorator."""
    if importlib.util.find_spec("celery") is not None:
        celery_module = importlib.import_module("celery")
        return celery_module.shared_task(*dargs, **dkwargs)

    def decorator(func: F) -> F:
        return func

    if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
        return dargs[0]
    return decorator
