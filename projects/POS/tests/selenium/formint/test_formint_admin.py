"""
Selenium tests for the Formint POS Unfold admin panel.

Verifies:
  - Login page renders with Unfold theme
  - Dashboard KPI cards incl. loyalty/settings metrics (Loyalty Members,
    Points Issued, Settings Rows)
  - Charts render (canvas elements)
  - Sidebar navigation links to loyalty/settings models
  - Changelist pages load for ClientCategory, LoyaltyTransaction, UserSettings
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import ADMIN_URL


class TestFormintLogin:
    """Formint admin login page tests."""

    def test_login_page_renders(self, driver) -> None:
        """Login page loads with the Formint branding."""
        driver.get(ADMIN_URL)
        wait = WebDriverWait(driver, 10)
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        source = driver.page_source
        assert "Formint POS" in source or "Formint" in source

    def test_successful_login_redirects_to_dashboard(self, driver, admin_login) -> None:
        """Logging in redirects away from /admin/login/."""
        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: "login" not in d.current_url)
        assert "login" not in driver.current_url


class TestFormintDashboard:
    """Formint Unfold dashboard (loyalty/settings focus)."""

    def test_kpi_cards_render(self, driver, admin_login) -> None:
        """KPI cards are present (10 expected)."""
        wait = WebDriverWait(driver, 10)
        cards = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pos-kpi-card"))
        )
        assert len(cards) >= 6, f"Expected >= 6 KPI cards, found {len(cards)}"

    def test_loyalty_kpi_cards(self, driver, admin_login) -> None:
        """Loyalty/settings KPI cards are present."""
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pos-kpi-card")))
        source = driver.page_source
        for kpi in ["Loyalty Members", "Points Issued", "Settings Rows"]:
            assert kpi in source, f"Missing KPI card: {kpi}"

    def test_dashboard_title(self, driver, admin_login) -> None:
        """Dashboard heading shows the Formint title."""
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pos-kpi-grid")))
        source = driver.page_source
        assert "Formint POS" in source

    def test_charts_render(self, driver, admin_login) -> None:
        """At least one chart canvas renders on the dashboard."""
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pos-kpi-grid")))
        charts = driver.find_elements(By.TAG_NAME, "canvas")
        assert len(charts) >= 1, "No chart canvases found"

    def test_sidebar_loyalty_links(self, driver, admin_login) -> None:
        """Sidebar links to loyalty/settings models exist."""
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pos-kpi-grid")))
        links = driver.find_elements(By.CSS_SELECTOR, "nav a")
        link_texts = [el.text.lower() for el in links]
        expected = ["client categories", "loyalty transactions", "user settings"]
        found = [e for e in expected if any(e in t for t in link_texts)]
        assert len(found) >= 2, (
            f"Expected loyalty/settings sidebar links, found only: {found}"
        )


class TestFormintChangelists:
    """Loyalty/settings changelist pages."""

    def test_client_category_changelist(self, driver, admin_login) -> None:
        driver.get(ADMIN_URL + "formint/clientcategory/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "login" not in driver.current_url

    def test_loyalty_transaction_changelist(self, driver, admin_login) -> None:
        driver.get(ADMIN_URL + "formint/loyaltytransaction/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "login" not in driver.current_url

    def test_user_settings_changelist(self, driver, admin_login) -> None:
        driver.get(ADMIN_URL + "formint/usersettings/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "login" not in driver.current_url
