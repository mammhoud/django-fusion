"""Initial smoke tests for lms-fusion.

Verifies the test runner, Django configuration, and basic imports work.
"""

from __future__ import annotations

from django.conf import settings
from django.test import Client, RequestFactory


class TestDjangoSetup:
    """Verify Django is configured correctly for tests."""

    def test_settings_loaded(self):
        """Django settings are accessible."""
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0
        assert settings.USE_TZ is True

    def test_middleware_contains_session(self):
        """SessionMiddleware is in MIDDLEWARE."""
        assert any(
            "SessionMiddleware" in m for m in settings.MIDDLEWARE
        )

    def test_database_engine_is_sqlite(self):
        """Database is configured as SQLite for testing."""
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"

    def test_allowed_hosts_configured(self):
        """ALLOWED_HOSTS is configured (not empty)."""
        assert len(settings.ALLOWED_HOSTS) > 0


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
    """Verify lms-fusion specific configuration."""

    def test_site_name_in_environment(self):
        """The WEBSITE environment variable is set."""
        import os
        assert os.environ.get("WEBSITE") is not None
        assert os.environ.get("WEBSITE_NAME") is not None
