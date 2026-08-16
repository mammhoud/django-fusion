"""Email queue manager backed exclusively by django-fusion Dramatiq."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EmailQueueManager:
    """Create EmailLog records and enqueue Precis email workers."""

    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 300, 900]

    def __init__(self):
        self.backend = "dramatiq"

    @staticmethod
    def _task():
        from plugins.workers.legacy_email_tasks import send_email_task

        return send_email_task

    def queue_email(
        self,
        recipient: str,
        subject: str,
        template_name: str,
        context: dict[str, Any],
        group_name: str = "",
    ):
        from apps.domain.services.email.models import EmailLog

        log = EmailLog.objects.create(
            recipient=recipient,
            subject=subject,
            template_used=template_name,
            status=EmailLog.Status.QUEUED,
            group_name=group_name,
        )
        try:
            message_id = self._task().send(
                log.id,
                recipient,
                subject,
                template_name,
                context,
            )
        except Exception:
            log.status = EmailLog.Status.FAILED
            log.save(update_fields=["status"])
            raise

        log.task_id = message_id
        log.save(update_fields=["task_id"])
        logger.info("Email queued: %s - %s (task_id=%s)", recipient, subject, message_id)
        return log

    def retry_failed_email(self, log_id: int) -> bool:
        from apps.domain.services.email.models import EmailLog

        try:
            log = EmailLog.objects.get(id=log_id)
        except EmailLog.DoesNotExist:
            logger.error("EmailLog not found: %s", log_id)
            return False

        if log.retry_count >= self.MAX_RETRIES:
            logger.warning("Max retries reached for log %s", log_id)
            return False

        delay = self.RETRY_DELAYS[min(log.retry_count, len(self.RETRY_DELAYS) - 1)]
        log.increment_retry()
        message_id = self._task().send(
            log.id,
            log.recipient,
            log.subject,
            log.template_used,
            {},
            _fusion_options={"delay": delay * 1000},
        )
        log.task_id = message_id
        log.status = log.Status.QUEUED
        log.save(update_fields=["task_id", "status"])
        logger.info("Email retry queued: log_id=%s delay=%ss", log_id, delay)
        return True

    def schedule_periodic_task(self, name: str, func: str, schedule_type: str = "D", repeats: int = -1):
        """Deprecated Django-Q API; schedules belong on ``@task(schedule=...)``."""
        logger.warning(
            "schedule_periodic_task(%s) is deprecated; migrate %s to a Dramatiq @task schedule",
            name,
            func,
        )
        return None
