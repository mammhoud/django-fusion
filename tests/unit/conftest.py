"""
Pytest configuration for structa top-level tests.

Configures a minimal Django environment with SQLite in-memory database
so that tests can use @pytest.mark.django_db without the full project
settings stack (Dynaconf, Wagtail, etc.).
"""
import pytest


@pytest.fixture(scope="session")
def base_url():
    """Override base_url to None for non-selenium tests.

    This prevents pytest-selenium from skipping all tests as 'destructive'.
    Selenium tests in tests/selenium/ override this with the actual server URL.
    """
    return None


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Switch to SQLite in-memory before the test database is created.

    pytest-django calls this fixture as a dependency of django_db_setup,
    right before setup_databases() is invoked.  Overriding DATABASES here
    ensures all @pytest.mark.django_db tests use SQLite and don't need a
    running PostgreSQL server.
    """
    from django.conf import settings
    from django.db import connections

    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    # Close all existing connections
    connections.close_all()
    # Delete the cached 'settings' property so ConnectionHandler re-reads
    # from django.conf.settings.DATABASES with our new SQLite config
    try:
        del connections.__dict__["settings"]
    except KeyError:
        pass
    # Reset _settings to None so configure_settings() re-reads from
    # django.conf.settings.DATABASES (our new SQLite config)
    connections._settings = None
    # Remove the cached 'default' connection from thread-local storage
    try:
        delattr(connections._connections, "default")
    except AttributeError:
        pass
