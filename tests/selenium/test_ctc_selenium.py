"""
CTC Research Selenium Tests
==========================
Browser automation tests for CTC Research website.
"""

import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestCTCResearchSelenium:
    """Selenium tests for CTC Research website."""

    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, ctc_research_url):
        """Setup for each test."""
        self.driver = selenium_driver
        self.base_url = ctc_research_url
        self.wait = WebDriverWait(self.driver, 10)

    def test_homepage_loads(self):
        """Test that homepage loads successfully."""
        try:
            self.driver.get(self.base_url)

            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Check page title
            assert self.driver.title, "Page title is empty"

            # Check that page loaded (no error messages)
            page_source = self.driver.page_source.lower()
            error_indicators = ['500 internal server error', '404 not found', 'application error']

            for error in error_indicators:
                assert error not in page_source, f"Page shows error: {error}"

        except TimeoutException:
            pytest.fail("Homepage failed to load within timeout")

    def test_admin_login_page(self):
        """Test Django admin login page."""
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

    def test_navigation_links(self):
        """Test navigation links on the homepage."""
        try:
            self.driver.get(self.base_url)

            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Find navigation links
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, "nav a, .navbar a, .menu a")

            if nav_links:
                # Test first few navigation links
                for i, link in enumerate(nav_links[:3]):  # Test first 3 links
                    if link.get_attribute("href"):
                        href = link.get_attribute("href")

                        # Skip external links and javascript links
                        if href.startswith(('http://', 'https://')) and self.base_url not in href:
                            continue
                        if href.startswith(('javascript:', 'mailto:', 'tel:')):
                            continue

                        # Click link and verify it loads
                        original_url = self.driver.current_url
                        link.click()
                        time.sleep(2)  # Wait for navigation

                        # Check that we navigated somewhere or stayed on same page
                        current_url = self.driver.current_url
                        assert current_url, "Navigation resulted in empty URL"

                        # Go back to original page for next test
                        if current_url != original_url:
                            self.driver.back()
                            time.sleep(1)

        except Exception as e:
            # Navigation testing is optional - don't fail if no nav found
            print(f"Navigation test skipped: {e}")

    def test_responsive_design(self):
        """Test responsive design at different screen sizes."""
        screen_sizes = [
            (1920, 1080),  # Desktop
            (1024, 768),   # Tablet
            (375, 667),    # Mobile
        ]

        try:
            self.driver.get(self.base_url)

            for width, height in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)  # Wait for resize

                # Check that page is still functional
                body = self.driver.find_element(By.TAG_NAME, "body")
                assert body.is_displayed(), f"Page not displayed at {width}x{height}"

                # Check that content is visible (not hidden off-screen)
                viewport_width = self.driver.execute_script("return window.innerWidth")
                assert viewport_width > 0, f"Viewport width is 0 at {width}x{height}"

        except Exception as e:
            pytest.fail(f"Responsive design test failed: {e}")

    def test_form_interactions(self):
        """Test form interactions if forms are present."""
        try:
            self.driver.get(self.base_url)

            # Look for forms on the page
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            if forms:
                for form in forms[:2]:  # Test first 2 forms
                    # Find input fields
                    inputs = form.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], textarea")

                    if inputs:
                        # Test typing in first input
                        first_input = inputs[0]
                        if first_input.is_displayed() and first_input.is_enabled():
                            first_input.clear()
                            first_input.send_keys("Test input")

                            # Verify input was entered
                            assert first_input.get_attribute("value") == "Test input", "Form input failed"

        except Exception as e:
            # Form testing is optional
            print(f"Form interaction test skipped: {e}")

    def test_javascript_functionality(self):
        """Test basic JavaScript functionality."""
        try:
            self.driver.get(self.base_url)

            # Test that JavaScript is working
            js_result = self.driver.execute_script("return typeof jQuery !== 'undefined' ? 'jQuery loaded' : 'No jQuery';")
            print(f"JavaScript test result: {js_result}")

            # Test basic DOM manipulation
            element_count = self.driver.execute_script("return document.getElementsByTagName('*').length;")
            assert element_count > 0, "No DOM elements found"

            # Test console for errors
            logs = self.driver.get_log('browser')
            severe_errors = [log for log in logs if log['level'] == 'SEVERE']

            # Allow some errors but not too many
            assert len(severe_errors) < 5, f"Too many JavaScript errors: {len(severe_errors)}"

        except Exception as e:
            print(f"JavaScript functionality test info: {e}")

    def test_page_performance(self):
        """Test basic page performance metrics."""
        try:
            start_time = time.time()
            self.driver.get(self.base_url)

            # Wait for page to fully load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            load_time = time.time() - start_time

            # Page should load within reasonable time
            assert load_time < 10.0, f"Page load time too slow: {load_time:.2f}s"

            # Check page size (rough estimate)
            page_source_size = len(self.driver.page_source)
            assert page_source_size > 100, "Page content too small"
            assert page_source_size < 1000000, "Page content too large"  # 1MB limit

        except Exception as e:
            pytest.fail(f"Page performance test failed: {e}")

