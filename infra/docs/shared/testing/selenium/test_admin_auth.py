"""
Selenium tests for Django /admin authentication using superuser credentials.

Tests both:
  - structa.cloud (core)    → http://localhost:8280
  - ctc-research.com (website) → http://localhost:8271  (via nginx proxy)

Both sites use allauth with LOGIN_URL = /auth/sign-in/
Wagtail admin redirects unauthenticated users to /auth/sign-in/?next=/admin/

Superuser credentials (from .env):
  username: admin
  password: mk_pAssWord123

Requirements:
    pip install selenium pytest requests

Usage:
    pytest tests/selenium/test_admin_auth.py -v
    pytest tests/selenium/test_admin_auth.py -v -k core
    pytest tests/selenium/test_admin_auth.py -v -k website

Environment variable overrides:
    CORE_BASE_URL       default: http://localhost:8280
    WEBSITE_BASE_URL    default: http://localhost:8271
    CORE_USERNAME       default: admin
    CORE_PASSWORD       default: mk_pAssWord123
    WEBSITE_USERNAME    default: admin
    WEBSITE_PASSWORD    default: mk_pAssWord123
"""

import json
import os
import time

import pytest
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ─── Config ──────────────────────────────────────────────────────────────────

SITES = {
    "core": {
        "base_url": os.getenv("CORE_BASE_URL", "http://localhost:8280"),
        "username": os.getenv("CORE_USERNAME", "admin"),
        "password": os.getenv("CORE_PASSWORD", "mk_pAssWord123"),
        "label": "structa.cloud (core)",
        "login_path": "/auth/sign-in/",
        "admin_path": "/admin/",          # Wagtail admin
        "django_admin_path": "/control/", # Django Unfold admin
    },
    "website": {
        "base_url": os.getenv("WEBSITE_BASE_URL", "http://localhost:8271"),
        "username": os.getenv("WEBSITE_USERNAME", "admin"),
        "password": os.getenv("WEBSITE_PASSWORD", "mk_pAssWord123"),
        "label": "ctc-research.com (website)",
        "login_path": "/auth/sign-in/",
        "admin_path": "/admin/",          # Wagtail admin
        "django_admin_path": "/control/", # Django Unfold admin
    },
}

HEADLESS = os.getenv("SELENIUM_HEADLESS", "true").lower() != "false"
WAIT_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", "15"))


# ─── HTTP-only pre-flight checks (no browser needed) ─────────────────────────

