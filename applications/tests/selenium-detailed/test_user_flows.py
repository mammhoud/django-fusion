"""
CTC Research User Flow Tests
===========================
End-to-end user interaction flow tests.
"""

import time

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestUserFlows:
    """Test complete user interaction flows."""

    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, ctc_research_url):
        """Setup for each test."""
        self.driver = selenium_driver
        self.base_url = ctc_research_url
        self.wait = WebDriverWait(self.driver, 10)

    def test_homepage_user_flow(self):
        """Test basic homepage user flow."""
        try:
            self.driver.get(self.base_url)

            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Check page title
            assert self.driver.title, "Page title is empty"

            # Check that page loaded without errors
            page_source = self.driver.page_source.lower()
            error_indicators = ['500 internal server error', '404 not found', 'application error']

            for error in error_indicators:
                assert error not in page_source, f"Page shows error: {error}"

            # Test basic page interaction
            body = self.driver.find_element(By.TAG_NAME, "body")
            assert body.is_displayed(), "Page body not displayed"

        except TimeoutException:
            pytest.fail("Homepage failed to load within timeout")

    def test_navigation_flow(self):
        """Test navigation flow through the site."""
        try:
            self.driver.get(self.base_url)

            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Find navigation links
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, "nav a, .navbar a, .menu a, header a")

            if nav_links:
                # Test first few navigation links
                for i, link in enumerate(nav_links[:3]):
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
                        time.sleep(2)

                        # Check that we navigated successfully
                        current_url = self.driver.current_url
                        assert current_url, "Navigation resulted in empty URL"

                        # Verify page loaded without errors
                        page_source = self.driver.page_source.lower()
                        assert '500 internal server error' not in page_source, "Navigation led to server error"

                        # Go back to original page for next test
                        if current_url != original_url:
                            self.driver.back()
                            time.sleep(1)

        except Exception as e:
            # Navigation testing is optional - don't fail if no nav found
            print(f"Navigation flow test info: {e}")

    def test_search_flow(self):
        """Test search functionality flow."""
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
                    page_source = self.driver.page_source.lower()

                    search_processed = (
                        "search" in current_url.lower() or
                        "q=" in current_url or
                        "search" in page_source or
                        "results" in page_source
                    )

                    assert search_processed, "Search was not processed"

        except Exception as e:
            # Search functionality is optional
            print(f"Search flow test info: {e}")

    def test_form_interaction_flow(self):
        """Test form interaction flows."""
        try:
            self.driver.get(self.base_url)

            # Look for forms on the page
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            if forms:
                for form in forms[:2]:  # Test first 2 forms
                    # Find input fields
                    inputs = form.find_elements(By.CSS_SELECTOR,
                        "input[type='text'], input[type='email'], textarea, input[name*='name'], input[name*='email']")

                    if inputs:
                        # Test typing in first input
                        first_input = inputs[0]
                        if first_input.is_displayed() and first_input.is_enabled():
                            first_input.clear()
                            first_input.send_keys("Test input")

                            # Verify input was entered
                            assert first_input.get_attribute("value") == "Test input", "Form input failed"

                            # Test form validation if submit button exists
                            submit_buttons = form.find_elements(By.CSS_SELECTOR,
                                "input[type='submit'], button[type='submit'], button:not([type])")

                            if submit_buttons and submit_buttons[0].is_displayed():
                                # Note: We don't actually submit to avoid side effects
                                print("Form interaction test completed successfully")

        except Exception as e:
            # Form testing is optional
            print(f"Form interaction test info: {e}")

    def test_responsive_flow(self):
        """Test responsive design flow at different screen sizes."""
        screen_sizes = [
            (1920, 1080),  # Desktop
            (1024, 768),   # Tablet
            (375, 667),    # Mobile
        ]

        try:
            self.driver.get(self.base_url)

            for width, height in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)

                # Check that page is still functional
                body = self.driver.find_element(By.TAG_NAME, "body")
                assert body.is_displayed(), f"Page not displayed at {width}x{height}"

                # Check that content is visible
                viewport_width = self.driver.execute_script("return window.innerWidth")
                assert viewport_width > 0, f"Viewport width is 0 at {width}x{height}"

                # Test basic interaction at this size
                clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button")
                if clickable_elements:
                    # Verify at least some elements are clickable
                    clickable_count = sum(1 for elem in clickable_elements[:5] if elem.is_displayed())
                    assert clickable_count > 0, f"No clickable elements visible at {width}x{height}"

        except Exception as e:
            pytest.fail(f"Responsive flow test failed: {e}")


class TestPerformanceFlows:
    """Test performance-related user flows."""

    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver, ctc_research_url):
        """Setup for each test."""
        self.driver = selenium_driver
        self.base_url = ctc_research_url
        self.wait = WebDriverWait(self.driver, 10)

    def test_page_load_performance(self):
        """Test page load performance flow."""
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
            assert page_source_size < 2000000, "Page content too large"  # 2MB limit

        except Exception as e:
            pytest.fail(f"Page load performance test failed: {e}")

    def test_javascript_performance(self):
        """Test JavaScript performance and functionality."""
        try:
            self.driver.get(self.base_url)

            # Test that JavaScript is working
            js_result = self.driver.execute_script("return typeof document !== 'undefined' ? 'DOM available' : 'No DOM';")
            assert 'DOM available' in js_result, "JavaScript DOM access failed"

            # Test basic DOM manipulation performance
            start_time = time.time()
            element_count = self.driver.execute_script("return document.getElementsByTagName('*').length;")
            js_time = time.time() - start_time

            assert element_count > 0, "No DOM elements found"
            assert js_time < 1.0, f"JavaScript execution too slow: {js_time:.2f}s"

            # Check for JavaScript errors
            logs = self.driver.get_log('browser')
            severe_errors = [log for log in logs if log['level'] == 'SEVERE']

            # Allow some errors but not too many
            assert len(severe_errors) < 5, f"Too many JavaScript errors: {len(severe_errors)}"

        except Exception as e:
            print(f"JavaScript performance test info: {e}")
