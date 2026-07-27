"""Initial smoke tests for cms-fusion.

Verifies the test runner, Django configuration, and basic imports work.
"""

from __future__ import annotations

from django.conf import settings
from django.test import Client, RequestFactory


class TestDjangoSetup:
    """Verify Django is configured correctly for tests."""

    def test_settings_loaded(self):
        """Django settings are accessible."""
        assert settings.SECRET_KEY == "test-secret-key-cms-fusion"
        assert settings.USE_TZ is True

    def test_middleware_contains_session(self):
        """SessionMiddleware is in MIDDLEWARE."""
        assert any(
            "SessionMiddleware" in m for m in settings.MIDDLEWARE
        )

    def test_database_engine_is_sqlite(self):
        """Database is configured as SQLite for testing."""
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"

    def test_allowed_hosts_allows_all(self):
        """ALLOWED_HOSTS allows all hosts for testing (testserver added by pytest-django)."""
        assert "*" in settings.ALLOWED_HOSTS


class TestDjangoComponents:
    """Verify Django test utilities work."""

    def test_client_instantiation(self):
        """Django test client can be instantiated."""
        client = Client()
        assert client is not None

    def test_request_factory_works(self):
        """Django RequestFactory can create requests."""
        factory = RequestFactory()
        request = factory.get("/test")
        assert request.method == "GET"
        assert request.path == "/test"

    def test_basic_assertion(self):
        """Basic Python assertions work in the test runner."""
        assert 1 + 1 == 2
        assert isinstance("hello", str)
        assert [1, 2, 3] == [1, 2, 3]


class TestSiteConfiguration:
    """Verify cms-fusion specific configuration."""

    def test_site_name_in_environment(self):
        """The WEBSITE environment variable is set correctly."""
        import os
        assert os.environ.get("WEBSITE") == "cms-fusion"
        assert os.environ.get("WEBSITE_NAME") == "cms-fusion"
