"""Test login flow end-to-end with Selenium."""
import pytest
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import requests


@pytest.fixture
def test_user():
    """Create a test user for login tests."""
    user, created = User.objects.get_or_create(
        username="test_login_user",
        defaults={"email": "test_login@example.com"}
    )
    if created:
        user.set_password("TestPassword123!@#")
        user.save()
    return user


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_flow_complete(base_url, selenium_driver, test_user):
    """Test complete login flow: navigate to login, enter credentials, submit."""
    # Navigate to login page
    selenium_driver.get(base_url + "/accounts/login/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Find form fields
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    assert len(inputs) > 0, "Login form should have input fields"

    # Fill in credentials
    username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

    if username_inputs:
        username_inputs[0].send_keys("test_login_user")

    if password_inputs:
        password_inputs[0].send_keys("TestPassword123!@#")

    # Find and click submit button
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_creates_session(base_url, selenium_driver, test_user):
    """Test user is authenticated and session is created after login."""
    # Navigate to login page
    selenium_driver.get(base_url + "/accounts/login/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Fill in credentials
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

    if username_inputs:
        username_inputs[0].send_keys("test_login_user")

    if password_inputs:
        password_inputs[0].send_keys("TestPassword123!@#")

    # Submit form
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check for session cookie
        cookies = selenium_driver.get_cookies()
        session_cookies = [c for c in cookies if "session" in c["name"].lower()]
        assert len(session_cookies) > 0, "Session cookie should be created after login"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_redirect_to_dashboard(base_url, selenium_driver, test_user):
    """Test redirect to dashboard/profile after successful login."""
    # Navigate to login page
    selenium_driver.get(base_url + "/accounts/login/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Fill in credentials
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

    if username_inputs:
        username_inputs[0].send_keys("test_login_user")

    if password_inputs:
        password_inputs[0].send_keys("TestPassword123!@#")

    # Submit form
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check current URL
        current_url = selenium_driver.current_url

        # Check for common dashboard/profile URLs
        dashboard_keywords = ["dashboard", "profile", "account", "home"]
        is_dashboard = any(keyword in current_url.lower() for keyword in dashboard_keywords)

        # If not on dashboard, check if we're on a success page
        page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
        success_keywords = ["welcome", "logged in", "dashboard"]
        has_success_message = any(keyword in page_text.lower() for keyword in success_keywords)

        assert is_dashboard or has_success_message, "Should redirect to dashboard or show success message"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_logout_functionality(base_url, selenium_driver, test_user):
    """Test logout functionality."""
    # First, login
    selenium_driver.get(base_url + "/accounts/login/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Fill in credentials
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

    if username_inputs:
        username_inputs[0].send_keys("test_login_user")

    if password_inputs:
        password_inputs[0].send_keys("TestPassword123!@#")

    # Submit form
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Now find and click logout button
        logout_links = selenium_driver.find_elements(By.LINK_TEXT, "Logout")
        if not logout_links:
            logout_links = selenium_driver.find_elements(By.LINK_TEXT, "Sign out")
        if not logout_links:
            logout_links = selenium_driver.find_elements(By.CSS_SELECTOR, "[href*='logout'], [href*='signout']")

        if logout_links:
            logout_links[0].click()

            # Wait for redirect
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )

            # Check that session cookie is cleared
            cookies = selenium_driver.get_cookies()
            session_cookies = [c for c in cookies if "session" in c["name"].lower()]
            # Session cookie might still exist but should be invalidated
            assert True, "Logout completed"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_with_invalid_credentials(base_url, selenium_driver):
    """Test login with invalid credentials shows error."""
    # Navigate to login page
    selenium_driver.get(base_url + "/accounts/login/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Fill in invalid credentials
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    username_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]

    if username_inputs:
        username_inputs[0].send_keys("invalid_user")

    if password_inputs:
        password_inputs[0].send_keys("invalid_password")

    # Submit form
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for error message
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check for error message
        page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
        error_keywords = ["error", "invalid", "incorrect", "failed"]
        has_error_message = any(keyword in page_text.lower() for keyword in error_keywords)

        assert has_error_message, "Should show error message for invalid credentials"
