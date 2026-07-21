"""
Selenium tests for admin login page.

Verifies:
  - Login page renders with Unfold theme
  - Correct credentials redirect to dashboard
  - Invalid credentials show error message
"""

from __future__ import annotations

from typing import Generator

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import ADMIN_URL, ADMIN_EMAIL, ADMIN_PASSWORD


class TestAdminLogin:
    """Admin login page tests."""

    def test_login_page_renders(self, driver) -> None:
        """Login page loads with Unfold-branded form."""
        driver.get(ADMIN_URL)
        wait = WebDriverWait(driver, 10)
        title = wait.until(EC.presence_of_element_located(
            (By.TAG_NAME, "h1")
        ))
        assert title.is_displayed()
        # Should show Unfold theme (dark background expected)
        body = driver.find_element(By.TAG_NAME, "body")
        bg_class = body.get_attribute("class") or ""
        assert "unfold" in driver.page_source.lower() or "dark" in bg_class.lower()

    def test_successful_login_redirects_to_dashboard(self, driver, admin_login) -> None:
        """Logging in redirects from /admin/login/ to /admin/."""
        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: "dashboard" in d.current_url.lower() or "admin/" in d.current_url)
        current = driver.current_url
        assert "login" not in current, f"Still on login page: {current}"

    def test_login_shows_admin_header(self, driver, admin_login) -> None:
        """Dashboard header is visible after login."""
        wait = WebDriverWait(driver, 10)
        header = wait.until(EC.presence_of_element_located(
            (By.TAG_NAME, "h1")
        ))
        assert header.is_displayed()

    def test_invalid_login_shows_error(self, driver) -> None:
        """Invalid credentials display an error message."""
        driver.get(ADMIN_URL)
        wait = WebDriverWait(driver, 10)
        user_field = wait.until(EC.presence_of_element_located(
            (By.NAME, "username")
        ))
        pwd_field = driver.find_element(By.NAME, "password")
        submit_btn = driver.find_element(By.XPATH, '//input[@type="submit"]')

        user_field.clear()
        user_field.send_keys("wrong@email.com")
        pwd_field.clear()
        pwd_field.send_keys("wrongpassword")
        submit_btn.click()

        # Should see error message
        error = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "errornote")
        ))
        assert error.is_displayed()
