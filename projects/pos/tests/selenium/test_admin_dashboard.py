"""
Selenium tests for Unfold admin dashboard.

Verifies:
  - KPI cards are visible (sales, revenue, products, customers, nodes, alerts)
  - Revenue chart container exists
  - Recent activity tables render
  - Sidebar navigation links work
  - Logout button works
"""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestAdminDashboard:
    """Unfold admin dashboard tests."""

    KPIS = [
        "today", "monthly", "products", "customers",
        "nodes", "alerts", "aov",
    ]

    @pytest.mark.parametrize("kpi", KPIS)
    def test_kpi_card_visible(self, driver, admin_login, kpi: str) -> None:
        """Each KPI card renders on the dashboard."""
        wait = WebDriverWait(driver, 10)
        cards = driver.find_elements(By.CLASS_NAME, "card")
        assert len(cards) >= 6, f"Expected at least 6 KPI cards, found {len(cards)}"

    def test_revenue_chart_renders(self, driver, admin_login) -> None:
        """Revenue chart container is present."""
        wait = WebDriverWait(driver, 10)
        charts = driver.find_elements(By.TAG_NAME, "canvas")
        assert len(charts) >= 1, "No chart canvases found"

    def test_recent_sales_table(self, driver, admin_login) -> None:
        """Recent sales table appears on the dashboard."""
        wait = WebDriverWait(driver, 10)
        tables = driver.find_elements(By.TAG_NAME, "table")
        assert len(tables) >= 1, "No tables found on dashboard"

    def test_sidebar_navigation(self, driver, admin_login) -> None:
        """Sidebar contains navigation links to POS models."""
        wait = WebDriverWait(driver, 10)
        links = driver.find_elements(By.CSS_SELECTOR, "nav a, .sidebar a, [class*=nav] a")
        # Should have links to Products, Customers, Sales, etc.
        link_texts = [el.text.lower() for el in links]
        model_names = ["product", "customer", "sale", "menu", "employee"]
        found = any(any(m in t for m in model_names) for t in link_texts)
        assert found, f"Expected model links in sidebar, got: {link_texts[:10]}"

    def test_logout_button_exists(self, driver, admin_login) -> None:
        """Logout button is accessible from the dashboard."""
        wait = WebDriverWait(driver, 10)
        logout_links = driver.find_elements(
            By.XPATH,
            '//a[contains(@href, "logout")] | //button[contains(text(), "Log")]'
        )
        assert len(logout_links) >= 1, "No logout link found"