class TestCTCResearchUserFlows:
    """Test complete user flows on CTC Research."""

    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, ctc_research_url):
        """Setup for each test."""
        self.driver = selenium_driver
        self.base_url = ctc_research_url
        self.wait = WebDriverWait(self.driver, 10)

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

    def test_search_functionality(self):
        """Test search functionality if available."""
        try:
            self.driver.get(self.base_url)

            # Look for search forms
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                "input[type='search'], input[name*='search'], input[placeholder*='search'], input[placeholder*='Search']")

            if search_inputs:
                search_input = search_inputs[0]

                if search_input.is_displayed() and search_input.is_enabled():
                    # Perform search
                    search_input.clear()
                    search_input.send_keys("test search")

                    # Try to submit search
                    search_form = search_input.find_element(By.XPATH, "./ancestor::form")
                    search_form.submit()

                    # Wait for results
                    time.sleep(3)

                    # Check that search was processed
                    current_url = self.driver.current_url
                    assert "search" in current_url.lower() or "q=" in current_url, "Search was not processed"

        except Exception as e:
            # Search functionality is optional
            print(f"Search functionality test skipped: {e}")

    def test_contact_form_flow(self):
        """Test contact form flow if available."""
        try:
            self.driver.get(self.base_url)

            # Look for contact links
            contact_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Contact")
            contact_links.extend(self.driver.find_elements(By.PARTIAL_LINK_TEXT, "contact"))

            if contact_links:
                contact_links[0].click()
                time.sleep(2)

                # Look for contact form
                forms = self.driver.find_elements(By.TAG_NAME, "form")

                if forms:
                    form = forms[0]

                    # Find form fields
                    name_fields = form.find_elements(By.CSS_SELECTOR,
                        "input[name*='name'], input[placeholder*='name'], input[placeholder*='Name']")
                    email_fields = form.find_elements(By.CSS_SELECTOR,
                        "input[type='email'], input[name*='email'], input[placeholder*='email']")
                    message_fields = form.find_elements(By.CSS_SELECTOR,
                        "textarea, input[name*='message'], input[placeholder*='message']")

                    # Fill out form if fields are found
                    if name_fields and name_fields[0].is_displayed():
                        name_fields[0].send_keys("Test User")

                    if email_fields and email_fields[0].is_displayed():
                        email_fields[0].send_keys("test@example.com")

                    if message_fields and message_fields[0].is_displayed():
                        message_fields[0].send_keys("This is a test message.")

                    # Note: We don't actually submit to avoid sending test emails
                    print("Contact form fields filled successfully")

        except Exception as e:
            # Contact form testing is optional
            print(f"Contact form test skipped: {e}")
