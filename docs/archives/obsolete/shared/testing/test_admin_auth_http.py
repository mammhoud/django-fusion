"""
Admin authentication tests using HTTP requests (no browser required).
Tests both structa.cloud (core, port 8280) and ctc-research.com (website, port 8271).

Covers:
  - Admin login page loads and shows login form
  - Superuser can log in successfully
  - Dashboard shows installed apps after login
  - Wrong password returns error, stays on login page
  - Logout works and redirects to login/logged-out page
  - Static assets are referenced on admin pages
  - Admin page has a proper title

Run:
    pytest tests/test_admin_auth_http.py -v
"""

import os
import re
import pytest
import requests

# ─── Config ──────────────────────────────────────────────────────────────────

SITES = {
    "core": {
        "admin_url": os.getenv("CORE_ADMIN_URL", "http://localhost:8280/admin/"),
        "username": os.getenv("CORE_USERNAME", "admin"),
        "password": os.getenv("CORE_PASSWORD", "mk_pAssWord123"),
        "label": "structa.cloud (core)",
    },
    "website": {
        "admin_url": os.getenv("WEBSITE_ADMIN_URL", "http://localhost:8271/admin/"),
        "username": os.getenv("WEBSITE_USERNAME", "admin"),
        "password": os.getenv("WEBSITE_PASSWORD", "mk_pAssWord123"),
        "label": "ctc-research.com (website)",
    },
}

TIMEOUT = 10


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_csrf(session: requests.Session, url: str) -> str:
    """GET the login page and extract the CSRF token."""
    resp = session.get(url, timeout=TIMEOUT, allow_redirects=True)
    assert resp.status_code == 200, f"Login page returned {resp.status_code}"
    match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', resp.text)
    if not match:
        match = re.search(r'csrfmiddlewaretoken.*?value=["\']([^"\']+)["\']', resp.text)
    assert match, "CSRF token not found on login page"
    return match.group(1)


