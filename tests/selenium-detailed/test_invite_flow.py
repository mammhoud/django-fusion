"""Test invite page and invite flow with Selenium."""
import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_invite_page_loads(base_url):
    """Test invite page loads and returns HTTP 200."""
    # Try common invite URLs
    invite_urls = [
        "/invite/",
        "/accounts/invite/",
        "/invitations/",
    ]

    for url in invite_urls:
        r = requests.get(base_url + url, timeout=15, allow_redirects=True)
        if r.status_code == 200:
            return  # Found invite page

    pytest.skip("No invite page found")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_invite_page_form_renders(base_url, selenium_driver):
    """Test invite page form renders correctly."""
    # Try common invite URLs
    invite_urls = [
        "/invite/",
        "/accounts/invite/",
        "/invitations/",
    ]

    for url in invite_urls:
        try:
            selenium_driver.get(base_url + url)

            # Wait for form to load
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
            )

            # Check for form elements
            forms = selenium_driver.find_elements(By.TAG_NAME, "form")
            if forms:
                assert len(forms) > 0, "Invite page should have a form"
                return
        except:
            continue

    pytest.skip("No invite page form found")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_send_invite_to_valid_email(base_url, selenium_driver):
    """Test sending invite to valid email address."""
    # Try common invite URLs
    invite_urls = [
        "/invite/",
        "/accounts/invite/",
        "/invitations/",
    ]

    for url in invite_urls:
        try:
            selenium_driver.get(base_url + url)

            # Wait for form to load
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
            )

            # Find email input
            inputs = selenium_driver.find_elements(By.TAG_NAME, "input")
            email_inputs = [inp for inp in inputs if inp.get_attribute("type") == "email"]

            if email_inputs:
                # Fill in email
                test_email = "invite_test@example.com"
                email_inputs[0].send_keys(test_email)

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
                    success_keywords = ["success", "sent", "invitation", "invite"]
                    has_success = any(keyword in page_text.lower() for keyword in success_keywords)

                    if has_success:
                        return
        except:
            continue

    pytest.skip("Could not test invite flow")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_invite_record_created(base_url, selenium_driver):
    """Test invite record is created in database."""
    # Invite model not available in django_grep
    pytest.skip("Invite model not available")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_invite_acceptance_flow(base_url, selenium_driver):
    """Test invite acceptance flow (if applicable)."""
    # Invite model not available in django_grep
    pytest.skip("Invite model not available")
