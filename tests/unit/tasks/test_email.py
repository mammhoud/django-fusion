"""Unit tests for tasks/email.py — send_email_task, send_bulk_email_task, send_email_raw."""

from unittest.mock import MagicMock, patch

import pytest

from tasks.email import (
    EMAIL_SERVICE_PATHS,
    send_bulk_email_task,
    send_email_raw,
    send_email_task,
)


# ---------------------------------------------------------------------------
# send_email_task
# ---------------------------------------------------------------------------

class TestSendEmailTask:
    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_successful_send(self, mock_configure, mock_import):
        mock_configure.return_value = "lms-demo"
        mock_service_instance = MagicMock()
        mock_service_instance.send.return_value = True
        mock_service_cls = MagicMock(return_value=mock_service_instance)
        mock_import.return_value = mock_service_cls

        result = send_email_task(
            to="user@example.com",
            subject="Welcome",
            template="welcome.html",
            context={"name": "Alice"},
            website="lms-demo",
        )
        assert result is True
        mock_service_instance.send.assert_called_once_with(
            to="user@example.com",
            subject="Welcome",
            template="welcome.html",
            context={"name": "Alice"},
        )

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_send_with_none_context(self, mock_configure, mock_import):
        mock_configure.return_value = "lms-demo"
        mock_service_instance = MagicMock()
        mock_service_instance.send.return_value = True
        mock_service_cls = MagicMock(return_value=mock_service_instance)
        mock_import.return_value = mock_service_cls

        send_email_task(to="u@e.com", subject="Hi", template="t.html")
        mock_service_instance.send.assert_called_once_with(
            to="u@e.com", subject="Hi", template="t.html", context={},
        )

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_raises_on_service_false(self, mock_configure, mock_import):
        mock_configure.return_value = "lms-demo"
        mock_service_instance = MagicMock()
        mock_service_instance.send.return_value = False
        mock_service_cls = MagicMock(return_value=mock_service_instance)
        mock_import.return_value = mock_service_cls

        with pytest.raises(RuntimeError, match="Email service returned False"):
            send_email_task(to="u@e.com", subject="Hi", template="t.html")


# ---------------------------------------------------------------------------
# send_bulk_email_task
# ---------------------------------------------------------------------------

class TestSendBulkEmailTask:
    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_bulk_send_all_succeed(self, mock_configure, mock_import):
        mock_service_instance = MagicMock()
        mock_service_instance.send.return_value = True
        mock_import.return_value = MagicMock(return_value=mock_service_instance)

        recipients = [
            {"email": "a@e.com", "context": {"name": "Alice"}},
            {"email": "b@e.com"},
        ]
        result = send_bulk_email_task(
            recipients=recipients,
            subject="News",
            template="news.html",
            base_context={"site": "test"},
        )
        assert result == {"success": 2, "failed": 0}

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_bulk_send_skips_no_email(self, mock_configure, mock_import):
        mock_service_instance = MagicMock()
        mock_service_instance.send.return_value = True
        mock_import.return_value = MagicMock(return_value=mock_service_instance)

        recipients = [
            {"email": "a@e.com"},
            {"context": {"name": "No email"}},  # missing email key
            {"email": ""},  # empty email
        ]
        result = send_bulk_email_task(
            recipients=recipients, subject="Hi", template="t.html",
        )
        assert result == {"success": 1, "failed": 0}

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_bulk_send_counts_failures(self, mock_configure, mock_import):
        mock_service_instance = MagicMock()
        mock_service_instance.send.return_value = False
        mock_import.return_value = MagicMock(return_value=mock_service_instance)

        recipients = [{"email": "a@e.com"}]
        result = send_bulk_email_task(
            recipients=recipients, subject="Hi", template="t.html",
        )
        assert result == {"success": 0, "failed": 1}

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_bulk_send_catches_exceptions(self, mock_configure, mock_import):
        mock_service_instance = MagicMock()
        mock_service_instance.send.side_effect = RuntimeError("SMTP error")
        mock_import.return_value = MagicMock(return_value=mock_service_instance)

        recipients = [{"email": "fail@e.com"}]
        result = send_bulk_email_task(
            recipients=recipients, subject="Hi", template="t.html",
        )
        assert result == {"success": 0, "failed": 1}

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_bulk_send_merges_context(self, mock_configure, mock_import):
        mock_service_instance = MagicMock()
        mock_service_instance.send.return_value = True
        mock_import.return_value = MagicMock(return_value=mock_service_instance)

        recipients = [{"email": "a@e.com", "context": {"name": "Alice"}}]
        send_bulk_email_task(
            recipients=recipients,
            subject="Hi",
            template="t.html",
            base_context={"site": "test"},
        )
        call_kwargs = mock_service_instance.send.call_args[1]
        assert call_kwargs["context"] == {"site": "test", "name": "Alice"}


# ---------------------------------------------------------------------------
# send_email_raw
# ---------------------------------------------------------------------------

class TestSendEmailRaw:
    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_send_raw_email(self, mock_configure, mock_import):
        mock_email = MagicMock()
        mock_email.send.return_value = 1
        mock_class = MagicMock(return_value=mock_email)
        mock_import.return_value = mock_class

        result = send_email_raw(
            subject="Test",
            recipients=["user@e.com"],
            html_content="<p>hi</p>",
            text_content="hi",
            from_email="noreply@e.com",
            reply_to="reply@e.com",
            bcc=["bcc@e.com"],
            attachments=[{"filename": "f.txt", "content": "data", "mimetype": "text/plain"}],
        )
        assert result is True
        mock_email.attach_alternative.assert_called_once_with("<p>hi</p>", "text/html")
        mock_email.attach.assert_called_once()

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_send_raw_email_no_reply_to(self, mock_configure, mock_import):
        mock_email = MagicMock()
        mock_email.send.return_value = 1
        mock_class = MagicMock(return_value=mock_email)
        mock_import.return_value = mock_class

        send_email_raw(
            subject="Test",
            recipients=["user@e.com"],
            html_content="<p>hi</p>",
            text_content="hi",
            from_email="noreply@e.com",
        )
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["reply_to"] is None

    @patch("tasks.email.import_first")
    @patch("tasks.email.configure_django_for_website")
    def test_send_raw_returns_false_on_zero(self, mock_configure, mock_import):
        mock_email = MagicMock()
        mock_email.send.return_value = 0
        mock_class = MagicMock(return_value=mock_email)
        mock_import.return_value = mock_class

        result = send_email_raw(
            subject="Test",
            recipients=["user@e.com"],
            html_content="<p>hi</p>",
            text_content="hi",
            from_email="noreply@e.com",
        )
        assert result is False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestEmailConstants:
    def test_email_service_paths_non_empty(self):
        assert len(EMAIL_SERVICE_PATHS) > 0

    def test_paths_end_with_email_service(self):
        for path in EMAIL_SERVICE_PATHS:
            assert path.endswith("EmailService")
