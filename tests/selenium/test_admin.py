"""Admin page smoke tests for structa.cloud."""
import pytest

import requests


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_redirects_to_login(base_url):
    r = requests.get(base_url + "/admin/", timeout=10, allow_redirects=False)
    assert r.status_code in (200, 301, 302)


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_login_form_present(base_url, selenium_driver):
    from selenium.webdriver.common.by import By
    selenium_driver.get(base_url + "/admin/login/")
    assert selenium_driver.find_elements(By.CSS_SELECTOR, "input[name='username']"), \
        "No username field on admin login"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_admin_css_loads(base_url):
    r = requests.get(base_url + "/static/admin/css/base.css", timeout=10)
    assert r.status_code == 200, f"Admin CSS returned {r.status_code}"
