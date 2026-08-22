"""Tests for the API v1 deprecation middleware.

Verifies that Deprecation/Sunset/Warning headers are added to /api/v1/
responses and absent from non-v1 paths.
"""

from __future__ import annotations

from django.test import Client, TestCase


class APIV1DeprecationMiddlewareTests(TestCase):
    """Middleware adds deprecation headers only on the /api/v1/ road."""

    def setUp(self) -> None:
        self.client = Client()

    def test_v1_routes_get_deprecation_headers(self) -> None:
        responses = [
            self.client.get("/api/v1/"),
            self.client.get("/api/v1/companies/"),
            self.client.get("/api/v1/board/"),
            self.client.get("/api/v1/workspace/current/"),
        ]
        for response in responses:
            self.assertEqual(response.get("Deprecation"), "true", f"Missing Deprecation on {response.request['PATH_INFO']}")
            self.assertIn("@", response.get("Sunset") or "", f"Missing Sunset on {response.request['PATH_INFO']}")
            self.assertIn("deprecated", response.get("Warning") or "", f"Missing Warning on {response.request['PATH_INFO']}")

    def test_non_v1_routes_do_not_get_deprecation_headers(self) -> None:
        responses = [
            self.client.get("/apis/core/dashboard/"),
            self.client.get("/apis/core/board/"),
            self.client.get("/apis/core/workspace/current/"),
            self.client.get("/apis/pages/home/"),
            self.client.get("/apis/me/"),
            self.client.get("/"),
        ]
        for response in responses:
            self.assertIsNone(
                response.get("Deprecation"),
                f"Unexpected Deprecation header on {response.request['PATH_INFO']}",
            )

    def test_v1_resource_detail_gets_deprecation_headers(self) -> None:
        response = self.client.get("/api/v1/companies/1/")
        # The resource detail road returns 404 (no fixture), but the middleware
        # should still add the deprecation headers.
        self.assertEqual(response.get("Deprecation"), "true")

    def test_v1_bolt_compat_tables_gets_deprecation_headers(self) -> None:
        response = self.client.get("/api/v1/tables/companies/")
        self.assertEqual(response.get("Deprecation"), "true")