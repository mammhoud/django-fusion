"""Precis email background jobs (Dramatiq/django-fusion tasks).

Queued by ``apps.domain.services.email.queue_manager.EmailQueueManager``
(``_task()`` imports ``send_email_task`` from this module). Renders and sends
one ``EmailLog`` record per execution; retry/backoff handled by the broker.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="email", max_retries=3, min_backoff=2_000, actor_name="precis.email.send")
def send_email_task(
    log_id: int,
    recipient: str,
    subject: str,
    template_name: str,
    context: dict | None = None,
) -> int:
    """Render and send one queued EmailLog record."""
    from apps.domain.services.email.email_service import EmailService
    from apps.domain.services.email.models import EmailLog

    log = EmailLog.objects.get(id=log_id)
    EmailService()._send_now(
        recipient=recipient,
        subject=subject,
        template_name=template_name,
        context=context or {},
        log=log,
    )
    logger.info("Email sent successfully: %s", recipient)
    return log_id


@task(queue="email", max_retries=1, actor_name="precis.email.process_queued")
def process_queued_emails() -> int:
    """Process all queued EmailLog rows once."""
    from apps.domain.services.email.email_service import EmailService
    from apps.domain.services.email.models import EmailLog

    logs = list(EmailLog.objects.filter(status=EmailLog.Status.QUEUED))
    service = EmailService()
    for log in logs:
        try:
            service._send_now(
                recipient=log.recipient,
                subject=log.subject,
                template_name=log.template_used,
                context={},
                log=log,
            )
        except Exception:
            logger.exception("Failed to send queued email %s", log.pk)
    logger.info("Processed %d queued emails", len(logs))
    return len(logs)


@task(queue="email", max_retries=1, actor_name="precis.email.retry_failed")
def retry_failed_emails() -> int:
    """Retry failed EmailLog rows until the configured limit is reached."""
    from apps.domain.services.email.email_service import EmailService
    from apps.domain.services.email.models import EmailLog

    limit = getattr(settings, "EMAIL_MAX_RETRIES", 3)
    logs = list(
        EmailLog.objects.filter(
            status=EmailLog.Status.FAILED,
            retry_count__lt=limit,
        )
    )
    service = EmailService()
    for log in logs:
        try:
            log.increment_retry()
            service._send_now(
                recipient=log.recipient,
                subject=log.subject,
                template_name=log.template_used,
                context={},
                log=log,
            )
        except Exception:
            logger.exception("Failed to retry email %s", log.pk)
    logger.info("Retried %d failed emails", len(logs))
    return len(logs)


__all__ = [
    "send_email_task",
    "process_queued_emails",
    "retry_failed_emails",
]
