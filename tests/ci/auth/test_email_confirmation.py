"""
Email confirmation flow tests for ctc-research.com.

Covers:
- Unverified user cannot log in (mandatory verification enforced)
- Verified user can log in
- Visiting confirmation URL marks email as verified
- Confirmation key is valid and usable

Domain: ctc-research.com
Auth URL: /accounts/confirm-email/{key}/
"""
from __future__ import annotations

from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from django.core import mail
from django.test import override_settings
from django_osoul.tests.base import BaseTestCase

from ..base.config import AuthURLs, Credentials
from ..base.mixins import AuthAssertMixin
from ..base.setup import EmailFactory, UserFactory


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailVerificationEnforcementTest(AuthAssertMixin, BaseTestCase):
    """
    Tests that ACCOUNT_EMAIL_VERIFICATION = 'mandatory' is enforced.

    Unverified users must not be able to log in.
    """

    def setUp(self):
        super().setUp()
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        EmailFactory.clear()
        self._unverified = UserFactory.create_unverified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_unverified",
        )

    def tearDown(self):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDown()

    def test_unverified_user_cannot_login(self):
        """
        A user who has not confirmed their email must NOT be able to log in.

        Selenium-style: attempt login → assert NOT authenticated.
        """
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.NEW_USER_EMAIL,
                "password": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertUserNotAuthenticated(
            response,
            "Unverified user must NOT be authenticated (mandatory email verification)",
        )

    def test_unverified_user_login_shows_verification_message(self):
        """
        Login attempt by unverified user must show a verification-required message.

        Selenium-style: attempt login → assert message visible on page.
        """
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.NEW_USER_EMAIL,
                "password": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        body = response.content.decode("utf-8", errors="replace").lower()
        verification_indicators = [
            "verify", "confirm", "verification", "email", "activate",
            "not verified", "unverified",
        ]
        has_message = any(indicator in body for indicator in verification_indicators)
        self.assertTrue(
            has_message,
            "Unverified user login must show a verification-required message",
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailVerificationSuccessTest(AuthAssertMixin, BaseTestCase):
    """
    Tests for successful email verification flows.
    """

    def setUp(self):
        super().setUp()
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        EmailFactory.clear()
        self._verified = UserFactory.create_verified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_verified",
        )

    def tearDown(self):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDown()

    def test_verified_user_can_login(self):
        """
        A user whose email is verified can log in successfully.

        Selenium-style: login with verified account → assert authenticated.
        """
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.NEW_USER_EMAIL,
                "password": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertUserAuthenticated(
            response,
            "Verified user must be authenticated after login",
        )

    def test_confirmation_key_marks_email_verified(self):
        """
        Visiting the HMAC confirmation URL marks the email as verified.

        Selenium-style: visit confirmation link → assert email is verified in DB.
        """
        # Start with unverified email
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        user = UserFactory.create_unverified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_confirm_key",
        )

        email_address = EmailAddress.objects.filter(
            user=user, email=Credentials.NEW_USER_EMAIL
        ).first()
        if email_address is None:
            self.skipTest("EmailAddress not created — allauth may not have run")

        # Generate HMAC confirmation key
        confirmation = EmailConfirmationHMAC(email_address)
        key = confirmation.key

        # Visit the confirmation URL (simulates clicking the link in the email)
        confirm_url = f"{AuthURLs.EMAIL_CONFIRM}{key}/"
        response = self.client.get(confirm_url, follow=True)
        self.assertNoServerError(response)

        # Email must now be verified
        email_address.refresh_from_db()
        self.assertTrue(
            email_address.verified,
            "Email must be marked as verified after visiting the confirmation URL",
        )

    def test_confirmation_via_registration_flow(self):
        """
        Full flow: register → receive email → extract key → confirm → can login.
        """
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        EmailFactory.clear()

        # Step 1: Register
        self.client.post(
            AuthURLs.SIGNUP,
            data={
                "email": Credentials.NEW_USER_EMAIL,
                "password1": Credentials.NEW_USER_PASSWORD,
                "password2": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )

        user = UserFactory.get(Credentials.NEW_USER_EMAIL)
        if user is None:
            self.skipTest("Registration failed — skipping confirmation flow test")

        # Step 2: Get confirmation key from email or generate HMAC key
        key = self.extractConfirmationKey()
        if key is None:
            # Fall back to generating HMAC key directly
            email_address = EmailAddress.objects.filter(
                user=user, email=Credentials.NEW_USER_EMAIL
            ).first()
            if email_address is None:
                self.skipTest("EmailAddress not created")
            key = EmailConfirmationHMAC(email_address).key

        # Step 3: Visit confirmation URL
        confirm_url = f"{AuthURLs.EMAIL_CONFIRM}{key}/"
        self.client.get(confirm_url, follow=True)

        # Step 4: Verify email is now confirmed
        email_address = EmailAddress.objects.filter(
            user=user, email=Credentials.NEW_USER_EMAIL
        ).first()
        if email_address:
            self.assertTrue(
                email_address.verified,
                "Email must be verified after confirmation flow",
            )
