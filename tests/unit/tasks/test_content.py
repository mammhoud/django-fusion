"""Unit tests for tasks/content.py — get_users_count, welcome notification tasks."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from configs.tools.worker.content import (
    get_users_count,
    send_user_welcome_notification,
    send_user_welcome_notification_task,
)

# ---------------------------------------------------------------------------
# get_users_count
# ---------------------------------------------------------------------------

class TestGetUsersCount:
    @patch("configs.tools.worker.content.import_first")
    @patch("configs.tools.worker.content.configure_django_for_website")
    def test_returns_user_count(self, mock_configure, mock_import):
        mock_model = MagicMock()
        mock_model.objects.count.return_value = 42
        mock_get_user_model = MagicMock(return_value=mock_model)
        mock_import.return_value = mock_get_user_model

        result = get_users_count(website="lms")
        assert result == 42


# ---------------------------------------------------------------------------
# send_user_welcome_notification_task
# ---------------------------------------------------------------------------

class TestSendUserWelcomeNotificationTask:
    @patch("configs.tools.worker.content.import_first")
    @patch("configs.tools.worker.content.configure_django_for_website")
    def test_sends_welcome_email(self, mock_configure, mock_import):
        mock_user = MagicMock()
        mock_user.email = "user@example.com"
        mock_user.get_full_name.return_value = "Alice Smith"
        mock_user.username = "alice"

        mock_model = MagicMock()
        mock_model.objects.get.return_value = mock_user
        mock_get_user_model = MagicMock(return_value=mock_model)

        mock_settings = MagicMock()
        mock_settings.WELCOME_EMAIL_SUBJECT = "Welcome!"
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@example.com"

        mock_send_mail = MagicMock(return_value=1)

        call_count = 0
        def import_side_effect(paths):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_get_user_model
            if call_count == 2:
                return mock_settings
            if call_count == 3:
                return mock_send_mail
            return MagicMock()

        mock_import.side_effect = import_side_effect

        result = send_user_welcome_notification_task(user_id=1, website="lms")
        assert result is True
        mock_send_mail.assert_called_once()

    @patch("configs.tools.worker.content.import_first")
    @patch("configs.tools.worker.content.configure_django_for_website")
    def test_skips_user_without_email(self, mock_configure, mock_import):
        mock_user = MagicMock()
        mock_user.email = ""

        mock_model = MagicMock()
        mock_model.objects.get.return_value = mock_user
        mock_get_user_model = MagicMock(return_value=mock_model)

        call_count = 0
        def import_side_effect(paths):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_get_user_model
            if call_count == 2:
                return MagicMock()  # settings
            if call_count == 3:
                return MagicMock()  # send_mail
            return MagicMock()

        mock_import.side_effect = import_side_effect

        result = send_user_welcome_notification_task(user_id=1)
        assert result is False


# ---------------------------------------------------------------------------
# send_user_welcome_notification (compat helper)
# ---------------------------------------------------------------------------

class TestSendUserWelcomeNotification:
    @patch("configs.tools.worker.content.send_user_welcome_notification_task")
    def test_uses_send_when_available(self, mock_task):
        mock_task.send = MagicMock()
        mock_user = MagicMock()
        mock_user.pk = 5

        send_user_welcome_notification(mock_user)
        mock_task.send.assert_called_once_with(5)

    @patch("configs.tools.worker.content.send_user_welcome_notification_task")
    def test_calls_directly_without_send(self, mock_task):
        mock_task.send = None
        mock_user = MagicMock()
        mock_user.pk = 7

        send_user_welcome_notification(mock_user)
        mock_task.assert_called_once_with(7)
