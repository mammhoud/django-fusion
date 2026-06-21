"""
Background tasks for email automation (Django-Q).

Contains Django-Q tasks for email sending, periodic registration checks,
and weekly report generation.

Migrated from django_seed/tasks.py.
"""

import logging
import os

from django_rseal.communication.email.models import EmailLog
from django_rseal.services.email_service import EmailService
from django_rseal.services.invitation_service import InvitationService
from django_rseal.services.queue_manager import EmailQueueManager
from django_rseal.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


def send_email_task(
    log_id: int,
    recipient: str,
    subject: str,
    template_name: str,
    context: dict,
):
    """
    Background task to send a single email.

    Called by Django Q. Uses EmailService._send_now() directly to avoid
    re-queuing. Updates EmailLog status on success or failure.

    Args:
        log_id: EmailLog primary key
        recipient: Recipient email address
        subject: Email subject
        template_name: Template file path
        context: Template context variables
    """
    try:
        log = EmailLog.objects.get(id=log_id)
    except EmailLog.DoesNotExist:
        logger.error(f"send_email_task: EmailLog not found: log_id={log_id}")
        return

    # Mark as sending
    log.status = EmailLog.Status.SENDING
    log.save(update_fields=['status', 'updated_at'])

    email_service = EmailService()

    try:
        email_service._send_now(recipient, subject, template_name, context, log)
        logger.info(
            f"send_email_task: email sent successfully "
            f"log_id={log_id} recipient={recipient}"
        )

    except Exception as e:
        logger.error(
            f"send_email_task: failed to send email "
            f"log_id={log_id} recipient={recipient} error={e}"
        )
        # Retry logic
        queue_manager = EmailQueueManager()
        retried = queue_manager.retry_failed_email(log_id)
        if not retried:
            # Max retries reached - send alert
            _send_failure_alert(recipient, subject, str(e))


def email_sent_hook(task):
    """
    Hook called by Django Q after a task completes.

    Receives the Django Q task object and logs the outcome.

    Args:
        task: Django Q Task instance with .id, .success, .result attributes
    """
    if task.success:
        logger.info(
            f"email_sent_hook: task completed successfully task_id={task.id}"
        )
    else:
        logger.error(
            f"email_sent_hook: task failed task_id={task.id} result={task.result}"
        )


def check_registrations_task():
    """
    Periodic task to check registrations and send invitations.

    Scheduled to run every 2 days. Reads emails.csv, sends invitations to
    unregistered users, and sends a batch report on completion.
    """
    csv_path = os.environ.get('EMAILS_CSV_PATH', 'emails.csv')

    logger.info(f"check_registrations_task: started csv_path={csv_path}")

    invitation_service = InvitationService(csv_path=csv_path)
    report_generator = ReportGenerator()

    try:
        logs = invitation_service.send_invitations_from_csv()

        logger.info(
            f"check_registrations_task: completed invitations_sent={len(logs)}"
        )

        # Send batch report after completion
        report_generator.send_batch_report(
            batch_type='registration_check',
            email_logs=logs,
        )

    except FileNotFoundError as e:
        logger.error(f"check_registrations_task: CSV file not found error={e}")
        report_generator.send_alert(
            alert_type='Registration Check Failed - CSV Not Found',
            message=str(e),
        )

    except Exception as e:
        logger.error(f"check_registrations_task: unexpected error={e}")
        report_generator.send_alert(
            alert_type='Registration Check Failed',
            message=str(e),
        )


def generate_weekly_report_task():
    """
    Periodic task to generate and send the weekly summary report.

    Scheduled to run weekly. Generates statistics for the past 7 days
    and sends a report with a CSV attachment.
    """
    logger.info("generate_weekly_report_task: started")

    report_generator = ReportGenerator()

    try:
        report_generator.send_weekly_report()
        logger.info("generate_weekly_report_task: completed")

    except Exception as e:
        logger.error(f"generate_weekly_report_task: failed error={e}")
        # Attempt to send an alert even if the report itself failed
        try:
            report_generator.send_alert(
                alert_type='Weekly Report Generation Failed',
                message=str(e),
            )
        except Exception as alert_err:
            logger.error(
                f"generate_weekly_report_task: alert also failed error={alert_err}"
            )


def setup_periodic_tasks():
    """
    Register periodic tasks with Django Q scheduler.

    Call this from AppConfig.ready() or a management command to ensure
    schedules are created on startup.
    """
    manager = EmailQueueManager()

    # Registration check every 2 days (minutes=2880)
    manager.schedule_periodic_task(
        name='check_registrations',
        func='django_rseal.tasks.django_q.check_registrations_task',
        schedule_type='D',
        repeats=-1,
    )

    # Weekly report
    manager.schedule_periodic_task(
        name='generate_weekly_report',
        func='django_rseal.tasks.django_q.generate_weekly_report_task',
        schedule_type='W',
        repeats=-1,
    )

    logger.info("setup_periodic_tasks: periodic tasks registered")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _send_failure_alert(recipient: str, subject: str, error: str):
    """Send an alert when an email exhausts all retries."""
    try:
        report_generator = ReportGenerator()
        report_generator.send_alert(
            alert_type='Email Delivery Failed After Max Retries',
            message=(
                f"Recipient: {recipient}\n"
                f"Subject: {subject}\n"
                f"Error: {error}"
            ),
        )
    except Exception as e:
        logger.error(f"_send_failure_alert: could not send alert error={e}")
