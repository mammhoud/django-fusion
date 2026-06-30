"""
Email Queue Manager for background email processing.

Manages email queue using Django Q or Celery.
Handles task queuing, retries, and scheduling.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class EmailQueueManager:
    """
    Manages email queue using Django Q or Celery.
    Handles task queuing, retries, and scheduling.
    """

    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min (exponential backoff)

    def __init__(self):
        self.logger = logger
        self._check_queue_backend()

    def _check_queue_backend(self):
        """Check which queue backend is available."""
        try:
            self.backend = 'django_q'
            logger.info("Using Django Q as queue backend")
        except ImportError:
            try:
                self.backend = 'celery'
                logger.info("Using Celery as queue backend")
            except ImportError:
                self.backend = None
                logger.warning("No queue backend available (Django Q or Celery)")

    def queue_email(
        self,
        recipient: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        group_name: str = ''
    ):
        """
        Queue an email for background processing.

        Args:
            recipient: Email address
            subject: Email subject
            template_name: Template file path
            context: Template context variables
            group_name: Optional group name

        Returns:
            EmailLog instance
        """
        from ceptor_ai.communication.email.models import EmailLog

        # Create log entry
        log = EmailLog.objects.create(
            recipient=recipient,
            subject=subject,
            template_used=template_name,
            status=EmailLog.Status.QUEUED,
            group_name=group_name
        )

        if self.backend == 'django_q':
            task_id = self._queue_with_django_q(log, recipient, subject, template_name, context)
        elif self.backend == 'celery':
            task_id = self._queue_with_celery(log, recipient, subject, template_name, context)
        else:
            # No queue backend - send immediately
            logger.warning("No queue backend available, sending email immediately")
            from .email_service import EmailService
            email_service = EmailService()
            email_service._send_now(recipient, subject, template_name, context, log)
            return log

        log.task_id = task_id
        log.save(update_fields=['task_id'])

        logger.info(f"Email queued: {recipient} - {subject} (task_id: {task_id})")

        return log

    def _queue_with_django_q(self, log, recipient, subject, template_name, context):
        """Queue email using Django Q."""
        from django_q.tasks import async_task

        task_id = async_task(
            'ceptor_ai.tasks.django_q.send_email_task',
            log.id,
            recipient,
            subject,
            template_name,
            context,
            hook='ceptor_ai.tasks.django_q.email_sent_hook',
            group='email',
            timeout=300  # 5 minutes
        )
        return task_id

    def _queue_with_celery(self, log, recipient, subject, template_name, context):
        """Queue email using Celery."""
        try:
            from ceptor_ai.communication.tasks.celery import send_email_task

            # Check if send_email_task is a Celery task (has .delay method)
            if hasattr(send_email_task, 'delay'):
                result = send_email_task.delay(
                    log.id,
                    recipient,
                    subject,
                    template_name,
                    context
                )
                return result.id
            else:
                # Celery not properly configured, fall back to immediate sending
                logger.warning("Celery task not properly decorated, sending immediately")
                from .email_service import EmailService
                email_service = EmailService()
                email_service._send_now(recipient, subject, template_name, context, log)
                return f"immediate-{log.id}"
        except Exception as e:
            logger.warning(f"Celery queuing failed: {e}, sending immediately")
            from .email_service import EmailService
            email_service = EmailService()
            email_service._send_now(recipient, subject, template_name, context, log)
            return f"immediate-{log.id}"

    def retry_failed_email(self, log_id: int) -> bool:
        """
        Retry a failed email send.

        Args:
            log_id: EmailLog ID

        Returns:
            True if retry was queued, False if max retries reached
        """
        from ceptor_ai.communication.email.models import EmailLog

        try:
            log = EmailLog.objects.get(id=log_id)
        except EmailLog.DoesNotExist:
            logger.error(f"EmailLog not found: {log_id}")
            return False

        if log.retry_count >= self.MAX_RETRIES:
            logger.warning(f"Max retries reached for log {log_id}")
            return False

        # Calculate delay based on retry count
        delay = self.RETRY_DELAYS[min(log.retry_count, len(self.RETRY_DELAYS) - 1)]

        # Increment retry count
        log.increment_retry()

        if self.backend == 'django_q':
            self._retry_with_django_q(log, delay)
        elif self.backend == 'celery':
            self._retry_with_celery(log, delay)
        else:
            logger.warning("No queue backend available for retry")
            return False

        logger.info(f"Email retry queued: log_id={log_id}, retry_count={log.retry_count}, delay={delay}s")

        return True

    def _retry_with_django_q(self, log, delay):
        """Retry email using Django Q."""
        from django_q.tasks import async_task

        task_id = async_task(
            'ceptor_ai.tasks.django_q.send_email_task',
            log.id,
            log.recipient,
            log.subject,
            log.template_used,
            {},  # Context should be stored in log if needed
            hook='ceptor_ai.tasks.django_q.email_sent_hook',
            group='email',
            timeout=300,
            schedule_type='O',  # Once
            next_run=delay
        )

        log.task_id = task_id
        log.status = log.Status.QUEUED
        log.save(update_fields=['task_id', 'status'])

    def _retry_with_celery(self, log, delay):
        """Retry email using Celery."""
        from ceptor_ai.communication.tasks.celery import send_email_task

        result = send_email_task.apply_async(
            args=[log.id, log.recipient, log.subject, log.template_used, {}],
            countdown=delay
        )

        log.task_id = result.id
        log.status = log.Status.QUEUED
        log.save(update_fields=['task_id', 'status'])

    def schedule_periodic_task(
        self,
        name: str,
        func: str,
        schedule_type: str = 'D',  # Daily
        repeats: int = -1  # Infinite
    ):
        """
        Schedule a periodic task.

        Args:
            name: Task name
            func: Function path (e.g., 'ceptor_ai.tasks.django_q.check_registrations_task')
            schedule_type: Schedule type (D=Daily, H=Hourly, etc.)
            repeats: Number of repeats (-1 = infinite)

        Returns:
            Schedule instance or None
        """
        if self.backend != 'django_q':
            logger.warning("Periodic tasks only supported with Django Q")
            return None

        from django_q.models import Schedule

        schedule_obj, created = Schedule.objects.get_or_create(
            name=name,
            defaults={
                'func': func,
                'schedule_type': schedule_type,
                'repeats': repeats
            }
        )

        if not created:
            schedule_obj.func = func
            schedule_obj.schedule_type = schedule_type
            schedule_obj.repeats = repeats
            schedule_obj.save()

        logger.info(f"Periodic task scheduled: {name} (created={created})")

        return schedule_obj
