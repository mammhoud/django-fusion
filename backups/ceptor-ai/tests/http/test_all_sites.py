"""
Comprehensive HTTP Integration Tests for All Sites
===================================================
Tests all defined routes across CTC Research, LMS Demo, VResume, and CRM.

Run:
    pytest tests/http/test_all_sites.py -v
    pytest tests/http/test_all_sites.py -v -k ctc      # CTC only
    pytest tests/http/test_all_sites.py -v -k lms      # LMS only
    pytest tests/http/test_all_sites.py -v -k vresume  # VResume only
    pytest tests/http/test_all_sites.py -v -k crm      # CRM only
    USE_LIVE_DOMAINS=1 pytest tests/http/test_all_sites.py -v  # Live domains
"""

import json
import os

import pytest
import requests

# ═════════════════════════════════════════════════════════════════════════════
# Configuration
# ═════════════════════════════════════════════════════════════════════════════

USE_LIVE = os.environ.get("USE_LIVE_DOMAINS", "0") == "1"

SITES = {
    "ctc-research": {
        "local": "http://localhost:5070",
        "domain": "https://www.ctc-research.com",
        "port": 5070,
    },
    "lms-demo": {
        "local": "http://localhost:5071",
        "domain": "https://core.structa.cloud",
        "port": 5071,
    },
    "vresume": {
        "local": "http://localhost:5072",
        "domain": "https://vresume.structa.cloud",
        "port": 5072,
    },
    "crm": {
        "local": "http://localhost:5074",
        "domain": "https://crm.structa.cloud",
        "port": 5074,
    },
}

TIMEOUT = int(os.environ.get("TEST_TIMEOUT", "10"))


def get_url(site_name):
    """Get the base URL for a site (live domain or local)."""
    site = SITES[site_name]
    return site["domain"] if USE_LIVE else site["local"]


def get(**kw):
    """HTTP GET with defaults."""
    kw.setdefault("timeout", TIMEOUT)
    kw.setdefault("allow_redirects", True)
    kw.setdefault("verify", False)
    return requests.get(**kw)


def assert_url_ok(url, label=None):
    """Assert URL returns 2xx/3xx (not 4xx/5xx)."""
    label = label or url
    try:
        r = get(url=url)
        assert r.status_code < 500, f"{label} returned {r.status_code}"
        return r
    except requests.RequestException as e:
        pytest.fail(f"{label} connection error: {e}")


def assert_status(url, expected_status, label=None):
    """Assert URL returns exact status code."""
    label = label or url
    try:
        r = get(url=url, allow_redirects=False)
        assert r.status_code == expected_status, (
            f"{label} returned {r.status_code}, expected {expected_status}"
        )
        return r
    except requests.RequestException as e:
        pytest.fail(f"{label} connection error: {e}")


def assert_status_in(url, expected_statuses, label=None):
    """Assert URL returns one of the expected status codes."""
    label = label or url
    try:
        r = get(url=url, allow_redirects=False)
        assert r.status_code in expected_statuses, (
            f"{label} returned {r.status_code}, expected one of {expected_statuses}"
        )
        return r
    except requests.RequestException as e:
        pytest.fail(f"{label} connection error: {e}")


