"""
Selenium/Playwright base test classes for django-grep.
"""


class SeleniumTestCase:
    """
    Base Selenium test case.

    Requires: pip install django-grep[selenium]

    Features:
    - Browser setup/teardown
    - Wait helpers
    - Element interaction helpers
    """

    browser: str = "chrome"
    headless: bool = True

    def setUp(self):
        """Setup browser."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
        except ImportError:
            raise ImportError(
                "selenium is required. Install with: pip install django-grep[selenium]"
            )

        if self.browser == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=options)
        else:
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)

        self.driver.implicitly_wait(10)

    def tearDown(self):
        """Cleanup browser."""
        if hasattr(self, "driver"):
            self.driver.quit()

    def wait_for_element(self, by, value: str, timeout: int = 10):
        """Wait for element to appear and return it."""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by, value: str, timeout: int = 10):
        """Wait for element to be clickable and return it."""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def get_url(self, path: str) -> str:
        """Build full URL from path."""
        live_server_url = getattr(self, "live_server_url", "http://localhost:8000")
        return f"{live_server_url}{path}"
