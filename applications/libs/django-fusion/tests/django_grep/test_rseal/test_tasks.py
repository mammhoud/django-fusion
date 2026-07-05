"""
Unit tests for background tasks.

Tests send_email_task, email_sent_hook, check_registrations_task,
and generate_weekly_report_task.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

from django.core import mail
from django.test import TestCase, override_settings
from ceptor_ai.communication.email.models import EmailLog
from ceptor_ai.communication.tasks import (
    check_registrations_task,
    email_sent_hook,
    generate_weekly_report_task,
    send_email_task,
)

# ---------------------------------------------------------------------------
# send_email_task tests
# ---------------------------------------------------------------------------

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='noreply@example.com',
)
class SendEmailTaskTestCase(TestCase):
    """Tests for send_email_task."""

    def setUp(self):
        self.log = EmailLog.objects.create(
            recipient='test@example.com',
            subject='Test Subject',
            template_used='emails/invitation.html',
            status=EmailLog.Status.QUEUED,
        )
        mail.outbox = []

    def test_send_email_task_success(self):
        """Task marks log as SENT when email sends successfully."""
        with patch('django_seed.tasks.EmailService') as MockService:
            instance = MockService.return_value
            instance._send_now.return_value = self.log

            send_email_task(
                log_id=self.log.id,
                recipient='test@example.com',
                subject='Test Subject',
                template_name='emails/invitation.html',
                context={'name': 'Alice'},
            )

            instance._send_now.assert_called_once_with(
                'test@example.com',
                'Test Subject',
                'emails/invitation.html',
                {'name': 'Alice'},
                self.log,
            )

        # Log should have been set to SENDING before the call
        self.log.refresh_from_db()
        self.assertEqual(self.log.status, EmailLog.Status.SENDING)

    def test_send_email_task_failure_triggers_retry(self):
        """Task triggers retry when email sending fails."""
        with patch('django_seed.tasks.EmailService') as MockService:
            instance = MockService.return_value
            instance._send_now.side_effect = Exception('SMTP error')

            with patch('django_seed.tasks.EmailQueueManager') as MockQM:
                qm_instance = MockQM.return_value
                qm_instance.retry_failed_email.return_value = True

                send_email_task(
                    log_id=self.log.id,
                    recipient='test@example.com',
                    subject='Test Subject',
                    template_name='emails/invitation.html',
                    context={},
                )

                qm_instance.retry_failed_email.assert_called_once_with(self.log.id)

    def test_send_email_task_max_retries_sends_alert(self):
        """Task sends alert when max retries are exhausted."""
        with patch('django_seed.tasks.EmailService') as MockService:
            instance = MockService.return_value
            instance._send_now.side_effect = Exception('SMTP error')

            with patch('django_seed.tasks.EmailQueueManager') as MockQM:
                qm_instance = MockQM.return_value
                # retry_failed_email returns False = max retries reached
                qm_instance.retry_failed_email.return_value = False

                with patch('django_seed.tasks._send_failure_alert') as mock_alert:
                    send_email_task(
                        log_id=self.log.id,
                        recipient='test@example.com',
                        subject='Test Subject',
                        template_name='emails/invitation.html',
                        context={},
                    )

                    mock_alert.assert_called_once()

    def test_send_email_task_missing_log(self):
        """Task handles missing EmailLog gracefully."""
        # Should not raise
        send_email_task(
            log_id=99999,
            recipient='test@example.com',
            subject='Test Subject',
            template_name='emails/invitation.html',
            context={},
        )

    def test_send_email_task_sets_status_to_sending(self):
        """Task sets log status to SENDING before attempting send."""
        with patch('django_seed.tasks.EmailService') as MockService:
            instance = MockService.return_value

            def capture_status(*args, **kwargs):
                # Check status at the moment _send_now is called
                self.log.refresh_from_db()
                self.assertEqual(self.log.status, EmailLog.Status.SENDING)
                return self.log

            instance._send_now.side_effect = capture_status

            send_email_task(
                log_id=self.log.id,
                recipient='test@example.com',
                subject='Test Subject',
                template_name='emails/invitation.html',
                context={},
            )


# ---------------------------------------------------------------------------
# email_sent_hook tests
# ---------------------------------------------------------------------------

class EmailSentHookTestCase(TestCase):
    """Tests for email_sent_hook."""

    def test_hook_logs_success(self):
        """Hook logs success when task.success is True."""
        task = MagicMock()
        task.id = 'abc-123'
        task.success = True
        task.result = None

        # Should not raise
        email_sent_hook(task)

    def test_hook_logs_failure(self):
        """Hook logs failure when task.success is False."""
        task = MagicMock()
        task.id = 'abc-456'
        task.success = False
        task.result = 'SMTP connection refused'

        # Should not raise
        email_sent_hook(task)


# ---------------------------------------------------------------------------
# check_registrations_task tests
# ---------------------------------------------------------------------------

class CheckRegistrationsTaskTestCase(TestCase):
    """Tests for check_registrations_task."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'emails.csv')
        with open(self.csv_path, 'w') as f:
            f.write('email,role\n')
            f.write('unregistered@example.com,instructor\n')

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        os.rmdir(self.temp_dir)

    def test_check_registrations_sends_invitations(self):
        """Task sends invitations and then a batch report."""
        mock_log = MagicMock()
        mock_log.status = EmailLog.Status.QUEUED

        with patch.dict(os.environ, {'EMAILS_CSV_PATH': self.csv_path}):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                is_instance.send_invitations_from_csv.return_value = [mock_log]

                with patch('django_seed.tasks.ReportGenerator') as MockRG:
                    rg_instance = MockRG.return_value

                    check_registrations_task()

                    is_instance.send_invitations_from_csv.assert_called_once()
                    rg_instance.send_batch_report.assert_called_once_with(
                        batch_type='registration_check',
                        email_logs=[mock_log],
                    )

    def test_check_registrations_csv_not_found_sends_alert(self):
        """Task sends alert when CSV file is not found."""
        with patch.dict(os.environ, {'EMAILS_CSV_PATH': '/nonexistent/emails.csv'}):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                is_instance.send_invitations_from_csv.side_effect = FileNotFoundError(
                    'CSV not found'
                )

                with patch('django_seed.tasks.ReportGenerator') as MockRG:
                    rg_instance = MockRG.return_value

                    check_registrations_task()

                    rg_instance.send_alert.assert_called_once()
                    alert_call = rg_instance.send_alert.call_args
                    self.assertIn('CSV Not Found', alert_call.kwargs['alert_type'])

    def test_check_registrations_unexpected_error_sends_alert(self):
        """Task sends alert on unexpected errors."""
        with patch.dict(os.environ, {'EMAILS_CSV_PATH': self.csv_path}):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                is_instance.send_invitations_from_csv.side_effect = RuntimeError(
                    'Unexpected failure'
                )

                with patch('django_seed.tasks.ReportGenerator') as MockRG:
                    rg_instance = MockRG.return_value

                    check_registrations_task()

                    rg_instance.send_alert.assert_called_once()

    def test_check_registrations_uses_env_csv_path(self):
        """Task reads EMAILS_CSV_PATH from environment."""
        custom_path = '/custom/path/emails.csv'

        with patch.dict(os.environ, {'EMAILS_CSV_PATH': custom_path}):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                is_instance.send_invitations_from_csv.return_value = []

                with patch('django_seed.tasks.ReportGenerator'):
                    check_registrations_task()

                    MockIS.assert_called_once_with(csv_path=custom_path)

    def test_check_registrations_defaults_to_emails_csv(self):
        """Task defaults to 'emails.csv' when env var is not set."""
        env = {k: v for k, v in os.environ.items() if k != 'EMAILS_CSV_PATH'}

        with patch.dict(os.environ, env, clear=True):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                is_instance.send_invitations_from_csv.return_value = []

                with patch('django_seed.tasks.ReportGenerator'):
                    check_registrations_task()

                    MockIS.assert_called_once_with(csv_path='emails.csv')


