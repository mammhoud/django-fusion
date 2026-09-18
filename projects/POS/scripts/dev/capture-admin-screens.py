#!/usr/bin/env python3
"""Capture Formint POS admin screenshots via Selenium (authenticated).

Logs into the Unfold admin at http://127.0.0.1:8767/admin/ as the superuser
and saves PNG screenshots to a temporary capture directory consumed by the related-media workflow.
"""
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE = os.environ.get("FORMINT_ADMIN_BASE", "http://127.0.0.1:8767")
USERNAME = os.environ.get("FORMINT_ADMIN_USERNAME", "admin")
PASSWORD = os.environ.get("FORMINT_ADMIN_PASSWORD", "admin123")
OUT_DIR = os.environ.get(
    "FORMINT_CAPTURE_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.tmp-screenshot-captures"),
)
OUT_DIR = os.path.abspath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

CHROME_BIN = os.environ.get(
    "CHROME_BIN",
    "/usr/bin/chromium-browser",
)

opts = Options()
opts.binary_location = CHROME_BIN
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-gpu")
opts.add_argument("--hide-scrollbars")
opts.add_argument("--window-size=1440,1080")

driver = webdriver.Chrome(options=opts)
try:
    # ── Login ──
    driver.get(f"{BASE}/admin/login/")
    time.sleep(2)
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "#login-form button[type=submit]").click()
    time.sleep(3)
    if "login" in driver.current_url:
        print(f"✗ login failed (still at {driver.current_url})", file=sys.stderr)
        sys.exit(2)
    print(f"✓ logged in as {USERNAME}")

    shots = {
        "03_admin_dashboard": f"{BASE}/admin/",
        "04_admin_products": f"{BASE}/admin/pos_full/product/",
        "05_admin_customers": f"{BASE}/admin/pos_full/customer/",
        "06_admin_sales": f"{BASE}/admin/pos_full/sale/",
        "07_admin_loyalty": f"{BASE}/admin/pos_full/clientcategory/",
        "08_admin_settings": f"{BASE}/admin/pos_full/usersettings/",
    }
    for name, url in shots.items():
        driver.get(url)
        time.sleep(4)
        src = driver.page_source
        if "name=\"username\"" in src:
            print(f"✗ {name} redirected to login", file=sys.stderr)
            continue
        path = os.path.join(OUT_DIR, f"{name}.png")
        driver.save_screenshot(path)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        if size > 5000:
            print(f"  ✓ {name} ({size} bytes)")
        else:
            print(f"  ✗ {name} too small ({size} bytes)")
finally:
    driver.quit()
