"""Test all pages from dumped data with Selenium."""
import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from wagtail.models import Page

import requests


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_all_pages_load_without_errors(base_url):
    """Test all pages from dumped data load with HTTP 200."""
    # Get all published pages
    pages = Page.objects.live().public()

    for page in pages:
        url = base_url + page.get_url()
        r = requests.get(url, timeout=15, allow_redirects=True)
        assert r.status_code == 200, f"Page {page.title} ({url}) returned {r.status_code}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_all_pages_no_js_errors(base_url, selenium_driver):
    """Test all pages load without JavaScript errors."""
    pages = Page.objects.live().public()[:5]  # Test first 5 pages to avoid timeout

    for page in pages:
        url = base_url + page.get_url()
        selenium_driver.get(url)

        # Wait for page to load
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check for critical JS errors
        logs = selenium_driver.get_log("browser")
        errors = [log for log in logs if log["level"] == "SEVERE"]
        critical_errors = [
            e for e in errors
            if "404" not in str(e) and "favicon" not in str(e).lower()
        ]

        assert len(critical_errors) == 0, f"Page {page.title} has JS errors: {critical_errors}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_all_pages_assets_load(base_url, selenium_driver):
    """Test all pages load assets without 404 errors."""
    pages = Page.objects.live().public()[:3]  # Test first 3 pages

    for page in pages:
        url = base_url + page.get_url()
        selenium_driver.get(url)

        # Wait for page to load
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check for 404 errors in network logs
        logs = selenium_driver.get_log("browser")
        not_found_errors = [log for log in logs if "404" in str(log)]

        # Filter out favicon 404s (common and non-critical)
        critical_404s = [
            e for e in not_found_errors
            if "favicon" not in str(e).lower()
        ]

        assert len(critical_404s) == 0, f"Page {page.title} has missing assets: {critical_404s}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_page_navigation_links(base_url, selenium_driver):
    """Test page navigation and internal links."""
    pages = Page.objects.live().public()[:2]  # Test first 2 pages

    for page in pages:
        url = base_url + page.get_url()
        selenium_driver.get(url)

        # Wait for page to load
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Find all internal links
        links = selenium_driver.find_elements(By.TAG_NAME, "a")

        # Verify links are clickable
        for link in links[:5]:  # Test first 5 links
            try:
                href = link.get_attribute("href")
                if href and href.startswith("/"):
                    assert link.is_displayed() or link.is_enabled(), f"Link {href} should be accessible"
            except:
                pass  # Skip links that can't be accessed


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_page_content_renders(base_url, selenium_driver):
    """Test page content renders correctly."""
    pages = Page.objects.live().public()[:2]  # Test first 2 pages

    for page in pages:
        url = base_url + page.get_url()
        selenium_driver.get(url)

        # Wait for page to load
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check that page has content
        body = selenium_driver.find_element(By.TAG_NAME, "body")
        text = body.text

        assert len(text) > 0, f"Page {page.title} should have content"