def do_login(session: requests.Session, admin_url: str, username: str, password: str) -> requests.Response:
    """POST login credentials and return the response."""
    login_url = admin_url.rstrip("/") + "/login/"
    csrf = get_csrf(session, login_url)
    resp = session.post(
        login_url,
        data={
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": csrf,
            "next": "/admin/",
        },
        headers={"Referer": login_url},
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    return resp


def do_logout(session: requests.Session, admin_url: str) -> requests.Response:
    """POST logout and return the response."""
    logout_url = admin_url.rstrip("/") + "/logout/"
    # Try GET first (some Django versions allow it)
    resp = session.get(logout_url, timeout=TIMEOUT, allow_redirects=True)
    if resp.status_code == 200 and ("logged out" in resp.text.lower() or "log in" in resp.text.lower()):
        return resp
    # Fall back to POST with CSRF
    csrf = session.cookies.get("csrftoken", "")
    resp = session.post(
        logout_url,
        data={"csrfmiddlewaretoken": csrf},
        headers={"Referer": admin_url},
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    return resp


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def session():
    """Fresh requests session per test."""
    s = requests.Session()
    yield s
    s.close()


# ─── Parametrized tests ───────────────────────────────────────────────────────

@pytest.mark.parametrize("site_key", ["core", "website"])
class TestAdminLogin:

    def test_admin_login_page_loads(self, session, site_key):
        """Admin login page returns 200 and contains the login form."""
        cfg = SITES[site_key]
        login_url = cfg["admin_url"].rstrip("/") + "/login/"
        resp = session.get(login_url, timeout=TIMEOUT, allow_redirects=True)

        assert resp.status_code == 200, (
            f"[{cfg['label']}] Login page returned {resp.status_code}, expected 200"
        )
        assert "csrfmiddlewaretoken" in resp.text, (
            f"[{cfg['label']}] CSRF token not found on login page"
        )
        assert 'name="username"' in resp.text or 'id="id_username"' in resp.text, (
            f"[{cfg['label']}] Username field not found on login page"
        )
        assert 'name="password"' in resp.text or 'id="id_password"' in resp.text, (
            f"[{cfg['label']}] Password field not found on login page"
        )

    def test_admin_login_page_has_title(self, session, site_key):
        """Admin login page has a non-empty HTML title."""
        cfg = SITES[site_key]
        login_url = cfg["admin_url"].rstrip("/") + "/login/"
        resp = session.get(login_url, timeout=TIMEOUT, allow_redirects=True)

        title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
        assert title_match, f"[{cfg['label']}] No <title> tag found on login page"
        title = title_match.group(1).strip()
        assert title, f"[{cfg['label']}] Page title is empty"
        assert "error" not in title.lower(), (
            f"[{cfg['label']}] Error in page title: {title}"
        )

    def test_superuser_login_succeeds(self, session, site_key):
        """Superuser credentials result in a successful login (redirect away from login page)."""
        cfg = SITES[site_key]
        resp = do_login(session, cfg["admin_url"], cfg["username"], cfg["password"])

        # After successful login we should be on the admin dashboard, not the login page
        assert "login" not in resp.url or resp.url.rstrip("/").endswith("/admin"), (
            f"[{cfg['label']}] Still on login page after login. URL: {resp.url}"
        )
        assert resp.status_code == 200, (
            f"[{cfg['label']}] Expected 200 after login, got {resp.status_code}"
        )
        # Should not show login form anymore
        body_lower = resp.text.lower()
        assert "please enter the correct" not in body_lower, (
            f"[{cfg['label']}] Login error message shown after correct credentials"
        )

    def test_admin_dashboard_shows_content(self, session, site_key):
        """After login, admin dashboard contains expected admin content."""
        cfg = SITES[site_key]
        resp = do_login(session, cfg["admin_url"], cfg["username"], cfg["password"])

        body = resp.text
        # Django admin dashboard always has "Site administration" or similar heading
        assert any(phrase in body for phrase in [
            "Site administration",
            "site administration",
            "Django administration",
            "Administration",
            "Dashboard",
        ]), f"[{cfg['label']}] Admin dashboard heading not found. URL: {resp.url}"

    def test_admin_dashboard_has_title(self, session, site_key):
        """Admin dashboard page has a proper title (not an error)."""
        cfg = SITES[site_key]
        resp = do_login(session, cfg["admin_url"], cfg["username"], cfg["password"])

        title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
        assert title_match, f"[{cfg['label']}] No <title> on admin dashboard"
        title = title_match.group(1).strip()
        assert title, f"[{cfg['label']}] Dashboard title is empty"
        assert "error" not in title.lower(), (
            f"[{cfg['label']}] Error in dashboard title: {title}"
        )

    def test_wrong_password_shows_error(self, session, site_key):
        """Wrong password keeps user on login page with an error message."""
        cfg = SITES[site_key]
        resp = do_login(session, cfg["admin_url"], cfg["username"], "wrong_password_xyz_123")

        # Should stay on login page
        assert "login" in resp.url or resp.status_code == 200, (
            f"[{cfg['label']}] Expected to stay on login page with wrong password. URL: {resp.url}"
        )
        body_lower = resp.text.lower()
        assert any(phrase in body_lower for phrase in [
            "please enter the correct",
            "invalid",
            "error",
            "incorrect",
            "please enter a correct",
        ]), f"[{cfg['label']}] No error message shown for wrong credentials"

    def test_wrong_username_shows_error(self, session, site_key):
        """Wrong username keeps user on login page with an error message."""
        cfg = SITES[site_key]
        resp = do_login(session, cfg["admin_url"], "nonexistent_user_xyz", "anypassword")

        body_lower = resp.text.lower()
        assert any(phrase in body_lower for phrase in [
            "please enter the correct",
            "invalid",
            "error",
            "incorrect",
            "please enter a correct",
        ]), f"[{cfg['label']}] No error message shown for wrong username"

    def test_admin_logout(self, session, site_key):
        """Superuser can log out and is redirected to login/logged-out page."""
        cfg = SITES[site_key]
        # Login first
        do_login(session, cfg["admin_url"], cfg["username"], cfg["password"])

        # Now logout
        resp = do_logout(session, cfg["admin_url"])

        assert resp.status_code == 200, (
            f"[{cfg['label']}] Logout returned {resp.status_code}"
        )
        body_lower = resp.text.lower()
        assert any(phrase in body_lower for phrase in [
            "logged out",
            "log in again",
            "log in",
            "login",
            "sign in",
        ]), f"[{cfg['label']}] Logout did not redirect to expected page. URL: {resp.url}"

    def test_admin_requires_auth(self, session, site_key):
        """Accessing admin without login redirects to login page."""
        cfg = SITES[site_key]
        resp = session.get(cfg["admin_url"], timeout=TIMEOUT, allow_redirects=True)

        # Should redirect to login
        assert "login" in resp.url or resp.status_code in (200, 302), (
            f"[{cfg['label']}] Unexpected response for unauthenticated admin access"
        )
        if "login" not in resp.url:
            # If not redirected, should show login form
            assert "csrfmiddlewaretoken" in resp.text, (
                f"[{cfg['label']}] Admin accessible without auth and no login form shown"
            )

    def test_session_cookie_set_after_login(self, session, site_key):
        """A session cookie is set after successful login."""
        cfg = SITES[site_key]
        do_login(session, cfg["admin_url"], cfg["username"], cfg["password"])

        cookie_names = [c.name for c in session.cookies]
        assert any("session" in name.lower() or "sessionid" in name.lower() for name in cookie_names), (
            f"[{cfg['label']}] No session cookie found after login. Cookies: {cookie_names}"
        )


@pytest.mark.parametrize("site_key", ["core", "website"])
class TestAdminAssets:

    def test_admin_static_css_referenced(self, session, site_key):
        """Admin login page references at least one CSS stylesheet."""
        cfg = SITES[site_key]
        login_url = cfg["admin_url"].rstrip("/") + "/login/"
        resp = session.get(login_url, timeout=TIMEOUT, allow_redirects=True)

        css_links = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', resp.text, re.IGNORECASE)
        assert len(css_links) > 0, (
            f"[{cfg['label']}] No stylesheet links found on admin login page"
        )

    def test_admin_static_css_loads(self, session, site_key):
        """At least one admin CSS file actually loads (200 response)."""
        cfg = SITES[site_key]
        login_url = cfg["admin_url"].rstrip("/") + "/login/"
        resp = session.get(login_url, timeout=TIMEOUT, allow_redirects=True)

        # Extract first CSS href
        match = re.search(r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
        if not match:
            match = re.search(r'href=["\']([^"\']+\.css[^"\']*)["\']', resp.text)

        assert match, f"[{cfg['label']}] No CSS href found on login page"
        css_href = match.group(1)

        # Build absolute URL
        if css_href.startswith("http"):
            css_url = css_href
        else:
            base = cfg["admin_url"].rstrip("/").rsplit("/admin", 1)[0]
            css_url = base + css_href

        css_resp = session.get(css_url, timeout=TIMEOUT)
        assert css_resp.status_code == 200, (
            f"[{cfg['label']}] CSS file returned {css_resp.status_code}: {css_url}"
        )

    def test_admin_dashboard_static_css_loads(self, session, site_key):
        """Admin dashboard CSS loads after login."""
        cfg = SITES[site_key]
        resp = do_login(session, cfg["admin_url"], cfg["username"], cfg["password"])

        match = re.search(r'href=["\']([^"\']+\.css[^"\']*)["\']', resp.text)
        assert match, f"[{cfg['label']}] No CSS href found on admin dashboard"
        css_href = match.group(1)

        if css_href.startswith("http"):
            css_url = css_href
        else:
            base = cfg["admin_url"].rstrip("/").rsplit("/admin", 1)[0]
            css_url = base + css_href

        css_resp = session.get(css_url, timeout=TIMEOUT)
        assert css_resp.status_code == 200, (
            f"[{cfg['label']}] Dashboard CSS returned {css_resp.status_code}: {css_url}"
        )
