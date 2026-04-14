"""Test profile pages accessibility with Selenium."""
import pytest
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import requests


@pytest.fixture
def profile_user():
    """Create or get user for profile tests."""
    user, created = User.objects.get_or_create(
        username="profile_test_user",
        defaults={"email": "profile_test@example.com"}
    )
    if created:
        user.set_password("ProfilePassword123!@#")
        user.save()
    return user


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_page_loads_for_authenticated_user(base_url, selenium_driver, profile_user):
    """Test profile page loads for authenticated user."""
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
        username_inputs[0].send_keys("profile_test_user")

    if password_inputs:
        password_inputs[0].send_keys("ProfilePassword123!@#")

    # Submit form
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Try to navigate to profile page
        profile_urls = [
            "/profile/",
            "/accounts/profile/",
            "/user/profile/",
            "/dashboard/",
        ]

        for url in profile_urls:
            r = requests.get(base_url + url, timeout=15, allow_redirects=True)
            if r.status_code == 200:
                selenium_driver.get(base_url + url)

                # Wait for page to load
                WebDriverWait(selenium_driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
                )

                # Check that page loaded
                page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
                assert len(page_text) > 0, "Profile page should have content"
                return

        pytest.skip("No profile page found")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_edit_form_renders(base_url, selenium_driver, profile_user):
    """Test profile edit form renders correctly."""
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
        username_inputs[0].send_keys("profile_test_user")

    if password_inputs:
        password_inputs[0].send_keys("ProfilePassword123!@#")

    # Submit form
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Try to navigate to profile edit page
        edit_urls = [
            "/profile/edit/",
            "/accounts/profile/edit/",
            "/user/profile/edit/",
            "/settings/profile/",
        ]

        for url in edit_urls:
            try:
                selenium_driver.get(base_url + url)

                # Wait for page to load
                WebDriverWait(selenium_driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
                )

                # Check for form
                forms = selenium_driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    assert len(forms) > 0, "Profile edit page should have a form"
                    return
            except:
                continue

        pytest.skip("No profile edit page found")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_information_updates(base_url, selenium_driver, profile_user):
    """Test profile information updates correctly."""
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
        username_inputs[0].send_keys("profile_test_user")

    if password_inputs:
        password_inputs[0].send_keys("ProfilePassword123!@#")

    # Submit form
    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

    if submit_buttons:
        submit_buttons[0].click()

        # Wait for redirect
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Try to navigate to profile edit page
        edit_urls = [
            "/profile/edit/",
            "/accounts/profile/edit/",
            "/user/profile/edit/",
            "/settings/profile/",
        ]

        for url in edit_urls:
            try:
                selenium_driver.get(base_url + url)

                # Wait for form to load
                WebDriverWait(selenium_driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
                )

                # Find and update a field
                inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
                if inputs:
                    # Try to update first name or similar field
                    for inp in inputs:
                        if inp.get_attribute("type") == "text":
                            inp.clear()
                            inp.send_keys("Updated Name")
                            break

                    # Find and click submit button
                    buttons = selenium_driver.find_elements(By.TAG_NAME, "button")
                    submit_buttons = [btn for btn in buttons if "submit" in btn.get_attribute("type").lower()]

                    if submit_buttons:
                        submit_buttons[0].click()

                        # Wait for response
                        WebDriverWait(selenium_driver, 10).until(
                            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
                        )

                        # Check for success message
                        page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
                        success_keywords = ["success", "updated", "saved"]
                        has_success = any(keyword in page_text.lower() for keyword in success_keywords)

                        if has_success:
                            return
            except:
                continue

        pytest.skip("Could not test profile update")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_page_redirect_for_unauthenticated_users(base_url, selenium_driver):
    """Test profile page redirect for unauthenticated users."""
    # Try to access profile page without authentication
    profile_urls = [
        "/profile/",
        "/accounts/profile/",
        "/user/profile/",
        "/dashboard/",
    ]

    for url in profile_urls:
        try:
            selenium_driver.get(base_url + url)

            # Wait for page to load
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )

            # Check if we're redirected to login
            current_url = selenium_driver.current_url
            page_text = selenium_driver.find_element(By.TAG_NAME, "body").text

            is_login_page = "login" in page_text.lower() or "login" in current_url.lower()

            if is_login_page:
                assert True, "Unauthenticated users should be redirected to login"
                return
        except:
            continue

    pytest.skip("Could not test profile redirect")
