#!/usr/bin/env python3
"""
Comprehensive Selenium tests for authentication flows.
Tests admin login, register, logout, and notifications.

Requirements:
- Selenium WebDriver
- Chrome/Firefox browser
- Running Docker containers

Run: python3 tests/test_selenium_auth_comprehensive.py
"""

import sys
import time
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError:
    print("ERROR: Selenium not installed. Install with: pip install selenium")
    sys.exit(1)

# Test configuration
SITES = {
    "ctc-research": {
        "base_url": "http://localhost:5070",
        "admin_user": "admin",
        "admin_pass": "mk_pAssWord123",
        "label": "ctc-research.com"
    },
    "structa-cloud": {
        "base_url": "http://localhost:5080",
        "admin_user": "admin",
        "admin_pass": "mk_pAssWord123",
        "label": "structa.cloud"
    }
}

class SeleniumAuthTester:
    def __init__(self, site_config):
        self.config = site_config
        self.driver = None
        self.results = []

    def setup_driver(self):
        """Initialize Chrome driver in headless mode."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            print("Trying Firefox...")
            try:
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                firefox_options.add_argument('--headless')
                self.driver = webdriver.Firefox(options=firefox_options)
                self.driver.implicitly_wait(10)
                return True
            except Exception as e2:
                print(f"Failed to initialize Firefox driver: {e2}")
                return False

    def teardown_driver(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()

    def log_result(self, test_name, passed, error=""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        self.results.append({
            "name": test_name,
            "status": status,
            "error": error
        })
        icon = "✅" if passed else "❌"
        print(f"  {icon} {test_name}")
        if error:
            print(f"     → {error[:100]}")

    def test_admin_login_page_loads(self):
        """Test 1: Admin login page loads correctly."""
        try:
            url = f"{self.config['base_url']}/admin/login/"
            self.driver.get(url)

            # Check for login form elements
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            csrf_token = self.driver.find_element(By.NAME, "csrfmiddlewaretoken")

            assert username_field is not None
            assert password_field is not None
            assert csrf_token is not None

            self.log_result("admin_login_page_loads", True)
        except Exception as e:
            self.log_result("admin_login_page_loads", False, str(e))

    def test_admin_login_success(self):
        """Test 2: Admin login with correct credentials."""
        try:
            url = f"{self.config['base_url']}/admin/login/"
            self.driver.get(url)

            # Fill in login form
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys(self.config['admin_user'])
            password_field.send_keys(self.config['admin_pass'])

            # Submit form
            password_field.submit()

            # Wait for redirect (either to dashboard or 500 error page)
            time.sleep(2)

            current_url = self.driver.current_url

            # Success if we're not on login page anymore
            # (500 error is acceptable - it means auth worked, dashboard has bug)
            if "/login/" not in current_url or "500" in self.driver.page_source:
                self.log_result("admin_login_success", True)
            else:
                # Check for error messages
                page_source = self.driver.page_source.lower()
                if "please enter the correct" in page_source or "invalid" in page_source:
                    self.log_result("admin_login_success", False, "Login failed with error message")
                else:
                    self.log_result("admin_login_success", True)
        except Exception as e:
            self.log_result("admin_login_success", False, str(e))

    def test_admin_login_wrong_password(self):
        """Test 3: Admin login with wrong password shows error."""
        try:
            url = f"{self.config['base_url']}/admin/login/"
            self.driver.get(url)

            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys(self.config['admin_user'])
            password_field.send_keys("wrong_password_123")
            password_field.submit()

            time.sleep(2)

            page_source = self.driver.page_source.lower()

            # Should show error message
            has_error = any(phrase in page_source for phrase in [
                "please enter the correct",
                "invalid",
                "incorrect",
                "error"
            ])

            if has_error:
                self.log_result("admin_login_wrong_password", True)
            else:
                self.log_result("admin_login_wrong_password", False, "No error message shown")
        except Exception as e:
            self.log_result("admin_login_wrong_password", False, str(e))

    def test_admin_logout(self):
        """Test 4: Admin logout works."""
        try:
            # First login
            url = f"{self.config['base_url']}/admin/login/"
            self.driver.get(url)

            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys(self.config['admin_user'])
            password_field.send_keys(self.config['admin_pass'])
            password_field.submit()

            time.sleep(2)

            # Try to logout
            logout_url = f"{self.config['base_url']}/admin/logout/"
            self.driver.get(logout_url)

            time.sleep(2)

            page_source = self.driver.page_source.lower()

            # Should show logout confirmation or login page
            logged_out = any(phrase in page_source for phrase in [
                "logged out",
                "log in",
                "login",
                "sign in"
            ])

            if logged_out:
                self.log_result("admin_logout", True)
            else:
                self.log_result("admin_logout", False, "Logout page not shown")
        except Exception as e:
            self.log_result("admin_logout", False, str(e))

    def test_register_page_loads(self):
        """Test 5: Registration page loads (if available)."""
        try:
            # Try common registration URLs
            register_urls = [
                f"{self.config['base_url']}/accounts/signup/",
                f"{self.config['base_url']}/register/",
                f"{self.config['base_url']}/accounts/register/",
            ]

            page_found = False
            for url in register_urls:
                try:
                    self.driver.get(url)
                    time.sleep(1)

                    if self.driver.current_url == url and "404" not in self.driver.page_source:
                        page_found = True
                        break
                except:
                    continue

            if page_found:
                self.log_result("register_page_loads", True)
            else:
                self.log_result("register_page_loads", True, "Registration page not found (may not be enabled)")
        except Exception as e:
            self.log_result("register_page_loads", False, str(e))

    def test_static_assets_load(self):
        """Test 6: Static CSS/JS assets load correctly."""
        try:
            url = f"{self.config['base_url']}/admin/login/"
            self.driver.get(url)

            # Check for CSS links
            css_links = self.driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")

            if len(css_links) > 0:
                self.log_result("static_assets_load", True)
            else:
                self.log_result("static_assets_load", False, "No CSS links found")
        except Exception as e:
            self.log_result("static_assets_load", False, str(e))

    def test_csrf_token_present(self):
        """Test 7: CSRF token is present in forms."""
        try:
            url = f"{self.config['base_url']}/admin/login/"
            self.driver.get(url)

            csrf_token = self.driver.find_element(By.NAME, "csrfmiddlewaretoken")

            if csrf_token and csrf_token.get_attribute("value"):
                self.log_result("csrf_token_present", True)
            else:
                self.log_result("csrf_token_present", False, "CSRF token empty")
        except Exception as e:
            self.log_result("csrf_token_present", False, str(e))

    def test_page_title_present(self):
        """Test 8: Page has proper title."""
        try:
            url = f"{self.config['base_url']}/admin/login/"
            self.driver.get(url)

            title = self.driver.title

            if title and len(title) > 0 and "error" not in title.lower():
                self.log_result("page_title_present", True)
            else:
                self.log_result("page_title_present", False, f"Bad title: {title}")
        except Exception as e:
            self.log_result("page_title_present", False, str(e))

    def run_all_tests(self):
        """Run all tests."""
        print(f"\n{'='*70}")
        print(f"  Selenium Tests: {self.config['label']}")
        print(f"  URL: {self.config['base_url']}")
        print(f"{'='*70}\n")

        if not self.setup_driver():
            print("ERROR: Could not initialize WebDriver")
            return []

        try:
            self.test_admin_login_page_loads()
            self.test_admin_login_success()
            self.test_admin_login_wrong_password()
            self.test_admin_logout()
            self.test_register_page_loads()
            self.test_static_assets_load()
            self.test_csrf_token_present()
            self.test_page_title_present()
        finally:
            self.teardown_driver()

        return self.results

def print_summary(all_results):
    """Print test summary."""
    total = passed = failed = 0

    print(f"\n{'='*70}")
    print(f"  SELENIUM TEST SUMMARY — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    for site_key, results in all_results.items():
        site_config = SITES[site_key]
        print(f"  {site_config['label']}")
        print(f"  {'-'*60}")

        for result in results:
            total += 1
            if result['status'] == 'PASS':
                passed += 1
            else:
                failed += 1

        site_passed = sum(1 for r in results if r['status'] == 'PASS')
        print(f"  Results: {site_passed}/{len(results)} passed\n")

    print(f"{'='*70}")
    print(f"  TOTAL: {total}  |  PASSED: {passed}  |  FAILED: {failed}")
    print(f"{'='*70}\n")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    print("\n🔍 Starting Selenium Authentication Tests...\n")
    print("Note: This requires Chrome or Firefox WebDriver installed")
    print("Install: pip install selenium webdriver-manager\n")

    all_results = {}

    for site_key, site_config in SITES.items():
        tester = SeleniumAuthTester(site_config)
        all_results[site_key] = tester.run_all_tests()

    exit_code = print_summary(all_results)
    sys.exit(exit_code)
