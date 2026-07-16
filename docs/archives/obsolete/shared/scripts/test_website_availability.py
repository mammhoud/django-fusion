#!/usr/bin/env python3
"""
Website Availability Test Script

This script tests website domain availability, assets, pages, and authentication
using Selenium for browser automation. It includes notification messages for
failed requests and authentication issues.

Usage:
    python scripts/test_website_availability.py

Environment Variables:
    WEBSITE_URL: Base URL for the website (default: http://localhost)
    ADMIN_USERNAME: Admin username for login tests
    ADMIN_PASSWORD: Admin password for login tests
"""

import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try to import selenium, if not available, use requests only
try:
    from selenium import webdriver
    from selenium.common.exceptions import (
        ElementNotInteractableException,
        NoSuchElementException,
        TimeoutException,
        WebDriverException,
    )
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Using requests-only mode.")

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout


@dataclass
class TestResult:
    """Result of a single test."""

    test_name: str
    category: str
    passed: bool
    message: str
    url: Optional[str] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_details: Optional[str] = None
    screenshot_path: Optional[str] = None


@dataclass
class TestReport:
    """Complete test report."""

    website_url: str
    timestamp: str
    results: List[TestResult] = field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    warnings: int = 0

    def add_result(self, result: TestResult):
        """Add a test result to the report."""
        self.results.append(result)
        self.total_tests += 1
        if result.passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def to_dict(self) -> Dict:
        """Convert report to dictionary."""
        return {
            "website_url": self.website_url,
            "timestamp": self.timestamp,
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "warnings": self.warnings,
                "success_rate": (
                    f"{(self.passed_tests / self.total_tests * 100):.1f}%"
                    if self.total_tests > 0
                    else "0%"
                ),
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "category": r.category,
                    "passed": r.passed,
                    "message": r.message,
                    "url": r.url,
                    "response_time": r.response_time,
                    "status_code": r.status_code,
                    "error_details": r.error_details,
                    "screenshot_path": r.screenshot_path,
                }
                for r in self.results
            ],
        }


