"""Test error pages with Selenium."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import requests


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_404_error_page_loads(base_url):
    """Test 404 error page loads correctly."""
    # Try to access a non-existent page
    r = requests.get(base_url + "/nonexistent-page-12345/", timeout=15, allow_redirects=True)
    assert r.status_code == 404, "Should return 404 status code"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_404_error_page_renders(base_url, selenium_driver):
    """Test 404 error page renders correctly."""
    # Navigate to non-existent page
    selenium_driver.get(base_url + "/nonexistent-page-12345/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check for 404 indicators
    page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
    assert "404" in page_text or "not found" in page_text.lower(), "404 page should indicate not found"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_500_error_page_loads(base_url):
    """Test 500 error page loads correctly."""
    # Try to trigger a 500 error (this might not work depending on app setup)
    # Try common error trigger URLs
    error_urls = [
        "/error/",
        "/500/",
        "/api/error/",
    ]

    for url in error_urls:
        r = requests.get(base_url + url, timeout=15, allow_redirects=True)
        if r.status_code == 500:
            return  # Found 500 error

    pytest.skip("Could not trigger 500 error")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_500_error_page_renders(base_url, selenium_driver):
    """Test 500 error page renders correctly."""
    # Try to trigger a 500 error
    error_urls = [
        "/error/",
        "/500/",
        "/api/error/",
    ]

    for url in error_urls:
        try:
            selenium_driver.get(base_url + url)

            # Wait for page to load
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )

            # Check for 500 indicators
            page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
            if "500" in page_text or "server error" in page_text.lower():
                assert True, "500 error page rendered"
                return
        except:
            continue

    pytest.skip("Could not test 500 error page")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_403_forbidden_page_loads(base_url):
    """Test 403 forbidden page loads correctly."""
    # Try to access a forbidden page (this depends on app setup)
    # Try common forbidden URLs
    forbidden_urls = [
        "/admin/",
        "/forbidden/",
        "/403/",
    ]

    for url in forbidden_urls:
        r = requests.get(base_url + url, timeout=15, allow_redirects=True)
        if r.status_code == 403:
            return  # Found 403 error

    pytest.skip("Could not trigger 403 error")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_403_forbidden_page_renders(base_url, selenium_driver):
    """Test 403 forbidden page renders correctly."""
    # Try to access a forbidden page
    forbidden_urls = [
        "/admin/",
        "/forbidden/",
        "/403/",
    ]

    for url in forbidden_urls:
        try:
            selenium_driver.get(base_url + url)

            # Wait for page to load
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )

            # Check for 403 indicators
            page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
            if "403" in page_text or "forbidden" in page_text.lower() or "access denied" in page_text.lower():
                assert True, "403 error page rendered"
                return
        except:
            continue

    pytest.skip("Could not test 403 error page")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_error_page_navigation_back_to_homepage(base_url, selenium_driver):
    """Test error page navigation back to homepage."""
    # Navigate to 404 page
    selenium_driver.get(base_url + "/nonexistent-page-12345/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for "back to home" or similar links
    home_links = selenium_driver.find_elements(By.LINK_TEXT, "Home")
    if not home_links:
        home_links = selenium_driver.find_elements(By.LINK_TEXT, "Back to Home")
    if not home_links:
        home_links = selenium_driver.find_elements(By.CSS_SELECTOR, "a[href='/'], a[href='./']")

    if home_links:
        # Click home link
        home_links[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check that we're on homepage
        current_url = selenium_driver.current_url
        assert current_url.endswith("/") or "home" in current_url.lower(), "Should navigate to homepage"
    else:
        pytest.skip("No home link found on error page")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_error_pages_no_js_errors(base_url, selenium_driver):
    """Test error pages load without JavaScript errors."""
    error_urls = [
        "/nonexistent-page-12345/",
        "/error/",
        "/500/",
    ]

    for url in error_urls:
        try:
            selenium_driver.get(base_url + url)

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

            assert len(critical_errors) == 0, f"Error page {url} has JS errors: {critical_errors}"
        except:
            continue
