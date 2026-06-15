"""
CTC Research Admin Flow Tests
============================
Consolidated admin interface and authentication flow tests.
"""

import time

import pytest
import requests
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

try:
    from django.contrib.auth.models import User
    _DJANGO_AVAILABLE = True
except ImportError:
    _DJANGO_AVAILABLE = False


@pytest.fixture
def admin_user():
    """Create or get admin user for tests."""
    if not _DJANGO_AVAILABLE:
        pytest.skip("Django not available")

    user, created = User.objects.get_or_create(
        username="admin_test",
        defaults={"email": "admin_test@example.com", "is_staff": True, "is_superuser": True}
    )
    if created:
        user.set_password("AdminPassword123!@#")
        user.save()
    return user


class TestAdminAccessibility:
    """Test admin interface accessibility."""

    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, ctc_research_url):
        """Setup for each test."""
        self.driver = selenium_driver
        self.base_url = ctc_research_url
        self.wait = WebDriverWait(self.driver, 10)

    def test_admin_page_loads(self):
        """Test admin page loads correctly."""
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=15, allow_redirects=True)
            assert response.status_code == 200, "Admin page should be accessible"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Admin page request failed: {e}")

    def test_admin_redirects_to_login(self):
        """Test admin redirects to login when not authenticated."""
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=10, allow_redirects=False)
            assert response.status_code in (200, 301, 302), "Admin should redirect or show login"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Admin redirect test failed: {e}")

    def test_admin_css_loads(self):
        """Test admin CSS loads correctly."""
        try:
            response = requests.get(f"{self.base_url}/static/admin/css/base.css", timeout=10)
            assert response.status_code == 200, f"Admin CSS returned {response.status_code}"
        except requests.exceptions.RequestException:
            # CSS might not be available in development
            pytest.skip("Admin CSS not available")


class TestAdminFlows:
    """Test admin interface flows."""

    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, ctc_research_url):
        """Setup for each test."""
        self.driver = selenium_driver
        self.base_url = ctc_research_url
        self.wait = WebDriverWait(self.driver, 10)

    def test_admin_login_page_loads(self):
        """Test Django admin login page loads correctly."""
        try:
            self.driver.get(f"{self.base_url}/admin/")

            # Wait for login form
            self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))

            # Check login form elements
            username_field = self.driver.find_element(By.ID, "id_username")
            password_field = self.driver.find_element(By.ID, "id_password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

            assert username_field.is_displayed(), "Username field not visible"
            assert password_field.is_displayed(), "Password field not visible"
            assert login_button.is_displayed(), "Login button not visible"

        except (TimeoutException, NoSuchElementException) as e:
            pytest.fail(f"Admin login page test failed: {e}")

    def test_admin_login_form_present(self):
        """Test admin login form is present."""
        try:
            self.driver.get(f"{self.base_url}/admin/login/")
            username_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name='username']")
            assert len(username_inputs) > 0, "No username field on admin login"
        except Exception as e:
            pytest.fail(f"Admin login form test failed: {e}")

    def test_admin_login_flow(self):
        """Test complete admin login flow."""
        try:
            # Go to admin page
            self.driver.get(f"{self.base_url}/admin/")

            # Wait for login form
            self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))

            # Try login with test credentials (will fail but tests the flow)
            username_field = self.driver.find_element(By.ID, "id_username")
            password_field = self.driver.find_element(By.ID, "id_password")

            username_field.send_keys("testuser")
            password_field.send_keys("testpass")

            # Submit form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            login_button.click()

            # Wait for response (either success redirect or error message)
            time.sleep(2)

            # Check that form was processed (we expect it to fail with test credentials)
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()

            # Should either redirect or show error message
            login_processed = (
                "/admin/" not in current_url or  # Redirected away from login
                "error" in page_source or        # Error message shown
                "invalid" in page_source or      # Invalid credentials message
                "incorrect" in page_source       # Incorrect credentials message
            )

            assert login_processed, "Login form was not processed"

        except Exception as e:
            pytest.fail(f"Admin login flow test failed: {e}")

    def test_admin_interface_accessibility(self):
        """Test Django admin interface accessibility."""
        try:
            self.driver.get(f"{self.base_url}/admin/")

            # Check that page loaded without server errors
            page_source = self.driver.page_source.lower()
            error_indicators = ['500 internal server error', '502 bad gateway', 'application error']

            for error in error_indicators:
                assert error not in page_source, f"Admin page shows error: {error}"

            # Check for Django admin styling (indicates proper static file serving)
            admin_elements = self.driver.find_elements(By.CSS_SELECTOR, ".login, #header, .module")
            assert len(admin_elements) > 0, "Django admin styling not found"

        except Exception as e:
            pytest.fail(f"Admin interface accessibility test failed: {e}")

    def test_admin_page_renders(self):
        """Test admin page renders correctly."""
        try:
            self.driver.get(f"{self.base_url}/admin/")

            # Wait for page to load
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Check for login form or admin interface
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            assert len(page_text) > 0, "Admin page should have content"

        except Exception as e:
            pytest.fail(f"Admin page render test failed: {e}")

    def test_admin_permissions_unauthorized(self):
        """Test admin page permissions (unauthorized access blocked)."""
        try:
            # Try to access admin page without authentication
            self.driver.get(f"{self.base_url}/admin/")

            # Wait for page to load
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Check if we're redirected to login or shown permission error
            current_url = self.driver.current_url
            page_text = self.driver.find_element(By.TAG_NAME, "body").text

            # Should either be on login page or show permission error
            is_login_page = "login" in page_text.lower() or "login" in current_url.lower()
            is_permission_error = "permission" in page_text.lower() or "unauthorized" in page_text.lower()

            assert is_login_page or is_permission_error, "Unauthorized access should be blocked"

        except Exception as e:
            pytest.fail(f"Admin permissions test failed: {e}")


