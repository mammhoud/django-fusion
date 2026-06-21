"""
pytest plugin for django-grep test utilities.

Auto-registered via pytest11 entry point when django-grep is installed.
Provides shared pytest fixtures for Django projects.
"""
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def test_user(db):
    """Create a standard test user."""
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def admin_user(db):
    """Create a superuser."""
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def authenticated_client(client, test_user):
    """Django test client logged in as test_user."""
    client.force_login(test_user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Django test client logged in as admin."""
    client.force_login(admin_user)
    return client


@pytest.fixture(autouse=False)
def clear_email_outbox():
    """Clear Django email outbox before and after each test."""
    from django.core import mail
    mail.outbox = []
    yield
    mail.outbox = []


# ---------------------------------------------------------------------------
# Selenium / HTTP smoke fixtures
# ---------------------------------------------------------------------------
import os


@pytest.fixture(scope="session")
def base_url():
    """Base URL for HTTP/Selenium tests. Set SELENIUM_BASE_URL env var to override."""
    return os.getenv("SELENIUM_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def selenium_driver():
    """
    Session-scoped Selenium WebDriver.
    Reads SELENIUM_BROWSER (chrome|firefox) and SELENIUM_HEADLESS (true|false).
    Requires: pip install django-grep[selenium]
    """
    browser = os.getenv("SELENIUM_BROWSER", "chrome").lower()
    headless = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
    except ImportError:
        pytest.skip("selenium not installed — pip install django-grep[selenium]")
        return

    if browser == "firefox":
        opts = FirefoxOptions()
        if headless:
            opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)
    else:
        opts = ChromeOptions()
        if headless:
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=opts)

    driver.implicitly_wait(10)
    yield driver
    driver.quit()


# ---------------------------------------------------------------------------
# Selectors loader fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def selectors():
    """
    Provide selectors dict for tests.
    Load order: SELENIUM_SELECTORS_FILE env var -> SELENIUM_SITE env var -> 'default'
    """
    site = os.getenv("SELENIUM_SITE", "default")
    try:
        from django_grep.tests.selectors import load_selectors
    except Exception:
        pytest.skip("selectors loader not available")

    try:
        return load_selectors(site)
    except FileNotFoundError:
        pytest.skip(f"No selectors YAML for site {site!r}")


# ---------------------------------------------------------------------------
# Pydoll (async) fixtures
# ---------------------------------------------------------------------------

# Require pytest-asyncio to provide async fixtures — but allow graceful skip
_use_pydoll = os.getenv("USE_PYDOLL", "0") == "1"

try:
    import pytest_asyncio  # noqa: F401
    _pytest_asyncio_available = True
except Exception:
    _pytest_asyncio_available = False

if _pytest_asyncio_available:
    import pytest_asyncio

    @pytest_asyncio.fixture(scope="session")
    async def pydoll_browser():
        """Session-scoped Pydoll browser instance (async).

        Enable by setting USE_PYDOLL=1 in the environment. Requires `pydoll`.
        """
        if not _use_pydoll:
            pytest.skip("pydoll fixtures disabled (USE_PYDOLL not set)")
        try:
            from pydoll.browser.chromium import Chrome
        except Exception:
            pytest.skip("pydoll not installed — pip install pydoll")

        async with Chrome() as browser:
            yield browser

    @pytest_asyncio.fixture
    async def pydoll_tab(pydoll_browser):
        """Create a fresh tab (page) for each test and close it afterwards."""
        tab = await pydoll_browser.start()
        try:
            yield tab
        finally:
            try:
                await tab.close()
            except Exception:
                pass
else:
    # Fallback fixtures that skip when pytest-asyncio is unavailable
    @pytest.fixture(scope="session")
    def pydoll_browser():
        pytest.skip("pytest-asyncio not available; install pytest-asyncio to use pydoll fixtures")

    @pytest.fixture
    def pydoll_tab():
        pytest.skip("pytest-asyncio not available; install pytest-asyncio to use pydoll fixtures")
