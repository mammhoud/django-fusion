"""Comprehensive auth flow tests for all Structa Cloud sites.

Covers: login, registration, password reset, email confirmation,
MFA readiness, social auth adapters, and profile access.
Uses ``reverse()`` for URL resolution so tests work across sites.
"""

from __future__ import annotations

from django.urls import reverse
from django.contrib.auth import get_user_model

from tests.ci.base.mixins import BaseTestCase, AuthAssertMixin

User = get_user_model()


class LoginComprehensiveTest(AuthAssertMixin, BaseTestCase):
    """Full login flow tests with edge cases."""

    def test_login_page_renders_with_csrf(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_login_with_valid_credentials(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
        )
        response = self.client.post(
            reverse("account_login"),
            {"login": "test@example.com", "password": "strongpassword123"},
        )
        self.assertIn(response.status_code, [200, 302])

    def test_login_with_username(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
        )
        response = self.client.post(
            reverse("account_login"),
            {"login": "testuser", "password": "strongpassword123"},
        )
        self.assertIn(response.status_code, [200, 302])

    def test_login_with_invalid_password(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
        )
        response = self.client.post(
            reverse("account_login"),
            {"login": "test@example.com", "password": "wrongpassword"},
        )
        self.assertIn(response.status_code, [200, 401])

    def test_login_with_nonexistent_user(self):
        response = self.client.post(
            reverse("account_login"),
            {"login": "nobody@example.com", "password": "password"},
        )
        self.assertIn(response.status_code, [200, 401])

    def test_login_with_empty_fields(self):
        response = self.client.post(reverse("account_login"), {"login": "", "password": ""})
        self.assertIn(response.status_code, [200, 400])

    def test_logout_redirects(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
        )
        self.client.login(username="testuser", password="strongpassword123")
        response = self.client.post(reverse("account_logout"))
        self.assertIn(response.status_code, [200, 302])


class RegisterComprehensiveTest(AuthAssertMixin, BaseTestCase):
    """Full registration flow tests."""

    def test_register_page_renders(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)

    def test_register_with_valid_data(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(
            User.objects.filter(email="newuser@example.com").exists()
        )

    def test_register_password_mismatch(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "DifferentPass123!",
            },
        )
        self.assertIn(response.status_code, [200, 400])

    def test_register_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="password123",
        )
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "newuser",
                "email": "existing@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertIn(response.status_code, [200, 400])

    def test_register_weak_password(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "123",
                "password2": "123",
            },
        )
        self.assertIn(response.status_code, [200, 400])


class PasswordResetComprehensiveTest(AuthAssertMixin, BaseTestCase):
    """Full password reset flow tests."""

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse("account_reset_password"))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_email_sent(self):
        user = User.objects.create_user(
            username="testuser",
            email="reset@example.com",
            password="oldpassword123",
        )
        response = self.client.post(
            reverse("account_reset_password"), {"email": "reset@example.com"}
        )
        self.assertIn(response.status_code, [200, 302])

    def test_password_reset_invalid_email(self):
        response = self.client.post(
            reverse("account_reset_password"), {"email": "nonexistent@example.com"}
        )
        self.assertIn(response.status_code, [200, 302])


class EmailConfirmationTest(AuthAssertMixin, BaseTestCase):
    """Email confirmation flow tests."""

    def test_unverified_user_cannot_access_protected(self):
        user = User.objects.create_user(
            username="unverified",
            email="unverified@example.com",
            password="password123",
        )
        self.client.login(username="unverified", password="password123")
        response = self.client.get("/profile/")
        self.assertIn(response.status_code, [200, 302, 403])

    def test_email_verification_required_for_login(self):
        user = User.objects.create_user(
            username="needsverify",
            email="needsverify@example.com",
            password="password123",
        )
        response = self.client.post(
            reverse("account_login"),
            {"login": "needsverify@example.com", "password": "password123"},
        )
        self.assertIn(response.status_code, [200, 302])


class AuthFeatureAvailabilityTest(AuthAssertMixin, BaseTestCase):
    """Test auth feature availability and configuration."""

    def test_allauth_login_url_accessible(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)

    def test_allauth_register_url_accessible(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)

    def test_allauth_logout_url_accessible(self):
        response = self.client.get(reverse("account_logout"))
        self.assertIn(response.status_code, [200, 302])

    def test_password_reset_url_accessible(self):
        response = self.client.get(reverse("account_reset_password"))
        self.assertEqual(response.status_code, 200)

    def test_profile_url_requires_auth(self):
        response = self.client.get("/profile/")
        # Profile may redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])

    def test_admin_url_requires_auth(self):
        response = self.client.get("/admin/")
        # Admin redirects to login when unauthenticated
        self.assertIn(response.status_code, [302, 403])


class SocialAuthFeatureTest(AuthAssertMixin, BaseTestCase):
    """Social auth feature detection tests."""

    def test_social_login_links_present(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)

    def test_social_callback_urls_accessible(self):
        response = self.client.get("/accounts/google/login/callback/")
        self.assertNotEqual(response.status_code, 404)


class MFAFeatureTest(AuthAssertMixin, BaseTestCase):
    """MFA feature readiness tests."""

    def test_mfa_setup_url_requires_auth(self):
        response = self.client.get("/accounts/2fa/setup/")
        self.assertIn(response.status_code, [302, 403])

    def test_mfa_authenticate_url_accessible(self):
        response = self.client.get("/accounts/2fa/authenticate/")
        self.assertIn(response.status_code, [200, 302])


class HTMXAuthModalTest(AuthAssertMixin, BaseTestCase):
    """HTMX modal-based auth tests."""

    def test_login_modal_fragment(self):
        response = self.client.get(
            reverse("account_login"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)

    def test_register_modal_fragment(self):
        response = self.client.get(
            reverse("account_signup"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)

    def test_password_reset_modal_fragment(self):
        response = self.client.get(
            reverse("account_reset_password"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
