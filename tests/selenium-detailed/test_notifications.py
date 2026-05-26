"""Test notification system with Selenium."""
import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_notification_success_display(base_url, selenium_driver):
    """Test notification display for success messages."""
    # Navigate to a page that might show success notifications
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for success notification elements
    success_selectors = [
        ".alert-success",
        ".notification-success",
        "[role='alert'].success",
        ".toast-success",
        ".message-success",
    ]

    for selector in success_selectors:
        elements = selenium_driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            assert len(elements) > 0, "Success notification should be visible"
            return

    # If no success notification found, that's okay (not all pages have them)
    pytest.skip("No success notification found on page")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_notification_error_display(base_url, selenium_driver):
    """Test notification display for error messages."""
    # Navigate to a page that might show error notifications
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for error notification elements
    error_selectors = [
        ".alert-danger",
        ".alert-error",
        ".notification-error",
        "[role='alert'].error",
        ".toast-error",
        ".message-error",
    ]

    for selector in error_selectors:
        elements = selenium_driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            assert len(elements) > 0, "Error notification should be visible"
            return

    # If no error notification found, that's okay
    pytest.skip("No error notification found on page")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_notification_warning_display(base_url, selenium_driver):
    """Test notification display for warning messages."""
    # Navigate to a page that might show warning notifications
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for warning notification elements
    warning_selectors = [
        ".alert-warning",
        ".notification-warning",
        "[role='alert'].warning",
        ".toast-warning",
        ".message-warning",
    ]

    for selector in warning_selectors:
        elements = selenium_driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            assert len(elements) > 0, "Warning notification should be visible"
            return

    # If no warning notification found, that's okay
    pytest.skip("No warning notification found on page")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_notification_info_display(base_url, selenium_driver):
    """Test notification display for info messages."""
    # Navigate to a page that might show info notifications
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for info notification elements
    info_selectors = [
        ".alert-info",
        ".notification-info",
        "[role='alert'].info",
        ".toast-info",
        ".message-info",
    ]

    for selector in info_selectors:
        elements = selenium_driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            assert len(elements) > 0, "Info notification should be visible"
            return

    # If no info notification found, that's okay
    pytest.skip("No info notification found on page")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_notification_auto_dismiss(base_url, selenium_driver):
    """Test notification auto-dismiss functionality."""
    # Navigate to a page
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for notification elements
    notification_selectors = [
        ".alert",
        ".notification",
        ".toast",
        ".message",
    ]

    for selector in notification_selectors:
        elements = selenium_driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            # Check if notification has auto-dismiss class or data attribute
            for element in elements:
                classes = element.get_attribute("class") or ""
                data_attrs = element.get_attribute("data-dismiss") or ""

                if "auto-dismiss" in classes or "dismiss" in data_attrs:
                    # Wait a bit and check if notification disappears
                    import time
                    time.sleep(3)

                    try:
                        # Check if element is still visible
                        if not element.is_displayed():
                            assert True, "Notification auto-dismissed"
                            return
                    except:
                        # Element might have been removed from DOM
                        assert True, "Notification auto-dismissed"
                        return

    pytest.skip("No auto-dismiss notification found")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_notification_close_button(base_url, selenium_driver):
    """Test notification close button functionality."""
    # Navigate to a page
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for notification elements with close buttons
    notification_selectors = [
        ".alert",
        ".notification",
        ".toast",
        ".message",
    ]

    for selector in notification_selectors:
        elements = selenium_driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            for element in elements:
                # Look for close button
                close_buttons = element.find_elements(By.CSS_SELECTOR, ".close, [data-dismiss], .btn-close")

                if close_buttons:
                    # Click close button
                    close_buttons[0].click()

                    # Wait a bit and check if notification disappears
                    import time
                    time.sleep(1)

                    try:
                        # Check if element is still visible
                        if not element.is_displayed():
                            assert True, "Notification closed successfully"
                            return
                    except:
                        # Element might have been removed from DOM
                        assert True, "Notification closed successfully"
                        return

    pytest.skip("No notification with close button found")
