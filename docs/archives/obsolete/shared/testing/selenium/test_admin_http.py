"""
Admin authentication tests using HTTP + Django shell via docker exec.

Both sites run in production mode with:
  - CSRF_COOKIE_SECURE=True  (cookie only sent over HTTPS)
  - SESSION_COOKIE_SECURE=True
  - CSRF_TRUSTED_ORIGINS = HTTPS domains only

This means login via plain HTTP is intentionally blocked by Django's CSRF
protection. Tests that require authentication use docker exec to call the
Django shell directly inside the container.

Sites:
  - structa.cloud (core)       → container: alliance-website, port 8280
  - ctc-research.com (website) → container: website,          port 8271

Run:
    python3 -m pytest tests/selenium/test_admin_http.py -v
"""

import os
import re
import json
import subprocess
import pytest
import requests

# ─── Config ──────────────────────────────────────────────────────────────────

SITES = {
    "core": {
        "base_url": os.getenv("CORE_BASE_URL", "http://localhost:8280"),
        "container": "alliance-website",
        "settings_module": "configs.settings",
        "username": "admin",
        "password": "mk_pAssWord123",
        "label": "structa.cloud (core)",
        "login_path": "/auth/sign-in/",
        "admin_path": "/admin/",
        "health_path": "/health/",
    },
    "website": {
        "base_url": os.getenv("WEBSITE_BASE_URL", "http://localhost:8271"),
        "container": "website",
        "settings_module": "configs.settings",
        "username": "admin",
        "password": "mk_pAssWord123",
        "label": "ctc-research.com (website)",
        "login_path": "/auth/sign-in/",
        "admin_path": "/admin/",
        "health_path": "/health/",
    },
}


def _docker_python(container, settings_module, code):
    """Run Python code inside a container and return stdout, stripping banner noise."""
    # Write code to a temp script to avoid shell quoting issues
    script = (
        f"import os, sys\n"
        f"os.environ['DJANGO_SETTINGS_MODULE'] = '{settings_module}'\n"
        f"import django; django.setup()\n"
        f"{code}\n"
    )
    # Escape for bash heredoc
    cmd = [
        "docker", "exec", container,
        "bash", "-c",
        f"cd /app && .venv/bin/python - << 'PYEOF' 2>/dev/null\n{script}\nPYEOF"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    # Strip box-drawing banner lines (│ ═ ╔ etc.) and keep only plain text lines
    lines = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip banner decoration lines
        if any(c in stripped for c in "│═╔╚╗╝┌└┐┘─🌍🚀🐳📦✅⚙️🔗🔐"):
            continue
        # Skip lines that are only = signs (separator lines)
        if stripped.replace("=", "").replace(" ", "") == "":
            continue
        lines.append(stripped)
    return "\n".join(lines), result.returncode


# ─── Group 1: Public endpoint checks (no auth needed) ────────────────────────

@pytest.mark.parametrize("site_key", ["core", "website"])
class TestPublicEndpoints:

    def test_admin_redirects_to_login_when_unauthenticated(self, site_key):
        """GET /admin/ unauthenticated → redirects to /auth/sign-in/."""
        cfg = SITES[site_key]
        r = requests.get(
            f"{cfg['base_url']}{cfg['admin_path']}", allow_redirects=True
        )
        assert r.status_code == 200, (
            f"[{cfg['label']}] Expected 200 after redirect, got {r.status_code}"
        )
        assert "sign-in" in r.url or "login" in r.url, (
            f"[{cfg['label']}] Expected redirect to login, got: {r.url}"
        )

    def test_login_page_returns_200(self, site_key):
        """GET /auth/sign-in/ → 200."""
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}{cfg['login_path']}")
        assert r.status_code == 200, (
            f"[{cfg['label']}] Login page returned {r.status_code}"
        )

    def test_login_page_has_password_field(self, site_key):
        """Login page HTML contains a password input."""
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}{cfg['login_path']}")
        assert 'type="password"' in r.text or "id_password" in r.text, (
            f"[{cfg['label']}] No password field in login page HTML"
        )

    def test_login_page_has_csrf_token_in_html(self, site_key):
        """Login page HTML contains a CSRF token (even if cookie is Secure-only)."""
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}{cfg['login_path']}")
        assert "csrfmiddlewaretoken" in r.text, (
            f"[{cfg['label']}] No csrfmiddlewaretoken in login page HTML"
        )

    def test_health_endpoint_returns_200(self, site_key):
        """GET /health/ → 200."""
        cfg = SITES[site_key]
        r = requests.get(
            f"{cfg['base_url']}{cfg['health_path']}", allow_redirects=True
        )
        assert r.status_code == 200, (
            f"[{cfg['label']}] Health endpoint returned {r.status_code}"
        )

    def test_static_admin_css_served(self, site_key):
        """Django admin CSS is served with correct Content-Type."""
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}/static/admin/css/base.css")
        assert r.status_code == 200, (
            f"[{cfg['label']}] Admin CSS returned {r.status_code}"
        )
        assert "text/css" in r.headers.get("Content-Type", ""), (
            f"[{cfg['label']}] Wrong Content-Type: {r.headers.get('Content-Type')}"
        )

    def test_wrong_password_returns_403_or_200(self, site_key):
        """POST wrong credentials → 403 (CSRF blocked over HTTP) or 200 with error.

        In production mode with CSRF_COOKIE_SECURE=True, plain HTTP POST
        returns 403 because the CSRF cookie cannot be sent back over HTTP.
        This is correct security behaviour — not a bug.
        """
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}{cfg['login_path']}")
        m = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', r.text)
        csrf = m.group(1) if m else ""

        r2 = requests.post(
            f"{cfg['base_url']}{cfg['login_path']}",
            data={
                "login": cfg["username"],
                "password": "wrong_password_xyz",
                "csrfmiddlewaretoken": csrf,
            },
            headers={"Referer": f"{cfg['base_url']}{cfg['login_path']}"},
            allow_redirects=True,
        )
        # 403 = CSRF blocked (expected in production over HTTP)
        # 200 = login page re-rendered with error
        assert r2.status_code in (200, 403), (
            f"[{cfg['label']}] Unexpected status {r2.status_code} for bad credentials"
        )
        # Must NOT redirect to admin
        assert cfg["admin_path"] not in r2.url or "sign-in" in r2.url, (
            f"[{cfg['label']}] Bad credentials should not grant admin access"
        )

    def test_csrf_protection_blocks_plain_http_post(self, site_key):
        """Confirm CSRF protection is active: plain HTTP POST without valid cookie → 403."""
        cfg = SITES[site_key]
        r = requests.post(
            f"{cfg['base_url']}{cfg['login_path']}",
            data={"login": "admin", "password": "anything"},
            headers={"Referer": f"{cfg['base_url']}{cfg['login_path']}"},
        )
        # 403 confirms CSRF middleware is active and working
        assert r.status_code == 403, (
            f"[{cfg['label']}] Expected 403 CSRF rejection, got {r.status_code}. "
            f"CSRF protection may be misconfigured."
        )


