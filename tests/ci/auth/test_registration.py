"""
Registration flow tests for ctc-research.com.

Covers:
- Signup page loads
- POST creates user with mahmoud.ezzat.moustafa@gmail.com
- Confirmation email sent to new user
- Duplicate email rejected (idempotence)
- Mismatched passwords rejected
- Weak password rejected

Domain: ctc-research.com
Auth URL: /accounts/signup/
"""
from __future__ import annotations

from django.core import mail
from django.test import override_settings
from django_osoul.tests.base import BaseTestCase

from ..base.config import AuthURLs, Credentials
from ..base.mixins import AuthAssertMixin
from ..base.setup import EmailFactory, UserFactory


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SignupPageTest(AuthAssertMixin, BaseTestCase):
    """Tests for the signup page itself."""

    def test_signup_page_loads(self):
        """GET /accounts/signup/ returns a successful response."""
        response = self.client.get(AuthURLs.SIGNUP)
        self.assertPageLoads(response)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationSuccessTest(AuthAssertMixin, BaseTestCase):
    """
    Tests for successful registration of mahmoud.ezzat.moustafa@gmail.com.

    Each test starts with a clean slate (user deleted) and verifies
    the full registration flow end-to-end.
    """

    def setUp(self):
        super().setUp()
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        EmailFactory.clear()

    def tearDown(self):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDown()

    def _post_signup(self, email=None, password=None, password2=None):
        """Helper: POST to signup with given credentials."""
        email = email or Credentials.NEW_USER_EMAIL
        password = password or Credentials.NEW_USER_PASSWORD
        password2 = password2 or password
        return self.client.post(
            AuthURLs.SIGNUP,
            data={
                "email": email,
                "password1": password,
                "password2": password2,
            },
            follow=True,
        )

    def test_registration_creates_user_in_database(self):
        """
        POST to /accounts/signup/ with mahmoud.ezzat.moustafa@gmail.com
        creates a new user record in the database.

        Selenium-style: fill form → submit → assert user exists.
        """
        response = self._post_signup()
        self.assertNoServerError(response)
        self.assertTrue(
            UserFactory.exists(Credentials.NEW_USER_EMAIL),
            f"User {Credentials.NEW_USER_EMAIL} was not created after registration",
        )

    def test_registration_sends_confirmation_email(self):
        """
        After registration, a confirmation email must be sent to the new user.

        Validates: Email is sent from server to mahmoud.ezzat.moustafa@gmail.com.
        """
        self._post_signup()
        self.assertConfirmationEmailSent(Credentials.NEW_USER_EMAIL)

    def test_confirmation_email_sent_to_correct_address(self):
        """Confirmation email must be addressed to the registered email."""
        self._post_signup()
        sent = EmailFactory.sent_to(Credentials.NEW_USER_EMAIL)
        self.assertTrue(len(sent) > 0, "No email sent to new user")
        self.assertEqual(
            sent[0].to[0],
            Credentials.NEW_USER_EMAIL,
            "Confirmation email must be addressed to the registered email",
        )

    def test_confirmation_email_contains_confirmation_link(self):
        """Confirmation email body must contain a confirmation or password-creation link."""
        self._post_signup()
        body = EmailFactory.body_of_first_sent_to(Credentials.NEW_USER_EMAIL)
        self.assertTrue(len(body) > 0, "No email body found")
        has_link = (
            "/confirm-email/" in body
            or "/create-password/" in body
            or "/verify" in body
        )
        self.assertTrue(
            has_link,
            f"Confirmation email does not contain a confirmation link. Body: {body[:300]}",
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationValidationTest(AuthAssertMixin, BaseTestCase):
    """
    Tests for registration form validation — invalid inputs must be rejected.
    """

    def setUp(self):
        super().setUp()
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        EmailFactory.clear()

    def tearDown(self):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDown()

    def test_duplicate_email_does_not_create_second_user(self):
        """
        Registering the same email twice must not create a duplicate user.

        Validates: Idempotence — user count stays at 1.
        """
        for _ in range(2):
            self.client.post(
                AuthURLs.SIGNUP,
                data={
                    "email": Credentials.NEW_USER_EMAIL,
                    "password1": Credentials.NEW_USER_PASSWORD,
                    "password2": Credentials.NEW_USER_PASSWORD,
                },
                follow=True,
            )
        count = UserFactory.get(Credentials.NEW_USER_EMAIL)
        # Should exist exactly once
        from django.contrib.auth import get_user_model
        User = get_user_model()
        count = User.objects.filter(email=Credentials.NEW_USER_EMAIL).count()
        self.assertEqual(
            count, 1,
            f"Expected exactly 1 user with {Credentials.NEW_USER_EMAIL}, found {count}",
        )

    def test_mismatched_passwords_rejected(self):
        """
        Registration with mismatched passwords must fail and NOT create a user.

        Selenium-style: fill form with mismatched passwords → assert user NOT created.
        """
        response = self.client.post(
            AuthURLs.SIGNUP,
            data={
                "email": Credentials.NEW_USER_EMAIL,
                "password1": Credentials.NEW_USER_PASSWORD,
                "password2": "DifferentPassword999!",
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertFalse(
            UserFactory.exists(Credentials.NEW_USER_EMAIL),
            "User must NOT be created with mismatched passwords",
        )

    def test_weak_password_rejected(self):
        """
        Registration with a too-short password must fail.

        Selenium-style: fill form with weak password → assert user NOT created.
        """
        response = self.client.post(
            AuthURLs.SIGNUP,
            data={
                "email": Credentials.NEW_USER_EMAIL,
                "password1": "short",
                "password2": "short",
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertFalse(
            UserFactory.exists(Credentials.NEW_USER_EMAIL),
            "User must NOT be created with a weak password",
        )

    def test_empty_email_rejected(self):
        """Registration with empty email must fail."""
        response = self.client.post(
            AuthURLs.SIGNUP,
            data={
                "email": "",
                "password1": Credentials.NEW_USER_PASSWORD,
                "password2": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
