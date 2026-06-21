"""
Management command to send queued emails.

Processes all queued emails and sends them.
"""

import logging

from django.core.management.base import BaseCommand

from django_rseal.communication.email.models import EmailLog
from django_rseal.communication.email.services import EmailService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Send queued emails management command."""

    help = "Send all queued emails"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of emails to send'
        )

    def handle(self, *args, **options):
        """Execute command."""
        limit = options.get('limit')

        # Get queued emails
        queued_logs = EmailLog.objects.filter(status=EmailLog.Status.QUEUED)
        if limit:
            queued_logs = queued_logs[:limit]

        service = EmailService()
        sent_count = 0
        failed_count = 0

        for log in queued_logs:
            try:
                service._send_now(
                    recipient=log.recipient,
                    subject=log.subject,
                    template_name=log.template_used,
                    context={},
                    log=log
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send email {log.id}: {e}")
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {sent_count} emails, {failed_count} failed"
            )
        )
