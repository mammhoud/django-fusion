"""pytest configuration for lms-fusion.

Configures a minimal Django environment so the test runner works
without depending on Docker infrastructure.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import django
from django.conf import settings

# ── Path setup ──────────────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent.parent  # projects/lms-fusion/backend

for _path in (
    str(_SITE_DIR),          # backend/
    str(_SITE_DIR / "www"),  # backend/www/
    str(_SITE_DIR.parent),   # lms-fusion/
):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# Set site-specific env vars (NOT DJANGO_SETTINGS_MODULE — that conflicts
# with pytest-django which will try to import the real settings module).
os.environ.setdefault("WEBSITE", "lms-fusion")
os.environ.setdefault("WEBSITE_NAME", "lms-fusion")
os.environ.setdefault("PROJECT_PATH", "lms-fusion")

# ── Django settings bootstrap ───────────────────────────────────────────────
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key-lms-fusion",
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "django.contrib.staticfiles",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "/tmp/lms_fusion_test.sqlite3",
                "TEST": {"NAME": "/tmp/lms_fusion_test.sqlite3"},
            },
        },
        USE_TZ=True,
        LANGUAGE_CODE="en-us",
        TIME_ZONE="UTC",
        USE_I18N=True,
        STATIC_URL="/static/",
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    )
    django.setup()
