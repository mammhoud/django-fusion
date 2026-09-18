"""Integration tests for the allauth headless API on Precis.

These cover the contract consumed by the Alpine login modal on both render
roads (Astro frontend + Django templates):

    GET  /api/auth/browser/v1/config    → auth configuration (flows)
    GET  /api/auth/browser/v1/session   → current session state
    POST /api/auth/browser/v1/auth/login → email + password session login

Mirrors precis-landing's apps/pages/tests.py::test_allauth_headless_*.
"""

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase

# Headless API paths (stable browser contract consumed by the Alpine modal).
# In the browser namespace, ``config`` lives at v1/config while the auth
# actions (session/login) nest under v1/auth/. Logout is a DELETE on the
# session endpoint — not a separate path.
CONFIG_URL = "/api/auth/browser/v1/config"
SESSION_URL = "/api/auth/browser/v1/auth/session"
LOGIN_URL = "/api/auth/browser/v1/auth/login"


class HeadlessAuthApiTests(TestCase):
    """The headless API is wired and serves the login/signup flows."""

    api_headers = {"HTTP_ACCEPT": "application/json"}

    def test_headless_config_reports_flows(self):
        """GET /api/auth/browser/v1/config advertises the email login flow."""
        response = self.client.get(CONFIG_URL, **self.api_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        data = payload["data"]
        # The browser config nests account/socialaccount/mfa sections.
        self.assertIn("login_methods", data["account"])
        self.assertIn("email", data["account"]["login_methods"])
        # MFA is advertised with the configured types (allauth.mfa installed).
        self.assertIn("mfa", data)
        self.assertEqual(
            data["mfa"]["supported_types"],
            ["recovery_codes", "totp", "webauthn"],
        )

    def test_headless_session_anonymous(self):
        """An anonymous session reports 401 with login/signup flows."""
        response = self.client.get(SESSION_URL, **self.api_headers)
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertIs(payload["meta"]["is_authenticated"], False)

    def test_headless_login_requires_csrf_for_browser_clients(self):
        """Browser login rejects missing CSRF and accepts the issued token."""
        User = get_user_model()
        user = User.objects.create_user(
            username="headless_csrf",
            email="headless_csrf@example.com",
            password="s3cret-passw0rd",
        )
        EmailAddress.objects.create(
            user=user, email=user.email, verified=True, primary=True
        )
        client = self.client.__class__(enforce_csrf_checks=True)
        client.get("/apis/auth/status/", **self.api_headers)
        csrf_token = client.cookies["csrftoken"].value

        blocked = client.post(
            LOGIN_URL,
            data={"email": user.email, "password": "s3cret-passw0rd"},
            content_type="application/json",
            **self.api_headers,
        )
        self.assertEqual(blocked.status_code, 403)

        allowed = client.post(
            LOGIN_URL,
            data={"email": user.email, "password": "s3cret-passw0rd"},
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
            **self.api_headers,
        )
        self.assertEqual(allowed.status_code, 200)

    def test_headless_logout_requires_csrf_for_browser_clients(self):
        """Browser logout rejects missing CSRF and accepts the issued token."""
        User = get_user_model()
        user = User.objects.create_user(
            username="headless_logout_csrf",
            email="headless_logout_csrf@example.com",
            password="s3cret-passw0rd",
        )
        client = self.client.__class__(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/apis/auth/status/", **self.api_headers)
        csrf_token = client.cookies["csrftoken"].value

        blocked = client.delete(SESSION_URL, **self.api_headers)
        self.assertEqual(blocked.status_code, 403)

        allowed = client.delete(
            SESSION_URL,
            HTTP_X_CSRFTOKEN=csrf_token,
            **self.api_headers,
        )
        self.assertEqual(allowed.status_code, 401)

    def test_auth_status_issues_a_csrf_cookie_without_auth_tokens(self):
        """The browser status endpoint establishes CSRF, not a bearer token."""
        response = self.client.get("/apis/auth/status/", **self.api_headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)
        self.assertNotIn("access_token", response.json())
        self.assertNotIn("refresh_token", response.json())

    def test_headless_login_round_trip(self):
        """A real login round-trip: verified user → POST → authenticated session."""
        User = get_user_model()
        user = User.objects.create_user(
            username="headless_tester",
            email="headless@example.com",
            password="s3cret-passw0rd",
        )
        EmailAddress.objects.create(
            user=user, email=user.email, verified=True, primary=True
        )

        response = self.client.post(
            LOGIN_URL,
            data={"email": user.email, "password": "s3cret-passw0rd"},
            content_type="application/json",
            **self.api_headers,
        )
        self.assertEqual(response.status_code, 200)
        # Session is now authenticated (200 with the signed-in user).
        session = self.client.get(SESSION_URL, **self.api_headers)
        self.assertEqual(session.status_code, 200)
        self.assertEqual(
            session.json()["data"]["user"]["email"], user.email
        )

    def test_headless_login_wrong_password(self):
        """Wrong credentials → 400 with the email/password mismatch error."""
        User = get_user_model()
        user = User.objects.create_user(
            username="headless_wrong",
            email="headless_wrong@example.com",
            password="s3cret-passw0rd",
        )
        EmailAddress.objects.create(
            user=user, email=user.email, verified=True, primary=True
        )

        response = self.client.post(
            LOGIN_URL,
            data={"email": user.email, "password": "wrong-password"},
            content_type="application/json",
            **self.api_headers,
        )
        # allauth headless reports bad credentials as 400 with a structured
        # error list carrying the email_password_mismatch code.
        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertIn("email_password_mismatch", [e["code"] for e in errors])

    def test_auth_status_anonymous(self):
        """GET /apis/auth/status/ reports anonymous for logged-out visitors."""
        response = self.client.get("/apis/auth/status/", **self.api_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIs(payload["authenticated"], False)
        self.assertIsNone(payload["user"])

    def test_auth_status_authenticated(self):
        """GET /apis/auth/status/ reports the session user when signed in."""
        User = get_user_model()
        user = User.objects.create_user(
            username="headless_status",
            email="headless_status@example.com",
            password="s3cret-passw0rd",
        )
        self.client.force_login(user)

        response = self.client.get("/apis/auth/status/", **self.api_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIs(payload["authenticated"], True)
        self.assertEqual(payload["user"]["email"], user.email)
        # Learning summary present (empty for a fresh user).
        self.assertEqual(payload["learning"]["active"], 0)

    def test_headless_logout(self):
        """DELETE on the session endpoint clears the session."""
        User = get_user_model()
        user = User.objects.create_user(
            username="headless_out",
            email="headless_out@example.com",
            password="s3cret-passw0rd",
        )
        self.client.force_login(user)

        response = self.client.delete(SESSION_URL, **self.api_headers)
        # Post-logout the session is anonymous again → 401 like the
        # anonymous session check (same contract as precis-landing).
        self.assertEqual(response.status_code, 401)

        session = self.client.get(SESSION_URL, **self.api_headers)
        self.assertEqual(session.status_code, 401)
        self.assertIs(session.json()["meta"]["is_authenticated"], False)
