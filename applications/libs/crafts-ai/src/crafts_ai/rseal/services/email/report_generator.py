"""
Report Generator service for email reporting.

Generates and sends email reports to administrators.
REPORT_EMAIL_FROM and REPORT_EMAIL_TO are read from os.environ (never hardcoded).
"""

import csv
import io
import logging
import os
from datetime import timedelta
from typing import Any, Dict, List

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.utils import timezone

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates and sends email reports to administrators.
    REPORT_EMAIL_FROM and REPORT_EMAIL_TO are read from os.environ.
    """

    def __init__(self):
        # Read from os.environ as required - never hardcoded
        self.report_email = os.environ.get(
            'REPORT_EMAIL_TO',
            getattr(settings, 'REPORT_EMAIL_TO', 'admin@example.com')
        )
        self.from_email = os.environ.get(
            'REPORT_EMAIL_FROM',
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        )

    def send_weekly_report(self):
        """Generate and send weekly summary report."""

        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)

        # Gather statistics
        stats = self._gather_statistics(start_date, end_date)

        # Generate CSV attachment
        csv_data = self._generate_csv_report(start_date, end_date)

        # Send email
        subject = (
            f"Weekly Email Report - "
            f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
        body = self._format_weekly_report(stats)

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=[self.report_email]
        )

        # Attach CSV
        email.attach('email_report.csv', csv_data, 'text/csv')
        email.send()

        logger.info(f"Weekly report sent to {self.report_email}")

    def send_batch_report(self, batch_type: str, email_logs: List):
        """
        Send report after batch operation.

        Args:
            batch_type: Type of batch (e.g., 'registration_check')
            email_logs: List of EmailLog instances from the batch
        """
        from crafts_ai.communication.email.models import EmailLog

        stats = {
            'total': len(email_logs),
            'sent': sum(1 for log in email_logs if log.status == EmailLog.Status.SENT),
            'failed': sum(1 for log in email_logs if log.status == EmailLog.Status.FAILED),
            'queued': sum(1 for log in email_logs if log.status == EmailLog.Status.QUEUED),
        }

        success_rate = (stats['sent'] / stats['total'] * 100) if stats['total'] > 0 else 0

        subject = f"Batch Report: {batch_type}"
        body = f"""
Batch Type: {batch_type}
Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total Emails: {stats['total']}
- Sent: {stats['sent']}
- Failed: {stats['failed']}
- Queued: {stats['queued']}

Success Rate: {success_rate:.1f}%
"""

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=[self.report_email]
        )
        email.send()

        logger.info(f"Batch report sent: {batch_type} to {self.report_email}")

    def send_alert(self, alert_type: str, message: str):
        """
        Send immediate alert email for critical errors.

        Args:
            alert_type: Type of alert
            message: Alert message
        """
        subject = f"ALERT: {alert_type}"
        body = f"""
Alert Type: {alert_type}
Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

Message:
{message}

This is an automated alert from the email automation system.
"""

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=[self.report_email]
        )
        email.send()

        logger.warning(f"Alert sent: {alert_type} to {self.report_email}")

    def _gather_statistics(self, start_date, end_date) -> Dict[str, Any]:
        """Gather email statistics for date range."""
        from crafts_ai.communication.email.models import EmailLog

        logs = EmailLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )

        return {
            'total_emails': logs.count(),
            'sent': logs.filter(status=EmailLog.Status.SENT).count(),
            'failed': logs.filter(status=EmailLog.Status.FAILED).count(),
            'queued': logs.filter(status=EmailLog.Status.QUEUED).count(),
            'bounced': logs.filter(status=EmailLog.Status.BOUNCED).count(),
            'unique_recipients': logs.values('recipient').distinct().count(),
            'avg_retry_count': logs.aggregate(avg=Avg('retry_count'))['avg'] or 0,
        }

    def _format_weekly_report(self, stats: Dict[str, Any]) -> str:
        """Format weekly report body."""
        success_rate = (
            (stats['sent'] / stats['total_emails'] * 100)
            if stats['total_emails'] > 0
            else 0
        )

        return f"""
Weekly Email Summary Report

Period: Last 7 days
Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

=== Summary Statistics ===
Total Emails Sent: {stats['total_emails']}
Successfully Delivered: {stats['sent']}
Failed: {stats['failed']}
Queued: {stats['queued']}
Bounced: {stats['bounced']}

Success Rate: {success_rate:.1f}%
Unique Recipients: {stats['unique_recipients']}
Average Retry Count: {stats['avg_retry_count']:.2f}

=== Detailed Report ===
See attached CSV file for detailed email log.

---
This is an automated report from the Email Automation System.
"""

    def _generate_csv_report(self, start_date, end_date) -> str:
        """Generate CSV report data."""
        from crafts_ai.communication.email.models import EmailLog

        logs = EmailLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('-timestamp')

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Timestamp',
            'Recipient',
            'Subject',
            'Status',
            'Template',
            'Retry Count',
            'Error Message'
        ])

        # Data rows
        for log in logs:
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.recipient,
                log.subject,
                log.get_status_display(),
                log.template_used,
                log.retry_count,
                log.error_message[:100] if log.error_message else ''
            ])

        return output.getvalue()
