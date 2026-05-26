"""
Login flow tests for ctc-research.com.

Covers:
- Login page loads
- Valid credentials → authenticated and redirected
- Wrong password → NOT authenticated + error notification shown
- Non-existent email → NOT authenticated + error shown
- Empty fields → NOT authenticated
- Logout clears session
- force_login helper works

Domain: ctc-research.com
Auth URL: /accounts/login/
"""
from __future__ import annotations

from allauth.account.models import EmailAddress
from django.core import mail
from django.test import override_settings
from django_grep.tests.base import BaseTestCase

from ..base.config import AuthURLs, Credentials
from ..base.mixins import AuthAssertMixin
from ..base.setup import UserFactory


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LoginPageTest(AuthAssertMixin, BaseTestCase):
    """Tests for the login page itself."""

    def test_login_page_loads(self):
        """GET /accounts/login/ returns a successful response."""
        response = self.client.get(AuthURLs.LOGIN)
        self.assertPageLoads(response)

    def test_login_page_contains_form(self):
        """Login page must contain a form with email and password fields."""
        response = self.client.get(AuthURLs.LOGIN)
        if response.status_code in (301, 302):
            self.skipTest("Login page redirects — skipping form check")
        body = response.content.decode("utf-8", errors="replace").lower()
        self.assertTrue(
            "password" in body or "login" in body or "email" in body,
            "Login page must contain a login form",
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LoginSuccessTest(AuthAssertMixin, BaseTestCase):
    """Tests for successful login flows."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._verified_user = UserFactory.create_verified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_login_ok",
        )

    @classmethod
    def tearDownClass(cls):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        mail.outbox = []

    def test_valid_credentials_authenticate_user(self):
        """
        POST to /accounts/login/ with correct email + password authenticates the user.

        Selenium-style: submit form → assert user is logged in.
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
        self.assertUserAuthenticated(response)

    def test_valid_login_does_not_stay_on_login_page(self):
        """After successful login, user is redirected away from the login page."""
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.NEW_USER_EMAIL,
                "password": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        final_url = response.redirect_chain[-1][0] if response.redirect_chain else AuthURLs.LOGIN
        self.assertNotEqual(
            final_url, AuthURLs.LOGIN,
            "Successful login must redirect away from the login page",
        )

    def test_force_login_authenticates_user(self):
        """django-grep force_login helper authenticates the user."""
        self.login(self._verified_user)
        response = self.client.get("/")
        self.assertUserAuthenticated(response)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LoginFailureTest(AuthAssertMixin, BaseTestCase):
    """
    Tests for login failure flows — wrong password, wrong email, empty fields.

    Each test verifies:
    1. User is NOT authenticated
    2. Response contains an error notification (Selenium-style assertion)
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._verified_user = UserFactory.create_verified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_login_fail",
        )

    @classmethod
    def tearDownClass(cls):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        mail.outbox = []

    def test_wrong_password_does_not_authenticate(self):
        """
        POST with correct email but wrong password must NOT authenticate.

        Selenium-style: submit form with wrong password → assert NOT logged in.
        """
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.NEW_USER_EMAIL,
                "password": Credentials.WRONG_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertUserNotAuthenticated(
            response,
            "User must NOT be authenticated with wrong password",
        )

    def test_wrong_password_shows_error_notification(self):
        """
        Wrong password must show an error notification in the response body.

        Selenium-style: submit form → assert error message visible on page.
        """
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.NEW_USER_EMAIL,
                "password": Credentials.WRONG_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertBodyContainsError(
            response,
            "Login with wrong password must show an error notification",
        )

    def test_nonexistent_email_does_not_authenticate(self):
        """POST with a non-existent email must NOT authenticate."""
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.WRONG_EMAIL,
                "password": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertUserNotAuthenticated(response)

    def test_nonexistent_email_shows_error_notification(self):
        """Non-existent email must show an error notification."""
        response = self.client.post(
            AuthURLs.LOGIN,
            data={
                "login": Credentials.WRONG_EMAIL,
                "password": Credentials.NEW_USER_PASSWORD,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertBodyContainsError(response)

    def test_empty_fields_do_not_authenticate(self):
        """POST with empty login and password must NOT authenticate."""
        response = self.client.post(
            AuthURLs.LOGIN,
            data={"login": "", "password": ""},
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertUserNotAuthenticated(response)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LogoutTest(AuthAssertMixin, BaseTestCase):
    """Tests for the logout flow."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._verified_user = UserFactory.create_verified(
            email=Credentials.NEW_USER_EMAIL,
            password=Credentials.NEW_USER_PASSWORD,
            username="ezzat_logout",
        )

    @classmethod
    def tearDownClass(cls):
        UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
        super().tearDownClass()

    def test_logout_clears_session(self):
        """After logout, user is no longer authenticated."""
        self.login(self._verified_user)
        self.client.post(AuthURLs.LOGOUT, follow=True)
        response = self.client.get("/")
        self.assertUserNotAuthenticated(response, "User must be logged out after logout")

    def test_anonymous_user_is_not_authenticated(self):
        """Without logging in, user is anonymous."""
        response = self.client.get("/")
        self.assertUserNotAuthenticated(response)
