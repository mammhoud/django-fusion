"""Smoke tests for LMS CMS URL routing."""

from __future__ import annotations

from django.urls import resolve


API_ROUTE_EXPECTATIONS = {
    "/apis/auth/login/": "api:auth_login",
    "/apis/auth/profile/": "api:auth_profile",
    "/apis/courses/": "api:course_list",
    "/apis/instructors/": "api:instructor_list",
}


def test_lms_api_routes_resolve_under_apis_prefix() -> None:
    """RTK Query's /apis/* URLs should resolve through the CMS URLconf."""
    for url, view_name in API_ROUTE_EXPECTATIONS.items():
        match = resolve(url)
        assert match.view_name == view_name
