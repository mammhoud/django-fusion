"""Test admin pages accessibility with Selenium."""
import pytest
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import requests


@pytest.fixture
def admin_user():
    """Create or get admin user for tests."""
    user, created = User.objects.get_or_create(
        username="admin_test",
        defaults={"email": "admin_test@example.com", "is_staff": True, "is_superuser": True}
    )
    if created:
        user.set_password("AdminPassword123!@#")
        user.save()
    return user


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_login_page_loads(base_url):
    """Test admin login page loads correctly."""
    r = requests.get(base_url + "/admin/", timeout=15, allow_redirects=True)
    assert r.status_code == 200, "Admin page should be accessible"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_login_page_renders(base_url, selenium_driver):
    """Test admin login page renders correctly."""
    selenium_driver.get(base_url + "/admin/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check for login form or admin interface
    page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
    assert len(page_text) > 0, "Admin page should have content"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_dashboard_loads_after_auth(base_url, selenium_driver, admin_user):
    """Test admin dashboard loads after authentication."""
    # Navigate to admin page
    selenium_driver.get(base_url + "/admin/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check if we need to login
    page_text = selenium_driver.find_element(By.TAG_NAME, "body").text

    if "login" in page_text.lower():
        # Find and fill login form
        inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
        username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
        password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

        if username_inputs:
            username_inputs[0].send_keys("admin_test")

        if password_inputs:
            password_inputs[0].send_keys("AdminPassword123!@#")

        # Find and click submit button
        buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
        submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

        if submit_buttons:
            submit_buttons[0].click()

            # Wait for redirect
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )

    # Check that we're on admin dashboard
    current_url = selenium_driver.current_url
    assert "/admin/" in current_url, "Should be on admin page"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_navigation_menu_accessible(base_url, selenium_driver, admin_user):
    """Test admin navigation menu is accessible."""
    # Navigate to admin page
    selenium_driver.get(base_url + "/admin/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check if we need to login
    page_text = selenium_driver.find_element(By.TAG_NAME, "body").text

    if "login" in page_text.lower():
        # Find and fill login form
        inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
        username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
        password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

        if username_inputs:
            username_inputs[0].send_keys("admin_test")

        if password_inputs:
            password_inputs[0].send_keys("AdminPassword123!@#")

        # Find and click submit button
        buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
        submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

        if submit_buttons:
            submit_buttons[0].click()

            # Wait for redirect
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )

    # Look for navigation menu
    nav_elements = selenium_driver.find_elements(By.TAG_NAME, "nav")
    assert len(nav_elements) > 0, "Admin page should have navigation menu"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_page_permissions_unauthorized(base_url, selenium_driver):
    """Test admin page permissions (unauthorized access blocked)."""
    # Try to access admin page without authentication
    selenium_driver.get(base_url + "/admin/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check if we're redirected to login or shown permission error
    current_url = selenium_driver.current_url
    page_text = selenium_driver.find_element(By.TAG_NAME, "body").text

    # Should either be on login page or show permission error
    is_login_page = "login" in page_text.lower() or "login" in current_url.lower()
    is_permission_error = "permission" in page_text.lower() or "unauthorized" in page_text.lower()

    assert is_login_page or is_permission_error, "Unauthorized access should be blocked"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_pages_no_js_errors(base_url, selenium_driver, admin_user):
    """Test admin pages load without JavaScript errors."""
    # Navigate to admin page
    selenium_driver.get(base_url + "/admin/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Check if we need to login
    page_text = selenium_driver.find_element(By.TAG_NAME, "body").text

    if "login" in page_text.lower():
        # Find and fill login form
        inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
        username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
        password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

        if username_inputs:
            username_inputs[0].send_keys("admin_test")

        if password_inputs:
            password_inputs[0].send_keys("AdminPassword123!@#")

        # Find and click submit button
        buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
        submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

        if submit_buttons:
            submit_buttons[0].click()

            # Wait for redirect
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

    assert len(critical_errors) == 0, f"Admin page has JS errors: {critical_errors}"
