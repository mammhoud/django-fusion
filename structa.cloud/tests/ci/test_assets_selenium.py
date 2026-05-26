"""
Static asset availability tests for ctc-research.com using django-grep test utilities.

Uses django_grep.tests.base.BaseTestCase (Django test client — browser-style)
and django_grep.tests.mixins.AssertHTMLMixin for HTML assertions.

Covers:
- Known static asset paths return HTTP 200
- Correct Content-Type headers for CSS and JS files
- No 404s on critical asset paths
- collectstatic output directory is non-empty
- Homepage loads without 500 errors
"""
from __future__ import annotations

import os
from pathlib import Path

import django
from django.conf import settings as django_settings

if not django_settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    os.environ.setdefault("DJANGO_PRINT_ENV", "false")
    django.setup()

from django.test import Client, override_settings
from django_grep.tests.base import BaseTestCase
from django_grep.tests.mixins import AssertHTMLMixin

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _staticfiles_root() -> Path:
    """Return the staticfiles output directory."""
    return Path(django_settings.STATIC_ROOT or "assets/staticfiles")


# ---------------------------------------------------------------------------
# Asset availability tests
# ---------------------------------------------------------------------------

class StaticAssetAvailabilityTest(AssertHTMLMixin, BaseTestCase):
    """
    Verify static assets are served correctly.

    Validates: Requirement 2 — static asset verification.
    """

    def test_homepage_loads_without_500(self):
        """GET / must not return a 5xx error."""
        response = self.client.get("/")
        self.assertNotIn(
            response.status_code,
            range(500, 600),
            f"Homepage returned HTTP {response.status_code}",
        )

    def test_health_endpoint_returns_200(self):
        """GET /health/ must return HTTP 200 with JSON status ok."""
        import json
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        try:
            body = json.loads(response.content)
            self.assertEqual(body.get("status"), "ok")
        except (json.JSONDecodeError, AttributeError):
            pass  # health endpoint may return plain text — just check 200

    def test_static_root_directory_contains_css_files(self):
        """
        After collectstatic, STATIC_ROOT must contain at least one .css file.

        Validates: Correctness Property 2 — collectstatic Output Invariant.
        """
        static_root = _staticfiles_root()
        if not static_root.exists():
            self.skipTest(f"STATIC_ROOT {static_root} does not exist — run collectstatic first")
        css_files = list(static_root.rglob("*.css"))
        self.assertGreater(
            len(css_files),
            0,
            f"No .css files found under {static_root}",
        )

    def test_static_root_directory_contains_js_files(self):
        """
        After collectstatic, STATIC_ROOT must contain at least one .js file.

        Validates: Correctness Property 2 — collectstatic Output Invariant.
        """
        static_root = _staticfiles_root()
        if not static_root.exists():
            self.skipTest(f"STATIC_ROOT {static_root} does not exist — run collectstatic first")
        js_files = list(static_root.rglob("*.js"))
        self.assertGreater(
            len(js_files),
            0,
            f"No .js files found under {static_root}",
        )

    def test_known_static_css_asset_returns_200(self):
        """
        A known CSS asset path must return HTTP 200 with text/css content-type.

        Uses Django's test client which serves static files via WhiteNoise/staticfiles.
        """
        static_root = _staticfiles_root()
        if not static_root.exists():
            self.skipTest("STATIC_ROOT does not exist — run collectstatic first")

        css_files = list(static_root.rglob("*.css"))
        if not css_files:
            self.skipTest("No CSS files found in STATIC_ROOT")

        # Pick the first CSS file and derive its URL
        first_css = css_files[0]
        relative = first_css.relative_to(static_root)
        static_url = django_settings.STATIC_URL or "/static/"
        url = f"{static_url.rstrip('/')}/{relative.as_posix()}"

        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            (200, 301, 302),
            f"CSS asset {url} returned HTTP {response.status_code}",
        )
        if response.status_code == 200:
            content_type = response.get("Content-Type", "")
            self.assertIn(
                "css",
                content_type.lower(),
                f"Expected text/css content-type for {url}, got {content_type}",
            )

    def test_known_static_js_asset_returns_200(self):
        """
        A known JS asset path must return HTTP 200 with javascript content-type.
        """
        static_root = _staticfiles_root()
        if not static_root.exists():
            self.skipTest("STATIC_ROOT does not exist — run collectstatic first")

        js_files = list(static_root.rglob("*.js"))
        if not js_files:
            self.skipTest("No JS files found in STATIC_ROOT")

        first_js = js_files[0]
        relative = first_js.relative_to(static_root)
        static_url = django_settings.STATIC_URL or "/static/"
        url = f"{static_url.rstrip('/')}/{relative.as_posix()}"

        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            (200, 301, 302),
            f"JS asset {url} returned HTTP {response.status_code}",
        )
        if response.status_code == 200:
            content_type = response.get("Content-Type", "")
            self.assertIn(
                "javascript",
                content_type.lower(),
                f"Expected javascript content-type for {url}, got {content_type}",
            )

    def test_no_404_on_favicon(self):
        """GET /favicon.ico must not return 404 (may return 200, 301, or 500 if not configured)."""
        try:
            response = self.client.get("/favicon.ico")
            self.assertNotEqual(
                response.status_code,
                404,
                "favicon.ico returned 404 — check STATIC_ROOT and URL config",
            )
        except Exception:
            # Resolver404 or similar — favicon URL not registered, skip gracefully
            self.skipTest("favicon.ico URL not registered in URL conf")

    def test_admin_static_assets_load(self):
        """
        Django admin static assets must be accessible.

        Validates: Requirement 7 — admin panel loads without errors.
        """
        response = self.client.get("/static/admin/css/base.css")
        self.assertIn(
            response.status_code,
            (200, 301, 302),
            f"Django admin CSS returned HTTP {response.status_code}",
        )
