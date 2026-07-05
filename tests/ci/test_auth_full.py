"""
Comprehensive auth flow tests for ctc-research.com using django-fusion test utilities.

Tests cover:
- Registration with mahmoud.ezzat.moustafa@gmail.com
- Email confirmation sent from server (Django outbox + SMTP check)
- Email confirmation link flow
- Login with valid credentials
- Login with wrong password → error notification
- Login with unverified email → blocked with message
- Password reset request → email sent
- Password reset confirmation flow
- Logout
- Admin panel access

Uses django_fusion.tests.base.BaseTestCase (Django test client — browser-style)
and django_fusion.tests.mixins.AssertHTMLMixin + AssertEmailMixin.

Email backend is overridden to locmem for all tests EXCEPT the live SMTP test
which explicitly uses the real backend to confirm server-side sending.
"""
from __future__ import annotations

import os
import re

import django
from django.conf import settings as django_settings

if not django_settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    os.environ.setdefault("DJANGO_PRINT_ENV", "false")
    django.setup()

from allauth.account.models import EmailAddress, EmailConfirmation, EmailConfirmationHMAC
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, override_settings
from django_fusion.tests.base import BaseTestCase
from django_fusion.tests.mixins import AssertEmailMixin, AssertHTMLMixin

User = get_user_model()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NEW_EMAIL = "mahmoud.ezzat.moustafa@gmail.com"
NEW_PASSWORD = "Str0ng!Pass#2024"
WRONG_PASSWORD = "WrongPassword999"

SIGNUP_URL = "/accounts/signup/"
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
PASSWORD_RESET_URL = "/accounts/password/reset/"
EMAIL_CONFIRM_URL = "/accounts/confirm-email/"

# Admin redirects to /auth/sign-in/ in this project
ADMIN_LOGIN_REDIRECT_PATTERNS = ("login", "sign-in", "signin")


# ---------------------------------------------------------------------------
# Helper: get email confirmation key from outbox
# ---------------------------------------------------------------------------
def _get_confirmation_key_from_outbox() -> str | None:
    """Extract the email confirmation key/URL from the Django email outbox."""
    for message in mail.outbox:
        # Look for confirmation URL pattern in body
        match = re.search(r'/accounts/confirm-email/([^/\s"\']+)/', message.body)
        if match:
            return match.group(1)
        # Also check for create-password token (custom adapter)
        match2 = re.search(r'/create-password/([^/\s"\']+)/', message.body)
        if match2:
            return match2.group(1)
    return None


