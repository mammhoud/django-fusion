"""Test settings for precis-ctc — inherits real settings, overrides DB to SQLite.

Uses the real INSTALLED_APPS (Wagtail, django_fusion, domain models, etc.)
but replaces the database with an in-memory SQLite backend so tests run
without Docker/Postgres. The project's committed migrations are applied by
the test runner so schema drift is detected instead of being hidden.
"""

import os

# Force development profile so configs.settings picks up the right base
os.environ["SERVER_ENV"] = "development"
os.environ["DJANGO_SERVER_ENV"] = "development"
os.environ["WEBSITE"] = "precis-ctc"
os.environ["WEBSITE_NAME"] = "precis-ctc"

# Import ALL real settings (Wagtail, domain apps, middleware, etc.)
# pylint: disable=wildcard-import,unused-wildcard-import
from settings import *  # noqa: E402, F403

# ── Override database to in-memory SQLite ───────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Test clients use plain HTTP and should exercise API responses directly,
# without production proxy HTTPS redirects.
DEBUG = True
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

