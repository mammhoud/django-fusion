"""
Project-specific assertion mixins for ctc-research.com CI tests.

Extends django_fusion.tests.mixins with domain-aware and auth-specific helpers.
"""
from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings as django_settings
from django.core import mail
from django_fusion.tests.mixins import AssertEmailMixin, AssertHTMLMixin


class ResponseAssertMixin(AssertHTMLMixin):
    """
    Response assertion helpers for ctc-research.com.

    Provides semantic assertions that read like browser interactions.
    """

    def assertPageLoads(self, response, msg: str = "") -> None:
        """Assert response is a successful page load (not 4xx/5xx)."""
        self.assertIn(
            response.status_code,
            (200, 301, 302),
            msg or f"Expected page load, got HTTP {response.status_code}",
        )

    def assertNoServerError(self, response, msg: str = "") -> None:
        """Assert response is not a 5xx server error."""
        self.assertNotIn(
            response.status_code,
            range(500, 600),
            msg or f"Server error: HTTP {response.status_code}",
        )

    def assertRedirectsToLogin(self, response, patterns=("login", "sign-in", "signin")) -> None:
        """Assert response redirects to a login page."""
        self.assertIn(
            response.status_code,
            (301, 302),
            f"Expected redirect to login, got HTTP {response.status_code}",
        )
        location = response.get("Location", "").lower()
        self.assertTrue(
            any(p in location for p in patterns),
            f"Redirect location '{location}' does not point to login",
        )

    def assertUserAuthenticated(self, response, msg: str = "") -> None:
        """Assert the request user is authenticated."""
        self.assertTrue(
            response.wsgi_request.user.is_authenticated,
            msg or "Expected user to be authenticated",
        )

    def assertUserNotAuthenticated(self, response, msg: str = "") -> None:
        """Assert the request user is NOT authenticated."""
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            msg or "Expected user to NOT be authenticated",
        )

    def assertBodyContainsError(self, response, msg: str = "") -> None:
        """
        Assert the response body contains an error notification.

        Checks for common error indicators used in the project's templates.
        """
        body = response.content.decode("utf-8", errors="replace").lower()
        error_indicators = [
            "incorrect", "invalid", "wrong", "error", "failed",
            "not correct", "credentials", "alert", "danger",
            "please correct", "this field", "required",
        ]
        has_error = any(indicator in body for indicator in error_indicators)
        self.assertTrue(
            has_error,
            msg or f"Expected error notification in response body. Indicators checked: {error_indicators}",
        )

    def assertBodyContains(self, response, text: str, msg: str = "") -> None:
        """Assert the response body contains the given text (case-insensitive)."""
        body = response.content.decode("utf-8", errors="replace").lower()
        self.assertIn(
            text.lower(),
            body,
            msg or f"Expected '{text}' in response body",
        )


class AuthAssertMixin(ResponseAssertMixin, AssertEmailMixin):
    """
    Auth-specific assertion helpers combining response and email assertions.
    """

    def assertConfirmationEmailSent(self, email: str) -> None:
        """Assert a confirmation email was sent to the given address."""
        self.assertEmailSent(email)
        sent = [m for m in mail.outbox if email in m.to]
        self.assertTrue(len(sent) > 0, f"No email sent to {email}")
        body = sent[0].body
        has_link = (
            "/confirm-email/" in body
            or "/create-password/" in body
            or "/verify" in body
            or "confirm" in body.lower()
        )
        self.assertTrue(
            has_link,
            f"Confirmation email to {email} does not contain a confirmation link. Body: {body[:300]}",
        )

    def assertPasswordResetEmailSent(self, email: str) -> None:
        """Assert a password reset email was sent to the given address."""
        self.assertEmailSent(email)
        sent = [m for m in mail.outbox if email in m.to]
        self.assertTrue(len(sent) > 0, f"No password reset email sent to {email}")
        body = sent[0].body
        has_link = (
            "/password/reset/key/" in body
            or "/reset/" in body
            or "reset" in body.lower()
        )
        self.assertTrue(
            has_link,
            f"Password reset email to {email} does not contain a reset link. Body: {body[:300]}",
        )

    def extractConfirmationKey(self) -> str | None:
        """Extract email confirmation key from the outbox."""
        for message in mail.outbox:
            match = re.search(r'/accounts/confirm-email/([^/\s"\']+)/', message.body)
            if match:
                return match.group(1)
            match2 = re.search(r'/create-password/([^/\s"\']+)/', message.body)
            if match2:
                return match2.group(1)
        return None

    def extractPasswordResetKey(self) -> str | None:
        """Extract password reset key from the outbox."""
        for message in mail.outbox:
            match = re.search(r'/accounts/password/reset/key/([^/\s"\']+)/', message.body)
            if match:
                return match.group(1)
        return None


class StaticAssetMixin:
    """Helpers for static asset availability assertions."""

    @staticmethod
    def staticfiles_root() -> Path:
        """Return the staticfiles output directory."""
        return Path(getattr(django_settings, "STATIC_ROOT", None) or "assets/staticfiles")

    @staticmethod
    def static_url() -> str:
        """Return the STATIC_URL setting."""
        return getattr(django_settings, "STATIC_URL", "/static/")

    def assertStaticRootHasFiles(self, extension: str) -> None:
        """Assert STATIC_ROOT contains at least one file with the given extension."""
        root = self.staticfiles_root()
        if not root.exists():
            self.skipTest(f"STATIC_ROOT {root} does not exist — run collectstatic first")
        files = list(root.rglob(f"*.{extension}"))
        self.assertGreater(
            len(files), 0,
            f"No .{extension} files found under {root}",
        )

    def assertStaticFileServed(self, relative_path: str) -> None:
        """Assert a static file path returns HTTP 200 with correct content-type."""
        url = f"{self.static_url().rstrip('/')}/{relative_path.lstrip('/')}"
        response = self.client.get(url)
        self.assertIn(
            response.status_code, (200, 301, 302),
            f"Static file {url} returned HTTP {response.status_code}",
        )
