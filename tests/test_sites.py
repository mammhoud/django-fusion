"""
Full integration tests for both websites.
Targets:
  - structa.cloud  → container port 5071  / domain core.structa.cloud
  - ctc-research.com → container port 5070 / domain www.ctc-research.com

Run locally:
  pytest tests/test_sites.py -v

Run against live domains:
  USE_LIVE_DOMAINS=1 pytest tests/test_sites.py -v
"""
import os

import pytest
import requests

# ── URL configuration ────────────────────────────────────────────────────────
USE_LIVE = os.environ.get("USE_LIVE_DOMAINS", "0") == "1"

STRUCTA_LOCAL  = "http://localhost:5071"
CTC_LOCAL      = "http://localhost:5070"
STRUCTA_DOMAIN = "https://core.structa.cloud"
CTC_DOMAIN     = "https://www.ctc-research.com"

STRUCTA_URL = STRUCTA_DOMAIN if USE_LIVE else STRUCTA_LOCAL
CTC_URL     = CTC_DOMAIN     if USE_LIVE else CTC_LOCAL

TIMEOUT = int(os.environ.get("TEST_TIMEOUT", "10"))

# ── Helpers ──────────────────────────────────────────────────────────────────

def get(url, **kw):
    kw.setdefault("timeout", TIMEOUT)
    kw.setdefault("allow_redirects", True)
    kw.setdefault("verify", False)
    return requests.get(url, **kw)


def url_ok(url):
    """Return True if URL responds with 2xx or 3xx."""
    try:
        r = get(url)
        return r.status_code < 400
    except requests.RequestException:
        return False


# ── structa.cloud tests ──────────────────────────────────────────────────────

class TestStructaCloud:

    def test_health_endpoint(self):
        r = get(f"{STRUCTA_URL}/health/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"

    def test_health_returns_json(self):
        r = get(f"{STRUCTA_URL}/health/")
        assert "application/json" in r.headers.get("content-type", "")

    def test_root_responds(self):
        r = get(f"{STRUCTA_URL}/")
        assert r.status_code < 500, f"Root returned {r.status_code}"

    def test_admin_login_page(self):
        r = get(f"{STRUCTA_URL}/django-admin/login/")
        assert r.status_code == 200

    def test_wagtail_admin_redirects(self):
        r = get(f"{STRUCTA_URL}/admin/", allow_redirects=False)
        # Should redirect to login or return 200
        assert r.status_code in (200, 301, 302)

    def test_set_language_url(self):
        """Language switching URL registered by configure_common_urls."""
        r = get(f"{STRUCTA_URL}/set-language/", allow_redirects=False)
        assert r.status_code in (200, 302, 405)  # 405 = GET not allowed (POST only)

    def test_sitemap_xml(self):
        r = get(f"{STRUCTA_URL}/sitemap.xml")
        assert r.status_code in (200, 404)  # 404 ok if no pages yet

    def test_robots_txt(self):
        r = get(f"{STRUCTA_URL}/robots.txt")
        assert r.status_code in (200, 404)

    def test_auth_login_page(self):
        r = get(f"{STRUCTA_URL}/auth/login/")
        assert r.status_code in (200, 301, 302)

    def test_auth_register_page(self):
        r = get(f"{STRUCTA_URL}/auth/register/")
        assert r.status_code in (200, 301, 302)

    def test_no_debug_in_production(self):
        """500 page should not expose Django debug info."""
        r = get(f"{STRUCTA_URL}/this-path-does-not-exist-xyz/")
        assert "Traceback" not in r.text or r.status_code != 500

    @pytest.mark.skipif(not USE_LIVE, reason="Live domain test only")
    def test_live_domain_ssl(self):
        r = requests.get(STRUCTA_DOMAIN, timeout=TIMEOUT, verify=True)
        assert r.status_code < 500

    @pytest.mark.skipif(not USE_LIVE, reason="Live domain test only")
    def test_live_domain_redirects_to_https(self):
        r = requests.get(
            STRUCTA_DOMAIN.replace("https://", "http://"),
            timeout=TIMEOUT, allow_redirects=False, verify=False
        )
        assert r.status_code in (301, 302)
        assert "https" in r.headers.get("location", "")


# ── ctc-research.com tests ───────────────────────────────────────────────────

class TestCTCResearch:

    def test_health_endpoint(self):
        r = get(f"{CTC_URL}/health/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"

    def test_health_returns_json(self):
        r = get(f"{CTC_URL}/health/")
        assert "application/json" in r.headers.get("content-type", "")

    def test_root_responds(self):
        r = get(f"{CTC_URL}/")
        assert r.status_code < 500, f"Root returned {r.status_code}"

    def test_admin_login_page(self):
        r = get(f"{CTC_URL}/django-admin/login/")
        assert r.status_code == 200

    def test_wagtail_admin_redirects(self):
        r = get(f"{CTC_URL}/admin/", allow_redirects=False)
        assert r.status_code in (200, 301, 302)

    def test_set_language_url(self):
        r = get(f"{CTC_URL}/set-language/", allow_redirects=False)
        assert r.status_code in (200, 302, 405)

    def test_sitemap_xml(self):
        r = get(f"{CTC_URL}/sitemap.xml")
        assert r.status_code in (200, 404)

    def test_robots_txt(self):
        r = get(f"{CTC_URL}/robots.txt")
        assert r.status_code in (200, 404)

    def test_auth_login_page(self):
        r = get(f"{CTC_URL}/auth/login/")
        assert r.status_code in (200, 301, 302)

    def test_auth_register_page(self):
        r = get(f"{CTC_URL}/auth/register/")
        assert r.status_code in (200, 301, 302)

    def test_no_debug_in_production(self):
        r = get(f"{CTC_URL}/this-path-does-not-exist-xyz/")
        assert "Traceback" not in r.text or r.status_code != 500

    @pytest.mark.skipif(not USE_LIVE, reason="Live domain test only")
    def test_live_domain_ssl(self):
        r = requests.get(CTC_DOMAIN, timeout=TIMEOUT, verify=True)
        assert r.status_code < 500

    @pytest.mark.skipif(not USE_LIVE, reason="Live domain test only")
    def test_live_domain_redirects_to_https(self):
        r = requests.get(
            CTC_DOMAIN.replace("https://", "http://"),
            timeout=TIMEOUT, allow_redirects=False, verify=False
        )
        assert r.status_code in (301, 302)
        assert "https" in r.headers.get("location", "")


# ── Cross-site tests ─────────────────────────────────────────────────────────

class TestBothSites:

    @pytest.mark.parametrize("url", [
        f"{STRUCTA_URL}/health/",
        f"{CTC_URL}/health/",
    ])
    def test_health_endpoints_up(self, url):
        r = get(url)
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    @pytest.mark.parametrize("site,url", [
        ("structa", STRUCTA_URL),
        ("ctc", CTC_URL),
    ])
    def test_no_server_error_on_root(self, site, url):
        r = get(url)
        assert r.status_code != 500, f"{site} root returned 500"

    @pytest.mark.parametrize("site,url", [
        ("structa", f"{STRUCTA_URL}/django-admin/login/"),
        ("ctc",     f"{CTC_URL}/django-admin/login/"),
    ])
    def test_admin_accessible(self, site, url):
        r = get(url)
        assert r.status_code == 200, f"{site} admin login returned {r.status_code}"
        assert "csrfmiddlewaretoken" in r.text or "login" in r.text.lower()
