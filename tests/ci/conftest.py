"""
pytest configuration for ctc-research.com CI test suite.

Handles:
- Django setup
- Test database cleanup (drops stale test_db_ctc before each session)
- Shared fixtures
- Custom markers
"""
from __future__ import annotations

import os
import subprocess

import django
import pytest
from django.conf import settings as django_settings

# ---------------------------------------------------------------------------
# Django setup (for standalone pytest runs)
# ---------------------------------------------------------------------------
if not django_settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    os.environ.setdefault("DJANGO_PRINT_ENV", "false")
    django.setup()


# ---------------------------------------------------------------------------
# Custom markers
# ---------------------------------------------------------------------------
def pytest_configure(config):
    config.addinivalue_line("markers", "smtp: marks tests that send real SMTP emails")
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")


def pytest_sessionstart(session):
    """Drop stale test database before the test session starts."""
    try:
        subprocess.run(
            ["psql", "-h", "postgres", "-U", "postgres",
             "-c", "DROP DATABASE IF EXISTS test_db_ctc;"],
            capture_output=True, timeout=10,
        )
    except Exception:
        pass  # postgres may not be reachable — test runner will handle it


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=False)
def clear_email_outbox():
    """Clear Django email outbox before and after each test."""
    from django.core import mail
    mail.outbox = []
    yield
    mail.outbox = []


@pytest.fixture(autouse=False)
def clean_test_user():
    """Delete the test user before and after each test."""
    from .base.config import Credentials
    from .base.setup import UserFactory
    UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
    yield
    UserFactory.cleanup(Credentials.NEW_USER_EMAIL)
