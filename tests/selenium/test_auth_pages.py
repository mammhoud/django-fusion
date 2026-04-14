"""Test authentication pages with Selenium."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import requests


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_page_loads(base_url):
    """Test login page loads and returns HTTP 200."""
    r = requests.get(base_url + "/accounts/login/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_page_form_renders(base_url, selenium_driver):
    """Test login page form renders correctly."""
    selenium_driver.get(base_url + "/accounts/login/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Check for login form elements
    forms = selenium_driver.find_elements(By.TAG_NAME, "form")
    assert len(forms) > 0, "Login page should have a form"

    # Check for username/email field
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    assert len(inputs) > 0, "Login form should have input fields"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_registration_page_loads(base_url):
    """Test registration page loads and returns HTTP 200."""
    r = requests.get(base_url + "/accounts/signup/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_registration_page_form_renders(base_url, selenium_driver):
    """Test registration page form renders correctly."""
    selenium_driver.get(base_url + "/accounts/signup/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Check for registration form elements
    forms = selenium_driver.find_elements(By.TAG_NAME, "form")
    assert len(forms) > 0, "Registration page should have a form"

    # Check for input fields
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    assert len(inputs) > 0, "Registration form should have input fields"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_password_reset_page_loads(base_url):
    """Test password reset page loads and returns HTTP 200."""
    r = requests.get(base_url + "/accounts/password/reset/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_password_reset_page_form_renders(base_url, selenium_driver):
    """Test password reset page form renders correctly."""
    selenium_driver.get(base_url + "/accounts/password/reset/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Check for password reset form
    forms = selenium_driver.find_elements(By.TAG_NAME, "form")
    assert len(forms) > 0, "Password reset page should have a form"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_invite_page_loads(base_url):
    """Test invite page loads (if applicable)."""
    # Try common invite URLs
    invite_urls = [
        "/invite/",
        "/accounts/invite/",
        "/invitations/",
    ]

    for url in invite_urls:
        r = requests.get(base_url + url, timeout=15, allow_redirects=True)
        if r.status_code == 200:
            # Found invite page
            return

    # If no invite page found, skip this test
    pytest.skip("No invite page found")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_auth_pages_no_js_errors(base_url, selenium_driver):
    """Test auth pages load without JavaScript errors."""
    auth_urls = [
        "/accounts/login/",
        "/accounts/signup/",
        "/accounts/password/reset/",
    ]

    for url in auth_urls:
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

        assert len(critical_errors) == 0, f"Auth page {url} has JS errors: {critical_errors}"
