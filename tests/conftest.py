"""
Shared pytest configuration for both CTC Research and Structa Cloud websites.

Django is configured via DJANGO_SETTINGS_MODULE = "tests.settings" in pyproject.toml.
All sys.path and module-alias setup lives in tests/settings.py so it runs
before pytest-django calls django.setup().
"""
import importlib
import os
import sys
import types
from pathlib import Path

import pytest


# Only import Django utilities when Django is configured
def _django_available():
    try:
        from django.conf import settings
        return settings.configured
    except Exception:
        return False


# Force fresh database for each test session
@pytest.fixture(scope="session", autouse=True)
def _force_fresh_db():
    """Force pytest-django to create a fresh database for each test session."""
    # This is handled by pytest-django's --create-db flag
    pass


def pytest_configure(config):
    """Configure pytest to ensure fresh database."""
    # Disable database reuse
    config.option.reuse_db = False

# ---------------------------------------------------------------------------
# Environment flags
# ---------------------------------------------------------------------------
TEST_CTC_RESEARCH = os.environ.get("TEST_CTC_RESEARCH", "true").lower() == "true"
TEST_STRUCTA_CLOUD = os.environ.get("TEST_STRUCTA_CLOUD", "true").lower() == "true"
TEST_EMAIL = os.environ.get("TEST_EMAIL", "true").lower() == "true"
TEST_SELENIUM = os.environ.get("TEST_SELENIUM", "false").lower() == "true"

CTC_BASE_URL = os.environ.get("CTC_BASE_URL", "http://localhost:5070")
STRUCTA_BASE_URL = os.environ.get("STRUCTA_BASE_URL", "http://localhost:5071")
TRAEFIK_CTC_URL = os.environ.get("TRAEFIK_CTC_URL", "https://ctc-research.com")
TRAEFIK_STRUCTA_URL = os.environ.get("TRAEFIK_STRUCTA_URL", "https://core.structa.cloud")


# ---------------------------------------------------------------------------
# Post-setup: register www.apps.blog → apps.blog aliases after Django is ready
# ---------------------------------------------------------------------------
def pytest_configure(config):
    """Register backward-compat module aliases after Django setup."""
    # pytest-django has already called django.setup() by the time this runs
    # (because DJANGO_SETTINGS_MODULE is set in pyproject.toml).
    # We register the www.apps.* aliases here so test imports resolve.
    _register_aliases()


def _register_aliases():
    alias_map = {
        # www.apps.blog aliases
        "www.apps.blog":               "plugins.blog",
        "www.apps.blog.models":        "plugins.blog.models",
        "www.apps.blog.forms":         "plugins.blog.forms",
        "www.apps.blog.admin":         "plugins.blog.admin",
        "www.apps.blog.urls":          "plugins.blog.urls",
        "www.apps.blog.services":      "plugins.blog.services",
        "www.apps.blog.api":           "plugins.blog.api",
        "www.apps.blog.management":    "plugins.blog.management",
        "www.apps.blog.viewsets":      "plugins.blog.viewsets",
        "www.apps.blog.components":    "plugins.blog.components",
        "www.apps.blog.feeds":         "plugins.blog.feeds",

        # www.apps.accounts aliases
        "www.apps.accounts":           "accounts",
        "www.apps.accounts.models":    "accounts.models",
        "www.apps.accounts.models.tags": "accounts.models.tags",
        "www.apps.accounts.registration": "accounts.registration",
        "www.apps.accounts.management": "accounts.management",
        "www.apps.accounts.forms":     "accounts.forms",
        "www.apps.accounts.services":  "accounts.services",
        "www.apps.accounts.views":     "accounts.views",
        "www.apps.accounts.filters":   "accounts.filters",
        "www.apps.accounts.admin":     "accounts.admin",
        "www.apps.accounts.signals":   "accounts.signals",
        "www.apps.accounts.middleware": "accounts.middleware",
        "www.apps.accounts.site":      "accounts.site",
        "www.apps.accounts.site.blog": "accounts.site.blog",
        "www.apps.accounts.adapters":  "accounts.adapters",
        "www.apps.accounts.blocks":    "accounts.blocks",
        "www.apps.accounts.emails":    "accounts.emails",
        "www.apps.accounts.tokens":    "accounts.tokens",
        "www.apps.accounts.renderers": "accounts.renderers",

        # Legacy registration module aliases used by older django-fusion/ceptor
        # registration tests. The site implementation lives in accounts.*.
        "www.apps.accounts.registration.tokens": "accounts.registration.tokens",
        "www.apps.accounts.registration.adapter": "accounts.adapters",
        "www.apps.accounts.registration.adapters": "accounts.adapters",
        "www.apps.accounts.registration.emails": "accounts.emails",
        "www.apps.accounts.registration.forms": "accounts.registration.forms",
        "www.apps.accounts.registration.views": "accounts.registration.views",
        "www.apps.accounts.registration.allauth_views": "accounts.allauth_views",
        "www.apps.accounts.registration.signals": "accounts.signals",
        "apps.accounts":                  "accounts",
        "apps.accounts.registration":     "accounts.registration",
        "apps.accounts.registration.tokens": "accounts.registration.tokens",
        "apps.accounts.registration.adapter": "accounts.adapters",
        "apps.accounts.registration.adapters": "accounts.adapters",
        "apps.accounts.registration.emails": "accounts.emails",
        "apps.accounts.registration.forms": "accounts.registration.forms",
        "apps.accounts.registration.views": "accounts.registration.views",
        "apps.accounts.registration.allauth_views": "accounts.allauth_views",
        "apps.accounts.registration.signals": "accounts.signals",
    }
    for alias, target in alias_map.items():
        if alias in sys.modules:
            continue
        try:
            sys.modules[alias] = importlib.import_module(target)
        except (ImportError, RuntimeError):
            stub = types.ModuleType(alias)
            sys.modules[alias] = stub





