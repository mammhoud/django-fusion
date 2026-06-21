"""Selenium test fixtures — re-exported from django_grep.tests.pytest_plugin."""
import os
import pytest


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("SELENIUM_BASE_URL", "http://localhost:8000")


# selenium_driver fixture is auto-registered via pytest11 entry point
