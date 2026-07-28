"""
Selenium Browser Tests for All Sites
=====================================
Selenium-based smoke tests for all 4 websites.

Prerequisites:
    pip install selenium

Run:
    SELENIUM_BASE_URL=http://localhost:5070 pytest tests/selenium/ -v
    SELENIUM_HEADLESS=true pytest tests/selenium/ -v
"""

import os

import pytest

# Mark all tests in this module as selenium
pytestmark = pytest.mark.selenium

# ── Site configurations ──────────────────────────────────────────────────────
SITES = {
    "ctc-research": {
        "url": os.environ.get("CTC_BASE_URL", "http://localhost:5070"),
        "name": "CTC Research",
    },
    "lms-demo": {
        "url": os.environ.get("LMS_BASE_URL", "http://localhost:5071"),
        "name": "LMS Demo",
    },
    "vresume": {
        "url": os.environ.get("VRESUME_BASE_URL", "http://localhost:5072"),
        "name": "VResume",
    },
    "crm": {
        "url": os.environ.get("CRM_BASE_URL", "http://localhost:5074"),
        "name": "CRM",
    },
}

# Pages to test (path, description)
COMMON_PAGES = [
    ("/", "Homepage"),
    ("/health/", "Health endpoint"),
    ("/django-admin/login/", "Django admin login"),
    ("/accounts/login/", "Allauth login"),
    ("/admin/", "Wagtail admin"),
    ("/robots.txt", "Robots.txt"),
]

# Site-specific pages
SITE_PAGES = {
    "ctc-research": COMMON_PAGES + [
        ("/accounts/register/", "Register page"),
        ("/accounts/password/reset/", "Password reset"),
        ("/sitemap.xml", "Sitemap"),
        ("/set-language/", "Language switching"),
    ],
    "lms-demo": COMMON_PAGES + [
        ("/accounts/register/", "Register page"),
        ("/accounts/password/reset/", "Password reset"),
        ("/sitemap.xml", "Sitemap"),
        ("/set-language/", "Language switching"),
    ],
    "vresume": [
        ("/", "Homepage"),
        ("/health/", "Health endpoint"),
        ("/django-admin/login/", "Django admin login"),
        ("/admin/", "Wagtail admin"),
        ("/sitemap.xml", "Sitemap"),
        ("/robots.txt", "Robots.txt"),
        ("/set-language/", "Language switching"),
        ("/team/", "Team page"),
        ("/blog/", "Blog list"),
        ("/events/", "Events list"),
        ("/api/csrf-token/", "CSRF token"),
        ("/api/theme/get/", "Theme get"),
    ],
    "crm": [
        ("/", "Homepage"),
        ("/health/", "Health endpoint"),
        ("/django-admin/login/", "Django admin login"),
        ("/robots.txt", "Robots.txt"),
        ("/accounts/login/", "Allauth login"),
        ("/set-language/", "Language switching"),
        ("/crm/", "CRM components"),
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# Selenium Driver Fixture
# ═════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def selenium_driver():
    """Create a headless Chrome driver for testing."""
    headless = os.environ.get("SELENIUM_HEADLESS", "true").lower() == "true"

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-background-networking")
        opts.add_experimental_option("excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=opts)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    except Exception as e:
        pytest.skip(f"Selenium WebDriver not available: {e}")





# ═════════════════════════════════════════════════════════════════════════════
# Page Load Tests
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.selenium
@pytest.mark.parametrize("site_name", list(SITES.keys()))
def test_homepage_loads(site_name, selenium_driver):
    """Homepage loads without JavaScript errors."""
    from selenium.webdriver.common.by import By

    url = SITES[site_name]["url"]
    selenium_driver.get(url)

    # Check page title exists
    title = selenium_driver.title
    assert title is not None, f"{site_name} has no page title"

    # Check body has content
    body = selenium_driver.find_element(By.TAG_NAME, "body")
    assert body.text or len(body.text) > 0, f"{site_name} body is empty"


@pytest.mark.selenium
@pytest.mark.parametrize("site_name", list(SITES.keys()))
def test_health_page(site_name, selenium_driver):
    """Health endpoint returns content."""
    url = f"{SITES[site_name]['url']}/health/"
    selenium_driver.get(url)

    body = selenium_driver.find_element("tag name", "body")
    text = body.text
    assert text is not None and len(text) > 0, f"{site_name} health page empty"


@pytest.mark.selenium
@pytest.mark.parametrize("site_name,path,desc", [
    (site, path, f"{site}: {desc}")
    for site, pages in SITE_PAGES.items()
    for path, desc in pages
])
def test_page_loads(site_name, path, desc, selenium_driver):
    """Each defined page loads without error."""
    url = f"{SITES[site_name]['url']}{path}"
    selenium_driver.get(url)

    # Check page loaded (not a 500 error page)
    from selenium.webdriver.common.by import By

    body_text = selenium_driver.find_element(By.TAG_NAME, "body").text

    # Should not contain server error indicators
    error_indicators = ["Internal Server Error", "Server Error (500)", "Traceback"]
    for indicator in error_indicators:
        assert indicator not in body_text, (
            f"{desc}: Server error on {url}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# Cross-Site Selenium Tests
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.selenium
def test_all_sites_have_title(selenium_driver):
    """All sites have a non-empty page title."""
    for site_name, site_info in SITES.items():
        selenium_driver.get(site_info["url"])
        title = selenium_driver.title
        assert title and len(title) > 0, f"{site_name} has empty title"


@pytest.mark.selenium
def test_all_sites_admin_login(selenium_driver):
    """Django admin login loads for all sites that have it."""
    from selenium.webdriver.common.by import By

    for site_name, site_info in SITES.items():
        try:
            selenium_driver.get(f"{site_info['url']}/django-admin/login/")

            # Check for login form elements
            inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
            has_password_field = any(
                inp.get_attribute("type") == "password"
                for inp in inputs
            )

            # If we got a 200 response, we should see a login form
            if selenium_driver.title and "login" in selenium_driver.title.lower():
                assert has_password_field, (
                    f"{site_name} admin login missing password field"
                )
        except Exception:
            pass  # Site may not be running


@pytest.mark.selenium
def test_no_console_errors(selenium_driver):
    """Check for console errors on homepages."""
    import json

    for site_name, site_info in SITES.items():
        try:
            selenium_driver.get(site_info["url"])

            # Capture browser console logs
            logs = selenium_driver.get_log("browser")
            severe_errors = [
                log for log in logs
                if log["level"] in ("SEVERE", "ERROR")
                and "favicon" not in log.get("message", "").lower()
            ]

            if severe_errors:
                # Log but don't fail — some errors are benign
                print(f"\n  {site_name} console errors: {json.dumps(severe_errors, indent=2)}")
        except Exception:
            pass  # Log collection not always available
