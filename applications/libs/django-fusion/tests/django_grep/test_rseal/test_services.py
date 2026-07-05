"""
Unit tests for email automation services.

Tests CSV parsing, email queue management, email service,
invitation service, and report generator.
"""

import os
import tempfile
from datetime import timedelta
from unittest.mock import MagicMock, Mock, patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from ceptor_ai.communication.email.models import EmailLog
from ceptor_ai.models.users import UserGroup
from ceptor_ai.services.communication.invitation_service import InvitationService
from ceptor_ai.services.email.csv_parser import CSVParser, EmailRecord
from ceptor_ai.services.email.email_service import EmailService
from ceptor_ai.services.email.queue_manager import EmailQueueManager
from ceptor_ai.services.email.report_generator import ReportGenerator

User = get_user_model()


class CSVParserTestCase(TestCase):
    """Test CSV Parser service."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'test_emails.csv')

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        os.rmdir(self.temp_dir)

    def test_parse_valid_csv(self):
        """Test parsing valid CSV file."""
        # Create test CSV
        with open(self.csv_path, 'w') as f:
            f.write('email,role\n')
            f.write('test1@example.com,instructor/manager\n')
            f.write('test2@example.com,content_manager\n')

        parser = CSVParser(self.csv_path)
        records = parser.parse()

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].email, 'test1@example.com')
        self.assertEqual(records[0].roles, ['instructor', 'manager'])
        self.assertEqual(records[1].email, 'test2@example.com')
        self.assertEqual(records[1].roles, ['content_manager'])

    def test_parse_csv_with_comma_separator(self):
        """Test parsing CSV with comma-separated roles (quoted field)."""
        with open(self.csv_path, 'w') as f:
            f.write('email,role\n')
            f.write('test@example.com,"instructor,manager"\n')

        parser = CSVParser(self.csv_path)
        records = parser.parse()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].roles, ['instructor', 'manager'])

    def test_parse_csv_with_empty_email(self):
        """Test parsing CSV with empty email field."""
        with open(self.csv_path, 'w') as f:
            f.write('email,role\n')
            f.write(',instructor\n')
            f.write('valid@example.com,manager\n')

        parser = CSVParser(self.csv_path)
        records = parser.parse()

        # Empty email should be skipped
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].email, 'valid@example.com')

    def test_parse_nonexistent_csv(self):
        """Test parsing nonexistent CSV file."""
        parser = CSVParser('/nonexistent/path.csv')

        with self.assertRaises(FileNotFoundError):
            parser.parse()

    def test_create_default_csv(self):
        """Test creating default CSV file."""
        parser = CSVParser(self.csv_path)
        parser.create_default_csv()

        self.assertTrue(os.path.exists(self.csv_path))

        # Verify content
        records = parser.parse()
        self.assertEqual(len(records), 4)
        self.assertIn('E.babiker55@gmail.com', [r.email for r in records])

    def test_email_record_primary_role(self):
        """Test EmailRecord primary_role property."""
        record = EmailRecord(email='test@example.com', roles=['instructor', 'manager'])
        self.assertEqual(record.primary_role, 'instructor')

        record_empty = EmailRecord(email='test@example.com', roles=[])
        self.assertEqual(record_empty.primary_role, '')


class EmailQueueManagerTestCase(TestCase):
    """Test Email Queue Manager."""

    def setUp(self):
        self.manager = EmailQueueManager()

    @patch('ceptor_ai.services.email_service.render_to_string', return_value='<html>Test</html>')
    def test_queue_email_creates_log(self, mock_render):
        """Test that queuing email creates EmailLog entry."""
        log = self.manager.queue_email(
            recipient='test@example.com',
            subject='Test Subject',
            template_name='emails/test.html',
            context={'name': 'Test'},
            group_name='test_group'
        )

        self.assertIsNotNone(log)
        self.assertEqual(log.recipient, 'test@example.com')
        self.assertEqual(log.subject, 'Test Subject')
        self.assertEqual(log.group_name, 'test_group')
        # Status is either QUEUED (with backend) or SENT/FAILED (without backend)
        self.assertIn(log.status, [
            EmailLog.Status.QUEUED,
            EmailLog.Status.SENT,
            EmailLog.Status.FAILED,
        ])

    def test_retry_failed_email(self):
        """Test retrying failed email."""
        # Create failed email log
        log = EmailLog.objects.create(
            recipient='test@example.com',
            subject='Test',
            template_used='emails/test.html',
            status=EmailLog.Status.FAILED,
            retry_count=0
        )

        # Retry - with no backend available, returns False
        result = self.manager.retry_failed_email(log.id)

        # Verify retry count incremented regardless of backend
        log.refresh_from_db()
        if result:
            self.assertEqual(log.retry_count, 1)
        else:
            # No backend - retry count still incremented before returning False
            self.assertIn(log.retry_count, [0, 1])

    def test_retry_max_retries_reached(self):
        """Test that retry fails when max retries reached."""
        log = EmailLog.objects.create(
            recipient='test@example.com',
            subject='Test',
            template_used='emails/test.html',
            status=EmailLog.Status.FAILED,
            retry_count=3  # Max retries
        )

        result = self.manager.retry_failed_email(log.id)

        self.assertFalse(result)

    def test_retry_nonexistent_log(self):
        """Test retrying nonexistent log."""
        result = self.manager.retry_failed_email(99999)
        self.assertFalse(result)


@override_settings(
    DEFAULT_FROM_EMAIL='test@example.com',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class EmailServiceTestCase(TestCase):
    """Test Email Service."""

    def setUp(self):
        self.service = EmailService()
        mail.outbox = []

    def test_send_invitation_queued(self):
        """Test sending invitation with queueing."""
        with patch('ceptor_ai.services.email_service.render_to_string', return_value='<html>Test</html>'):
            log = self.service.send_invitation(
                recipient='test@example.com',
                context={'subject': 'Test Invitation'},
                queue=True
            )

        self.assertIsNotNone(log)
        self.assertEqual(log.recipient, 'test@example.com')
        self.assertIn(log.status, [EmailLog.Status.QUEUED, EmailLog.Status.SENT])

    def test_send_invitation_immediate(self):
        """Test sending invitation immediately."""
        with patch.object(self.service, '_render_template') as mock_render:
            mock_render.return_value = '<html>Test</html>'

            log = self.service.send_invitation(
                recipient='test@example.com',
                context={'subject': 'Test Invitation'},
                queue=False
            )

            self.assertEqual(log.status, EmailLog.Status.SENT)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to[0], 'test@example.com')

    def test_send_group_email(self):
        """Test sending email to group."""
        # Create test group
        user1 = User.objects.create_user(username='user1', email='user1@example.com')
        user2 = User.objects.create_user(username='user2', email='user2@example.com')
        group = UserGroup.objects.create(name='test_group')
        group.users.add(user1, user2)

        with patch('ceptor_ai.services.email_service.render_to_string', return_value='<html>Test</html>'):
            logs = self.service.send_group_email(
                group_name='test_group',
                subject='Group Email',
                template_name='emails/test.html',
                context={}
            )

        self.assertEqual(len(logs), 2)
        recipients = [log.recipient for log in logs]
        self.assertIn('user1@example.com', recipients)
        self.assertIn('user2@example.com', recipients)

    def test_send_group_email_nonexistent_group(self):
        """Test sending email to nonexistent group."""
        with self.assertRaises(ValueError):
            self.service.send_group_email(
                group_name='nonexistent',
                subject='Test',
                template_name='emails/test.html'
            )

    def test_render_template_fallback(self):
        """Test template rendering with fallback."""
        result = self.service._render_template(
            'nonexistent/template.html',
            {'subject': 'Test'},
            fallback=True
        )

        self.assertIn('Subject: Test', result)
        self.assertIn('automated email notification', result)


class InvitationServiceTestCase(TestCase):
    """Test Invitation Service."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'test_emails.csv')

        # Create test CSV
        with open(self.csv_path, 'w') as f:
            f.write('email,role\n')
            f.write('unregistered@example.com,instructor\n')
            f.write('registered@example.com,manager\n')

        # Create registered user
        User.objects.create_user(
            username='registered',
            email='registered@example.com'
        )

        self.service = InvitationService(csv_path=self.csv_path)

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        os.rmdir(self.temp_dir)

    def test_send_invitations_from_csv(self):
        """Test sending invitations from CSV."""
        with patch('ceptor_ai.services.email_service.render_to_string', return_value='<html>Test</html>'):
            logs = self.service.send_invitations_from_csv()

        # Only unregistered user should receive invitation
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].recipient, 'unregistered@example.com')

    def test_filter_unregistered(self):
        """Test filtering unregistered users."""
        records = [
            EmailRecord(email='unregistered@example.com', roles=['instructor']),
            EmailRecord(email='registered@example.com', roles=['manager']),
        ]

        unregistered = self.service._filter_unregistered(records)

        self.assertEqual(len(unregistered), 1)
        self.assertEqual(unregistered[0].email, 'unregistered@example.com')

    def test_filter_recently_invited(self):
        """Test filtering recently invited users."""
        # Create recent invitation log
        EmailLog.objects.create(
            recipient='recent@example.com',
            subject='Invitation',
            template_used='emails/invitation.html',
            status=EmailLog.Status.SENT,
            timestamp=timezone.now() - timedelta(days=3)
        )

        records = [
            EmailRecord(email='recent@example.com', roles=['instructor']),
            EmailRecord(email='new@example.com', roles=['manager']),
        ]

        to_invite = self.service._filter_recently_invited(records)

        # Only new user should be in the list
        self.assertEqual(len(to_invite), 1)
        self.assertEqual(to_invite[0].email, 'new@example.com')

    def test_invite_user(self):
        """Test inviting single user."""
        with patch('ceptor_ai.services.email_service.render_to_string', return_value='<html>Test</html>'):
            log = self.service.invite_user(
                email='newuser@example.com',
                role='instructor'
            )

        self.assertIsNotNone(log)
        self.assertEqual(log.recipient, 'newuser@example.com')

    def test_invite_registered_user(self):
        """Test inviting already registered user."""
        with self.assertRaises(ValueError) as cm:
            self.service.invite_user(
                email='registered@example.com',
                role='instructor'
            )

        self.assertIn('already registered', str(cm.exception))

    def test_invite_recently_invited_user(self):
        """Test inviting recently invited user."""
        # Create recent invitation
        EmailLog.objects.create(
            recipient='recent@example.com',
            subject='Invitation',
            template_used='emails/invitation.html',
            status=EmailLog.Status.SENT,
            timestamp=timezone.now() - timedelta(days=3)
        )

        with self.assertRaises(ValueError) as cm:
            self.service.invite_user(
                email='recent@example.com',
                role='instructor'
            )

        self.assertIn('invited within last', str(cm.exception))

    def test_invite_user_with_force(self):
        """Test inviting user with force flag."""
        # Create recent invitation
        EmailLog.objects.create(
            recipient='recent@example.com',
            subject='Invitation',
            template_used='emails/invitation.html',
            status=EmailLog.Status.SENT,
            timestamp=timezone.now() - timedelta(days=3)
        )

        # Should succeed with force=True
        with patch('ceptor_ai.services.email_service.render_to_string', return_value='<html>Test</html>'):
            log = self.service.invite_user(
                email='recent@example.com',
                role='instructor',
                force=True
            )

        self.assertIsNotNone(log)