# ---------------------------------------------------------------------------
# generate_weekly_report_task tests
# ---------------------------------------------------------------------------

class GenerateWeeklyReportTaskTestCase(TestCase):
    """Tests for generate_weekly_report_task."""

    def test_weekly_report_calls_send_weekly_report(self):
        """Task calls ReportGenerator.send_weekly_report()."""
        with patch('django_seed.tasks.ReportGenerator') as MockRG:
            rg_instance = MockRG.return_value

            generate_weekly_report_task()

            rg_instance.send_weekly_report.assert_called_once()

    def test_weekly_report_sends_alert_on_failure(self):
        """Task sends alert when report generation fails."""
        with patch('django_seed.tasks.ReportGenerator') as MockRG:
            rg_instance = MockRG.return_value
            rg_instance.send_weekly_report.side_effect = Exception('SMTP down')

            generate_weekly_report_task()

            rg_instance.send_alert.assert_called_once()
            alert_call = rg_instance.send_alert.call_args
            self.assertIn('Weekly Report', alert_call.kwargs['alert_type'])

    def test_weekly_report_handles_alert_failure_gracefully(self):
        """Task does not raise even when both report and alert fail."""
        with patch('django_seed.tasks.ReportGenerator') as MockRG:
            rg_instance = MockRG.return_value
            rg_instance.send_weekly_report.side_effect = Exception('SMTP down')
            rg_instance.send_alert.side_effect = Exception('Alert also failed')

            # Should not raise
            generate_weekly_report_task()
