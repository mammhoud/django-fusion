"""Selenium / HTTP smoke tests for profile blog management (create, edit, delete)."""
import os

import pytest

import requests


def _server_running(base_url):
    """Return True if the dev server is reachable."""
    try:
        requests.get(base_url + "/blog/", timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        return False


# ---------------------------------------------------------------------------
# HTTP-level tests – unauthenticated access should redirect to login
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_blog_list_redirects_unauthenticated(base_url):
    """/profile/blog/ redirects to login when not authenticated (302 or 401)."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/profile/blog/", timeout=15, allow_redirects=False)
    assert r.status_code in (302, 301, 401), (
        f"Expected redirect/auth challenge, got {r.status_code}"
    )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_blog_create_redirects_unauthenticated(base_url):
    """/profile/blog/create/ redirects to login when not authenticated."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/profile/blog/create/", timeout=15, allow_redirects=False)
    assert r.status_code in (302, 301, 401), (
        f"Expected redirect/auth challenge, got {r.status_code}"
    )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_blog_edit_redirects_unauthenticated(base_url):
    """/profile/blog/999/edit/ redirects to login when not authenticated."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/profile/blog/999/edit/", timeout=15, allow_redirects=False)
    assert r.status_code in (302, 301, 401, 404), (
        f"Expected redirect/auth challenge or 404, got {r.status_code}"
    )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_blog_delete_redirects_unauthenticated(base_url):
    """/profile/blog/999/delete/ redirects to login when not authenticated."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/profile/blog/999/delete/", timeout=15, allow_redirects=False)
    assert r.status_code in (302, 301, 401, 404), (
        f"Expected redirect/auth challenge or 404, got {r.status_code}"
    )


# ---------------------------------------------------------------------------
# Selenium (browser) tests – unauthenticated redirects
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_blog_list_redirects_to_login_selenium(base_url, selenium_driver):
    """Visiting /profile/blog/ unauthenticated lands on a login page."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    selenium_driver.get(base_url + "/profile/blog/")
    current = selenium_driver.current_url
    assert "login" in current or "signin" in current, (
        f"Expected redirect to login page, but ended up at: {current}"
    )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_blog_create_redirects_to_login_selenium(base_url, selenium_driver):
    """Visiting /profile/blog/create/ unauthenticated lands on a login page."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    selenium_driver.get(base_url + "/profile/blog/create/")
    current = selenium_driver.current_url
    assert "login" in current or "signin" in current, (
        f"Expected redirect to login page, but ended up at: {current}"
    )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_login_form_present_on_redirect(base_url, selenium_driver):
    """The login redirect page contains a login form."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + "/profile/blog/")
    # Should have been redirected to login; look for a form with a password field
    password_inputs = selenium_driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
    assert password_inputs, "No password input found on the login redirect page"
    assert password_inputs[0].is_displayed()


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_profile_blog_list_loads_after_login(base_url, selenium_driver):
    """After logging in, /profile/blog/ loads with blog management content."""
    username = os.getenv("SELENIUM_TEST_USER")
    password = os.getenv("SELENIUM_TEST_PASS")
    if not username or not password:
        pytest.skip("SELENIUM_TEST_USER / SELENIUM_TEST_PASS not set")
    if not _server_running(base_url):
        pytest.skip("Server not running")

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    # Navigate to the profile blog list — will redirect to login
    selenium_driver.get(base_url + "/profile/blog/")

    # Fill in credentials
    wait = WebDriverWait(selenium_driver, 10)
    user_field = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[name='username'], input[name='login']"))
    )
    user_field.clear()
    user_field.send_keys(username)

    pass_field = selenium_driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    pass_field.clear()
    pass_field.send_keys(password)

    # Submit the form
    pass_field.submit()

    # After login, should land on or be redirected to the profile blog list
    wait.until(lambda d: "login" not in d.current_url and "signin" not in d.current_url)

    # Verify we're on a blog management page (URL or page content)
    current = selenium_driver.current_url
    page_source = selenium_driver.page_source
    assert "/profile/blog" in current or "blog" in page_source.lower(), (
        f"Expected blog management content after login, got URL: {current}"
    )
