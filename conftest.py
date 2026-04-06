"""
Pytest configuration for the Alliance/Structa project.
"""
import os

import django
from django.test.utils import override_settings


def pytest_configure(config):
    """Configure Django settings for pytest."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    os.environ.setdefault("DJANGO_PRINT_ENV", "false")

    # Provide required settings that may be missing in test environment
    from django.conf import settings as django_settings

    # django-rq requires RQ_QUEUES to be defined
    if not hasattr(django_settings, "RQ_QUEUES"):
        django_settings.RQ_QUEUES = {}
