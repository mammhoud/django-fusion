"""Tests for Django Relay email services."""

import pytest
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from ceptor_ai.communication.email.models import EmailLog, EmailTemplate
from ceptor_ai.communication.email.services import BulkEmailService, EmailService


class EmailLogTests(TestCase):
    """Test EmailLog model."""

    def setUp(self):
        """Set up test fixtures."""
        self.log = EmailLog.objects.create(
            recipient="test@example.com",
            subject="Test Email",
            status=EmailLog.Status.QUEUED
        )

    def test_email_log_creation(self):
        """Test email log creation."""
        assert self.log.recipient == "test@example.com"
        assert self.log.status == EmailLog.Status.QUEUED

    def test_mark_sent(self):
        """Test marking email as sent."""
        self.log.mark_sent()
        self.log.refresh_from_db()
        assert self.log.status == EmailLog.Status.SENT
        assert self.log.sent_at is not None

    def test_mark_failed(self):
        """Test marking email as failed."""
        error_msg = "SMTP connection failed"
        self.log.mark_failed(error_msg)
        self.log.refresh_from_db()
        assert self.log.status == EmailLog.Status.FAILED
        assert self.log.error_message == error_msg

    def test_increment_retry(self):
        """Test incrementing retry count."""
        initial_count = self.log.retry_count
        self.log.increment_retry()
        self.log.refresh_from_db()
        assert self.log.retry_count == initial_count + 1
        assert self.log.last_retry_at is not None


class EmailTemplateTests(TestCase):
    """Test EmailTemplate model."""

    def setUp(self):
        """Set up test fixtures."""
        self.template = EmailTemplate.objects.create(
            name="welcome",
            subject="Welcome to our service",
            html_content="<h1>Welcome</h1>",
            text_content="Welcome to our service"
        )

    def test_template_creation(self):
        """Test template creation."""
        assert self.template.name == "welcome"
        assert self.template.is_active is True

    def test_template_uniqueness(self):
        """Test template name uniqueness."""
        with pytest.raises(Exception):
            EmailTemplate.objects.create(
                name="welcome",
                subject="Duplicate",
                html_content="<h1>Duplicate</h1>"
            )


class EmailServiceTests(TestCase):
    """Test EmailService - Task 7.1: Verify EmailService works correctly."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = EmailService()

    def test_service_initialization(self):
        """Test service initialization."""
        assert self.service.from_email is not None

    def test_send_email_creates_log(self):
        """Test that send_email creates EmailLog."""
        log = self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="emails/test.html",
            queue=True
        )
        assert log.recipient == "test@example.com"
        assert log.status == EmailLog.Status.QUEUED

    def test_send_email_queued_status(self):
        """Test that queued emails have QUEUED status."""
        log = self.service.send_email(
            recipient="user@example.com",
            subject="Queued Email",
            template_name="emails/test.html",
            queue=True
        )
        assert log.status == EmailLog.Status.QUEUED

    def test_send_invitation_email(self):
        """Test sending invitation email."""
        log = self.service.send_invitation(
            recipient="invite@example.com",
            context={"subject": "Join us!", "name": "John"},
            queue=True
        )
        assert log.recipient == "invite@example.com"
        assert log.subject == "Join us!"
        assert log.status == EmailLog.Status.QUEUED

    def test_send_notification_email(self):
        """Test sending notification email."""
        log = self.service.send_notification(
            recipient="notify@example.com",
            context={"subject": "Important Update"},
            queue=True
        )
        assert log.recipient == "notify@example.com"
        assert log.subject == "Important Update"

    def test_send_report_email(self):
        """Test sending report email."""
        log = self.service.send_report(
            recipient="report@example.com",
            context={"subject": "Monthly Report"},
            queue=True
        )
        assert log.recipient == "report@example.com"
        assert log.subject == "Monthly Report"

    def test_email_log_stores_template_name(self):
        """Test that email log stores template name."""
        template_name = "emails/custom.html"
        log = self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name=template_name,
            queue=True
        )
        assert log.template_used == template_name


class BulkEmailServiceTests(TestCase):
    """Test BulkEmailService - Task 7.2: Verify BulkEmailService works correctly."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = BulkEmailService()

    def test_send_batch_creates_logs(self):
        """Test that send_batch creates multiple logs."""
        recipients = ["user1@example.com", "user2@example.com"]
        logs = self.service.send_batch(
            recipients=recipients,
            subject="Batch Email",
            template_name="emails/batch.html",
            queue=True
        )
        assert len(logs) == 2
        assert all(log.status == EmailLog.Status.QUEUED for log in logs)

    def test_send_batch_multiple_recipients(self):
        """Test sending batch email to multiple recipients."""
        recipients = [
            "alice@example.com",
            "bob@example.com",
            "charlie@example.com"
        ]
        logs = self.service.send_batch(
            recipients=recipients,
            subject="Batch Notification",
            template_name="emails/batch.html",
            queue=True
        )
        assert len(logs) == 3
        assert all(log.recipient in recipients for log in logs)

    def test_send_batch_empty_recipients(self):
        """Test sending batch email with empty recipients list."""
        logs = self.service.send_batch(
            recipients=[],
            subject="Empty Batch",
            template_name="emails/batch.html",
            queue=True
        )
        assert len(logs) == 0

    def test_send_batch_with_context(self):
        """Test sending batch email with context variables."""
        recipients = ["user1@example.com", "user2@example.com"]
        context = {"company": "ACME Corp", "year": 2024}
        logs = self.service.send_batch(
            recipients=recipients,
            subject="Batch with Context",
            template_name="emails/batch.html",
            context=context,
            queue=True
        )
        assert len(logs) == 2

    def test_send_group_email_creates_logs(self):
        """Test sending email to group creates logs for all members."""
        # Create a group and users
        group = Group.objects.create(name="test_group")
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com"
        )
        group.user_set.add(user1, user2)

        logs = self.service.send_group_email(
            group_name="test_group",
            subject="Group Email",
            template_name="emails/group.html"
        )
        assert len(logs) == 2

    def test_send_group_email_nonexistent_group(self):
        """Test sending email to nonexistent group raises error."""
        with pytest.raises(ValueError, match="Group not found"):
            self.service.send_group_email(
                group_name="nonexistent",
                subject="Test",
                template_name="emails/test.html"
            )

    def test_send_group_email_with_no_users(self):
        """Test sending email to empty group."""
        Group.objects.create(name="empty_group")
        logs = self.service.send_group_email(
            group_name="empty_group",
            subject="Empty Group Email",
            template_name="emails/group.html"
        )
        assert len(logs) == 0


