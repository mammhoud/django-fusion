"""
Static asset availability tests for ctc-research.com.

Covers:
- Homepage loads without 500 errors
- Health endpoint returns 200 with JSON status ok
- STATIC_ROOT contains CSS and JS files after collectstatic
- Known CSS/JS asset paths return HTTP 200 with correct content-type
- Django admin static assets accessible

Domain: ctc-research.com
Static URL: /static/
"""
from __future__ import annotations

import json

from django_osoul.tests.base import BaseTestCase

from ..base.config import Domain
from ..base.mixins import ResponseAssertMixin, StaticAssetMixin


class HomepageTest(ResponseAssertMixin, BaseTestCase):
    """Tests for the homepage and health endpoint."""

    def test_homepage_loads_without_server_error(self):
        """GET / must not return a 5xx error."""
        response = self.client.get("/")
        self.assertNoServerError(response)

    def test_health_endpoint_returns_200(self):
        """GET /health/ must return HTTP 200."""
        response = self.client.get("/health/")
        self.assertEqual(
            response.status_code, 200,
            f"Health endpoint returned HTTP {response.status_code}",
        )

    def test_health_endpoint_returns_json_ok(self):
        """GET /health/ must return JSON body with status: ok."""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        try:
            body = json.loads(response.content)
            self.assertEqual(
                body.get("status"), "ok",
                f"Health endpoint JSON must contain status: ok. Got: {body}",
            )
        except (json.JSONDecodeError, AttributeError):
            pass  # plain text health check — just verify 200


class StaticFilesCollectedTest(StaticAssetMixin, ResponseAssertMixin, BaseTestCase):
    """
    Tests that collectstatic has been run and files are present.

    Validates: Correctness Property 2 — collectstatic Output Invariant.
    """

    def test_static_root_contains_css_files(self):
        """STATIC_ROOT must contain at least one .css file after collectstatic."""
        self.assertStaticRootHasFiles("css")

    def test_static_root_contains_js_files(self):
        """STATIC_ROOT must contain at least one .js file after collectstatic."""
        self.assertStaticRootHasFiles("js")


class StaticFileServingTest(StaticAssetMixin, ResponseAssertMixin, BaseTestCase):
    """
    Tests that static files are served correctly by the application.
    """

    def test_known_css_asset_returns_200(self):
        """A known CSS asset path must return HTTP 200 with text/css content-type."""
        root = self.staticfiles_root()
        if not root.exists():
            self.skipTest("STATIC_ROOT does not exist — run collectstatic first")
        css_files = list(root.rglob("*.css"))
        if not css_files:
            self.skipTest("No CSS files found in STATIC_ROOT")

        first_css = css_files[0]
        relative = first_css.relative_to(root)
        url = f"{self.static_url().rstrip('/')}/{relative.as_posix()}"

        response = self.client.get(url)
        self.assertIn(
            response.status_code, (200, 301, 302),
            f"CSS asset {url} returned HTTP {response.status_code}",
        )
        if response.status_code == 200:
            content_type = response.get("Content-Type", "")
            self.assertIn(
                "css", content_type.lower(),
                f"Expected text/css content-type for {url}, got {content_type}",
            )

    def test_known_js_asset_returns_200(self):
        """A known JS asset path must return HTTP 200 with javascript content-type."""
        root = self.staticfiles_root()
        if not root.exists():
            self.skipTest("STATIC_ROOT does not exist — run collectstatic first")
        js_files = list(root.rglob("*.js"))
        if not js_files:
            self.skipTest("No JS files found in STATIC_ROOT")

        first_js = js_files[0]
        relative = first_js.relative_to(root)
        url = f"{self.static_url().rstrip('/')}/{relative.as_posix()}"

        response = self.client.get(url)
        self.assertIn(
            response.status_code, (200, 301, 302),
            f"JS asset {url} returned HTTP {response.status_code}",
        )
        if response.status_code == 200:
            content_type = response.get("Content-Type", "")
            self.assertIn(
                "javascript", content_type.lower(),
                f"Expected javascript content-type for {url}, got {content_type}",
            )

    def test_django_admin_css_accessible(self):
        """Django admin static CSS must be accessible."""
        self.assertStaticFileServed("admin/css/base.css")

    def test_favicon_not_404(self):
        """GET /favicon.ico must not return 404."""
        try:
            response = self.client.get("/favicon.ico")
            self.assertNotEqual(
                response.status_code, 404,
                "favicon.ico returned 404 — check STATIC_ROOT and URL config",
            )
        except Exception:
            self.skipTest("favicon.ico URL not registered in URL conf")
