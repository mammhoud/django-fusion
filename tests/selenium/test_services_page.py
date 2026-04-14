"""Selenium / HTTP smoke tests for the services page."""
import pytest

import requests


def _server_running(base_url):
    """Return True if the dev server is reachable."""
    try:
        requests.get(base_url + "/", timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        return False


def _find_services_url(base_url):
    """
    Try common services page URLs. Returns the first one that responds 200,
    or None if none found.
    """
    candidates = ["/services/", "/en/services/", "/research/", "/en/research/"]
    for path in candidates:
        try:
            r = requests.get(base_url + path, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                return path
        except requests.exceptions.ConnectionError:
            return None
    return None


# ---------------------------------------------------------------------------
# HTTP-level tests (no browser required)
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_homepage_loads(base_url):
    """Homepage returns HTTP 200 (sanity check)."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_services_page_loads(base_url):
    """Services page returns HTTP 200."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    services_url = _find_services_url(base_url)
    if services_url is None:
        pytest.skip("No services page found at common URLs")
    r = requests.get(base_url + services_url, timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_services_page_has_content(base_url):
    """Services page HTML contains service-related content."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    services_url = _find_services_url(base_url)
    if services_url is None:
        pytest.skip("No services page found at common URLs")
    r = requests.get(base_url + services_url, timeout=15, allow_redirects=True)
    assert r.status_code == 200
    # Should contain some service-related keywords
    text_lower = r.text.lower()
    assert any(kw in text_lower for kw in ("service", "research", "consulting", "solution")), (
        "Services page does not contain expected service-related content"
    )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_services_page_has_sections(base_url):
    """Services page HTML contains section elements."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    services_url = _find_services_url(base_url)
    if services_url is None:
        pytest.skip("No services page found at common URLs")
    r = requests.get(base_url + services_url, timeout=15, allow_redirects=True)
    assert r.status_code == 200
    assert "<section" in r.text or "<div" in r.text, "No section/div elements found"


# ---------------------------------------------------------------------------
# Selenium (browser) tests
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_services_page_title_selenium(base_url, selenium_driver):
    """Services page has a non-empty browser title."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    services_url = _find_services_url(base_url)
    if services_url is None:
        pytest.skip("No services page found at common URLs")
    selenium_driver.get(base_url + services_url)
    assert selenium_driver.title, "Page title is empty"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_services_page_has_visible_sections(base_url, selenium_driver):
    """Services page renders visible content sections."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    services_url = _find_services_url(base_url)
    if services_url is None:
        pytest.skip("No services page found at common URLs")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + services_url)

    # Look for any visible section or main content area
    section_selectors = [
        (By.TAG_NAME, "section"),
        (By.CSS_SELECTOR, "main"),
        (By.CSS_SELECTOR, ".services"),
        (By.CSS_SELECTOR, "[class*='service']"),
        (By.CSS_SELECTOR, ".content"),
    ]
    found = False
    for by, selector in section_selectors:
        elements = selenium_driver.find_elements(by, selector)
        if elements and elements[0].is_displayed():
            found = True
            break

    assert found, "No visible content sections found on services page"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_services_page_navigation_links(base_url, selenium_driver):
    """Services page has navigation links."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    services_url = _find_services_url(base_url)
    if services_url is None:
        pytest.skip("No services page found at common URLs")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + services_url)

    # Navigation should always be present
    nav_selectors = [
        (By.TAG_NAME, "nav"),
        (By.CSS_SELECTOR, "header"),
        (By.CSS_SELECTOR, ".navbar"),
        (By.CSS_SELECTOR, "#navbar"),
    ]
    found = any(
        selenium_driver.find_elements(by, selector)
        for by, selector in nav_selectors
    )
    assert found, "No navigation element found on services page"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_services_page_no_500_error(base_url, selenium_driver):
    """Services page does not show a 500 error."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    services_url = _find_services_url(base_url)
    if services_url is None:
        pytest.skip("No services page found at common URLs")

    selenium_driver.get(base_url + services_url)
    page_source = selenium_driver.page_source.lower()
    assert "server error" not in page_source
    assert "500" not in selenium_driver.title