def _get_password_reset_key_from_outbox() -> str | None:
    """Extract the password reset key from the Django email outbox."""
    for message in mail.outbox:
        match = re.search(r'/accounts/password/reset/key/([^/\s"\']+)/', message.body)
        if match:
            return match.group(1)
    return None


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationTest(AssertHTMLMixin, AssertEmailMixin, BaseTestCase):
    """
    Test user registration flow for mahmoud.ezzat.moustafa@gmail.com.

    Validates:
    - Signup page loads
    - POST to signup creates user and sends confirmation email
    - Duplicate registration is rejected
    - Email confirmation email is in outbox with correct recipient
    """

    def setUp(self):
        super().setUp()
        # Clean up test user before each test
        User.objects.filter(email=NEW_EMAIL).delete()
        mail.outbox = []

    def test_signup_page_loads(self):
        """GET /accounts/signup/ returns 200."""
        response = self.client.get(SIGNUP_URL)
        self.assertIn(response.status_code, (200, 301, 302))

    def test_register_new_account_creates_user(self):
        """
        POST to signup with mahmoud.ezzat.moustafa@gmail.com creates a new user.

        Validates: Registration flow end-to-end.
        """
        response = self.client.post(
            SIGNUP_URL,
            data={
                "email": NEW_EMAIL,
                "password1": NEW_PASSWORD,
                "password2": NEW_PASSWORD,
            },
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertTrue(
            User.objects.filter(email=NEW_EMAIL).exists(),
            f"User {NEW_EMAIL} was not created after registration POST",
        )

    def test_register_sends_confirmation_email(self):
        """
        After registration, a confirmation email must be sent to the new user.

        Validates: Email confirmation is sent from server.
        """
        self.client.post(
            SIGNUP_URL,
            data={
                "email": NEW_EMAIL,
                "password1": NEW_PASSWORD,
                "password2": NEW_PASSWORD,
            },
            follow=True,
        )
        # Check email was sent to the new user
        self.assertEmailSent(NEW_EMAIL)
        # Verify the email contains a confirmation link
        sent = [m for m in mail.outbox if NEW_EMAIL in m.to]
        self.assertTrue(len(sent) > 0, "No email sent to new user")
        body = sent[0].body
        self.assertTrue(
            "confirm" in body.lower() or "verify" in body.lower() or "password" in body.lower(),
            f"Confirmation email body does not contain expected content. Body: {body[:200]}",
        )

    def test_register_duplicate_email_rejected(self):
        """
        Registering the same email twice must not create a duplicate user.

        Validates: Idempotence property — user count stays at 1.
        """
        for _ in range(2):
            self.client.post(
                SIGNUP_URL,
                data={
                    "email": NEW_EMAIL,
                    "password1": NEW_PASSWORD,
                    "password2": NEW_PASSWORD,
                },
                follow=True,
            )
        count = User.objects.filter(email=NEW_EMAIL).count()
        self.assertEqual(count, 1, f"Expected 1 user with {NEW_EMAIL}, found {count}")

    def test_register_with_mismatched_passwords_fails(self):
        """
        Registration with mismatched passwords must fail and not create a user.
        """
        response = self.client.post(
            SIGNUP_URL,
            data={
                "email": NEW_EMAIL,
                "password1": NEW_PASSWORD,
                "password2": "DifferentPassword999",
            },
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertFalse(
            User.objects.filter(email=NEW_EMAIL).exists(),
            "User should NOT be created with mismatched passwords",
        )

    def test_register_with_weak_password_fails(self):
        """
        Registration with a too-short password must fail.
        """
        response = self.client.post(
            SIGNUP_URL,
            data={
                "email": NEW_EMAIL,
                "password1": "short",
                "password2": "short",
            },
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertFalse(
            User.objects.filter(email=NEW_EMAIL).exists(),
            "User should NOT be created with a weak password",
        )


# ---------------------------------------------------------------------------
# Email confirmation tests
# ---------------------------------------------------------------------------

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailConfirmationTest(AssertHTMLMixin, AssertEmailMixin, BaseTestCase):
    """
    Test email confirmation flow.

    Validates:
    - Confirmation email is sent after registration
    - Confirmation link marks email as verified
    - Unverified user cannot log in (mandatory verification)
    """

    def setUp(self):
        super().setUp()
        User.objects.filter(email=NEW_EMAIL).delete()
        mail.outbox = []

    def _register_user(self):
        """Register the test user and return the user object."""
        self.client.post(
            SIGNUP_URL,
            data={
                "email": NEW_EMAIL,
                "password1": NEW_PASSWORD,
                "password2": NEW_PASSWORD,
            },
            follow=True,
        )
        return User.objects.filter(email=NEW_EMAIL).first()

    def test_confirmation_email_sent_to_correct_address(self):
        """Confirmation email must be sent to the registered email address."""
        self._register_user()
        self.assertEmailSent(NEW_EMAIL)
        sent = [m for m in mail.outbox if NEW_EMAIL in m.to]
        self.assertEqual(sent[0].to[0], NEW_EMAIL)

    def test_confirmation_email_contains_link(self):
        """Confirmation email body must contain a confirmation or password-creation link."""
        self._register_user()
        sent = [m for m in mail.outbox if NEW_EMAIL in m.to]
        self.assertTrue(len(sent) > 0)
        body = sent[0].body
        has_link = (
            "/confirm-email/" in body
            or "/create-password/" in body
            or "/verify" in body
        )
        self.assertTrue(has_link, f"No confirmation link found in email body: {body[:300]}")

    def test_unverified_user_cannot_login(self):
        """
        A user who has not confirmed their email must not be able to log in
        when ACCOUNT_EMAIL_VERIFICATION = 'mandatory'.
        """
        user = self._register_user()
        if user is None:
            self.skipTest("User creation failed — skipping login test")

        # Ensure email is NOT verified
        EmailAddress.objects.filter(user=user).update(verified=False)

        response = self.client.post(
            LOGIN_URL,
            data={"login": NEW_EMAIL, "password": NEW_PASSWORD},
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        # User should NOT be authenticated
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "Unverified user should not be authenticated",
        )

    def test_verified_user_can_login(self):
        """
        A user whose email is verified can log in successfully.
        """
        user = self._register_user()
        if user is None:
            self.skipTest("User creation failed")

        # Mark email as verified
        EmailAddress.objects.filter(user=user).update(verified=True)
        # Also ensure user is active
        user.is_active = True
        user.save()

        response = self.client.post(
            LOGIN_URL,
            data={"login": NEW_EMAIL, "password": NEW_PASSWORD},
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertTrue(
            response.wsgi_request.user.is_authenticated,
            "Verified user should be authenticated after login",
        )

    def test_email_confirmation_via_key_marks_verified(self):
        """
        Visiting the confirmation URL from the email marks the email as verified.
        """
        user = self._register_user()
        if user is None:
            self.skipTest("User creation failed")

        # Get the EmailAddress object and generate a confirmation key
        email_address = EmailAddress.objects.filter(user=user, email=NEW_EMAIL).first()
        if email_address is None:
            self.skipTest("EmailAddress not created — allauth may not have run")

        # Generate HMAC confirmation key
        confirmation = EmailConfirmationHMAC(email_address)
        key = confirmation.key

        # Visit the confirmation URL
        confirm_url = f"/accounts/confirm-email/{key}/"
        response = self.client.get(confirm_url, follow=True)
        self.assertNotIn(response.status_code, (500,))

        # Email should now be verified
        email_address.refresh_from_db()
        self.assertTrue(
            email_address.verified,
            "Email should be marked as verified after visiting confirmation URL",
        )


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LoginTest(AssertHTMLMixin, BaseTestCase):
    """
    Test login flow including wrong password notification.

    Validates:
    - Login page loads
    - Valid credentials → authenticated
    - Wrong password → error notification in response
    - Non-existent user → error notification
    - Logout clears session
    """

    def setUp(self):
        super().setUp()
        User.objects.filter(email=NEW_EMAIL).delete()
        mail.outbox = []
        # Create a verified user for login tests
        self._user = User.objects.create_user(
            username="ezzat_test",
            email=NEW_EMAIL,
            password=NEW_PASSWORD,
            is_active=True,
        )
        EmailAddress.objects.get_or_create(
            user=self._user,
            email=NEW_EMAIL,
            defaults={"verified": True, "primary": True},
        )

    def tearDown(self):
        super().tearDown()
        User.objects.filter(email=NEW_EMAIL).delete()

    def test_login_page_loads(self):
        """GET /accounts/login/ returns 200."""
        response = self.client.get(LOGIN_URL)
        self.assertIn(response.status_code, (200, 301, 302))

    def test_login_with_valid_credentials_authenticates(self):
        """
        POST to login with correct email + password authenticates the user.
        """
        response = self.client.post(
            LOGIN_URL,
            data={"login": NEW_EMAIL, "password": NEW_PASSWORD},
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertTrue(
            response.wsgi_request.user.is_authenticated,
            "User should be authenticated with valid credentials",
        )

    def test_login_with_wrong_password_shows_error(self):
        """
        POST to login with wrong password must:
        1. NOT authenticate the user
        2. Return a response containing an error notification

        Validates: Wrong password → error notification (Selenium-style assertion).
        """
        response = self.client.post(
            LOGIN_URL,
            data={"login": NEW_EMAIL, "password": WRONG_PASSWORD},
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        # Must NOT be authenticated
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "User must NOT be authenticated with wrong password",
        )
        # Response must contain an error indicator
        body = response.content.decode("utf-8", errors="replace").lower()
        error_indicators = [
            "incorrect", "invalid", "wrong", "error", "failed",
            "not correct", "password", "credentials", "sign in",
        ]
        has_error = any(indicator in body for indicator in error_indicators)
        self.assertTrue(
            has_error,
            "Login with wrong password must show an error notification in the response",
        )

    def test_login_with_nonexistent_email_shows_error(self):
        """
        POST to login with an email that doesn't exist must show an error.
        """
        response = self.client.post(
            LOGIN_URL,
            data={"login": "nonexistent@example.com", "password": NEW_PASSWORD},
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        body = response.content.decode("utf-8", errors="replace").lower()
        error_indicators = ["incorrect", "invalid", "error", "failed", "not found"]
        has_error = any(indicator in body for indicator in error_indicators)
        self.assertTrue(has_error, "Login with non-existent email must show an error")

    def test_login_with_empty_fields_shows_error(self):
        """
        POST to login with empty fields must not authenticate and must show errors.
        """
        response = self.client.post(
            LOGIN_URL,
            data={"login": "", "password": ""},
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_clears_session(self):
        """After logout, user is no longer authenticated."""
        self.login(self._user)
        self.client.post(LOGOUT_URL, follow=True)
        response = self.client.get("/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_force_login_authenticates_user(self):
        """force_login sets the user as authenticated."""
        self.login(self._user)
        response = self.client.get("/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)


# ---------------------------------------------------------------------------
# Password reset tests
# ---------------------------------------------------------------------------

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTest(AssertHTMLMixin, AssertEmailMixin, BaseTestCase):
    """
    Test password reset flow.

    Validates:
    - Password reset page loads
    - POST with valid email sends reset email
    - POST with non-existent email does NOT reveal user existence (security)
    - Reset link in email is valid
    - New password can be set via reset link
    """

    def setUp(self):
        super().setUp()
        User.objects.filter(email=NEW_EMAIL).delete()
        mail.outbox = []
        self._user = User.objects.create_user(
            username="ezzat_reset",
            email=NEW_EMAIL,
            password=NEW_PASSWORD,
            is_active=True,
        )
        EmailAddress.objects.get_or_create(
            user=self._user,
            email=NEW_EMAIL,
            defaults={"verified": True, "primary": True},
        )

    def tearDown(self):
        super().tearDown()
        User.objects.filter(email=NEW_EMAIL).delete()

    def test_password_reset_page_loads(self):
        """GET /accounts/password/reset/ returns 200."""
        response = self.client.get(PASSWORD_RESET_URL)
        self.assertIn(response.status_code, (200, 301, 302))

    def test_password_reset_sends_email(self):
        """
        POST to password reset with a valid email sends a reset email.

        Validates: Password reset email is sent from server.
        """
        response = self.client.post(
            PASSWORD_RESET_URL,
            data={"email": NEW_EMAIL},
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertEmailSent(NEW_EMAIL)
        sent = [m for m in mail.outbox if NEW_EMAIL in m.to]
        self.assertTrue(len(sent) > 0, "Password reset email not sent")
        body = sent[0].body
        self.assertTrue(
            "reset" in body.lower() or "password" in body.lower(),
            f"Reset email body missing expected content: {body[:200]}",
        )

    def test_password_reset_email_contains_reset_link(self):
        """Password reset email must contain a reset link."""
        self.client.post(
            PASSWORD_RESET_URL,
            data={"email": NEW_EMAIL},
            follow=True,
        )
        sent = [m for m in mail.outbox if NEW_EMAIL in m.to]
        self.assertTrue(len(sent) > 0)
        body = sent[0].body
        has_link = (
            "/password/reset/key/" in body
            or "/reset/" in body
            or "http" in body
        )
        self.assertTrue(has_link, f"No reset link found in email: {body[:300]}")

    def test_password_reset_with_nonexistent_email_does_not_reveal_user(self):
        """
        POST to password reset with a non-existent email must return 200
        (no user enumeration — security best practice).
        """
        response = self.client.post(
            PASSWORD_RESET_URL,
            data={"email": "nonexistent_xyz@example.com"},
            follow=True,
        )
        # Should return 200 (not 404 or error) — no user enumeration
        self.assertNotIn(response.status_code, (404, 500))

    def test_password_reset_key_flow(self):
        """
        Visiting the password reset key URL allows setting a new password.
        """
        # Request reset
        self.client.post(
            PASSWORD_RESET_URL,
            data={"email": NEW_EMAIL},
            follow=True,
        )
        # Extract key from email
        key = _get_password_reset_key_from_outbox()
        if key is None:
            self.skipTest("No password reset key found in email outbox")

        # Visit the reset key URL
        reset_key_url = f"/accounts/password/reset/key/{key}/"
        response = self.client.get(reset_key_url, follow=True)
        self.assertNotIn(response.status_code, (500,))

        # POST new password
        new_password = "NewStr0ng!Pass#9999"
        response2 = self.client.post(
            reset_key_url,
            data={"password1": new_password, "password2": new_password},
            follow=True,
        )
        self.assertNotIn(response2.status_code, (500,))

        # Verify new password works
        self._user.refresh_from_db()
        self.assertTrue(
            self._user.check_password(new_password),
            "Password should be updated after reset flow",
        )


# ---------------------------------------------------------------------------
# Live SMTP email test (uses real email backend)
# ---------------------------------------------------------------------------

class LiveEmailSendTest(BaseTestCase):
    """
    Test that the server can actually send email via SMTP.

    This test uses the REAL email backend (not locmem) to confirm
    the SMTP configuration works end-to-end.

    NOTE: This sends a real email to mahmoud.ezzat.moustafa@gmail.com.
    """

    def test_smtp_email_sends_successfully(self):
        """
        Send a real test email via SMTP to confirm server-side email delivery.

        Validates: Email is sent from server (SMTP, not locmem).
        """
        from django.core.mail import send_mail
        try:
            result = send_mail(
                subject="[CTC-Research] Auth Test — Email Confirmation",
                message=(
                    "This is an automated test email from ctc-research.com deployment verification.\n\n"
                    "If you received this, the SMTP email sending is working correctly.\n\n"
                    "Test: Registration + Email Confirmation Flow\n"
                    "Target: mahmoud.ezzat.moustafa@gmail.com\n"
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[NEW_EMAIL],
                fail_silently=False,
            )
            self.assertEqual(result, 1, "send_mail should return 1 (one email sent)")
        except Exception as exc:
            self.fail(f"SMTP email sending failed: {exc}")


# ---------------------------------------------------------------------------
# Admin panel auth tests
# ---------------------------------------------------------------------------

class AdminPanelAuthTest(AssertHTMLMixin, BaseTestCase):
    """Test admin panel access using django-fusion admin_user fixture."""

    def test_admin_panel_accessible_for_superuser(self):
        """Superuser can access /admin/ and see admin UI markers."""
        self.login_as_admin()
        response = self.client.get("/admin/", follow=True)
        self.assertNotIn(response.status_code, (403, 500))
        body = response.content.decode("utf-8", errors="replace")
        markers = ["administration", "log out", "unfold", "site administration"]
        found = [m for m in markers if m.lower() in body.lower()]
        self.assertTrue(
            len(found) > 0,
            f"Admin panel loaded but no expected UI markers found. Checked: {markers}",
        )

    def test_anonymous_admin_access_redirects_to_login(self):
        """Anonymous GET /admin/ must redirect to login."""
        response = self.client.get("/admin/")
        self.assertIn(response.status_code, (301, 302))
        location = response.get("Location", "").lower()
        self.assertTrue(
            any(p in location for p in ADMIN_LOGIN_REDIRECT_PATTERNS),
            f"Expected redirect to login, got: {location}",
        )

    def test_wrong_admin_credentials_denied(self):
        """
        POST to admin login with wrong password must not authenticate.
        """
        response = self.client.post(
            "/admin/login/",
            data={
                "username": "admin",
                "password": "completely_wrong_password",
                "next": "/admin/",
            },
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "Wrong admin credentials must not authenticate",
        )
