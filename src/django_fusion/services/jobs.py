import logging
import traceback

from django.utils import timezone

logger = logging.getLogger(__name__)


def _get_task_log_model():
    """Load the optional task-log model only when a job is dispatched."""
    try:
        from django_fusion.models.tasks import BackgroundTaskLog
    except ImportError:
        return None
    return BackgroundTaskLog

def dispatch_job(func, *args, queue_name="default", **kwargs):
    """
    Enqueues a job and logs it in BackgroundTaskLog.
    """
    BackgroundTaskLog = _get_task_log_model()
    if BackgroundTaskLog is None:
        try:
            import django_rq
        except ImportError as exc:
            raise RuntimeError(
                "dispatch_job requires django-rq when no task-log model is configured"
            ) from exc
        return django_rq.get_queue(queue_name).enqueue(func, *args, **kwargs)

    try:
        # Create log entry
        log_entry = BackgroundTaskLog.objects.create(
            task_name=f"{func.__module__}.{func.__name__}",
            queue_name=queue_name,
            args=list(args),
            kwargs=kwargs,
            status="queued"
        )

        # Enqueue the job, passing the log_entry ID so the worker can update it
        import django_rq
        queue = django_rq.get_queue(queue_name)
        job = queue.enqueue(run_logged_job, *args, log_entry_id=str(log_entry.id), func=func, **kwargs)

        # Update log entry with job ID
        log_entry.job_id = job.id
        log_entry.save(update_fields=["job_id"])

        return job
    except Exception as e:
        logger.error(f"Failed to dispatch job {func.__name__}: {e}")
        raise e

def run_logged_job(log_entry_id, func, *args, **kwargs):
    """
    Wrapper function to run the actual job and update the log.
    """
    BackgroundTaskLog = _get_task_log_model()
    if BackgroundTaskLog is None:
        return func(*args, **kwargs)

    try:
        log_entry = BackgroundTaskLog.objects.get(id=log_entry_id)
        log_entry.status = "started"
        log_entry.started_at = timezone.now()
        log_entry.save(update_fields=["status", "started_at"])
    except BackgroundTaskLog.DoesNotExist:
        logger.warning(f"Log entry {log_entry_id} not found for job {func.__name__}")
        log_entry = None

    try:
        result = func(*args, **kwargs)

        if log_entry:
            log_entry.status = "finished"
            # Handle result if it's not serializable
            try:
                log_entry.result = result
            except Exception:
                log_entry.result = str(result)
            log_entry.completed_at = timezone.now()
            log_entry.save(update_fields=["status", "result", "completed_at"])

        return result
    except Exception as e:
        if log_entry:
            log_entry.status = "failed"
            log_entry.error_message = traceback.format_exc()
            log_entry.completed_at = timezone.now()
            log_entry.save(update_fields=["status", "error_message", "completed_at"])
        raise e