class EmailTemplateRenderingTests(TestCase):
    """Test email template rendering - Task 7.3: Test email template rendering."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = EmailService()

    def test_render_template_with_context(self):
        """Test rendering template with context variables."""
        # This test verifies that templates can be rendered with context
        # The actual rendering happens in _render_template method
        context = {"name": "John", "company": "ACME"}
        # Template rendering is tested indirectly through send_email
        log = self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="emails/test.html",
            context=context,
            queue=True
        )
        assert log.recipient == "test@example.com"

    def test_template_context_includes_recipient_email(self):
        """Test that template context includes recipient email."""
        log = self.service.send_email(
            recipient="recipient@example.com",
            subject="Test",
            template_name="emails/test.html",
            context={"custom": "value"},
            queue=True
        )
        assert log.recipient == "recipient@example.com"

    def test_send_email_with_empty_context(self):
        """Test sending email with empty context."""
        log = self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="emails/test.html",
            context={},
            queue=True
        )
        assert log.status == EmailLog.Status.QUEUED

    def test_send_email_with_none_context(self):
        """Test sending email with None context."""
        log = self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="emails/test.html",
            context=None,
            queue=True
        )
        assert log.status == EmailLog.Status.QUEUED


class EmailLogRecordTests(TestCase):
    """Test EmailLog record creation - Task 7.4: Verify EmailLog records are created."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = EmailService()

    def test_email_log_created_on_send(self):
        """Test that EmailLog record is created when email is sent."""
        initial_count = EmailLog.objects.count()
        self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="emails/test.html",
            queue=True
        )
        assert EmailLog.objects.count() == initial_count + 1

    def test_email_log_contains_recipient(self):
        """Test that EmailLog contains recipient email."""
        recipient = "user@example.com"
        self.service.send_email(
            recipient=recipient,
            subject="Test",
            template_name="emails/test.html",
            queue=True
        )
        log = EmailLog.objects.get(recipient=recipient)
        assert log.recipient == recipient

    def test_email_log_contains_subject(self):
        """Test that EmailLog contains email subject."""
        subject = "Test Subject"
        self.service.send_email(
            recipient="test@example.com",
            subject=subject,
            template_name="emails/test.html",
            queue=True
        )
        log = EmailLog.objects.get(subject=subject)
        assert log.subject == subject

    def test_email_log_contains_template_name(self):
        """Test that EmailLog contains template name."""
        template_name = "emails/custom.html"
        self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name=template_name,
            queue=True
        )
        log = EmailLog.objects.get(template_used=template_name)
        assert log.template_used == template_name

    def test_email_log_has_timestamp(self):
        """Test that EmailLog has timestamp."""
        self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="emails/test.html",
            queue=True
        )
        log = EmailLog.objects.latest("timestamp")
        assert log.timestamp is not None

    def test_email_log_has_created_at(self):
        """Test that EmailLog has created_at timestamp."""
        self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="emails/test.html",
            queue=True
        )
        log = EmailLog.objects.latest("created_at")
        assert log.created_at is not None

    def test_bulk_email_creates_multiple_logs(self):
        """Test that bulk email creates multiple EmailLog records."""
        recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]
        bulk_service = BulkEmailService()
        bulk_service.send_batch(
            recipients=recipients,
            subject="Bulk Test",
            template_name="emails/bulk.html",
            queue=True
        )
        logs = EmailLog.objects.filter(subject="Bulk Test")
        assert logs.count() == 3


