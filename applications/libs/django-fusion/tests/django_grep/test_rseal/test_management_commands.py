"""
Unit tests for Django management commands.

Tests invite_user and send_pending_invitations management commands
using Django's call_command() helper.
"""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone
from ceptor_ai.communication.email.models import EmailLog

User = get_user_model()


# ---------------------------------------------------------------------------
# invite_user command
# ---------------------------------------------------------------------------


class InviteUserCommandTestCase(TestCase):
    """Tests for the invite_user management command."""

    def _call(self, *args, **kwargs):
        """Helper: run invite_user and capture stdout/stderr."""
        stdout = StringIO()
        stderr = StringIO()
        call_command("invite_user", *args, stdout=stdout, stderr=stderr, **kwargs)
        return stdout.getvalue(), stderr.getvalue()

    # ------------------------------------------------------------------
    # Happy-path
    # ------------------------------------------------------------------

    @patch("ceptor_ai.management.commands.invite_user.InvitationService")
    def test_valid_inputs_queues_invitation(self, MockService):
        """Command succeeds and prints success message for valid inputs."""
        mock_log = MagicMock()
        mock_log.id = 42
        mock_log.status = EmailLog.Status.QUEUED
        MockService.return_value.invite_user.return_value = mock_log

        stdout, stderr = self._call("--email", "new@example.com", "--role", "instructor")

        MockService.return_value.invite_user.assert_called_once_with(
            email="new@example.com", role="instructor", force=False
        )
        self.assertIn("42", stdout)
        self.assertEqual(stderr, "")

    @patch("ceptor_ai.management.commands.invite_user.InvitationService")
    def test_force_flag_passed_to_service(self, MockService):
        """--force flag is forwarded to InvitationService.invite_user()."""
        mock_log = MagicMock()
        mock_log.id = 7
        mock_log.status = EmailLog.Status.QUEUED
        MockService.return_value.invite_user.return_value = mock_log

        self._call("--email", "user@example.com", "--role", "manager", "--force")

        MockService.return_value.invite_user.assert_called_once_with(
            email="user@example.com", role="manager", force=True
        )

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def test_missing_email_raises_error(self):
        """Command fails when --email is omitted."""
        with self.assertRaises(CommandError):
            call_command("invite_user", "--role", "instructor")

    def test_missing_role_raises_error(self):
        """Command fails when --role is omitted."""
        with self.assertRaises(CommandError):
            call_command("invite_user", "--email", "user@example.com")

    @patch("ceptor_ai.management.commands.invite_user.InvitationService")
    def test_already_registered_user_raises_command_error(self, MockService):
        """Command raises CommandError when user is already registered."""
        MockService.return_value.invite_user.side_effect = ValueError(
            "User already registered: user@example.com"
        )

        with self.assertRaises(CommandError) as cm:
            call_command("invite_user", "--email", "user@example.com", "--role", "instructor")

        self.assertIn("already registered", str(cm.exception))

    @patch("ceptor_ai.management.commands.invite_user.InvitationService")
    def test_recently_invited_user_raises_command_error(self, MockService):
        """Command raises CommandError when user was recently invited."""
        MockService.return_value.invite_user.side_effect = ValueError(
            "User was invited within last 7 days"
        )

        with self.assertRaises(CommandError) as cm:
            call_command("invite_user", "--email", "recent@example.com", "--role", "instructor")

        self.assertIn("7 days", str(cm.exception))

    @patch("ceptor_ai.management.commands.invite_user.InvitationService")
    def test_force_bypasses_duplicate_prevention(self, MockService):
        """--force flag allows re-inviting a recently invited user."""
        mock_log = MagicMock()
        mock_log.id = 99
        mock_log.status = EmailLog.Status.QUEUED
        MockService.return_value.invite_user.return_value = mock_log

        # Should NOT raise even though user was recently invited (service handles force)
        stdout, _ = self._call(
            "--email", "recent@example.com", "--role", "instructor", "--force"
        )

        MockService.return_value.invite_user.assert_called_once_with(
            email="recent@example.com", role="instructor", force=True
        )
        self.assertIn("99", stdout)

    @patch("ceptor_ai.management.commands.invite_user.InvitationService")
    def test_unexpected_exception_raises_command_error(self, MockService):
        """Unexpected exceptions are wrapped in CommandError."""
        MockService.return_value.invite_user.side_effect = RuntimeError("DB is down")

        with self.assertRaises(CommandError) as cm:
            call_command("invite_user", "--email", "x@example.com", "--role", "instructor")

        self.assertIn("DB is down", str(cm.exception))

    # ------------------------------------------------------------------
    # Database / logging integration
    # ------------------------------------------------------------------

    @patch("ceptor_ai.management.commands.invite_user.InvitationService")
    def test_email_log_created_by_service(self, MockService):
        """EmailLog record is created (via service) when invitation is queued."""
        log = EmailLog.objects.create(
            recipient="newuser@example.com",
            subject="You are invited!",
            template_used="emails/invitation.html",
            status=EmailLog.Status.QUEUED,
        )
        MockService.return_value.invite_user.return_value = log

        self._call("--email", "newuser@example.com", "--role", "instructor")

        self.assertTrue(EmailLog.objects.filter(recipient="newuser@example.com").exists())