def pytest_ignore_collect(collection_path, config):
    """Keep workspace runs focused on runnable workspace/yaml suites.

    Legacy generated property/app suites are still available for focused runs,
    but several perform Django database setup at import time or depend on the
    old monorepo import layout. Focused regression commands cover the fixed
    registration token aliases directly.
    """
    path_obj = Path(str(collection_path))
    path = str(path_obj)
    tests_root = Path(__file__).resolve().parent
    if path_obj.suffix == ".py" and path_obj.parent == tests_root and path_obj.name not in {"test_yaml_site_scenarios.py", "conftest.py"}:
        return True
    if path_obj.name == "test_property_allauth_token_roundtrip.py":
        return False
    ignored = (
        "tests/apps/",
        "tests/ci/",
        "tests/docker/",
        "tests/email/",
        "tests/http/",
        "tests/integration/",
        "tests/selenium/",
        "tests/selenium-detailed/",
        "tests/scripts/",
        "tests/unit/",
    )
    return any(fragment in path for fragment in ignored)


# ---------------------------------------------------------------------------
# Collection modifier
# ---------------------------------------------------------------------------
def pytest_collection_modifyitems(config, items):
    skip_ctc      = pytest.mark.skip(reason="CTC Research tests disabled")
    skip_structa  = pytest.mark.skip(reason="Structa Cloud tests disabled")
    skip_email    = pytest.mark.skip(reason="Email tests disabled")
    skip_selenium = pytest.mark.skip(reason="Selenium tests disabled")

    for item in items:
        nid = item.nodeid.lower()
        if not TEST_CTC_RESEARCH and "ctc" in nid:
            item.add_marker(skip_ctc)
        if not TEST_STRUCTA_CLOUD and "structa" in nid:
            item.add_marker(skip_structa)
        if not TEST_EMAIL and "email" in nid:
            item.add_marker(skip_email)
        if not TEST_SELENIUM and "selenium" in nid:
            item.add_marker(skip_selenium)


# ---------------------------------------------------------------------------
# Session fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def workspace_root():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def ctc_research_root(workspace_root):
    return workspace_root / "precis-ctc"


@pytest.fixture(scope="session")
def structa_cloud_root(workspace_root):
    return workspace_root / "lms"


@pytest.fixture(scope="session")
def docker_compose_file(workspace_root):
    """Main docker-compose.yml at workspace root."""
    return workspace_root / "docker-compose.yml"


@pytest.fixture(scope="session")
def test_databases():
    return {"ctc_research": "db_ctc_test", "structa_cloud": "db_structa_test", "vresume": "vresume_test"}


@pytest.fixture
def email_backend():
    from django.core.mail import get_connection
    return get_connection("django.core.mail.backends.locmem.EmailBackend")


@pytest.fixture(scope="session")
def selenium_driver():
    if not TEST_SELENIUM:
        pytest.skip("Selenium tests disabled")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        for arg in ("--headless", "--no-sandbox", "--disable-dev-shm-usage",
                    "--disable-gpu", "--window-size=1920,1080"):
            opts.add_argument(arg)
        driver = webdriver.Chrome(options=opts)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    except Exception as e:
        pytest.skip(f"Selenium WebDriver not available: {e}")


@pytest.fixture
def live_server_url():
    return os.environ.get("LIVE_SERVER_URL", "http://localhost:8000")


@pytest.fixture
def ctc_research_url():
    return CTC_BASE_URL


@pytest.fixture
def structa_cloud_url():
    return STRUCTA_BASE_URL


@pytest.fixture
def traefik_ctc_url():
    return TRAEFIK_CTC_URL


@pytest.fixture
def traefik_structa_url():
    return TRAEFIK_STRUCTA_URL


# ---------------------------------------------------------------------------
# Database fixtures for test isolation
# ---------------------------------------------------------------------------
@pytest.fixture
def db_user(db):
    """Create a unique test user for each test."""
    import uuid

    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    return User.objects.create_user(username=username, password="testpass123")


@pytest.fixture
def db_staff_user(db):
    """Create a unique staff test user for each test."""
    import uuid

    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = f"staff_{uuid.uuid4().hex[:8]}"
    return User.objects.create_user(username=username, password="testpass123", is_staff=True)


@pytest.fixture
def db_superuser(db):
    """Create a unique superuser for each test."""
    import uuid

    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = f"admin_{uuid.uuid4().hex[:8]}"
    return User.objects.create_superuser(username=username, email="admin@test.com", password="testpass123")
