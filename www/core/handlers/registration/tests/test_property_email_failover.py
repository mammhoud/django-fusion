"""
Property-based tests for email failover in send_registration_email().

**Validates: Requirements 5.8, 5.9, 17.3**

Tests the failover behavior of `send_registration_email()` from
`apps.accounts.registration.emails`.

Property 3: When primary SMTP sender raises `SMTPException`,
`send_registration_email()` attempts the secondary sender.

Specifically:
  1. When the primary SMTP sender raises SMTPException, the secondary
     sender is attempted.
  2. When both SMTP senders fail, the Django backend fallback is attempted.
  3. When the primary sender succeeds, the secondary sender is NOT called.
  4. The function returns True when any sender succeeds, False when all fail.
"""

# ---------------------------------------------------------------------------
# Minimal Django setup — must happen before any django.* import
# ---------------------------------------------------------------------------
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
            }
        },
        SECRET_KEY="test-secret-key-for-property-tests-at-least-50-chars-long!!",
        USE_TZ=True,
        DEFAULT_FROM_EMAIL="noreply@structa.cloud",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": False,
                "OPTIONS": {"context_processors": []},
            }
        ],
    )
    django.setup()

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import smtplib  # noqa: E402
from unittest.mock import call, patch  # noqa: E402

from hypothesis import given  # noqa: E402
from hypothesis import settings as h_settings
from hypothesis import strategies as st  # noqa: E402
from plugins.accounts.registration.emails import (  # noqa: E402
    send_registration_email,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid-ish email addresses for the recipient
email_strategy = st.emails()

# Confirmation URLs — simple https URLs with a path token
url_strategy = st.builds(
    "https://structa.cloud/create-password/{}/".format,
    st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
        min_size=8,
        max_size=64,
    ),
)

# Two controlled sender accounts returned by _get_sender_accounts
_FAKE_ACCOUNTS = [
    {"email": "sender1@example.com", "password": "pass1", "name": "CTC Research"},
    {"email": "sender2@example.com", "password": "pass2", "name": "CTC Research"},
]


def _make_fake_user(email: str):
    """Create a minimal fake user object."""

    class FakeUser:
        pass

    user = FakeUser()
    user.email = email
    user.first_name = "Test"
    user.last_name = "User"
    return user


# ---------------------------------------------------------------------------
# Property 3a: Primary failure → secondary sender is attempted
# ---------------------------------------------------------------------------


@given(email_strategy, url_strategy)
@h_settings(max_examples=50)
def test_secondary_sender_attempted_when_primary_fails(
    recipient_email: str, confirmation_url: str
):
    """
    **Property 3 (part 1) — Validates: Requirements 5.8, 5.9, 17.3**

    When the primary SMTP sender raises SMTPException, the secondary
    sender must be attempted.

    The call count on _send_via_smtp must be exactly 2 (primary tried,
    secondary tried) when the primary raises and the secondary succeeds.
    """
    user = _make_fake_user(recipient_email)

    smtp_exc = smtplib.SMTPException("primary sender failed")

    # primary raises, secondary succeeds
    side_effects = [smtp_exc, True]

    with patch(
        "apps.accounts.registration.emails._get_sender_accounts",
        return_value=_FAKE_ACCOUNTS,
    ), patch(
        "apps.accounts.registration.emails._send_via_smtp",
        side_effect=side_effects,
    ) as mock_smtp, patch(
        "apps.accounts.registration.emails.render_to_string",
        return_value="<html>email</html>",
    ):
        result = send_registration_email(user, confirmation_url)

    assert result is True, (
        "send_registration_email() should return True when the secondary "
        "sender succeeds after the primary raises SMTPException."
    )
    assert mock_smtp.call_count == 2, (
        f"_send_via_smtp should be called twice (primary + secondary), "
        f"but was called {mock_smtp.call_count} time(s)."
    )
    # Verify the second call used the secondary account credentials
    second_call_kwargs = mock_smtp.call_args_list[1]
    assert second_call_kwargs == call(
        sender_email=_FAKE_ACCOUNTS[1]["email"],
        sender_password=_FAKE_ACCOUNTS[1]["password"],
        sender_name=_FAKE_ACCOUNTS[1]["name"],
        recipient_email=recipient_email,
        subject=mock_smtp.call_args_list[0].kwargs["subject"],
        html_content=mock_smtp.call_args_list[0].kwargs["html_content"],
        text_content=mock_smtp.call_args_list[0].kwargs["text_content"],
    ), "Second _send_via_smtp call must use the secondary sender account."


