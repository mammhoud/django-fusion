"""Dramatiq backend for django-fusion tasks."""

from __future__ import annotations

import json
import logging
import socket
import time
import traceback
import uuid
from urllib.parse import urlparse

from django_fusion.tasks.backends.base import AbstractTaskBackend

logger = logging.getLogger(__name__)

#: How long a broker probe result is reused before re-probing (seconds).
_BROKER_PROBE_TTL = 5.0


class DramatiqBackend(AbstractTaskBackend):
    """Dramatiq backend with durable execution auditing.

    The backend records every execution in **two** places:

    * the shared ``BackgroundTaskLog`` audit table (when the host project has
      migrated it — e.g. Precis's ``shared`` app), and
    * the product-local ``TaskExecution`` website record (when the project sets
      ``FUSION_TASK_EXECUTION_MODEL`` — e.g. ``core.TaskExecution``).

    A ``website``/``site`` keyword (or the resolved default site) is recorded in
    ``app_label_field``/``site_id`` on the shared record and ``site_name`` on
    the website record, so each product can filter its own task history.
    """

    #: Fail fast on a down broker before ``enqueue`` performs its Redis
    #: round-trip. Off by default; products opt in via ``FUSION_TASKS``
    #: (``GATE_ON_BROKER_REACHABLE: true``). Class-level so ``__new__``
    #: bypass instances (used by unit tests) default safely to off.
    gate_on_broker_reachable: bool = False

    def __init__(
        self,
        broker_url: str = "redis://localhost:6379/1",
        gate_on_broker_reachable: bool = False,
    ):
        self.broker_url = broker_url
        self.gate_on_broker_reachable = gate_on_broker_reachable
        self._broker_reachable_cache: tuple[float, bool] | None = None
        self._actors = {}
        self.broker = None
        try:
            import dramatiq
            from dramatiq.brokers.redis import RedisBroker

            # django-dramatiq may already have installed the application's
            # broker. The shared infrastructure path owns its broker, so set
            # it explicitly and make the configured Redis URL observable.
            self.broker = RedisBroker(url=broker_url)
            dramatiq.set_broker(self.broker)
        except (ImportError, RuntimeError):
            # Keep imports/test collection usable when the optional broker
            # dependency is absent; enqueue will surface the real error.
            logger.debug("Dramatiq Redis broker unavailable", exc_info=True)

    def broker_reachable(self, timeout: float = 0.4) -> bool:
        """Probe whether the configured broker answers, cached briefly.

        ``enqueue`` otherwise pays a Redis round-trip (and, with a down
        broker, a connection error) on every call. This probes once and
        reuses the answer for ``_BROKER_PROBE_TTL`` seconds so a down broker
        is skipped immediately instead of re-attempted per enqueue.
        """
        now = time.monotonic()
        if self._broker_reachable_cache is not None and now - self._broker_reachable_cache[0] < _BROKER_PROBE_TTL:
            return self._broker_reachable_cache[1]
        reachable = self._probe_broker(timeout)
        self._broker_reachable_cache = (now, reachable)
        return reachable

    def _probe_broker(self, timeout: float) -> bool:
        """Dependency-free TCP probe of the broker host/port."""
        try:
            parsed = urlparse(self.broker_url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 6379
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (OSError, TypeError, ValueError):
            return False

    def register_tasks(self, registry) -> None:
        """Declare every discovered fusion task as a Dramatiq actor.

        Dramatiq workers need actor declarations in the worker process, not
        only in the producer process. Registering after project-path discovery
        makes the shared worker consume the same task set that producers use.
        """
        for registration in registry._tasks.values():
            self._get_or_create_actor(registration)

    def enqueue(self, registration, args: tuple, kwargs: dict, options: dict | None = None) -> str:
        actor = self._get_or_create_actor(registration)
        job_id = str(uuid.uuid4())
        log_entry = self._create_log(
            registration,
            args=args,
            kwargs=kwargs,
            job_id=job_id,
            status="queued",
        )
        if self.gate_on_broker_reachable and not self.broker_reachable():
            error = "Queue publish failed: broker unreachable"
            self._update_log(
                log_entry,
                status="failed",
                error_message=error,
                error_traceback="broker unreachable",
            )
            self._touch_website_log(job_id, status="failed", error_message=error)
            raise ConnectionError(error)
        try:
            broker_options = dict(options or {})
            if broker_options:
                # Dramatiq's delayed/options API is keyword-only: positional
                # task arguments belong in ``args`` and task kwargs belong in
                # ``kwargs``. The non-delayed fast path keeps the ordinary
                # actor.send() call shape.
                message = actor.send_with_options(
                    args=args,
                    kwargs={**kwargs, "_fusion_job_id": job_id},
                    **broker_options,
                )
            else:
                message = actor.send(*args, _fusion_job_id=job_id, **kwargs)
        except Exception as exc:
            self._update_log(
                log_entry,
                status="failed",
                error_message=f"Queue publish failed: {exc}",
                error_traceback=traceback.format_exc(),
            )
            self._touch_website_log(
                job_id,
                status="failed",
                error_message=f"Queue publish failed: {exc}",
            )
            raise
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
        """Wrap the task function and update both durable audit records."""
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
            self._update_log(log_entry, status="started", started_at=self._now())
            self._touch_website_log(job_id, status="started", started_at=self._now())

            try:
                result = original(*args, **kwargs)
                self._update_log(
                    log_entry,
                    status="finished",
                    result=self._json_safe(result),
                    completed_at=self._now(),
                )
                self._touch_website_log(
                    job_id,
                    status="finished",
                    result=self._json_safe(result),
                    completed_at=self._now(),
                )
                return result
            except Exception as exc:
                self._update_log(
                    log_entry,
                    status="failed",
                    error_message=str(exc),
                    error_traceback=traceback.format_exc(),
                    completed_at=self._now(),
                )
                self._touch_website_log(
                    job_id,
                    status="failed",
                    error_message=str(exc),
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
    def _website_record_model():
        """Resolve the configured TaskExecution website-record model (or None)."""
        try:
            from django.conf import settings

            model_path = getattr(settings, "FUSION_TASK_EXECUTION_MODEL", "")
            if not model_path:
                return None
            from django.apps import apps

            if "." in model_path:
                app_label, model_name = model_path.rsplit(".", 1)
            else:
                app_label, model_name = model_path, "TaskExecution"
            return apps.get_model(app_label, model_name)
        except Exception:
            return None

    @staticmethod
    def _site_and_id(kwargs: dict) -> tuple[str, int | None]:
        """Resolve the (site_name, site_id) pair for a log record."""
        website = (
            kwargs.get("website")
            or kwargs.get("site")
            or DramatiqBackend._default_site()
        )
        site_id = kwargs.get("site_id")
        if site_id is None and isinstance(website, int):
            # ``site=<int>`` callers record the numeric site id directly.
            site_id = website
            website = ""
        return str(website), site_id

    @staticmethod
    def _create_log(registration, *, args, kwargs, job_id, status):
        website, site_id = DramatiqBackend._site_and_id(kwargs)
        shared = None
        try:
            from django_fusion.models.tasks import BackgroundTaskLog

            shared = BackgroundTaskLog.objects.create(
                id=uuid.uuid4(),
                job_id=job_id,
                task_name=registration.name,
                queue_name=registration.queue,
                args=list(args),
                kwargs=kwargs,
                status=status,
                backend="dramatiq",
                max_retries=registration.max_retries,
                site_id=site_id,
                app_label_field=website,
            )
        except Exception:
            # Task execution must remain available when an older consumer has
            # not migrated the audit table yet; the exception is logged without
            # masking the real queue/handler result.
            logger.warning("BackgroundTaskLog unavailable for %s", registration.name, exc_info=True)
        DramatiqBackend._create_website_log(registration, website, job_id, status)
        return shared

    @staticmethod
    def _create_website_log(registration, website: str, job_id: str | None, status: str):
        model = DramatiqBackend._website_record_model()
        if model is None or not job_id:
            return
        try:
            model.objects.update_or_create(
                job_id=job_id,
                defaults={
                    "task_name": registration.name,
                    "queue_name": registration.queue,
                    "site_name": website,
                    "status": status,
                    "created_at": DramatiqBackend._now(),
                },
            )
        except Exception:
            logger.debug("TaskExecution unavailable for %s", registration.name, exc_info=True)

    @staticmethod
    def _touch_website_log(job_id, **values):
        """Update the website TaskExecution record for an in-flight job."""
        if not job_id:
            return
        model = DramatiqBackend._website_record_model()
        if model is None:
            return
        allowed = {"status", "result", "error_message", "started_at", "completed_at"}
        fields = {key: value for key, value in values.items() if key in allowed}
        if not fields:
            return
        try:
            model.objects.filter(job_id=job_id).update(**fields)
        except Exception:
            logger.debug("Could not update TaskExecution %s", job_id, exc_info=True)

    @staticmethod
    def _default_site() -> str:
        """Resolve the owning website name for a log record.

        Priority: ``settings.FUSION_TASK_SITE_NAME`` → ``settings.WEBSITE_NAME``
        → ``settings.WEBSITE`` → the ``WEBSITE``/``DJANGO_WEBSITE`` env vars.
        This lets the shared worker stamp each product's jobs without every
        ``.send()`` call repeating the site keyword.
        """
        try:
            from django.conf import settings

            for attr in ("FUSION_TASK_SITE_NAME", "WEBSITE_NAME", "WEBSITE"):
                value = getattr(settings, attr, None)
                if value:
                    return str(value)
        except Exception:
            pass
        import os

        return os.environ.get("WEBSITE") or os.environ.get("DJANGO_WEBSITE") or ""

    @staticmethod
    def _update_log(log_entry, **values):
        if log_entry is None:
            return
        try:
            for key, value in values.items():
                setattr(log_entry, key, value)
            log_entry.save(update_fields=list(values))
        except Exception:
            logger.warning("Could not update BackgroundTaskLog %s", log_entry.pk, exc_info=True)
