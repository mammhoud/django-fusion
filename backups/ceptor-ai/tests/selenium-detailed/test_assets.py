"""Test asset loading and verification with Selenium."""
import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_css_files_load_without_404(base_url, selenium_driver):
    """Verify all CSS files load without 404 errors."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Find all CSS links
    css_links = selenium_driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")

    for link in css_links:
        href = link.get_attribute("href")
        if href:
            # Make request to CSS file
            r = requests.get(href, timeout=10, allow_redirects=True)
            assert r.status_code == 200, f"CSS file {href} returned {r.status_code}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_javascript_files_load_without_404(base_url, selenium_driver):
    """Verify all JavaScript files load without 404 errors."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Find all script tags
    scripts = selenium_driver.find_elements(By.TAG_NAME, "script")

    for script in scripts:
        src = script.get_attribute("src")
        if src:
            # Make request to JS file
            r = requests.get(src, timeout=10, allow_redirects=True)
            assert r.status_code == 200, f"JS file {src} returned {r.status_code}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_images_load_without_404(base_url, selenium_driver):
    """Verify all images load without 404 errors."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Find all images
    images = selenium_driver.find_elements(By.TAG_NAME, "img")

    for img in images[:10]:  # Test first 10 images to avoid timeout
        src = img.get_attribute("src")
        if src and not src.startswith("data:"):
            # Make request to image file
            r = requests.get(src, timeout=10, allow_redirects=True)
            assert r.status_code == 200, f"Image {src} returned {r.status_code}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_no_console_errors_related_to_missing_assets(base_url, selenium_driver):
    """Verify no console errors related to missing assets."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check browser console for 404 errors
    logs = selenium_driver.get_log("browser")

    # Filter for 404 errors (excluding favicon which is common)
    asset_404_errors = [
        log for log in logs
        if "404" in str(log) and "favicon" not in str(log).lower()
    ]

    assert len(asset_404_errors) == 0, f"Found 404 errors for assets: {asset_404_errors}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_css_content_type_correct(base_url, selenium_driver):
    """Verify CSS files have correct content-type."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Find all CSS links
    css_links = selenium_driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")

    for link in css_links:
        href = link.get_attribute("href")
        if href:
            # Make request to CSS file
            r = requests.get(href, timeout=10, allow_redirects=True)
            content_type = r.headers.get("content-type", "")
            assert "text/css" in content_type or "css" in content_type.lower(), \
                f"CSS file {href} has incorrect content-type: {content_type}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_javascript_content_type_correct(base_url, selenium_driver):
    """Verify JavaScript files have correct content-type."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Find all script tags
    scripts = selenium_driver.find_elements(By.TAG_NAME, "script")

    for script in scripts:
        src = script.get_attribute("src")
        if src:
            # Make request to JS file
            r = requests.get(src, timeout=10, allow_redirects=True)
            content_type = r.headers.get("content-type", "")
            assert "javascript" in content_type.lower() or "application" in content_type.lower(), \
                f"JS file {src} has incorrect content-type: {content_type}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_images_content_type_correct(base_url, selenium_driver):
    """Verify images have correct content-type."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Find all images
    images = selenium_driver.find_elements(By.TAG_NAME, "img")

    for img in images[:5]:  # Test first 5 images
        src = img.get_attribute("src")
        if src and not src.startswith("data:"):
            # Make request to image file
            r = requests.get(src, timeout=10, allow_redirects=True)
            content_type = r.headers.get("content-type", "")
            assert "image" in content_type.lower(), \
                f"Image {src} has incorrect content-type: {content_type}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_assets_load_with_correct_status_codes(base_url, selenium_driver):
    """Verify all assets load with correct HTTP status codes."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Collect all asset URLs
    asset_urls = []

    # CSS files
    css_links = selenium_driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
    for link in css_links:
        href = link.get_attribute("href")
        if href:
            asset_urls.append(href)

    # JS files
    scripts = selenium_driver.find_elements(By.TAG_NAME, "script")
    for script in scripts:
        src = script.get_attribute("src")
        if src:
            asset_urls.append(src)

    # Images
    images = selenium_driver.find_elements(By.TAG_NAME, "img")
    for img in images[:5]:
        src = img.get_attribute("src")
        if src and not src.startswith("data:"):
            asset_urls.append(src)

    # Test all assets
    for url in asset_urls:
        r = requests.get(url, timeout=10, allow_redirects=True)
        assert r.status_code in [200, 304], f"Asset {url} returned {r.status_code}"