# ---------------------------------------------------------------------------
# Property 3b: Both SMTP senders fail → Django backend fallback is attempted
# ---------------------------------------------------------------------------


@given(email_strategy, url_strategy)
@h_settings(max_examples=50)
def test_django_backend_attempted_when_all_smtp_fail(
    recipient_email: str, confirmation_url: str
):
    """
    **Property 3 (part 2) — Validates: Requirements 5.8, 5.9, 17.3**

    When both SMTP senders raise SMTPException, the Django backend
    fallback must be attempted.
    """
    user = _make_fake_user(recipient_email)

    smtp_exc = smtplib.SMTPException("smtp sender failed")

    with patch(
        "apps.accounts.registration.emails._get_sender_accounts",
        return_value=_FAKE_ACCOUNTS,
    ), patch(
        "apps.accounts.registration.emails._send_via_smtp",
        side_effect=[smtp_exc, smtp_exc],
    ) as mock_smtp, patch(
        "apps.accounts.registration.emails._send_with_django_backend",
        return_value=True,
    ) as mock_django, patch(
        "apps.accounts.registration.emails.render_to_string",
        return_value="<html>email</html>",
    ):
        result = send_registration_email(user, confirmation_url)

    assert result is True, (
        "send_registration_email() should return True when the Django "
        "backend fallback succeeds after both SMTP senders fail."
    )
    assert mock_smtp.call_count == 2, (
        f"_send_via_smtp should be called twice (both senders tried), "
        f"but was called {mock_smtp.call_count} time(s)."
    )
    mock_django.assert_called_once(), (
        "_send_with_django_backend must be called exactly once as the "
        "final fallback when all SMTP senders fail."
    )


# ---------------------------------------------------------------------------
# Property 3c: Primary succeeds → secondary sender is NOT called
# ---------------------------------------------------------------------------


@given(email_strategy, url_strategy)
@h_settings(max_examples=50)
def test_secondary_not_called_when_primary_succeeds(
    recipient_email: str, confirmation_url: str
):
    """
    **Property 3 (part 3) — Validates: Requirements 5.8, 5.9, 17.3**

    When the primary SMTP sender succeeds, the secondary sender must
    NOT be called. The function should short-circuit on first success.
    """
    user = _make_fake_user(recipient_email)

    with patch(
        "apps.accounts.registration.emails._get_sender_accounts",
        return_value=_FAKE_ACCOUNTS,
    ), patch(
        "apps.accounts.registration.emails._send_via_smtp",
        return_value=True,
    ) as mock_smtp, patch(
        "apps.accounts.registration.emails._send_with_django_backend",
    ) as mock_django, patch(
        "apps.accounts.registration.emails.render_to_string",
        return_value="<html>email</html>",
    ):
        result = send_registration_email(user, confirmation_url)

    assert result is True, (
        "send_registration_email() should return True when the primary "
        "sender succeeds."
    )
    assert mock_smtp.call_count == 1, (
        f"_send_via_smtp should be called exactly once (primary only), "
        f"but was called {mock_smtp.call_count} time(s). "
        "Secondary sender must not be attempted when primary succeeds."
    )
    mock_django.assert_not_called(), (
        "_send_with_django_backend must not be called when the primary "
        "SMTP sender succeeds."
    )


# ---------------------------------------------------------------------------
# Property 3d: All senders fail → function returns False
# ---------------------------------------------------------------------------


@given(email_strategy, url_strategy)
@h_settings(max_examples=50)
def test_returns_false_when_all_senders_fail(
    recipient_email: str, confirmation_url: str
):
    """
    **Property 3 (part 4) — Validates: Requirements 5.8, 5.9, 17.3**

    When all SMTP senders raise SMTPException AND the Django backend
    also fails, send_registration_email() must return False.
    """
    user = _make_fake_user(recipient_email)

    smtp_exc = smtplib.SMTPException("smtp sender failed")

    with patch(
        "apps.accounts.registration.emails._get_sender_accounts",
        return_value=_FAKE_ACCOUNTS,
    ), patch(
        "apps.accounts.registration.emails._send_via_smtp",
        side_effect=[smtp_exc, smtp_exc],
    ), patch(
        "apps.accounts.registration.emails._send_with_django_backend",
        return_value=False,
    ), patch(
        "apps.accounts.registration.emails.render_to_string",
        return_value="<html>email</html>",
    ):
        result = send_registration_email(user, confirmation_url)

    assert result is False, (
        "send_registration_email() must return False when all SMTP senders "
        "raise SMTPException and the Django backend also fails."
    )
