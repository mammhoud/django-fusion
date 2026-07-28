"""
Tests for recovered tasks.py files — send_user_welcome_notification.

Validates that the recovered apps.pages.tasks and apps.content.tasks modules
provide the send_user_welcome_notification function that signals/user.py expects.

These are simple import and unit tests that don't require Django setup.
"""
from unittest.mock import MagicMock, patch


def _make_user(username="testuser", email="test@example.com", full_name=""):
    user = MagicMock()
    user.username = username
    user.email = email
    user.get_full_name.return_value = full_name
    return user


def test_pages_tasks_function_exists():
    """send_user_welcome_notification must be importable from apps.pages.tasks."""
    from apps.pages.tasks import send_user_welcome_notification  # noqa: F401
    assert callable(send_user_welcome_notification)


def test_content_tasks_function_exists():
    """send_user_welcome_notification must be importable from apps.content.tasks."""
    from apps.content.tasks import send_user_welcome_notification  # noqa: F401
    assert callable(send_user_welcome_notification)


def test_pages_sends_email_to_user():
    """Should call send_mail with the user's email address."""
    from apps.pages.tasks import send_user_welcome_notification

    user = _make_user(email="hello@example.com")
    profile = MagicMock()

    with patch("django.core.mail.send_mail") as mock_send:
        send_user_welcome_notification(user, profile)
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        recipient_list = kwargs.get("recipient_list") or args[3]
        assert "hello@example.com" in recipient_list


def test_pages_uses_full_name_when_available():
    """Should use full name in message when available."""
    from apps.pages.tasks import send_user_welcome_notification

    user = _make_user(full_name="Alice Smith")
    profile = MagicMock()

    with patch("django.core.mail.send_mail") as mock_send:
        send_user_welcome_notification(user, profile)
        args, kwargs = mock_send.call_args
        message = kwargs.get("message") or args[1]
        assert "Alice Smith" in message


def test_pages_falls_back_to_username():
    """Should use username in message when full name is empty."""
    from apps.pages.tasks import send_user_welcome_notification

    user = _make_user(username="bob123", full_name="")
    profile = MagicMock()

    with patch("django.core.mail.send_mail") as mock_send:
        send_user_welcome_notification(user, profile)
        args, kwargs = mock_send.call_args
        message = kwargs.get("message") or args[1]
        assert "bob123" in message


def test_pages_does_not_raise_on_send_failure():
    """Should not raise even if send_mail raises an exception."""
    from apps.pages.tasks import send_user_welcome_notification

    user = _make_user()
    profile = MagicMock()

    with patch("django.core.mail.send_mail", side_effect=Exception("SMTP error")):
        send_user_welcome_notification(user, profile)  # must not raise


def test_content_sends_email_to_user():
    """Should call send_mail with the user's email address."""
    from apps.content.tasks import send_user_welcome_notification

    user = _make_user(email="content@example.com")
    profile = MagicMock()

    with patch("django.core.mail.send_mail") as mock_send:
        send_user_welcome_notification(user, profile)
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        recipient_list = kwargs.get("recipient_list") or args[3]
        assert "content@example.com" in recipient_list


def test_content_does_not_raise_on_send_failure():
    """Should not raise even if send_mail raises an exception."""
    from apps.content.tasks import send_user_welcome_notification

    user = _make_user()
    profile = MagicMock()

    with patch("django.core.mail.send_mail", side_effect=Exception("SMTP error")):
        send_user_welcome_notification(user, profile)  # must not raise

