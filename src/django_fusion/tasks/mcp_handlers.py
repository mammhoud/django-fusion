"""MCP handlers — execute tool requests against the task system."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, Min, Avg, F
from django.utils import timezone


def handle_task_inspect(task_id=None, task_name=None):
    """Handler for task.inspect."""
    from django_fusion.models.tasks import BackgroundTaskLog

    if task_id:
        log = BackgroundTaskLog.objects.filter(id=task_id).first()
    elif task_name:
        log = BackgroundTaskLog.objects.filter(
            task_name=task_name
        ).order_by("-created_at").first()
    else:
        return {"error": "Provide task_id or task_name"}

    if not log:
        return {"error": "Task not found"}

    return {
        "task_id": str(log.id),
        "job_id": log.job_id,
        "task_name": log.task_name,
        "status": log.status,
        "queue": log.queue_name,
        "backend": log.backend,
        "retry_count": log.retry_count,
        "max_retries": log.max_retries,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "started_at": log.started_at.isoformat() if log.started_at else None,
        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        "duration_seconds": log.duration,
        "error": log.error_message[:500] if log.error_message else None,
    }


def handle_task_queues():
    """Handler for task.queues."""
    from django_fusion.models.tasks import BackgroundTaskLog

    pending_statuses = ["queued", "started", "retrying"]
    queue_counts = (
        BackgroundTaskLog.objects.filter(status__in=pending_statuses)
        .values("queue_name")
        .annotate(count=Count("id"), oldest=Min("created_at"))
        .order_by("-count")
    )

    return {
        "queues": [
            {
                "name": q["queue_name"],
                "pending": q["count"],
                "oldest_pending": (
                    q["oldest"].isoformat() if q["oldest"] else None
                ),
            }
            for q in queue_counts
        ],
        "total_pending": sum(q["count"] for q in queue_counts),
    }


def handle_task_history(
    status=None, queue=None, task_name=None, since=None, limit=20
):
    """Handler for task.history."""
    from django_fusion.models.tasks import BackgroundTaskLog

    qs = BackgroundTaskLog.objects.all()
    if status:
        qs = qs.filter(status=status)
    if queue:
        qs = qs.filter(queue_name=queue)
    if task_name:
        qs = qs.filter(task_name__icontains=task_name)
    if since:
        qs = qs.filter(created_at__gte=since)
    qs = qs[:limit]

    return {
        "results": [
            {
                "id": str(log.id),
                "name": log.task_name,
                "status": log.status,
                "queue": log.queue_name,
                "backend": log.backend,
                "created": log.created_at.isoformat() if log.created_at else None,
                "duration": log.duration,
                "error": (
                    log.error_message[:200] if log.error_message else None
                ),
            }
            for log in qs
        ],
        "count": len(qs),
        "total_matching": qs.count(),
    }


def handle_task_retry(task_id):
    """Handler for task.retry."""
    from django_fusion.models.tasks import BackgroundTaskLog
    from django_fusion.tasks.registry import task_registry

    log = BackgroundTaskLog.objects.filter(
        id=task_id, status="failed"
    ).first()
    if not log:
        return {"error": "Task not found or not in failed state"}

    reg = task_registry.get(log.task_name)
    if not reg:
        return {
            "error": f"Task '{log.task_name}' is not registered",
            "available": task_registry.list_tasks()[:20],
        }

    msg_id = task_registry.send(reg.func, *log.args, **log.kwargs)
    return {"status": "re-queued", "message_id": str(msg_id)}


def handle_task_trigger(task_name, args=None, kwargs=None):
    """Handler for task.trigger."""
    from django_fusion.tasks.registry import task_registry

    reg = task_registry.get(task_name)
    if not reg:
        return {
            "error": f"Task '{task_name}' not found",
            "available_tasks": task_registry.list_tasks()[:20],
        }

    msg_id = task_registry.send(reg.func, *(args or []), **(kwargs or {}))
    return {"status": "triggered", "message_id": str(msg_id)}


def handle_task_stats(period="24h"):
    """Handler for task.stats."""
    from django_fusion.models.tasks import BackgroundTaskLog

    deltas = {
        "1h": timedelta(hours=1),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
    }
    since = timezone.now() - deltas.get(period, timedelta(hours=24))

    qs = BackgroundTaskLog.objects.filter(created_at__gte=since)
    total = qs.count()

    by_status = dict(
        qs.values("status").annotate(count=Count("id")).values_list(
            "status", "count"
        )
    )

    failed = by_status.get("failed", 0)
    failure_rate = round(failed / max(total, 1) * 100, 1)

    completed = qs.exclude(completed_at=None).filter(started_at__isnull=False)
    avg_duration = completed.aggregate(
        avg=Avg(F("completed_at") - F("started_at"))
    )["avg"]

    return {
        "period": period,
        "total": total,
        "by_status": by_status,
        "failure_rate": failure_rate,
        "avg_duration_seconds": (
            avg_duration.total_seconds() if avg_duration else None
        ),
    }


def handle_task_purge(older_than_days=30, status="finished"):
    """Handler for task.purge."""
    from django_fusion.models.tasks import BackgroundTaskLog

    since = timezone.now() - timedelta(days=older_than_days)
    deleted, _ = BackgroundTaskLog.objects.filter(
        status=status, created_at__lt=since
    ).delete()
    return {
        "deleted_count": deleted,
        "older_than_days": older_than_days,
        "status": status,
    }


def handle_task_workers():
    """Handler for task.workers."""
    return {
        "backend": "django_fusion.tasks",
        "note": "Worker introspection requires the active broker runtime.",
    }
