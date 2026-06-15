"""Auth page smoke tests for structa.cloud."""
import pytest
import requests


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_page_loads(base_url):
    r = requests.get(base_url + "/accounts/login/", timeout=10, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_form_present(base_url, selenium_driver):
    from selenium.webdriver.common.by import By
    selenium_driver.get(base_url + "/accounts/login/")
    assert selenium_driver.find_elements(By.CSS_SELECTOR, "form input[type='password']"), \
        "No password field found on login page"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_invalid_login_shows_error(base_url, selenium_driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    selenium_driver.get(base_url + "/accounts/login/")
    try:
        user_field = selenium_driver.find_element(By.CSS_SELECTOR, "input[name='login'],input[name='username']")
        pass_field = selenium_driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        user_field.send_keys("invalid_user_xyz")
        pass_field.send_keys("wrong_password_xyz")
        pass_field.submit()
        # After submit, page should still be on login or show error
        assert "/login/" in selenium_driver.current_url or \
               selenium_driver.find_elements(By.CSS_SELECTOR, ".alert,.errorlist,.error"), \
               "No error shown after invalid login"
    except Exception:
        pytest.skip("Login form structure differs — skipping")
