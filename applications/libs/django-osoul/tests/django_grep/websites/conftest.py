"""Fixtures for website integration tests."""
import os

import pytest


@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("SELENIUM_BASE_URL", "")
    if not url:
        pytest.skip("SELENIUM_BASE_URL not set — integration test requires a running server")
    return url