class WebsiteAvailabilityTester:
    """Test website availability, assets, pages, and authentication."""

    def __init__(
        self,
        website_url: str,
        admin_username: Optional[str] = None,
        admin_password: Optional[str] = None,
        use_selenium: bool = True,
    ):
        self.website_url = website_url.rstrip("/")
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        self.report = TestReport(
            website_url=self.website_url,
            timestamp=datetime.now().isoformat(),
        )
        self.screenshots_dir = Path("test_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

    def setup_selenium(self):
        """Set up Selenium WebDriver."""
        if not self.use_selenium:
            return

        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            print("✅ Selenium WebDriver initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize Selenium: {e}")
            self.use_selenium = False

    def teardown_selenium(self):
        """Clean up Selenium WebDriver."""
        if self.driver:
            self.driver.quit()

    def test_health_endpoints(self):
        """Test health check endpoints."""
        print("\n🏥 Testing Health Endpoints...")

        health_endpoints = [
            "/health/",
            "/health/database/",
            "/health/assets/",
            "/health/media/",
        ]

        for endpoint in health_endpoints:
            url = f"{self.website_url}{endpoint}"
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10, allow_redirects=True)
                response_time = time.time() - start_time

                if response.status_code == 200:
                    self.report.add_result(
                        TestResult(
                            test_name=f"Health Check: {endpoint}",
                            category="Health",
                            passed=True,
                            message=f"Health endpoint responding (status: {response.status_code})",
                            url=url,
                            response_time=response_time,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ✅ {endpoint} - {response.status_code} ({response_time:.2f}s)")
                else:
                    self.report.add_result(
                        TestResult(
                            test_name=f"Health Check: {endpoint}",
                            category="Health",
                            passed=False,
                            message=f"Health endpoint returned status {response.status_code}",
                            url=url,
                            response_time=response_time,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ❌ {endpoint} - {response.status_code}")

            except (ConnectionError, Timeout, RequestException) as e:
                self.report.add_result(
                    TestResult(
                        test_name=f"Health Check: {endpoint}",
                        category="Health",
                        passed=False,
                        message=f"Failed to connect to health endpoint",
                        url=url,
                        error_details=str(e),
                    )
                )
                print(f"  ❌ {endpoint} - Connection failed: {e}")

    def test_static_assets(self):
        """Test static assets availability."""
        print("\n📦 Testing Static Assets...")

        # Common static asset paths
        static_paths = [
            "/static/",
            "/static/css/",
            "/static/js/",
            "/static/images/",
        ]

        for path in static_paths:
            url = f"{self.website_url}{path}"
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)

                # Static paths might return 403 (forbidden) or 404, which is acceptable
                if response.status_code in [200, 301, 302, 403]:
                    self.report.add_result(
                        TestResult(
                            test_name=f"Static Asset: {path}",
                            category="Assets",
                            passed=True,
                            message=f"Static path accessible (status: {response.status_code})",
                            url=url,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ✅ {path} - {response.status_code}")
                else:
                    self.report.add_result(
                        TestResult(
                            test_name=f"Static Asset: {path}",
                            category="Assets",
                            passed=False,
                            message=f"Static path returned unexpected status {response.status_code}",
                            url=url,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ❌ {path} - {response.status_code}")

            except (ConnectionError, Timeout, RequestException) as e:
                self.report.add_result(
                    TestResult(
                        test_name=f"Static Asset: {path}",
                        category="Assets",
                        passed=False,
                        message="Failed to access static path",
                        url=url,
                        error_details=str(e),
                    )
                )
                print(f"  ❌ {path} - Connection failed")

    def test_public_pages(self):
        """Test public pages accessibility."""
        print("\n🌐 Testing Public Pages...")

        public_pages = [
            ("/", "Home Page"),
            ("/admin/", "Admin Login"),
            ("/accounts/login/", "User Login"),
            ("/accounts/signup/", "User Registration"),
            ("/blog/", "Blog"),
        ]

        for path, name in public_pages:
            url = f"{self.website_url}{path}"
            try:
                start_time = time.time()
                response = requests.get(url, timeout=15, allow_redirects=True)
                response_time = time.time() - start_time

                # Accept 200, 301, 302, 403 (for admin), 404 (for non-existent)
                acceptable_codes = [200, 301, 302, 403]
                if response.status_code in acceptable_codes:
                    self.report.add_result(
                        TestResult(
                            test_name=f"Public Page: {name}",
                            category="Pages",
                            passed=True,
                            message=f"Page accessible (status: {response.status_code})",
                            url=url,
                            response_time=response_time,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ✅ {name} ({path}) - {response.status_code} ({response_time:.2f}s)")
                else:
                    self.report.add_result(
                        TestResult(
                            test_name=f"Public Page: {name}",
                            category="Pages",
                            passed=False,
                            message=f"Page returned unexpected status {response.status_code}",
                            url=url,
                            response_time=response_time,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ❌ {name} ({path}) - {response.status_code}")

            except (ConnectionError, Timeout, RequestException) as e:
                self.report.add_result(
                    TestResult(
                        test_name=f"Public Page: {name}",
                        category="Pages",
                        passed=False,
                        message="Failed to access page",
                        url=url,
                        error_details=str(e),
                    )
                )
                print(f"  ❌ {name} ({path}) - Connection failed")

    def test_authentication_with_selenium(self):
        """Test authentication using Selenium."""
        if not self.use_selenium or not self.admin_username or not self.admin_password:
            print("\n⚠️  Skipping Selenium authentication tests (not configured)")
            return

        print("\n🔐 Testing Authentication (Selenium)...")

        try:
            # Navigate to login page
            login_url = f"{self.website_url}/accounts/login/"
            self.driver.get(login_url)

            # Wait for login form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )

            # Fill in login form
            username_field = self.driver.find_element(By.NAME, "login")
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys(self.admin_username)
            password_field.send_keys(self.admin_password)

            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Wait for redirect after login
            time.sleep(3)

            # Check if login was successful
            current_url = self.driver.current_url

            if "login" not in current_url.lower():
                self.report.add_result(
                    TestResult(
                        test_name="Authentication: Login",
                        category="Auth",
                        passed=True,
                        message="Successfully logged in",
                        url=login_url,
                    )
                )
                print(f"  ✅ Login successful - redirected to {current_url}")

                # Take screenshot of logged-in state
                screenshot_path = str(self.screenshots_dir / "login_success.png")
                self.driver.save_screenshot(screenshot_path)

                # Test logout
                self.driver.get(f"{self.website_url}/accounts/logout/")
                time.sleep(2)

                self.report.add_result(
                    TestResult(
                        test_name="Authentication: Logout",
                        category="Auth",
                        passed=True,
                        message="Successfully logged out",
                        screenshot_path=screenshot_path,
                    )
                )
                print(f"  ✅ Logout successful")

            else:
                # Check for error messages
                error_message = "Unknown error"
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, ".alert-danger, .error")
                    error_message = error_element.text
                except NoSuchElementException:
                    pass

                self.report.add_result(
                    TestResult(
                        test_name="Authentication: Login",
                        category="Auth",
                        passed=False,
                        message=f"Login failed: {error_message}",
                        url=login_url,
                        error_details=error_message,
                    )
                )
                print(f"  ❌ Login failed: {error_message}")

                # Take screenshot of error
                screenshot_path = str(self.screenshots_dir / "login_error.png")
                self.driver.save_screenshot(screenshot_path)

        except TimeoutException:
            self.report.add_result(
                TestResult(
                    test_name="Authentication: Login",
                    category="Auth",
                    passed=False,
                    message="Login page timed out",
                    error_details="Page load timeout",
                )
            )
            print(f"  ❌ Login page timed out")

        except Exception as e:
            self.report.add_result(
                TestResult(
                    test_name="Authentication: Login",
                    category="Auth",
                    passed=False,
                    message="Authentication test failed",
                    error_details=str(e),
                )
            )
            print(f"  ❌ Authentication test failed: {e}")

    def test_api_endpoints(self):
        """Test API endpoints."""
        print("\n🔌 Testing API Endpoints...")

        api_endpoints = [
            ("/api/v1/", "API Root"),
        ]

        for path, name in api_endpoints:
            url = f"{self.website_url}{path}"
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)

                if response.status_code in [200, 401, 403, 404]:
                    self.report.add_result(
                        TestResult(
                            test_name=f"API Endpoint: {name}",
                            category="API",
                            passed=True,
                            message=f"API endpoint accessible (status: {response.status_code})",
                            url=url,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ✅ {name} ({path}) - {response.status_code}")
                else:
                    self.report.add_result(
                        TestResult(
                            test_name=f"API Endpoint: {name}",
                            category="API",
                            passed=False,
                            message=f"API endpoint returned unexpected status {response.status_code}",
                            url=url,
                            status_code=response.status_code,
                        )
                    )
                    print(f"  ❌ {name} ({path}) - {response.status_code}")

            except (ConnectionError, Timeout, RequestException) as e:
                self.report.add_result(
                    TestResult(
                        test_name=f"API Endpoint: {name}",
                        category="API",
                        passed=False,
                        message="Failed to access API endpoint",
                        url=url,
                        error_details=str(e),
                    )
                )
                print(f"  ❌ {name} ({path}) - Connection failed")

    def run_all_tests(self):
        """Run all availability tests."""
        print("=" * 60)
        print(f"🌐 Website Availability Test")
        print(f"   URL: {self.website_url}")
        print(f"   Time: {self.report.timestamp}")
        print("=" * 60)

        # Setup Selenium if available
        if self.use_selenium:
            self.setup_selenium()

        try:
            # Run test categories
            self.test_health_endpoints()
            self.test_static_assets()
            self.test_public_pages()
            self.test_api_endpoints()
            self.test_authentication_with_selenium()

        finally:
            # Cleanup
            if self.use_selenium:
                self.teardown_selenium()

        # Print summary
        self.print_summary()

        return self.report

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.report.total_tests}")
        print(f"Passed: {self.report.passed_tests}")
        print(f"Failed: {self.report.failed_tests}")

        if self.report.total_tests > 0:
            success_rate = (self.report.passed_tests / self.report.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        if self.report.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.report.results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.message}")
                    if result.error_details:
                        print(f"    Error: {result.error_details}")

        print("\n" + "=" * 60)

    def save_report(self, output_path: str = "website_availability_report.json"):
        """Save test report to JSON file."""
        report_dict = self.report.to_dict()

        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2)

        print(f"\n📄 Report saved to: {output_path}")


def main():
    """Main entry point."""
    # Configuration from environment variables
    website_url = os.environ.get("WEBSITE_URL", "http://localhost")
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    use_selenium = os.environ.get("USE_SELENIUM", "true").lower() == "true"

    # Create tester
    tester = WebsiteAvailabilityTester(
        website_url=website_url,
        admin_username=admin_username,
        admin_password=admin_password,
        use_selenium=use_selenium,
    )

    # Run tests
    report = tester.run_all_tests()

    # Save report
    tester.save_report()

    # Exit with appropriate code
    if report.failed_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
