"""In-process backend — runs tasks synchronously.  For tests and dev."""

from __future__ import annotations

from django_fusion.tasks.backends.base import AbstractTaskBackend


class InProcessBackend(AbstractTaskBackend):
    """Runs tasks synchronously in the calling thread.

    Intended for unit tests and local development.  No broker
    dependency required.
    """

    def enqueue(self, registration, args: tuple, kwargs: dict, options: dict | None = None) -> str:
        _log_start(registration.name, args, kwargs)
        try:
            result = registration.func(*args, **kwargs)
            _log_finish(registration.name, result)
            return "inprocess"
        except Exception:
            _log_failure(registration.name)
            raise


def _log_start(name, args, kwargs):
    try:
        from django_fusion.models.tasks import BackgroundTaskLog
        import uuid
        BackgroundTaskLog.objects.create(
            id=uuid.uuid4(),
            task_name=name,
            queue_name="inprocess",
            args=list(args),
            kwargs=kwargs,
            status="started",
            backend="inprocess",
        )
    except Exception:
        pass


def _log_finish(name, result):
    try:
        from django_fusion.models.tasks import BackgroundTaskLog
        log = BackgroundTaskLog.objects.filter(
            task_name=name, status="started"
        ).order_by("-created_at").first()
        if log:
            log.status = "finished"
            try:
                log.result = result
            except Exception:
                log.result = str(result)
            log.save(update_fields=["status", "result"])
    except Exception:
        pass


def _log_failure(name):
    try:
        from django_fusion.models.tasks import BackgroundTaskLog
        import traceback
        log = BackgroundTaskLog.objects.filter(
            task_name=name, status="started"
        ).order_by("-created_at").first()
        if log:
            log.status = "failed"
            log.error_message = traceback.format_exc()
            log.save(update_fields=["status", "error_message"])
    except Exception:
        pass
