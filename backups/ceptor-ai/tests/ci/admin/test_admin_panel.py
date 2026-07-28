"""
Admin panel and Django Unfold access tests for ctc-research.com.

Covers:
- Anonymous access redirects to login
- Superuser can access admin panel
- Django Unfold UI markers present
- Wrong admin credentials denied
- Admin panel returns no 500 errors

Domain: ctc-research.com
Admin URL: /control/ (Wagtail) / /admin/ (Django admin redirect)
"""
from __future__ import annotations

from django_fusion.tests.base import BaseTestCase

from ..base.config import AdminURLs, AuthURLs, Credentials
from ..base.mixins import AuthAssertMixin, ResponseAssertMixin


class AdminAccessTest(ResponseAssertMixin, BaseTestCase):
    """
    Tests for admin panel access control.

    Uses django-fusion BaseTestCase which provides self.admin_user (superuser)
    and self.login_as_admin() helper.
    """

    def test_anonymous_admin_access_redirects_to_login(self):
        """
        Anonymous GET /admin/ must redirect to a login page.

        Selenium-style: visit admin without login → assert redirect to login.
        """
        response = self.client.get(AdminURLs.DJANGO_ADMIN)
        self.assertRedirectsToLogin(
            response,
            patterns=AuthURLs.LOGIN_REDIRECT_PATTERNS,
        )

    def test_superuser_can_access_admin_panel(self):
        """
        Superuser can access /admin/ and receive a non-error response.

        Selenium-style: login as admin → visit admin → assert page loads.
        """
        self.login_as_admin()
        response = self.client.get(AdminURLs.DJANGO_ADMIN, follow=True)
        self.assertNoServerError(response)

    def test_admin_panel_shows_unfold_ui_markers(self):
        """
        Admin panel must contain Django Unfold UI markers after superuser login.

        Validates: Django Unfold admin control page is active.
        """
        self.login_as_admin()
        response = self.client.get(AdminURLs.DJANGO_ADMIN, follow=True)
        self.assertNoServerError(response)
        body = response.content.decode("utf-8", errors="replace").lower()
        found = [m for m in AdminURLs.UI_MARKERS if m.lower() in body]
        self.assertTrue(
            len(found) > 0,
            f"Admin panel must show Unfold UI markers. Checked: {AdminURLs.UI_MARKERS}. "
            f"None found in response body.",
        )

    def test_wrong_admin_credentials_denied(self):
        """
        POST to admin login with wrong password must NOT authenticate.

        Selenium-style: submit wrong credentials → assert NOT logged in.
        """
        response = self.client.post(
            AdminURLs.LOGIN,
            data={
                "username": Credentials.SUPERUSER_USERNAME,
                "password": Credentials.WRONG_PASSWORD,
                "next": AdminURLs.DJANGO_ADMIN,
            },
            follow=True,
        )
        self.assertNoServerError(response)
        self.assertUserNotAuthenticated(
            response,
            "Wrong admin credentials must NOT authenticate",
        )

    def test_admin_login_page_loads(self):
        """GET /admin/login/ returns a successful response."""
        response = self.client.get(AdminURLs.LOGIN)
        self.assertPageLoads(response)


class AdminUnfoldTest(ResponseAssertMixin, BaseTestCase):
    """
    Tests specifically for Django Unfold admin integration.
    """

    def test_unfold_installed_in_apps(self):
        """django-unfold must be in INSTALLED_APPS."""
        from django.conf import settings
        installed = [a.lower() for a in settings.INSTALLED_APPS]
        self.assertTrue(
            any("unfold" in a for a in installed),
            "django-unfold must be in INSTALLED_APPS",
        )

    def test_admin_index_accessible_for_superuser(self):
        """Superuser can access the admin index without errors."""
        self.login_as_admin()
        response = self.client.get(AdminURLs.DJANGO_ADMIN, follow=True)
        self.assertNotIn(
            response.status_code,
            (403, 500),
            f"Admin index returned HTTP {response.status_code} for superuser",
        )