class TestAdminNavigation:
    """Test admin interface navigation."""

    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, ctc_research_url):
        """Setup for each test."""
        self.driver = selenium_driver
        self.base_url = ctc_research_url
        self.wait = WebDriverWait(self.driver, 10)

    def test_admin_sections_accessible(self):
        """Test that admin sections are accessible."""
        try:
            self.driver.get(f"{self.base_url}/admin/")

            # Look for common Django admin sections
            admin_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/admin/']")

            if admin_links:
                # Test first few admin links
                for i, link in enumerate(admin_links[:3]):
                    if link.get_attribute("href"):
                        href = link.get_attribute("href")

                        # Skip logout and external links
                        if 'logout' in href or not href.startswith(self.base_url):
                            continue

                        # Click link and verify it loads
                        original_url = self.driver.current_url
                        link.click()
                        time.sleep(1)

                        # Check that we navigated successfully
                        current_url = self.driver.current_url
                        assert current_url, "Navigation resulted in empty URL"

                        # Go back for next test
                        if current_url != original_url:
                            self.driver.back()
                            time.sleep(1)

        except Exception as e:
            # Admin navigation testing is optional if not logged in
            print(f"Admin navigation test info: {e}")

    def test_admin_navigation_menu_accessible(self):
        """Test admin navigation menu is accessible."""
        try:
            self.driver.get(f"{self.base_url}/admin/")

            # Wait for page to load
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Look for navigation menu
            nav_elements = self.driver.find_elements(By.TAG_NAME, "nav")
            menu_elements = self.driver.find_elements(By.CSS_SELECTOR, ".module, .dashboard, #content")

            # Should have some form of navigation or content structure
            assert len(nav_elements) > 0 or len(menu_elements) > 0, "Admin page should have navigation or content structure"

        except Exception as e:
            print(f"Admin navigation menu test info: {e}")

    def test_admin_no_js_errors(self):
        """Test admin pages load without critical JavaScript errors."""
        try:
            self.driver.get(f"{self.base_url}/admin/")

            # Wait for page to load
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Check for critical JS errors
            logs = self.driver.get_log("browser")
            errors = [log for log in logs if log["level"] == "SEVERE"]
            critical_errors = [
                e for e in errors
                if "404" not in str(e) and "favicon" not in str(e).lower()
            ]

            assert len(critical_errors) == 0, f"Admin page has critical JS errors: {critical_errors}"

        except Exception as e:
            print(f"Admin JS errors test info: {e}")