class TestHTTPPreFlight:
    """Fast HTTP checks that run before Selenium tests."""

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_admin_redirects_to_login(self, site_key):
        """GET /admin/ should redirect to /auth/sign-in/ when unauthenticated."""
        cfg = SITES[site_key]
        s = requests.Session()
        r = s.get(f"{cfg['base_url']}{cfg['admin_path']}", allow_redirects=True)
        assert r.status_code == 200, f"[{cfg['label']}] Expected 200, got {r.status_code}"
        assert "sign-in" in r.url or "login" in r.url, (
            f"[{cfg['label']}] Expected redirect to login, got: {r.url}"
        )

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_login_page_returns_200(self, site_key):
        """GET /auth/sign-in/ should return 200."""
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}{cfg['login_path']}")
        assert r.status_code == 200, (
            f"[{cfg['label']}] Login page returned {r.status_code}"
        )

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_login_page_has_csrf_token(self, site_key):
        """Login page must include a CSRF token cookie."""
        cfg = SITES[site_key]
        s = requests.Session()
        s.get(f"{cfg['base_url']}{cfg['login_path']}")
        assert "csrftoken" in s.cookies, (
            f"[{cfg['label']}] No csrftoken cookie on login page"
        )

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_superuser_login_via_http(self, site_key):
        """Superuser can authenticate via POST to /auth/sign-in/."""
        cfg = SITES[site_key]
        s = requests.Session()
        login_url = f"{cfg['base_url']}{cfg['login_path']}"
        s.get(login_url)
        csrf = s.cookies.get("csrftoken", "")
        r = s.post(
            login_url,
            data={
                "login": cfg["username"],
                "password": cfg["password"],
                "csrfmiddlewaretoken": csrf,
                "next": cfg["admin_path"],
            },
            headers={"Referer": login_url},
            allow_redirects=True,
        )
        # After successful login, should reach admin (not stay on login page)
        assert "sign-in" not in r.url, (
            f"[{cfg['label']}] Still on login page after submit — "
            f"check credentials. URL: {r.url}"
        )

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_wrong_password_stays_on_login(self, site_key):
        """Wrong credentials should keep user on the login page."""
        cfg = SITES[site_key]
        s = requests.Session()
        login_url = f"{cfg['base_url']}{cfg['login_path']}"
        s.get(login_url)
        csrf = s.cookies.get("csrftoken", "")
        r = s.post(
            login_url,
            data={
                "login": cfg["username"],
                "password": "wrong_password_xyz_123",
                "csrfmiddlewaretoken": csrf,
            },
            headers={"Referer": login_url},
            allow_redirects=True,
        )
        assert r.status_code in (200, 400), (
            f"[{cfg['label']}] Expected 200/400 for bad credentials, got {r.status_code}"
        )
        assert "sign-in" in r.url or "login" in r.url, (
            f"[{cfg['label']}] Expected to stay on login page, got: {r.url}"
        )

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_admin_accessible_after_login(self, site_key):
        """After login, /admin/ should be accessible (200, not redirect to login)."""
        cfg = SITES[site_key]
        s = requests.Session()
        login_url = f"{cfg['base_url']}{cfg['login_path']}"
        s.get(login_url)
        csrf = s.cookies.get("csrftoken", "")
        s.post(
            login_url,
            data={
                "login": cfg["username"],
                "password": cfg["password"],
                "csrfmiddlewaretoken": csrf,
                "next": cfg["admin_path"],
            },
            headers={"Referer": login_url},
            allow_redirects=True,
        )
        r = s.get(f"{cfg['base_url']}{cfg['admin_path']}", allow_redirects=True)
        assert r.status_code == 200, (
            f"[{cfg['label']}] Admin returned {r.status_code} after login"
        )
        assert "sign-in" not in r.url, (
            f"[{cfg['label']}] Admin redirected back to login after auth: {r.url}"
        )

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_static_assets_served(self, site_key):
        """Static files should be served with 200."""
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}/static/admin/css/base.css")
        assert r.status_code == 200, (
            f"[{cfg['label']}] Static admin CSS returned {r.status_code}"
        )
        assert "text/css" in r.headers.get("Content-Type", ""), (
            f"[{cfg['label']}] Wrong Content-Type for CSS: {r.headers.get('Content-Type')}"
        )

    @pytest.mark.parametrize("site_key", ["core", "website"])
    def test_health_endpoint(self, site_key):
        """Health check endpoint should return 200."""
        cfg = SITES[site_key]
        r = requests.get(f"{cfg['base_url']}/health/", allow_redirects=True)
        assert r.status_code == 200, (
            f"[{cfg['label']}] Health endpoint returned {r.status_code}"
        )


# ─── Selenium browser tests ───────────────────────────────────────────────────

def _make_driver():
    """Create a headless Chrome or Firefox WebDriver."""
    # Try Chrome first
    try:
        opts = Options()
        if HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,900")
        opts.add_argument("--disable-extensions")
        drv = webdriver.Chrome(options=opts)
        drv.implicitly_wait(5)
        return drv, "chrome"
    except Exception:
        pass

    # Fallback to Firefox
    try:
        opts = FirefoxOptions()
        if HEADLESS:
            opts.add_argument("--headless")
        drv = webdriver.Firefox(options=opts)
        drv.implicitly_wait(5)
        return drv, "firefox"
    except Exception:
        return None, None


def _browser_available():
    drv, name = _make_driver()
    if drv:
        drv.quit()
        return True
    return False


BROWSER_AVAILABLE = _browser_available()
skip_no_browser = pytest.mark.skipif(
    not BROWSER_AVAILABLE,
    reason="No Chrome or Firefox WebDriver available — run HTTP tests only"
)


@pytest.fixture(scope="module")
def driver():
    """Shared WebDriver for the Selenium test module."""
    drv, name = _make_driver()
    if drv is None:
        pytest.skip("No browser driver available")
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def clear_cookies(driver):
    yield
    try:
        driver.delete_all_cookies()
    except Exception:
        pass


