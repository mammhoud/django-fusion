"""Reusable Task Center view and context helpers.

Products include this to render an authenticated task-execution history
page that merges two storage records:

* the shared ``BackgroundTaskLog`` audit trail (written by the task backend), and
* the product-local ``TaskExecution`` website record (configured through
  ``FUSION_TASK_EXECUTION_MODEL`` and kept in sync from the shared record).

Usage (per-product ``urls.py``)::

    from django.urls import path
    from django_fusion.tasks.views import TaskCenterView

    urlpatterns += [
        path(
            "tasks/",
            TaskCenterView.as_view(
                site_name="loop-crm",
                template_name="dashboard/tasks.html",
            ),
            name="tasks",
        ),
    ]

``site_name`` filters both records (``app_label_field`` / ``site_name``) so a
website only sees the jobs it owns.  When ``FUSION_TASK_EXECUTION_MODEL`` is
not configured the view renders the shared record only.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE = "django_fusion/tasks/task_center.html"


def resolve_default_site() -> str:
    """Resolve the owning website name using the same chain as the backend.

    Priority: ``settings.FUSION_TASK_SITE_NAME`` → ``settings.WEBSITE_NAME``
    → ``settings.WEBSITE`` → the ``WEBSITE``/``DJANGO_WEBSITE`` env vars.
    Keeping this chain identical to ``DramatiqBackend._default_site()`` means
    an empty ``site_name`` on the view always filters on exactly what the
    worker records.
    """
    try:
        for attr in ("FUSION_TASK_SITE_NAME", "WEBSITE_NAME", "WEBSITE"):
            value = getattr(settings, attr, None)
            if value:
                return str(value)
    except Exception:
        pass
    import os

    return os.environ.get("WEBSITE") or os.environ.get("DJANGO_WEBSITE") or ""


def _task_execution_model():
    """Resolve the configured TaskExecution website-record model (or None)."""
    model_path = getattr(settings, "FUSION_TASK_EXECUTION_MODEL", "")
    if not model_path:
        return None
    try:
        from django.apps import apps

        if "." in model_path:
            app_label, model_name = model_path.rsplit(".", 1)
        else:
            app_label, model_name = model_path, "TaskExecution"
        return apps.get_model(app_label, model_name)
    except Exception:
        logger.debug("TaskExecution model %r unavailable", model_path, exc_info=True)
        return None


def _shared_logs(site_name: str = "") -> list[Any]:
    """Read the shared BackgroundTaskLog audit trail, degrading to [] on error."""
    try:
        from django_fusion.models.tasks import BackgroundTaskLog
    except Exception:
        return []
    try:
        qs = BackgroundTaskLog.objects.all()
        if site_name:
            qs = qs.filter(app_label_field=site_name)
        return list(qs.order_by("-created_at")[:250])
    except Exception:
        logger.debug("BackgroundTaskLog unavailable in task center", exc_info=True)
        return []


def _website_logs(site_name: str = "") -> list[Any]:
    """Read the product-local TaskExecution website record, degrading to []."""
    model = _task_execution_model()
    if model is None:
        return []
    try:
        qs = model.objects.all()
        if site_name:
            qs = qs.filter(site_name=site_name)
        return list(qs.order_by("-created_at")[:250])
    except Exception:
        logger.debug("TaskExecution unavailable in task center", exc_info=True)
        return []


def sync_website_record(site_name: str = "") -> int:
    """Copy shared ``BackgroundTaskLog`` rows into the website ``TaskExecution``.

    Idempotent on ``job_id`` (falls back to the shared primary key when no job
    id exists).  Returns the number of records written.  This is the concrete
    "website record" persistence path: the shared worker writes the shared
    record, and the website mirrors it into its own database so the Task
    Center page never depends on the shared-infra database being reachable.
    """
    model = _task_execution_model()
    if model is None:
        return 0
    written = 0
    for log in _shared_logs(site_name):
        key = log.job_id or f"pk:{log.pk}"
        defaults = {
            "task_name": log.task_name,
            "queue_name": log.queue_name,
            "site_name": getattr(log, "app_label_field", "") or site_name,
            "status": log.status,
            "result": getattr(log, "result", None),
            "error_message": getattr(log, "error_message", "") or "",
            "created_at": getattr(log, "created_at", None),
            "started_at": getattr(log, "started_at", None),
            "completed_at": getattr(log, "completed_at", None),
        }
        try:
            model.objects.update_or_create(job_id=key, defaults=defaults)
            written += 1
        except Exception:
            logger.debug("Could not sync TaskExecution for %s", log.task_name, exc_info=True)
    return written


def merge_task_logs(shared: list[Any], website: list[Any]) -> list[Any]:
    """Merge shared and website records, deduped by job_id, newest first."""
    merged: dict[str, Any] = {}
    for log in website:
        merged[log.job_id or f"pk:{log.pk}"] = log
    for log in shared:
        merged.setdefault(log.job_id or f"pk:{log.pk}", log)

    def sort_key(row: Any) -> datetime:
        created = getattr(row, "created_at", None)
        return created if created is not None else datetime.min

    return sorted(merged.values(), key=sort_key, reverse=True)


def task_center_context(site_name: str = "", *, limit: int = 100) -> dict[str, Any]:
    """Return the context dict for a Task Center page."""
    sync_website_record(site_name)
    rows = merge_task_logs(_shared_logs(site_name), _website_logs(site_name))[:limit]
    return {
        "task_logs": rows,
        "site_name": site_name,
        "total": len(rows),
        "is_empty": not rows,
    }


class TaskCenterView(LoginRequiredMixin, TemplateView):
    """Authenticated task-execution history page.

    ``site_name`` filters both records; leave it empty to resolve the site
    from settings/env (the same chain the task backend stamps into each log).
    """

    template_name = DEFAULT_TEMPLATE
    site_name = ""
    limit = 100

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        site_name = self.site_name or resolve_default_site()
        context.update(task_center_context(site_name, limit=self.limit))
        return context