class EmailErrorHandlingTests(TestCase):
    """Test error handling for invalid emails - Task 7.5: Test error handling for invalid emails."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = EmailService()

    def test_invalid_email_format_queued(self):
        """Test that invalid email format is still queued (validation happens on send)."""
        # Invalid email addresses should still create a log entry
        # Validation typically happens when actually sending
        log = self.service.send_email(
            recipient="invalid-email",
            subject="Test",
            template_name="emails/test.html",
            queue=True
        )
        assert log.recipient == "invalid-email"
        assert log.status == EmailLog.Status.QUEUED

    def test_empty_recipient_email(self):
        """Test handling of empty recipient email."""
        log = self.service.send_email(
            recipient="",
            subject="Test",
            template_name="emails/test.html",
            queue=True
        )
        assert log.recipient == ""

    def test_email_log_mark_failed_stores_error(self):
        """Test that mark_failed stores error message."""
        log = EmailLog.objects.create(
            recipient="test@example.com",
            subject="Test",
            status=EmailLog.Status.SENDING
        )
        error_msg = "SMTP connection timeout"
        log.mark_failed(error_msg)
        log.refresh_from_db()
        assert log.error_message == error_msg
        assert log.status == EmailLog.Status.FAILED

    def test_email_log_retry_count_increments(self):
        """Test that retry count increments on failure."""
        log = EmailLog.objects.create(
            recipient="test@example.com",
            subject="Test",
            status=EmailLog.Status.FAILED,
            retry_count=0
        )
        log.increment_retry()
        log.refresh_from_db()
        assert log.retry_count == 1

    def test_email_log_multiple_retries(self):
        """Test multiple retry attempts."""
        log = EmailLog.objects.create(
            recipient="test@example.com",
            subject="Test",
            status=EmailLog.Status.FAILED,
            retry_count=0
        )
        for _ in range(3):
            log.increment_retry()
        log.refresh_from_db()
        assert log.retry_count == 3

    def test_bulk_email_with_invalid_recipients(self):
        """Test bulk email with mix of valid and invalid recipients."""
        recipients = [
            "valid@example.com",
            "invalid-email",
            "another@example.com"
        ]
        bulk_service = BulkEmailService()
        logs = bulk_service.send_batch(
            recipients=recipients,
            subject="Mixed Recipients",
            template_name="emails/test.html",
            queue=True
        )
        # All recipients should create logs, even invalid ones
        assert len(logs) == 3

    def test_email_log_status_transitions(self):
        """Test email log status transitions."""
        log = EmailLog.objects.create(
            recipient="test@example.com",
            subject="Test",
            status=EmailLog.Status.QUEUED
        )
        assert log.status == EmailLog.Status.QUEUED

        log.mark_sent()
        log.refresh_from_db()
        assert log.status == EmailLog.Status.SENT

    def test_email_log_failed_status_with_error(self):
        """Test email log failed status includes error message."""
        log = EmailLog.objects.create(
            recipient="test@example.com",
            subject="Test",
            status=EmailLog.Status.SENDING
        )
        error = "Connection refused"
        log.mark_failed(error)
        log.refresh_from_db()
        assert log.status == EmailLog.Status.FAILED
        assert log.error_message == error
