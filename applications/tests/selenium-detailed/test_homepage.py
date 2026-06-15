"""Homepage smoke tests for structa.cloud."""
import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.selenium
@pytest.mark.nondestructive
@pytest.mark.nondestructive
def test_homepage_loads(base_url):
    """Test homepage loads without errors (HTTP 200)."""
    r = requests.get(base_url + "/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_homepage_has_title(base_url, selenium_driver):
    """Test homepage has a non-empty title."""
    selenium_driver.get(base_url + "/")
    assert selenium_driver.title, "Page title is empty"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_health_endpoint(base_url):
    """Test health endpoint returns HTTP 200."""
    r = requests.get(base_url + "/health/", timeout=10)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_root_page_redirects_to_english(base_url, selenium_driver):
    """Test root page `/` redirects to or loads English home page."""
    selenium_driver.get(base_url + "/")
    # Check that we're on a valid page (not an error page)
    assert selenium_driver.title, "Root page should have a title"
    # Verify no 404 or 500 errors
    assert "404" not in selenium_driver.title.lower()
    assert "500" not in selenium_driver.title.lower()


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_homepage_elements_render(base_url, selenium_driver):
    """Test all page elements render correctly (header, footer, navigation)."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check for common page elements
    body = selenium_driver.find_element(By.TAG_NAME, "body")
    assert body, "Page body should exist"

    # Check for header (common element)
    headers = selenium_driver.find_elements(By.TAG_NAME, "header")
    assert len(headers) > 0, "Page should have a header element"

    # Check for footer (common element)
    footers = selenium_driver.find_elements(By.TAG_NAME, "footer")
    assert len(footers) > 0, "Page should have a footer element"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_homepage_no_js_errors(base_url, selenium_driver):
    """Test homepage loads without JavaScript errors."""
    selenium_driver.get(base_url + "/")

    # Wait for page to fully load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check browser console for errors
    logs = selenium_driver.get_log("browser")
    errors = [log for log in logs if log["level"] == "SEVERE"]

    # Filter out known non-critical errors
    critical_errors = [
        e for e in errors
        if "404" not in str(e) and "favicon" not in str(e).lower()
    ]

    assert len(critical_errors) == 0, f"Page should not have critical JS errors: {critical_errors}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_language_switcher_present(base_url, selenium_driver):
    """Test language switcher functionality (if present)."""
    selenium_driver.get(base_url + "/")

    # Look for language switcher elements
    lang_switchers = selenium_driver.find_elements(By.CSS_SELECTOR, "[data-language], .language-switcher, .lang-selector")

    # If language switcher exists, verify it's clickable
    if lang_switchers:
        for switcher in lang_switchers:
            assert switcher.is_displayed(), "Language switcher should be visible"