# ---------------------------------------------------------------------------
# send_pending_invitations command
# ---------------------------------------------------------------------------


class SendPendingInvitationsCommandTestCase(TestCase):
    """Tests for the send_pending_invitations management command."""

    def _call(self, *args, **kwargs):
        stdout = StringIO()
        stderr = StringIO()
        call_command("send_pending_invitations", *args, stdout=stdout, stderr=stderr, **kwargs)
        return stdout.getvalue(), stderr.getvalue()

    def _make_queued_log(self, recipient, subject="Invitation"):
        return EmailLog.objects.create(
            recipient=recipient,
            subject=subject,
            template_used="emails/invitation.html",
            status=EmailLog.Status.QUEUED,
        )

    # ------------------------------------------------------------------
    # Happy-path
    # ------------------------------------------------------------------

    @patch("ceptor_ai.management.commands.send_pending_invitations.EmailService")
    def test_processes_all_queued_logs(self, MockEmailService):
        """Command processes every QUEUED EmailLog entry."""
        log1 = self._make_queued_log("a@example.com")
        log2 = self._make_queued_log("b@example.com")

        mock_service = MockEmailService.return_value
        mock_service._send_now.side_effect = lambda **kw: kw.get("log") or log1

        stdout, _ = self._call()

        self.assertEqual(mock_service._send_now.call_count, 2)
        self.assertIn("Total: 2", stdout)

    @patch("ceptor_ai.management.commands.send_pending_invitations.EmailService")
    def test_limit_parameter_restricts_processing(self, MockEmailService):
        """--limit N processes at most N pending invitations."""
        for i in range(5):
            self._make_queued_log(f"user{i}@example.com")

        mock_service = MockEmailService.return_value
        mock_service._send_now.return_value = None

        stdout, _ = self._call("--limit", "3")

        self.assertEqual(mock_service._send_now.call_count, 3)
        self.assertIn("Total: 3", stdout)

    @patch("ceptor_ai.management.commands.send_pending_invitations.EmailService")
    def test_no_pending_invitations(self, MockEmailService):
        """Command handles empty queue gracefully."""
        stdout, _ = self._call()

        MockEmailService.return_value._send_now.assert_not_called()
        self.assertIn("0", stdout)

    @patch("ceptor_ai.management.commands.send_pending_invitations.EmailService")
    def test_skips_non_queued_logs(self, MockEmailService):
        """Command only processes QUEUED logs, not SENT or FAILED ones."""
        EmailLog.objects.create(
            recipient="sent@example.com",
            subject="Already sent",
            template_used="emails/invitation.html",
            status=EmailLog.Status.SENT,
        )
        EmailLog.objects.create(
            recipient="failed@example.com",
            subject="Failed",
            template_used="emails/invitation.html",
            status=EmailLog.Status.FAILED,
        )
        queued = self._make_queued_log("queued@example.com")

        mock_service = MockEmailService.return_value
        mock_service._send_now.return_value = None

        stdout, _ = self._call()

        self.assertEqual(mock_service._send_now.call_count, 1)
        call_kwargs = mock_service._send_now.call_args
        recipient = call_kwargs.kwargs.get("recipient") or call_kwargs[1].get("recipient")
        self.assertEqual(recipient, "queued@example.com")

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    @patch("ceptor_ai.management.commands.send_pending_invitations.EmailService")
    def test_failed_send_does_not_abort_remaining(self, MockEmailService):
        """A failure for one email does not stop processing of subsequent ones."""
        self._make_queued_log("fail@example.com")
        self._make_queued_log("ok@example.com")

        mock_service = MockEmailService.return_value

        def side_effect(*args, **kwargs):
            recipient = kwargs.get("recipient", "")
            if recipient == "fail@example.com":
                raise Exception("SMTP error")
            # Simulate mark_sent on the log
            log = kwargs.get("log")
            if log:
                log.status = EmailLog.Status.SENT
                log.save(update_fields=["status"])

        mock_service._send_now.side_effect = side_effect

        stdout, stderr = self._call()

        self.assertEqual(mock_service._send_now.call_count, 2)
        self.assertIn("Failed: 1", stdout)
        self.assertIn("Sent: 1", stdout)

    @patch("ceptor_ai.management.commands.send_pending_invitations.EmailService")
    def test_database_updated_after_send(self, MockEmailService):
        """EmailLog status is updated to SENT after successful send."""
        log = self._make_queued_log("update@example.com")

        def mark_sent_side_effect(*args, **kwargs):
            kw_log = kwargs.get("log")
            if kw_log:
                kw_log.mark_sent()

        MockEmailService.return_value._send_now.side_effect = mark_sent_side_effect

        self._call()

        log.refresh_from_db()
        self.assertEqual(log.status, EmailLog.Status.SENT)

    @patch("ceptor_ai.management.commands.send_pending_invitations.EmailService")
    def test_summary_printed_to_stdout(self, MockEmailService):
        """Command prints a summary line with sent/failed/total counts."""
        self._make_queued_log("x@example.com")
        MockEmailService.return_value._send_now.return_value = None

        stdout, _ = self._call()

        self.assertIn("Sent:", stdout)
        self.assertIn("Failed:", stdout)
        self.assertIn("Total:", stdout)
