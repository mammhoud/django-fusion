"""Dramatiq backend for django-fusion tasks."""

from __future__ import annotations

import logging

from django_fusion.tasks.backends.base import AbstractTaskBackend

logger = logging.getLogger(__name__)


class DramatiqBackend(AbstractTaskBackend):
    """Dramatiq backend for django-fusion tasks.

    Wraps ``dramatiq.actor()`` around registered tasks so the
    Dramatiq worker discovers and executes them.
    """

    def __init__(self, broker_url: str = "redis://localhost:6379/1"):
        self.broker_url = broker_url
        self._actors = {}

    def enqueue(self, registration, args: tuple, kwargs: dict) -> str:
        actor = self._get_or_create_actor(registration)
        message = actor.send(*args, **kwargs)
        return message.message_id

    # ── internal ───────────────────────────────────────────────

    def _get_or_create_actor(self, registration):
        import dramatiq

        actor_name = registration.name
        if actor_name in self._actors:
            return self._actors[actor_name]

        opts = registration.options
        actor = dramatiq.actor(
            actor_name=actor_name,
            queue_name=registration.queue,
            max_retries=opts.get("max_retries", 3),
            min_backoff=opts.get("min_backoff", 15000),
            max_backoff=opts.get("max_backoff", 86_400_000),
            time_limit=opts.get("time_limit", 1_800_000),
        )(self._wrap_with_logging(registration))

        self._actors[actor_name] = actor
        return actor

    def _wrap_with_logging(self, registration):
        """Wrap the task function with BackgroundTaskLog tracking."""
        original = registration.func

        def tracked(*args, **kwargs):
            from django_fusion.models.tasks import BackgroundTaskLog
            import uuid
            import traceback

            log_entry = BackgroundTaskLog.objects.create(
                id=uuid.uuid4(),
                task_name=registration.name,
                queue_name=registration.queue,
                args=list(args),
                kwargs=kwargs,
                status="started",
                backend="dramatiq",
                max_retries=registration.max_retries,
            )

            try:
                result = original(*args, **kwargs)
                log_entry.status = "finished"
                try:
                    log_entry.result = result
                except Exception:
                    log_entry.result = str(result)
                log_entry.save(
                    update_fields=["status", "result"]
                )
                return result
            except Exception:
                log_entry.status = "failed"
                log_entry.error_message = traceback.format_exc()
                log_entry.save(
                    update_fields=["status", "error_message"]
                )
                raise

        tracked.__name__ = original.__name__
        tracked.__module__ = original.__module__
        return tracked
