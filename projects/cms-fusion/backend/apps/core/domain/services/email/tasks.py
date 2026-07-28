"""
Celery configuration and task definitions for Django Relay.

Provides Celery app configuration and common task definitions.
"""

import logging

from celery import Celery, shared_task
from django.conf import settings

logger = logging.getLogger(__name__)

# Create Celery app
app = Celery('shared')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()


@shared_task(bind=True, max_retries=3)
def send_email_task(self, log_id: int, recipient: str, subject: str,
                    template_name: str, context: dict = None):
    """
    Celery task for sending emails.

    Args:
        log_id: EmailLog ID
        recipient: Email address
        subject: Email subject
        template_name: Template file path
        context: Template context variables

    Returns:
        EmailLog ID
    """
    from apps.core.domain.services.email.email_service import EmailService
    from apps.core.domain.services.email.models import EmailLog

    try:
        log = EmailLog.objects.get(id=log_id)
        service = EmailService()

        service._send_now(
            recipient=recipient,
            subject=subject,
            template_name=template_name,
            context=context or {},
            log=log
        )

        logger.info(f"Email sent successfully: {recipient}")
        return log_id

    except EmailLog.DoesNotExist:
        logger.error(f"EmailLog not found: {log_id}")
        raise

    except Exception as exc:
        logger.error(f"Email send failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task
def process_queued_emails():
    """
    Process all queued emails.

    Sends all emails with status QUEUED.
    """
    from apps.core.domain.services.email.email_service import EmailService
    from apps.core.domain.services.email.models import EmailLog

    queued_logs = EmailLog.objects.filter(status=EmailLog.Status.QUEUED)
    service = EmailService()

    for log in queued_logs:
        try:
            service._send_now(
                recipient=log.recipient,
                subject=log.subject,
                template_name=log.template_used,
                context={},
                log=log
            )
        except Exception as e:
            logger.error(f"Failed to send email {log.id}: {e}")

    logger.info(f"Processed {queued_logs.count()} queued emails")


@shared_task
def retry_failed_emails():
    """
    Retry failed emails.

    Retries emails with status FAILED up to max retries.
    """
    from apps.core.domain.services.email.email_service import EmailService
    from apps.core.domain.services.email.models import EmailLog

    max_retries = getattr(settings, 'EMAIL_MAX_RETRIES', 3)
    failed_logs = EmailLog.objects.filter(
        status=EmailLog.Status.FAILED,
        retry_count__lt=max_retries
    )
    service = EmailService()

    for log in failed_logs:
        try:
            log.increment_retry()
            service._send_now(
                recipient=log.recipient,
                subject=log.subject,
                template_name=log.template_used,
                context={},
                log=log
            )
        except Exception as e:
            logger.error(f"Failed to retry email {log.id}: {e}")

    logger.info(f"Retried {failed_logs.count()} failed emails")
