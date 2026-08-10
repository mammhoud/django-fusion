"""Task middleware — logging, retry semantics, metrics hooks.

Middleware classes are composable wrappers that sit between the
``@task`` decorator and the backend adapter.  They fire before/after
every task execution.

Built-in middleware:

- ``LoggingMiddleware`` — records ``BackgroundTaskLog`` entries
  and updates their status across the lifecycle.
- ``RetryMiddleware`` — catches transient failures and re-enqueues
  according to the task's ``max_retries`` / ``min_backoff`` /
  ``max_backoff`` configuration.
"""

from __future__ import annotations

import logging
import time
import traceback
from typing import Any, Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Wraps a task callable so every execution is recorded in
    ``BackgroundTaskLog``."""

    def __init__(self, func: Callable, task_name: str, queue: str,
                 max_retries: int = 3, **_kw: Any):
        self._func = func
        self._task_name = task_name
        self._queue = queue
        self._max_retries = max_retries

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        from django_fusion.models.tasks import BackgroundTaskLog
        import uuid

        log_entry = BackgroundTaskLog.objects.create(
            id=uuid.uuid4(),
            task_name=self._task_name,
            queue_name=self._queue,
            args=list(args),
            kwargs=kwargs,
            status="started",
            max_retries=self._max_retries,
        )
        started = time.monotonic()

        try:
            result = self._func(*args, **kwargs)
            log_entry.status = "finished"
            try:
                log_entry.result = result
            except Exception:
                log_entry.result = str(result)
            log_entry.completed_at = log_entry.created_at.replace(
                microsecond=0
            )  # approximate
            log_entry.save(update_fields=["status", "result", "completed_at"])
            return result
        except Exception:
            log_entry.status = "failed"
            log_entry.error_message = traceback.format_exc()
            log_entry.completed_at = log_entry.created_at.replace(
                microsecond=0
            )
            log_entry.save(
                update_fields=["status", "error_message", "completed_at"]
            )
            raise
        finally:
            elapsed = (time.monotonic() - started) * 1000
            logger.debug(
                "Task %r finished in %.1f ms [%s]",
                self._task_name, elapsed, log_entry.status,
            )


class RetryMiddleware:
    """Re-enqueues a failed task with exponential backoff.

    Must be applied *outside* the ``LoggingMiddleware`` so the log
    entry reflects each individual attempt.
    """

    def __init__(self, func: Callable, task_name: str, queue: str,
                 max_retries: int = 3, min_backoff: int = 15_000,
                 max_backoff: int = 86_400_000, **_kw: Any):
        self._func = func
        self._task_name = task_name
        self._queue = queue
        self._max_retries = max_retries
        self._min_backoff = min_backoff
        self._max_backoff = max_backoff

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        attempt = kwargs.pop("_fusion_retry_attempt", 0)

        try:
            return self._func(*args, **kwargs)
        except Exception:
            if attempt >= self._max_retries:
                logger.error(
                    "Task %r exhausted %d retries.", self._task_name, attempt
                )
                raise

            delay = min(
                self._min_backoff * (2 ** attempt),
                self._max_backoff,
            )
            logger.warning(
                "Task %r failed (attempt %d/%d); retrying in %.0f ms.",
                self._task_name, attempt + 1, self._max_retries, delay,
            )

            # Re-enqueue with incremented attempt counter
            from django_fusion.tasks.registry import task_registry
            kwargs["_fusion_retry_attempt"] = attempt + 1
            task_registry.send(self._func, *args, **kwargs)
            return None  # signal that the attempt was deferred
