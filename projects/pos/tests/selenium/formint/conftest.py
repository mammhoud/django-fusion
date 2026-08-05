"""
Selenium test configuration for the Formint POS Unfold admin panel.

Requires:
  - Chromium/Chrome installed
  - selenium (`pip install selenium webdriver-manager`)
  - formint-pos backend running on :8000 with superuser seeded
    (python manage.py --ensure-superuser)

Usage:
    cd projects/pos
    pytest tests/selenium/formint/ -v --tb=short
"""

from __future__ import annotations

import os
import shutil

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ── Config ──────────────────────────────────────────────────────────────
ADMIN_URL = os.environ.get("FORMINT_ADMIN_URL", "http://127.0.0.1:8000/admin/")
ADMIN_EMAIL = os.environ.get("FORMINT_ADMIN_EMAIL", "admin@formint.local")
ADMIN_PASSWORD = os.environ.get("FORMINT_ADMIN_PASSWORD", "admin123")


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
    """Log in to the Formint Unfold admin panel once per session."""
    driver.get(ADMIN_URL)
    wait = WebDriverWait(driver, 15)

    user_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    pwd_field = driver.find_element(By.NAME, "password")
    submit_btn = driver.find_element(By.XPATH, '//input[@type="submit"]')

    user_field.send_keys(ADMIN_EMAIL)
    pwd_field.send_keys(ADMIN_PASSWORD)
    submit_btn.click()

    # Wait for redirect to dashboard (or login error)
    wait.until(lambda d: "admin/login" not in d.current_url)
