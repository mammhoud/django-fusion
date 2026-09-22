"""
Pytest configuration for pos-cloud unit tests.

Overrides the global DJANGO_SETTINGS_MODULE (tests.settings) with a minimal
in-memory SQLite configuration. Uses django_db_modify_db_settings fixture
which runs after settings are configured but before the test database is created.
"""
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Override Django settings with minimal pos-cloud config BEFORE test DB creation."""
    from django.conf import settings

    _root = Path(__file__).resolve().parents[3]  # structa.cloud/
    _pos_cloud = _root / "projects" / "pos" / "pos-cloud"
    if str(_pos_cloud) not in sys.path:
        sys.path.insert(0, str(_pos_cloud))

    # Override the pre-configured settings from DJANGO_SETTINGS_MODULE
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    settings.INSTALLED_APPS = [
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "core",
    ]
    settings.MIDDLEWARE = [
        "django.middleware.common.CommonMiddleware",
    ]
    settings.SECRET_KEY = "test-secret-key"
    settings.DEBUG = True
    settings.ALLOWED_HOSTS = ["*"]
    settings.DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    settings.USE_TZ = True
    settings.STATIC_URL = "/static/"
    settings.MEDIA_URL = "/media/"
    settings.COMPONENTS_INCLUDE_PATH_ROOTS = []
    settings.FUSION_SITE_NAME = "pos_cloud"
    settings.FUSION_SITE_TITLE = "POS Cloud Test"
    settings.TEMPLATES = [{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }]

    # Close existing connections so the new SQLite DB takes effect
    from django.db import connections
    connections.close_all()
    try:
        del connections.__dict__["settings"]
    except KeyError:
        pass
    connections._settings = None
    try:
        delattr(connections._connections, "default")
    except AttributeError:
        pass
