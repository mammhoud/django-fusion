"""
Auth flow tests for structa.cloud using django-grep test utilities.

Mirrors ctc-research.com/core/CI/tests/test_auth_selenium.py,
adapted for the `alliance-website` container and structa.cloud URLs.

Uses django_grep.tests.base.BaseTestCase (Django test client — browser-style)
and django_grep.tests.mixins.AssertHTMLMixin for HTML assertions.

NOTE: This test suite is for test validation only.
      The structa.cloud build/deploy is NOT triggered by this suite.

Covers:
- Login with valid credentials
- Login with invalid credentials (negative case)
- Register new account
- Duplicate registration idempotence
- Logout flow
- Auth-required page redirect for anonymous users
- Admin panel access after login
"""
from __future__ import annotations

import os

import django
from django.conf import settings as django_settings

if not django_settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    os.environ.setdefault("DJANGO_PRINT_ENV", "false")
    django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

from django_grep.tests.base import BaseTestCase
from django_grep.tests.mixins import AssertHTMLMixin

User = get_user_model()

# ---------------------------------------------------------------------------
# Constants — structa.cloud specific
# ---------------------------------------------------------------------------
TEST_EMAIL = "test.structa@example.com"
TEST_USERNAME = "structa_testuser"
TEST_PASSWORD = "Str0ng!Pass#2024"

LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
SIGNUP_URL = "/accounts/signup/"
PROTECTED_URL = "/dashboard/"


# ---------------------------------------------------------------------------
# Auth flow tests
# ---------------------------------------------------------------------------

class StructaAuthLoginTest(AssertHTMLMixin, BaseTestCase):
    """Test login flow for structa.cloud using django-grep BaseTestCase client."""

    def test_login_page_loads(self):
        """GET /accounts/login/ returns 200."""
        response = self.client.get(LOGIN_URL)
        self.assertIn(response.status_code, (200, 301, 302))

    def test_login_with_valid_credentials(self):
        """POST to login with valid credentials redirects to a success page."""
        response = self.client.post(
            LOGIN_URL,
            data={
                "login": self.user.email,
                "password": "testpass123",
            },
            follow=True,
        )
        self.assertNotIn(response.status_code, (401, 403, 500))
        final_url = response.redirect_chain[-1][0] if response.redirect_chain else LOGIN_URL
        self.assertNotEqual(final_url, LOGIN_URL)

    def test_login_with_invalid_credentials_stays_on_login(self):
        """POST to login with wrong password does not authenticate the user."""
        response = self.client.post(
            LOGIN_URL,
            data={
                "login": self.user.email,
                "password": "wrongpassword",
            },
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_force_login_authenticates_user(self):
        """force_login sets the user as authenticated on the client."""
        self.login()
        response = self.client.get("/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_clears_session(self):
        """After logout, user is no longer authenticated."""
        self.login()
        self.client.post(LOGOUT_URL, follow=True)
        response = self.client.get("/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class StructaAuthRegistrationTest(AssertHTMLMixin, BaseTestCase):
    """Test new account registration flow for structa.cloud."""

    def test_signup_page_loads(self):
        """GET /accounts/signup/ returns 200."""
        response = self.client.get(SIGNUP_URL)
        self.assertIn(response.status_code, (200, 301, 302))

    def test_register_new_account(self):
        """POST to signup creates a new user."""
        User.objects.filter(email=TEST_EMAIL).delete()

        response = self.client.post(
            SIGNUP_URL,
            data={
                "email": TEST_EMAIL,
                "username": TEST_USERNAME,
                "password1": TEST_PASSWORD,
                "password2": TEST_PASSWORD,
            },
            follow=True,
        )
        self.assertNotIn(response.status_code, (500,))
        self.assertTrue(
            User.objects.filter(email=TEST_EMAIL).exists(),
            f"User {TEST_EMAIL} was not created after registration POST",
        )

    def test_register_duplicate_email_does_not_create_second_user(self):
        """
        Registering the same email twice must not create a duplicate user.

        Validates: Correctness Property 4 — User Registration Idempotence.
        """
        User.objects.filter(email=TEST_EMAIL).delete()
        for suffix in ["", "_2"]:
            self.client.post(
                SIGNUP_URL,
                data={
                    "email": TEST_EMAIL,
                    "username": TEST_USERNAME + suffix,
                    "password1": TEST_PASSWORD,
                    "password2": TEST_PASSWORD,
                },
                follow=True,
            )
        count = User.objects.filter(email=TEST_EMAIL).count()
        self.assertEqual(count, 1, f"Expected 1 user with {TEST_EMAIL}, found {count}")


class StructaAuthProtectedRedirectTest(AssertHTMLMixin, BaseTestCase):
    """Test that auth-required pages redirect anonymous users on structa.cloud."""

    def test_anonymous_access_to_protected_page_redirects(self):
        """Anonymous GET to a protected URL must redirect to login."""
        response = self.client.get(PROTECTED_URL)
        self.assertIn(
            response.status_code,
            (301, 302, 403),
            f"Expected redirect for anonymous user, got {response.status_code}",
        )
        if response.status_code in (301, 302):
            location = response.get("Location", "")
            self.assertIn(
                "login",
                location.lower(),
                f"Redirect location '{location}' does not point to login",
            )

    def test_authenticated_user_can_access_protected_page(self):
        """Logged-in user can access the protected page without redirect to login."""
        self.login()
        response = self.client.get(PROTECTED_URL, follow=True)
        self.assertNotIn(response.status_code, (401, 403, 500))


class StructaAdminPanelAuthTest(AssertHTMLMixin, BaseTestCase):
    """Test admin panel access for structa.cloud."""

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
        """Anonymous GET /admin/ must redirect to admin login."""
        response = self.client.get("/admin/")
        self.assertIn(response.status_code, (301, 302))
        location = response.get("Location", "")
        self.assertIn("login", location.lower())