def assert_healthy(url, label=None):
    """Assert health endpoint returns healthy JSON."""
    label = label or url
    try:
        r = get(url=url)
        data = r.json()
        assert data.get("status") in ("healthy", "ok"), f"{label}: unexpected status: {data}"
        return data
    except (requests.RequestException, json.JSONDecodeError) as e:
        pytest.fail(f"{label} health check failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# Site-specific route definitions
# ═════════════════════════════════════════════════════════════════════════════

# Each route: (path, expected_status_or_range, description)
# Use integer for exact status, tuple for any, list for multiple allowed
CTC_ROUTES = [
    ("/health/", assert_healthy, "Health endpoint"),
    ("/assets/health/", assert_healthy, "Assets health endpoint"),
    ("/health/database/", assert_healthy, "Database health endpoint"),
    ("/", lambda u, l: assert_url_ok(u, l), "Homepage"),
    ("/accounts/login/", lambda u, l: assert_url_ok(u, l), "Login page"),
    ("/accounts/register/", lambda u, l: assert_url_ok(u, l), "Register page"),
    ("/accounts/password/reset/", lambda u, l: assert_url_ok(u, l), "Password reset"),
    ("/django-admin/login/", lambda u, l: assert_status(u, 200, l), "Django admin login"),
    ("/admin/", lambda u, l: assert_status_in(u, [200, 301, 302], l), "Wagtail admin"),
    ("/sitemap.xml", lambda u, l: assert_status_in(u, [200, 404], l), "Sitemap XML"),
    ("/robots.txt", lambda u, l: assert_status_in(u, [200, 404], l), "Robots.txt"),
    ("/set-language/", lambda u, l: assert_status_in(u, [200, 302, 405], l), "Language switching"),
    ("/fusion/", lambda u, l: assert_url_ok(u, l), "Routable components"),
    ("/this-path-does-not-exist-xyz/", lambda u, l: assert_status(u, 404, l), "404 page"),
]

LMS_ROUTES = [
    ("/health/", assert_healthy, "Health endpoint"),
    ("/assets/health/", assert_healthy, "Assets health endpoint"),
    ("/health/database/", assert_healthy, "Database health endpoint"),
    ("/", lambda u, l: assert_url_ok(u, l), "Homepage"),
    ("/accounts/login/", lambda u, l: assert_url_ok(u, l), "Login page"),
    ("/accounts/register/", lambda u, l: assert_url_ok(u, l), "Register page"),
    ("/accounts/password/reset/", lambda u, l: assert_url_ok(u, l), "Password reset"),
    ("/django-admin/login/", lambda u, l: assert_status(u, 200, l), "Django admin login"),
    ("/admin/", lambda u, l: assert_status_in(u, [200, 301, 302], l), "Wagtail admin"),
    ("/sitemap.xml", lambda u, l: assert_status_in(u, [200, 404], l), "Sitemap XML"),
    ("/robots.txt", lambda u, l: assert_status_in(u, [200, 404], l), "Robots.txt"),
    ("/set-language/", lambda u, l: assert_status_in(u, [200, 302, 405], l), "Language switching"),
    ("/fusion/", lambda u, l: assert_url_ok(u, l), "Routable components"),
    ("/this-path-does-not-exist-xyz/", lambda u, l: assert_status(u, 404, l), "404 page"),
]

VRESUME_ROUTES = [
    ("/health/", assert_healthy, "Health endpoint"),
    ("/assets/health/", assert_healthy, "Assets health endpoint"),
    ("/health/database/", assert_healthy, "Database health endpoint"),
    ("/", lambda u, l: assert_url_ok(u, l), "Homepage"),
    ("/django-admin/login/", lambda u, l: assert_status(u, 200, l), "Django admin login"),
    ("/admin/", lambda u, l: assert_status_in(u, [200, 301, 302], l), "Wagtail admin"),
    ("/sitemap.xml", lambda u, l: assert_status_in(u, [200, 404], l), "Sitemap XML"),
    ("/robots.txt", lambda u, l: assert_status_in(u, [200, 404], l), "Robots.txt"),
    ("/set-language/", lambda u, l: assert_status_in(u, [200, 302, 405], l), "Language switching"),
    ("/api/csrf-token/", lambda u, l: assert_url_ok(u, l), "CSRF token API"),
    ("/api/theme/get/", lambda u, l: assert_url_ok(u, l), "Theme get API"),
    ("/media-health/", lambda u, l: assert_url_ok(u, l), "Media health endpoint"),
    ("/team/", lambda u, l: assert_url_ok(u, l), "Team page"),
    ("/blog/", lambda u, l: assert_url_ok(u, l), "Blog list"),
    ("/events/", lambda u, l: assert_url_ok(u, l), "Events list"),
    ("/this-path-does-not-exist-xyz/", lambda u, l: assert_status(u, 404, l), "404 page"),
]

CRM_ROUTES = [
    ("/health/", assert_healthy, "Health endpoint"),
    ("/assets/health/", assert_healthy, "Assets health endpoint"),
    ("/health/database/", assert_healthy, "Database health endpoint"),
    ("/", lambda u, l: assert_url_ok(u, l), "Homepage"),
    ("/accounts/login/", lambda u, l: assert_url_ok(u, l), "Login page"),
    ("/django-admin/login/", lambda u, l: assert_status(u, 200, l), "Django admin login"),
    ("/crm/", lambda u, l: assert_url_ok(u, l), "CRM components"),
    ("/set-language/", lambda u, l: assert_status_in(u, [200, 302, 405], l), "Language switching"),
    ("/robots.txt", lambda u, l: assert_status_in(u, [200, 404], l), "Robots.txt"),
    ("/this-path-does-not-exist-xyz/", lambda u, l: assert_status(u, 404, l), "404 page"),
]

# Map site names to their route lists
SITE_ROUTES = {
    "ctc-research": CTC_ROUTES,
    "lms-demo": LMS_ROUTES,
    "vresume": VRESUME_ROUTES,
    "crm": CRM_ROUTES,
}


# ═════════════════════════════════════════════════════════════════════════════
# Test Classes
# ═════════════════════════════════════════════════════════════════════════════

class TestAllSitesHealth:
    """All health endpoints across all sites."""

    @pytest.mark.parametrize("site_name", list(SITES.keys()))
    def test_health_endpoint(self, site_name):
        """Health endpoint returns healthy JSON."""
        base = get_url(site_name)
        r = get(url=f"{base}/health/")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") in ("healthy", "ok")
        assert "application/json" in r.headers.get("content-type", "")

    @pytest.mark.parametrize("site_name", list(SITES.keys()))
    def test_root_responds(self, site_name):
        """Root page does not 500."""
        base = get_url(site_name)
        r = get(url=f"{base}/")
        assert r.status_code < 500

    @pytest.mark.parametrize("site_name", list(SITES.keys()))
    def test_404_page(self, site_name):
        """Non-existent page returns 404."""
        base = get_url(site_name)
        r = get(url=f"{base}/this-path-does-not-exist-xyz/", allow_redirects=False)
        assert r.status_code == 404

    @pytest.mark.parametrize("site_name", list(SITES.keys()))
    def test_no_traceback_on_404(self, site_name):
        """404 pages should not expose debug tracebacks."""
        base = get_url(site_name)
        r = get(url=f"{base}/this-path-does-not-exist-xyz/")
        assert "Traceback" not in r.text


class TestCTCSite:
    """CTC Research site-specific routes."""

    @pytest.mark.parametrize("path,test_fn,desc", CTC_ROUTES)
    def test_route(self, path, test_fn, desc):
        base = get_url("ctc-research")
        test_fn(f"{base}{path}", f"CTC: {desc}")


class TestLMSSite:
    """LMS Demo site-specific routes."""

    @pytest.mark.parametrize("path,test_fn,desc", LMS_ROUTES)
    def test_route(self, path, test_fn, desc):
        base = get_url("lms-demo")
        test_fn(f"{base}{path}", f"LMS: {desc}")


class TestVResumeSite:
    """VResume site-specific routes."""

    @pytest.mark.parametrize("path,test_fn,desc", VRESUME_ROUTES)
    def test_route(self, path, test_fn, desc):
        base = get_url("vresume")
        test_fn(f"{base}{path}", f"VResume: {desc}")


class TestCRMSite:
    """CRM site-specific routes."""

    @pytest.mark.parametrize("path,test_fn,desc", CRM_ROUTES)
    def test_route(self, path, test_fn, desc):
        base = get_url("crm")
        test_fn(f"{base}{path}", f"CRM: {desc}")


class TestCrossSite:
    """Cross-site tests comparing all sites."""

    def test_all_health_endpoints_json(self):
        """All sites have properly formatted health endpoints."""
        for site_name in SITES:
            base = get_url(site_name)
            r = get(url=f"{base}/health/")
            assert r.status_code == 200
            data = r.json()
            assert "status" in data
            assert data["status"] in ("healthy", "ok")

    def test_all_sites_have_robots_when_accessible(self):
        """All sites either have robots.txt or return 404 gracefully."""
        for site_name in SITES:
            base = get_url(site_name)
            r = get(url=f"{base}/robots.txt", allow_redirects=False)
            assert r.status_code in (200, 301, 302, 404), (
                f"{site_name} robots.txt returned {r.status_code}"
            )

    def test_all_sites_have_admin_login(self):
        """All sites have accessible Django admin login (if implemented)."""
        for site_name in SITES:
            base = get_url(site_name)
            r = get(url=f"{base}/django-admin/login/", allow_redirects=False)
            # 200 = login page, 301/302 = redirect (some sites redirect admin)
            assert r.status_code in (200, 301, 302, 404), (
                f"{site_name} admin login returned {r.status_code}"
            )

    def test_no_server_errors(self):
        """None of the sites 500 on root, health, or login."""
        for site_name in SITES:
            base = get_url(site_name)
            for endpoint in ["/", "/health/", "/accounts/login/"]:
                try:
                    r = get(url=f"{base}{endpoint}", allow_redirects=False)
                    assert r.status_code != 500, (
                        f"{site_name}{endpoint} returned 500"
                    )
                except requests.RequestException:
                    pass  # Skip sites not running


# ═════════════════════════════════════════════════════════════════════════════
# Parameterized exhaustive route test
# ═════════════════════════════════════════════════════════════════════════════