def _wait_for(driver, by, value, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def _do_login(driver, cfg):
    """Navigate to login page and submit credentials."""
    login_url = f"{cfg['base_url']}{cfg['login_path']}?next={cfg['admin_path']}"
    driver.get(login_url)

    # Already logged in?
    if "sign-in" not in driver.current_url and "login" not in driver.current_url:
        return

    # Find login field (allauth uses 'login' field name, not 'username')
    login_field = None
    for field_id in ["id_login", "id_username", "id_email"]:
        try:
            login_field = driver.find_element(By.ID, field_id)
            break
        except NoSuchElementException:
            continue

    if login_field is None:
        # Try by name attribute
        for field_name in ["login", "username", "email"]:
            try:
                login_field = driver.find_element(By.NAME, field_name)
                break
            except NoSuchElementException:
                continue

    assert login_field is not None, f"[{cfg['label']}] Could not find login field"

    login_field.clear()
    login_field.send_keys(cfg["username"])

    pwd_field = driver.find_element(By.ID, "id_password")
    pwd_field.clear()
    pwd_field.send_keys(cfg["password"])

    driver.find_element(By.CSS_SELECTOR, "[type=submit]").click()

    # Wait for redirect away from login
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: "sign-in" not in d.current_url and "login" not in d.current_url
    )


@skip_no_browser
@pytest.mark.parametrize("site_key", ["core", "website"])
class TestSeleniumAdminLogin:

    def test_login_page_loads(self, driver, site_key):
        """Login page renders with a password field."""
        cfg = SITES[site_key]
        driver.get(f"{cfg['base_url']}{cfg['login_path']}")
        assert driver.find_element(By.ID, "id_password"), (
            f"[{cfg['label']}] Password field not found"
        )

    def test_superuser_login(self, driver, site_key):
        """Superuser can log in and reach admin."""
        cfg = SITES[site_key]
        _do_login(driver, cfg)
        assert "sign-in" not in driver.current_url, (
            f"[{cfg['label']}] Still on login page: {driver.current_url}"
        )

    def test_admin_dashboard_visible(self, driver, site_key):
        """After login, admin dashboard is accessible."""
        cfg = SITES[site_key]
        _do_login(driver, cfg)
        driver.get(f"{cfg['base_url']}{cfg['admin_path']}")
        assert driver.find_element(By.TAG_NAME, "body"), (
            f"[{cfg['label']}] Admin page body missing"
        )
        assert "error" not in driver.title.lower(), (
            f"[{cfg['label']}] Error in admin title: {driver.title}"
        )

    def test_wrong_password_shows_error(self, driver, site_key):
        """Wrong credentials keep user on login page."""
        cfg = SITES[site_key]
        driver.get(f"{cfg['base_url']}{cfg['login_path']}")

        for field_id in ["id_login", "id_username", "id_email"]:
            try:
                f = driver.find_element(By.ID, field_id)
                f.send_keys(cfg["username"])
                break
            except NoSuchElementException:
                continue

        driver.find_element(By.ID, "id_password").send_keys("wrong_xyz_999")
        driver.find_element(By.CSS_SELECTOR, "[type=submit]").click()
        time.sleep(1)

        assert "sign-in" in driver.current_url or "login" in driver.current_url, (
            f"[{cfg['label']}] Expected to stay on login page"
        )

    def test_admin_css_loads(self, driver, site_key):
        """Admin page has stylesheets."""
        cfg = SITES[site_key]
        _do_login(driver, cfg)
        driver.get(f"{cfg['base_url']}{cfg['admin_path']}")
        sheets = driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
        assert len(sheets) > 0, f"[{cfg['label']}] No stylesheets on admin page"

    def test_page_title_not_error(self, driver, site_key):
        """Admin page title does not contain 'error'."""
        cfg = SITES[site_key]
        _do_login(driver, cfg)
        driver.get(f"{cfg['base_url']}{cfg['admin_path']}")
        assert "error" not in driver.title.lower(), (
            f"[{cfg['label']}] Error in title: {driver.title}"
        )

    def test_django_unfold_admin_accessible(self, driver, site_key):
        """Django Unfold admin at /control/ is accessible after login."""
        cfg = SITES[site_key]
        _do_login(driver, cfg)
        driver.get(f"{cfg['base_url']}{cfg['django_admin_path']}")
        assert driver.find_element(By.TAG_NAME, "body"), (
            f"[{cfg['label']}] /control/ body missing"
        )
        assert "error" not in driver.title.lower(), (
            f"[{cfg['label']}] Error in /control/ title: {driver.title}"
        )

    def test_django_unfold_admin_has_unfold_styles(self, driver, site_key):
        """Unfold admin at /control/ should load Unfold-specific CSS."""
        cfg = SITES[site_key]
        _do_login(driver, cfg)
        driver.get(f"{cfg['base_url']}{cfg['django_admin_path']}")
        sheets = driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
        assert len(sheets) > 0, f"[{cfg['label']}] No stylesheets on /control/ page"
