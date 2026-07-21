"""
Selenium test configuration for POS admin panel.

Requires:
  - Chromium/Chrome installed
  - selenium (`pip install selenium webdriver-manager`)
  - pos-full sidecar running on :8000 with superuser seeded

Usage:
    cd projects/pos
    pytest tests/selenium/ -v --tb=short
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ── Paths ───────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent          # pos/tests/selenium/
_TESTS = _HERE.parent                            # pos/tests/
_POS = _TESTS.parent                             # pos/
_SIDECAR_FULL = _POS / "pos-full" / "sidecar"

if str(_SIDECAR_FULL) not in sys.path:
    sys.path.insert(0, str(_SIDECAR_FULL))

# ── Config ──────────────────────────────────────────────────────────────
ADMIN_URL = os.environ.get("POS_ADMIN_URL", "http://127.0.0.1:8000/admin/")
ADMIN_EMAIL = os.environ.get("POS_ADMIN_EMAIL", "admin@pos-full.local")
ADMIN_PASSWORD = os.environ.get("POS_ADMIN_PASSWORD", "admin123")


@pytest.fixture(scope="session")
def chrome_options() -> Options:
    """Headless Chrome options for CI / headless environments."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1440,1080")
    opts.add_argument("--hide-scrollbars")
    return opts


@pytest.fixture(scope="session")
def driver(chrome_options: Options) -> webdriver.Chrome:
    """Create a headless Chrome driver session."""
    # Try common Chrome binary locations
    import shutil
    chrome_paths = [
        shutil.which("chromium-browser"),
        shutil.which("chromium"),
        shutil.which("google-chrome"),
        shutil.which("chrome"),
    ]
    chrome_bin = next((p for p in chrome_paths if p), None)
    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def admin_login(driver: webdriver.Chrome) -> None:
    """Log in to the Unfold admin panel once per session."""
    driver.get(ADMIN_URL)
    wait = WebDriverWait(driver, 15)

    # Wait for login form
    user_field = wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    pwd_field = driver.find_element(By.NAME, "password")
    submit_btn = driver.find_element(By.XPATH, '//input[@type="submit"]')

    user_field.send_keys(ADMIN_EMAIL)
    pwd_field.send_keys(ADMIN_PASSWORD)
    submit_btn.click()

    # Wait for redirect to dashboard (or login error)
    wait.until(lambda d: "admin/login" not in d.current_url)
