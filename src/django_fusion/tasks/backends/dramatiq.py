"""Dramatiq backend for django-fusion tasks."""

from __future__ import annotations

import json
import logging
import traceback
import uuid

from django_fusion.tasks.backends.base import AbstractTaskBackend

logger = logging.getLogger(__name__)


class DramatiqBackend(AbstractTaskBackend):
    """Dramatiq backend with durable execution auditing.

    The backend creates a queued ``BackgroundTaskLog`` before publishing and
    updates the same row while the worker executes. A ``website`` or ``site``
    keyword is recorded in ``app_label_field`` so each product can filter its
    own task history without running a product-specific worker container.
    """

    def __init__(self, broker_url: str = "redis://localhost:6379/1"):
        self.broker_url = broker_url
        self._actors = {}

    def enqueue(self, registration, args: tuple, kwargs: dict) -> str:
        actor = self._get_or_create_actor(registration)
        job_id = str(uuid.uuid4())
        log_entry = self._create_log(
            registration,
            args=args,
            kwargs=kwargs,
            job_id=job_id,
            status="queued",
        )
        try:
            message = actor.send(*args, _fusion_job_id=job_id, **kwargs)
        except Exception as exc:
            if log_entry is not None:
                self._update_log(
                    log_entry,
                    status="failed",
                    error_message=f"Queue publish failed: {exc}",
                    error_traceback=traceback.format_exc(),
                )
            raise
        if log_entry is not None:
            self._update_log(log_entry, job_id=message.message_id)
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
        """Wrap the task function and update one durable audit record."""
        original = registration.func

        def tracked(*args, **kwargs):
            job_id = kwargs.pop("_fusion_job_id", None)
            log_entry = self._get_log(job_id)
            if log_entry is None:
                log_entry = self._create_log(
                    registration,
                    args=args,
                    kwargs=kwargs,
                    job_id=job_id,
                    status="started",
                )
            if log_entry is not None:
                self._update_log(
                    log_entry,
                    status="started",
                    started_at=self._now(),
                )

            try:
                result = original(*args, **kwargs)
                if log_entry is not None:
                    self._update_log(
                        log_entry,
                        status="finished",
                        result=self._json_safe(result),
                        completed_at=self._now(),
                    )
                return result
            except Exception as exc:
                if log_entry is not None:
                    self._update_log(
                        log_entry,
                        status="failed",
                        error_message=str(exc),
                        error_traceback=traceback.format_exc(),
                        completed_at=self._now(),
                    )
                raise

        tracked.__name__ = original.__name__
        tracked.__module__ = original.__module__
        return tracked

    @staticmethod
    def _now():
        from django.utils import timezone

        return timezone.now()

    @staticmethod
    def _json_safe(value):
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            return str(value)
        return value

    @staticmethod
    def _get_log(job_id):
        if not job_id:
            return None
        try:
            from django_fusion.models.tasks import BackgroundTaskLog

            return BackgroundTaskLog.objects.filter(job_id=job_id).first()
        except Exception:
            logger.debug("BackgroundTaskLog unavailable while reading job %s", job_id, exc_info=True)
            return None

    @staticmethod
    def _create_log(registration, *, args, kwargs, job_id, status):
        try:
            from django_fusion.models.tasks import BackgroundTaskLog

            website = kwargs.get("website") or kwargs.get("site") or ""
            return BackgroundTaskLog.objects.create(
                id=uuid.uuid4(),
                job_id=job_id,
                task_name=registration.name,
                queue_name=registration.queue,
                args=list(args),
                kwargs=kwargs,
                status=status,
                backend="dramatiq",
                max_retries=registration.max_retries,
                app_label_field=str(website),
            )
        except Exception:
            # Task execution must remain available when an older consumer has
            # not migrated the audit table yet; the exception is logged without
            # masking the real queue/handler result.
            logger.warning("BackgroundTaskLog unavailable for %s", registration.name, exc_info=True)
            return None

    @staticmethod
    def _update_log(log_entry, **values):
        try:
            for key, value in values.items():
                setattr(log_entry, key, value)
            log_entry.save(update_fields=list(values))
        except Exception:
            logger.warning("Could not update BackgroundTaskLog %s", log_entry.pk, exc_info=True)
