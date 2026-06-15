"""Selenium test configuration for structa.cloud."""
import os

import pytest


@pytest.fixture(scope="session")
def base_url():
    """Base URL — override with SELENIUM_BASE_URL env var."""
    # Default to localhost:8270 for external tests
    # But if running inside container, use internal port
    default_url = os.getenv("SELENIUM_BASE_URL", "http://localhost:8270")

    # Check if we're inside a container by looking for /.dockerenv
    if os.path.exists("/.dockerenv"):
        # Inside container, use internal port
        default_url = "http://127.0.0.1:5070"

    return default_url


@pytest.fixture(scope="session")
def selenium_driver():
    """
    Chrome driver — supports both local headless and remote Selenium Grid.

    - Set SELENIUM_REMOTE_URL to use a remote Selenium Grid (e.g. docker service).
    - Set SELENIUM_HEADLESS=false to run with a visible browser locally.
    """
    headless = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
    remote_url = os.getenv("SELENIUM_REMOTE_URL", "")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        pytest.skip("selenium not installed")
        return

    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")

    if remote_url:
        driver = webdriver.Remote(command_executor=remote_url, options=opts)
    else:
        driver = webdriver.Chrome(options=opts)

    driver.implicitly_wait(10)
    yield driver
    driver.quit()