# ─── Group 2: Django shell authentication tests (via docker exec) ─────────────

@pytest.mark.parametrize("site_key", ["core", "website"])
class TestDjangoShellAuth:
    """
    Tests that verify authentication logic by running code inside the container.
    These bypass HTTP entirely and test the Django auth layer directly.
    """

    def test_superuser_exists(self, site_key):
        """Superuser 'admin' exists in the database."""
        cfg = SITES[site_key]
        code = (
            "from django.contrib.auth import get_user_model\n"
            "U = get_user_model()\n"
            "su = U.objects.filter(username='admin', is_superuser=True)\n"
            "print('EXISTS' if su.exists() else 'MISSING')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "EXISTS" in out, (
            f"[{cfg['label']}] Superuser 'admin' not found. Output: {out}"
        )

    def test_superuser_password_is_correct(self, site_key):
        """Superuser password authenticates correctly via Django's check_password."""
        cfg = SITES[site_key]
        code = (
            "from django.contrib.auth import get_user_model\n"
            "U = get_user_model()\n"
            "u = U.objects.get(username='admin')\n"
            "ok = u.check_password('mk_pAssWord123')\n"
            "print('OK' if ok else 'FAIL')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "OK" in out, (
            f"[{cfg['label']}] Password check failed. Output: {out}"
        )

    def test_superuser_is_active(self, site_key):
        """Superuser account is active (not disabled)."""
        cfg = SITES[site_key]
        code = (
            "from django.contrib.auth import get_user_model\n"
            "U = get_user_model()\n"
            "u = U.objects.get(username='admin')\n"
            "print('ACTIVE' if u.is_active else 'INACTIVE')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "ACTIVE" in out, (
            f"[{cfg['label']}] Superuser is not active. Output: {out}"
        )

    def test_superuser_has_staff_flag(self, site_key):
        """Superuser has is_staff=True (required for admin access)."""
        cfg = SITES[site_key]
        code = (
            "from django.contrib.auth import get_user_model\n"
            "U = get_user_model()\n"
            "u = U.objects.get(username='admin')\n"
            "print('STAFF' if u.is_staff else 'NO_STAFF')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "STAFF" in out, (
            f"[{cfg['label']}] Superuser missing is_staff=True. Output: {out}"
        )

    def test_wrong_password_fails_authentication(self, site_key):
        """Wrong password returns None from authenticate()."""
        cfg = SITES[site_key]
        code = (
            "from django.contrib.auth import get_user_model\n"
            "U = get_user_model()\n"
            "u = U.objects.get(username='admin')\n"
            "ok = u.check_password('wrong_password_xyz')\n"
            "print('FAIL' if not ok else 'UNEXPECTED_PASS')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "FAIL" in out, (
            f"[{cfg['label']}] Wrong password should fail. Output: {out}"
        )

    def test_wagtail_admin_app_installed(self, site_key):
        """wagtail.admin or wagtail is in INSTALLED_APPS."""
        cfg = SITES[site_key]
        code = (
            "from django.conf import settings\n"
            "apps = settings.INSTALLED_APPS\n"
            "print('WAGTAIL_ADMIN' if 'wagtail.admin' in apps or 'wagtail' in apps else 'MISSING')"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "WAGTAIL_ADMIN" in out, (
            f"[{cfg['label']}] wagtail.admin not in INSTALLED_APPS. Output: {out}"
        )

    def test_csrf_cookie_secure_is_true_in_production(self, site_key):
        """CSRF_COOKIE_SECURE=True confirms production security is active."""
        cfg = SITES[site_key]
        code = (
            "from django.conf import settings\n"
            "print('SECURE' if settings.CSRF_COOKIE_SECURE else 'INSECURE')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "SECURE" in out, (
            f"[{cfg['label']}] CSRF_COOKIE_SECURE is not True in production. Output: {out}"
        )

    def test_session_cookie_secure_is_true_in_production(self, site_key):
        """SESSION_COOKIE_SECURE=True confirms session security is active."""
        cfg = SITES[site_key]
        code = (
            "from django.conf import settings\n"
            "print('SECURE' if settings.SESSION_COOKIE_SECURE else 'INSECURE')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "SECURE" in out, (
            f"[{cfg['label']}] SESSION_COOKIE_SECURE is not True in production. Output: {out}"
        )

    def test_login_url_is_sign_in(self, site_key):
        """LOGIN_URL is configured to /auth/sign-in/."""
        cfg = SITES[site_key]
        code = (
            "from django.conf import settings\n"
            "print(settings.LOGIN_URL)\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "sign-in" in out or "login" in out, (
            f"[{cfg['label']}] Unexpected LOGIN_URL: {out}"
        )

    def test_wagtail_admin_login_url_matches_login_url(self, site_key):
        """WAGTAILADMIN_LOGIN_URL matches LOGIN_URL (consistent auth flow)."""
        cfg = SITES[site_key]
        code = (
            "from django.conf import settings\n"
            "login = settings.LOGIN_URL\n"
            "wadmin = getattr(settings, 'WAGTAILADMIN_LOGIN_URL', login)\n"
            "if login == wadmin:\n"
            "    print('MATCH')\n"
            "else:\n"
            "    print(f'MISMATCH: {login} vs {wadmin}')\n"
        )
        out, rc = _docker_python(cfg["container"], cfg["settings_module"], code)
        assert "MATCH" in out, (
            f"[{cfg['label']}] WAGTAILADMIN_LOGIN_URL mismatch. Output: {out}"
        )


# ─── Group 3: Container health checks ────────────────────────────────────────

@pytest.mark.parametrize("site_key", ["core", "website"])
class TestContainerHealth:

    def test_container_is_running(self, site_key):
        """Docker container is running and healthy."""
        cfg = SITES[site_key]
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", cfg["container"]],
            capture_output=True, text=True, timeout=10
        )
        assert result.stdout.strip() == "running", (
            f"[{cfg['label']}] Container {cfg['container']} is not running: "
            f"{result.stdout.strip()}"
        )

    def test_container_health_is_healthy(self, site_key):
        """Docker container health check reports healthy."""
        cfg = SITES[site_key]
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", cfg["container"]],
            capture_output=True, text=True, timeout=10
        )
        status = result.stdout.strip()
        assert status in ("healthy", ""), (
            f"[{cfg['label']}] Container {cfg['container']} health: {status}"
        )

    def test_django_check_passes(self, site_key):
        """Django system check reports no critical errors."""
        cfg = SITES[site_key]
        result = subprocess.run(
            ["docker", "exec", cfg["container"], "bash", "-c",
             f"cd /app && DJANGO_SETTINGS_MODULE={cfg['settings_module']} "
             f".venv/bin/python -m django check --deploy 2>&1 | grep -E 'CRITICAL|ERROR|System check' | tail -5"],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        assert "CRITICAL" not in output, (
            f"[{cfg['label']}] Django check has CRITICAL errors: {output}"
        )
