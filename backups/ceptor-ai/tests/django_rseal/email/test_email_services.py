"""
Tests for django-rseal EmailService and BulkEmailService.

These tests verify email sending functionality, logging, and batch operations.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add the project root to Python path so tests.settings can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from django.core.mail import EmailMultiAlternatives
from django.test.utils import override_settings

# Configure Django settings before importing django-rseal
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

from ceptor_ai.email.models import EmailLog
from ceptor_ai.email.services import BulkEmailService, EmailService  # noqa: E402


@pytest.fixture
def email_service():
    """Module-level fixture providing EmailService instance."""
    return EmailService()


@pytest.fixture
def email_context():
    """Module-level fixture providing email context."""
    return {
        "user_name": "Test User",
        "site_name": "Test Site",
        "action": "Test Action",
    }


@pytest.mark.django_db
class TestEmailService:
    """Test EmailService functionality."""

    @pytest.fixture
    def email_service(self):
        """Fixture providing EmailService instance."""
        return EmailService()

    @pytest.fixture
    def email_context(self):
        """Fixture providing email context."""
        return {
            "user_name": "Test User",
            "site_name": "Test Site",
            "action": "Test Action",
        }

    def test_email_service_initialization(self):
        """Test EmailService initialization."""
        service = EmailService()
        assert service.from_email == "noreply@example.com"  # Default from settings

        # Test with custom settings
        with override_settings(DEFAULT_FROM_EMAIL="custom@example.com"):
            service2 = EmailService()
            assert service2.from_email == "custom@example.com"

    @patch('django.core.mail.EmailMultiAlternatives')
    @patch('django.template.loader.render_to_string')
    def test_send_email_immediate(self, mock_render, mock_email_class, email_service):
        """Test immediate email sending."""
        # Mock dependencies
        mock_render.return_value = "<h1>Test Email</h1>"
        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        # Send email immediately (queue=False)
        log = email_service.send_email(
            recipient="test@example.com",
            subject="Test Subject",
            template_name="emails/test.html",
            context={"test": "data"},
            queue=False,
        )

        # Verify email was sent
        assert log is not None
        assert log.recipient == "test@example.com"
        assert log.subject == "Test Subject"
        assert log.template_used == "emails/test.html"
        assert log.status == EmailLog.Status.SENT

        # Verify render_to_string was called
        mock_render.assert_called_once_with("emails/test.html", {"test": "data"})

        # Verify EmailMultiAlternatives was created
        mock_email_class.assert_called_once_with(
            subject="Test Subject",
            body="<h1>Test Email</h1>",
            from_email="noreply@example.com",
            to=["test@example.com"],
            reply_to=None,
        )

        # Verify email was sent
        mock_email_instance.attach_alternative.assert_called_once_with("<h1>Test Email</h1>", "text/html")
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    def test_send_email_queued(self, email_service):
        """Test queued email sending."""
        # Send email with queue=True (default)
        log = email_service.send_email(
            recipient="test@example.com",
            subject="Test Subject",
            template_name="emails/test.html",
            context={"test": "data"},
            queue=True,
        )

        # Verify log was created with QUEUED status
        assert log is not None
        assert log.recipient == "test@example.com"
        assert log.subject == "Test Subject"
        assert log.template_used == "emails/test.html"
        assert log.status == EmailLog.Status.QUEUED

    @patch('django.core.mail.EmailMultiAlternatives')
    @patch('django.template.loader.render_to_string')
    def test_send_email_failure(self, mock_render, mock_email_class, email_service):
        """Test email sending failure handling."""
        # Mock failure
        mock_render.return_value = "<h1>Test Email</h1>"
        mock_email_instance = MagicMock()
        mock_email_instance.send.side_effect = Exception("SMTP Error")
        mock_email_class.return_value = mock_email_instance

        # Send email that will fail
        log = email_service.send_email(
            recipient="test@example.com",
            subject="Test Subject",
            template_name="emails/test.html",
            context={"test": "data"},
            queue=False,
        )

        # Verify log was marked as failed
        assert log is not None
        assert log.status == EmailLog.Status.FAILED
        assert "SMTP Error" in log.error_message

    def test_send_invitation(self, email_service):
        """Test invitation email sending."""
        context = {
            "inviter": "Admin User",
            "invite_url": "https://example.com/invite/123",
            "organization": "Test Org",
        }

        log = email_service.send_invitation(
            recipient="invitee@example.com",
            context=context,
            template_name="emails/invitation.html",
            queue=True,
        )

        assert log is not None
        assert log.recipient == "invitee@example.com"
        assert log.template_used == "emails/invitation.html"
        assert log.status == EmailLog.Status.QUEUED

        # Test with custom subject
        context_with_subject = context.copy()
        context_with_subject["subject"] = "Custom Invitation Subject"

        log2 = email_service.send_invitation(
            recipient="invitee2@example.com",
            context=context_with_subject,
            template_name="emails/invitation.html",
            queue=True,
        )

        assert log2.subject == "Custom Invitation Subject"

    def test_send_notification(self, email_service):
        """Test notification email sending."""
        context = {
            "notification_type": "alert",
            "message": "System alert notification",
            "priority": "high",
        }

        log = email_service.send_notification(
            recipient="user@example.com",
            context=context,
            template_name="emails/notification.html",
            queue=True,
        )

        assert log is not None
        assert log.recipient == "user@example.com"
        assert log.template_used == "emails/notification.html"
        assert log.status == EmailLog.Status.QUEUED

        # Test with custom subject
        context_with_subject = context.copy()
        context_with_subject["subject"] = "Custom Notification"

        log2 = email_service.send_notification(
            recipient="user2@example.com",
            context=context_with_subject,
            template_name="emails/notification.html",
            queue=True,
        )

        assert log2.subject == "Custom Notification"

    def test_send_report(self, email_service):
        """Test report email sending."""
        context = {
            "report_type": "weekly",
            "period": "2026-04-11 to 2026-04-18",
            "data": {"users": 150, "activities": 1200},
        }

        log = email_service.send_report(
            recipient="admin@example.com",
            context=context,
            template_name="emails/report.html",
            queue=True,
        )

        assert log is not None
        assert log.recipient == "admin@example.com"
        assert log.template_used == "emails/report.html"
        assert log.status == EmailLog.Status.QUEUED

        # Test with custom subject
        context_with_subject = context.copy()
        context_with_subject["subject"] = "Custom Report"

        log2 = email_service.send_report(
            recipient="admin2@example.com",
            context=context_with_subject,
            template_name="emails/report.html",
            queue=True,
        )

        assert log2.subject == "Custom Report"


@pytest.mark.django_db
class TestBulkEmailService:
    """Test BulkEmailService functionality."""

    @pytest.fixture
    def bulk_email_service(self):
        """Fixture providing BulkEmailService instance."""
        return BulkEmailService()

    @pytest.fixture
    def recipient_list(self):
        """Fixture providing list of recipients."""
        return [
            "user1@example.com",
            "user2@example.com",
            "user3@example.com",
            "user4@example.com",
            "user5@example.com",
        ]

    def test_bulk_service_initialization(self):
        """Test BulkEmailService initialization."""
        service = BulkEmailService()
        assert service._service is not None
        assert isinstance(service._service, EmailService)

    def test_send_batch_queued(self, bulk_email_service, recipient_list):
        """Test batch email sending with queue=True."""
        logs = bulk_email_service.send_batch(
            recipients=recipient_list,
            subject="Batch Test Email",
            template_name="emails/batch_test.html",
            context={"batch_id": "test-123"},
            queue=True,
        )

        # Verify logs were created
        assert len(logs) == len(recipient_list)

        for i, log in enumerate(logs):
            assert log.recipient == recipient_list[i]
            assert log.subject == "Batch Test Email"
            assert log.template_used == "emails/batch_test.html"
            assert log.status == EmailLog.Status.QUEUED

    @patch('ceptor_ai.email.services.EmailService.send_email')
    def test_send_batch_immediate(self, mock_send_email, bulk_email_service, recipient_list):
        """Test batch email sending with queue=False."""
        # Mock individual email sends
        mock_logs = []
        for recipient in recipient_list:
            mock_log = MagicMock()
            mock_log.recipient = recipient
            mock_log.status = EmailLog.Status.SENT
            mock_logs.append(mock_log)

        mock_send_email.side_effect = mock_logs

        logs = bulk_email_service.send_batch(
            recipients=recipient_list,
            subject="Immediate Batch Test",
            template_name="emails/immediate.html",
            context={"urgent": True},
            queue=False,
        )

        # Verify send_email was called for each recipient
        assert mock_send_email.call_count == len(recipient_list)

        # Verify logs were returned
        assert len(logs) == len(recipient_list)
        for log in logs:
            assert log.status == EmailLog.Status.SENT

    @patch('django.contrib.auth.models.Group')
    def test_send_group_email(self, mock_group_class, bulk_email_service):
        """Test sending email to Django auth group."""
        # Mock group and users
        mock_user1 = MagicMock()
        mock_user1.email = "user1@example.com"

        mock_user2 = MagicMock()
        mock_user2.email = "user2@example.com"

        mock_user3 = MagicMock()
        mock_user3.email = "user3@example.com"

        mock_group = MagicMock()
        mock_group.name = "Test Group"
        mock_group.user_set.values_list.return_value = [
            "user1@example.com",
            "user2@example.com",
            "user3@example.com",
        ]

        mock_group_class.objects.get.return_value = mock_group

        # Mock the underlying batch send
        with patch.object(bulk_email_service, 'send_batch') as mock_send_batch:
            mock_send_batch.return_value = [MagicMock(), MagicMock(), MagicMock()]

            logs = bulk_email_service.send_group_email(
                group_name="Test Group",
                subject="Group Email",
                template_name="emails/group.html",
                context={"group": "Test Group"},
            )

            # Verify group was retrieved
            mock_group_class.objects.get.assert_called_once_with(name="Test Group")

            # Verify batch was sent
            mock_send_batch.assert_called_once_with(
                recipients=["user1@example.com", "user2@example.com", "user3@example.com"],
                subject="Group Email",
                template_name="emails/group.html",
                template_obj=None,
                context={"group": "Test Group"},
                queue=True,
            )

            assert len(logs) == 3

    @patch('django.contrib.auth.models.Group')
    def test_send_group_email_nonexistent_group(self, mock_group_class, bulk_email_service):
        """Test sending email to non-existent group."""
        from django.core.exceptions import ObjectDoesNotExist

        # Mock group not found using ObjectDoesNotExist
        mock_group_class.objects.get.side_effect = ObjectDoesNotExist("Group not found")

        # Should raise ValueError
        with pytest.raises(ValueError, match="Group not found"):
            bulk_email_service.send_group_email(
                group_name="Non-existent Group",
                subject="Test",
                template_name="emails/test.html",
                context={},
            )

    def test_bulk_email_performance(self, bulk_email_service, recipient_list):
        """Test bulk email performance."""
        import time

        # Create larger recipient list
        large_recipient_list = [f"user{i}@example.com" for i in range(100)]

        start_time = time.time()

        logs = bulk_email_service.send_batch(
            recipients=large_recipient_list,
            subject="Performance Test",
            template_name="emails/performance.html",
            context={"test": "performance"},
            queue=True,  # Queue for performance
        )

        end_time = time.time()
        duration = end_time - start_time

        # Verify all logs were created
        assert len(logs) == len(large_recipient_list)

        # Performance check: 100 emails should be processed quickly
        # This is a sanity check, not a strict performance requirement
        assert duration < 5.0, f"Batch processing took {duration:.2f} seconds for 100 emails"


@pytest.mark.django_db
class TestEmailServiceIntegration:
    """Test EmailService integration with templates and models."""

    @pytest.fixture
    def email_template(self):
        """Fixture providing email template."""
        from ceptor_ai.email.models.models import EmailTemplate

        return EmailTemplate.objects.create(
            name="Integration Test Template",
            template_type="notification",
            template_source="inline",
            subject_template="Integration Test: {{ action }}",
            html_content="<h1>Hello {{ user_name }}</h1><p>This is an integration test.</p>",
            css_content="body { background: #f0f0f0; }",
            text_content="Hello {{ user_name }}\nThis is an integration test.",
            language="en",
            is_active=True,
        )

    @patch('django.core.mail.EmailMultiAlternatives')
    @patch('django.template.loader.render_to_string')
    def test_service_with_template_context(self, mock_render, mock_email_class, email_service, email_template):
        """Test email service with template context."""
        # Mock rendering
        mock_render.return_value = "<h1>Hello Test User</h1><p>This is an integration test.</p>"
        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        context = {
            "action": "Test Action",
            "user_name": "Test User",
        }

        # Send email using template
        log = email_service.send_email(
            recipient="test@example.com",
            subject=f"Integration Test: {context['action']}",
            template_name="components/email/notification.html",
            context=context,
            queue=False,
        )

        # Verify email was sent
        assert log is not None
        assert log.recipient == "test@example.com"
        assert "Integration Test: Test Action" in log.subject

        # Verify template was rendered with context
        mock_render.assert_called_once_with(
            "components/email/notification.html",
            context,
        )

    def test_email_log_integration(self, email_service):
        """Test integration between EmailService and EmailLog."""
        # Send multiple emails
        logs = []
        for i in range(3):
            log = email_service.send_email(
                recipient=f"user{i}@example.com",
                subject=f"Test Email {i}",
                template_name="emails/test.html",
                context={"index": i},
                queue=True,
            )
            logs.append(log)

        # Verify logs were created
        assert len(logs) == 3

        # Verify log properties
        for i, log in enumerate(logs):
            assert log.recipient == f"user{i}@example.com"
            assert log.subject == f"Test Email {i}"
            assert log.template_used == "emails/test.html"
            assert log.status == EmailLog.Status.QUEUED

        # Test log status transitions
        log = logs[0]

        # Mark as sending
        log.status = EmailLog.Status.SENDING
        log.save()
        log.refresh_from_db()
        assert log.status == EmailLog.Status.SENDING

        # Mark as sent
        log.mark_sent()
        log.refresh_from_db()
        assert log.status == EmailLog.Status.SENT
        assert log.sent_at is not None

        # Mark as failed
        log2 = logs[1]
        log2.mark_failed("SMTP error")
        log2.refresh_from_db()
        assert log2.status == EmailLog.Status.FAILED
        assert "SMTP error" in log2.error_message

    @patch('django.core.mail.EmailMultiAlternatives')
    @patch('django.template.loader.render_to_string')
    def test_complete_email_flow(self, mock_render, mock_email_class, email_service):
        """Test complete email flow from service to sending."""
        # Mock dependencies
        mock_render.return_value = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial; }
                .container { max-width: 600px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome {{ user_name }}!</h1>
                <p>Thank you for joining {{ site_name }}.</p>
                <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
            </div>
        </body>
        </html>
        """

        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        context = {
            "user_name": "New User",
            "site_name": "Test Platform",
            "dashboard_url": "https://example.com/dashboard",
        }

        # Send welcome email
        log = email_service.send_email(
            recipient="newuser@example.com",
            subject="Welcome to Test Platform!",
            template_name="emails/welcome.html",
            context=context,
            queue=False,
        )

        # Verify complete flow
        assert log is not None
        assert log.recipient == "newuser@example.com"
        assert log.subject == "Welcome to Test Platform!"
        assert log.template_used == "emails/welcome.html"
        assert log.status == EmailLog.Status.SENT

        # Verify email was constructed correctly
        mock_email_class.assert_called_once_with(
            subject="Welcome to Test Platform!",
            body=mock_render.return_value,
            from_email="noreply@example.com",
            to=["newuser@example.com"],
            reply_to=None,
        )

        # Verify HTML alternative was attached
        mock_email_instance.attach_alternative.assert_called_once_with(
            mock_render.return_value,
            "text/html",
        )

        # Verify email was sent
        mock_email_instance.send.assert_called_once_with(fail_silently=False)