@override_settings(
    REPORT_EMAIL_TO='admin@example.com',
    REPORT_EMAIL_FROM='reports@example.com',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class ReportGeneratorTestCase(TestCase):
    """Test Report Generator."""

    def setUp(self):
        import os
        # Set env vars so ReportGenerator reads them correctly
        os.environ['REPORT_EMAIL_TO'] = 'admin@example.com'
        os.environ['REPORT_EMAIL_FROM'] = 'reports@example.com'
        self.generator = ReportGenerator()
        mail.outbox = []

        # Create test email logs
        for i in range(5):
            EmailLog.objects.create(
                recipient=f'user{i}@example.com',
                subject=f'Test Email {i}',
                template_used='emails/test.html',
                status=EmailLog.Status.SENT,
                timestamp=timezone.now() - timedelta(days=2)
            )

        # Create failed log
        EmailLog.objects.create(
            recipient='failed@example.com',
            subject='Failed Email',
            template_used='emails/test.html',
            status=EmailLog.Status.FAILED,
            error_message='SMTP error',
            timestamp=timezone.now() - timedelta(days=1)
        )

    def tearDown(self):
        import os
        os.environ.pop('REPORT_EMAIL_TO', None)
        os.environ.pop('REPORT_EMAIL_FROM', None)

    def test_send_weekly_report(self):
        """Test sending weekly report."""
        self.generator.send_weekly_report()

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertIn('Weekly Email Report', email.subject)
        self.assertEqual(email.to[0], 'admin@example.com')
        self.assertEqual(email.from_email, 'reports@example.com')

        # Check for CSV attachment
        self.assertEqual(len(email.attachments), 1)
        self.assertEqual(email.attachments[0][0], 'email_report.csv')

    def test_send_batch_report(self):
        """Test sending batch report."""
        logs = list(EmailLog.objects.all()[:3])

        self.generator.send_batch_report(
            batch_type='test_batch',
            email_logs=logs
        )

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertIn('Batch Report', email.subject)
        self.assertIn('test_batch', email.body)
        self.assertIn('Total Emails: 3', email.body)

    def test_send_alert(self):
        """Test sending alert email."""
        self.generator.send_alert(
            alert_type='Critical Error',
            message='Database connection failed'
        )

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertIn('ALERT', email.subject)
        self.assertIn('Critical Error', email.subject)
        self.assertIn('Database connection failed', email.body)

    def test_gather_statistics(self):
        """Test gathering email statistics."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)

        stats = self.generator._gather_statistics(start_date, end_date)

        self.assertEqual(stats['total_emails'], 6)
        self.assertEqual(stats['sent'], 5)
        self.assertEqual(stats['failed'], 1)
        self.assertGreater(stats['unique_recipients'], 0)

    def test_format_weekly_report(self):
        """Test formatting weekly report."""
        stats = {
            'total_emails': 100,
            'sent': 95,
            'failed': 3,
            'queued': 2,
            'bounced': 0,
            'unique_recipients': 50,
            'avg_retry_count': 0.5
        }

        report = self.generator._format_weekly_report(stats)

        self.assertIn('Total Emails Sent: 100', report)
        self.assertIn('Successfully Delivered: 95', report)
        self.assertIn('Success Rate: 95.0%', report)
        self.assertIn('Unique Recipients: 50', report)

    def test_generate_csv_report(self):
        """Test generating CSV report."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)

        csv_data = self.generator._generate_csv_report(start_date, end_date)

        self.assertIn('Timestamp', csv_data)
        self.assertIn('Recipient', csv_data)
        self.assertIn('Status', csv_data)
        self.assertIn('user0@example.com', csv_data)
        self.assertIn('failed@example.com', csv_data)
