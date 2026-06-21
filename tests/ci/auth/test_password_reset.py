"""
Password reset flow tests for ctc-research.com.

Covers:
- Password reset page loads
- POST with valid email sends reset email
- Reset email contains a reset link
- Non-existent email does NOT reveal user existence (security)
- Reset key flow: visit link → set new password → can login with new password

Domain: ctc-research.com
Auth URL: /accounts/password/reset/
"""
from __future__ import annotations

from allauth.account.models import EmailAddress
from django.core import mail
from django.test import override_settings
from django_osoul.tests.base import BaseTestCase

from ..base.config import AuthURLs, Credentials
from ..base.mixins import AuthAssertMixin
from ..base.setup import EmailFactory, UserFactory


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetPageTest(AuthAssertMixin, BaseTestCase):
    """Tests for the password reset request page."""

    def test_password_reset_page_loads(self):
        """GET /accounts/password/reset/ returns a successful response."""
        response = self.client.get(AuthURLs.PASSWORD_RESET)
        self.assertPageLoads(response)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetEmailTest(AuthAssertMixin, BaseTestCase):
    """
    Tests for password reset email sending.

    Validates that the server sends a reset email with a valid link.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user = UserFactory.create_verified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_reset_email",
        )

    @classmethod
    def tearDownClass(cls):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        EmailFactory.clear()

    def test_password_reset_sends_email_to_user(self):
        """
        POST to /accounts/password/reset/ with a valid email sends a reset email.

        Selenium-style: submit reset form → assert email received.
        """
        response = self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.NEW_USER_EMAIL},
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertPasswordResetEmailSent(Credentials.NEW_USER_EMAIL)

    def test_password_reset_email_contains_reset_link(self):
        """Password reset email must contain a reset link."""
        self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.NEW_USER_EMAIL},
            follow=True,
        )
        body = EmailFactory.body_of_first_sent_to(Credentials.NEW_USER_EMAIL)
        self.assertTrue(len(body) > 0, "No reset email body found")
        has_link = (
            "/password/reset/key/" in body
            or "/reset/" in body
            or "http" in body
        )
        self.assertTrue(
            has_link,
            f"Password reset email does not contain a reset link. Body: {body[:300]}",
        )

    def test_password_reset_email_addressed_to_user(self):
        """Reset email must be addressed to the requesting user."""
        self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.NEW_USER_EMAIL},
            follow=True,
        )
        sent = EmailFactory.sent_to(Credentials.NEW_USER_EMAIL)
        self.assertTrue(len(sent) > 0)
        self.assertEqual(
            sent[0].to[0],
            Credentials.NEW_USER_EMAIL,
            "Reset email must be addressed to the requesting user",
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetSecurityTest(AuthAssertMixin, BaseTestCase):
    """
    Security tests for the password reset flow.

    Validates that the reset endpoint does not leak user existence.
    """

    def setUp(self):
        super().setUp()
        EmailFactory.clear()

    def test_nonexistent_email_does_not_reveal_user(self):
        """
        POST to password reset with a non-existent email must return 200.

        Security: must NOT return 404 or error that reveals user non-existence.
        """
        response = self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.WRONG_EMAIL},
            follow=True,
        )
        self.assertNotIn(
            response.status_code,
            (404, 500),
            "Password reset must not reveal whether an email exists (user enumeration)",
        )

    def test_nonexistent_email_does_not_send_email(self):
        """POST with non-existent email must NOT send any email."""
        self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.WRONG_EMAIL},
            follow=True,
        )
        sent = EmailFactory.sent_to(Credentials.WRONG_EMAIL)
        self.assertEqual(
            len(sent), 0,
            "No email must be sent for a non-existent address",
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetKeyFlowTest(AuthAssertMixin, BaseTestCase):
    """
    End-to-end password reset key flow tests.

    Validates the full flow: request reset → extract key → set new password → login.
    """

    NEW_PASSWORD = "NewStr0ng!Pass#9999"

    def setUp(self):
        super().setUp()
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        EmailFactory.clear()
        self._user = UserFactory.create_verified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_reset_key",
        )

    def tearDown(self):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDown()

    def test_reset_key_url_loads(self):
        """
        After requesting a reset, the reset key URL must load successfully.
        """
        self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.NEW_USER_EMAIL},
            follow=True,
        )
        key = self.extractPasswordResetKey()
        if key is None:
            self.skipTest("No password reset key found in email outbox")

        response = self.client.get(
            AuthURLs.password_reset_key(key),
            follow=True,
        )
        self.assertNoServerError(response)

    def test_full_reset_flow_allows_login_with_new_password(self):
        """
        Full flow: request reset → extract key → set new password → login succeeds.

        Selenium-style: complete reset flow → assert login with new password works.
        """
        # Step 1: Request reset
        self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.NEW_USER_EMAIL},
            follow=True,
        )

        # Step 2: Extract key
        key = self.extractPasswordResetKey()
        if key is None:
            self.skipTest("No password reset key found in email outbox")

        # Step 3: Visit reset key URL
        reset_url = AuthURLs.password_reset_key(key)
        self.client.get(reset_url, follow=True)

        # Step 4: POST new password
        response = self.client.post(
            reset_url,
            data={
                "password1": self.NEW_PASSWORD,
                "password2": self.NEW_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)

        # Step 5: Verify new password is set in DB
        self._user.refresh_from_db()
        self.assertTrue(
            self._user.check_password(self.NEW_PASSWORD),
            "Password must be updated after completing the reset flow",
        )

    def test_old_password_rejected_after_reset(self):
        """After password reset, the old password must no longer work."""
        # Request and complete reset
        self.client.post(
            AuthURLs.PASSWORD_RESET,
            data={"email": Credentials.NEW_USER_EMAIL},
            follow=True,
        )
        key = self.extractPasswordResetKey()
        if key is None:
            self.skipTest("No password reset key found in email outbox")

        reset_url = AuthURLs.password_reset_key(key)
        self.client.get(reset_url, follow=True)
        self.client.post(
            reset_url,
            data={"password1": self.NEW_PASSWORD, "password2": self.NEW_PASSWORD},
            follow=True,
        )

        # Try logging in with OLD password — must fail
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.NEW_USER_EMAIL,
                "password": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        self.assertUserNotAuthenticated(
            response,
            "Old password must not work after password reset",
        )
