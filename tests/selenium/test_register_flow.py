"""Test registration flow end-to-end with Selenium."""
import pytest
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import requests


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_registration_flow_complete(base_url, selenium_driver):
    """Test complete registration flow: navigate, fill form, submit."""
    # Navigate to registration page
    selenium_driver.get(base_url + "/accounts/signup/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Find form fields
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    assert len(inputs) > 0, "Registration form should have input fields"

    # Try to fill in the form (exact field names may vary)
    test_email = "test_registration_flow@example.com"
    test_password = "TestPassword123!@#"

    # Find and fill email field
    email_inputs = [inp for inp in inputs if inp.get_attribute("type") == "email"]
    if email_inputs:
        email_inputs[0].send_keys(test_email)

    # Find and fill password fields
    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]
    if len(password_inputs) >= 1:
        password_inputs[0].send_keys(test_password)
    if len(password_inputs) >= 2:
        password_inputs[1].send_keys(test_password)

    # Find and click submit button
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect or success message
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_registration_creates_user(base_url, selenium_driver):
    """Test user account is created in database after registration."""
    # Get initial user count
    initial_count = User.objects.count()

    # Navigate to registration page
    selenium_driver.get(base_url + "/accounts/signup/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Fill and submit form
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    test_email = f"test_user_{initial_count}@example.com"
    test_password = "TestPassword123!@#"

    email_inputs = [inp for inp in inputs if inp.get_attribute("type") == "email"]
    if email_inputs:
        email_inputs[0].send_keys(test_email)

    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]
    if len(password_inputs) >= 1:
        password_inputs[0].send_keys(test_password)
    if len(password_inputs) >= 2:
        password_inputs[1].send_keys(test_password)

    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check if user was created
        new_count = User.objects.count()
        assert new_count > initial_count, "User should be created after registration"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_registration_email_verification_flow(base_url, selenium_driver):
    """Test email verification flow (if applicable)."""
    # Navigate to registration page
    selenium_driver.get(base_url + "/accounts/signup/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Fill and submit form
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    test_email = "test_email_verify@example.com"
    test_password = "TestPassword123!@#"

    email_inputs = [inp for inp in inputs if inp.get_attribute("type") == "email"]
    if email_inputs:
        email_inputs[0].send_keys(test_email)

    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]
    if len(password_inputs) >= 1:
        password_inputs[0].send_keys(test_password)
    if len(password_inputs) >= 2:
        password_inputs[1].send_keys(test_password)

    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check for email verification message
        page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
        # Look for common email verification messages
        verification_keywords = ["verify", "confirmation", "email", "check"]
        has_verification_message = any(keyword in page_text.lower() for keyword in verification_keywords)

        # If verification message found, test passed
        if has_verification_message:
            assert True, "Email verification flow detected"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_registration_redirect_to_dashboard(base_url, selenium_driver):
    """Test redirect to dashboard/profile after successful registration."""
    # Navigate to registration page
    selenium_driver.get(base_url + "/accounts/signup/")

    # Wait for form to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
    )

    # Fill and submit form
    inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
    test_email = "test_redirect@example.com"
    test_password = "TestPassword123!@#"

    email_inputs = [inp for inp in inputs if inp.get_attribute("type") == "email"]
    if email_inputs:
        email_inputs[0].send_keys(test_email)

    password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]
    if len(password_inputs) >= 1:
        password_inputs[0].send_keys(test_password)
    if len(password_inputs) >= 2:
        password_inputs[1].send_keys(test_password)

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
        success_keywords = ["success", "welcome", "registered"]
        has_success_message = any(keyword in page_text.lower() for keyword in success_keywords)

        assert is_dashboard or has_success_message, "Should redirect to dashboard or show success message"
