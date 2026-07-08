"""
Minimal Django settings for django-fusion tests.
"""
import os
import sys
from pathlib import Path

# Add tests directory to path so fake_accounts can be found
sys.path.insert(0, str(Path(__file__).parent))

# Add django-fusion src to path so the package can be imported
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

SECRET_KEY = "django-fusion-test-secret-key"
DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "fake_accounts.apps.FakeAccountsConfig",  # Stub for accounts app
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
SITE_ID = 1
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# Static and media files
STATIC_ROOT = os.path.join(Path(__file__).parent.parent, "static")
MEDIA_ROOT = os.path.join(Path(__file__).parent.parent, "media")
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Root URL configuration for testing
ROOT_URLCONF = "tests.urls"

# Skip migrations that depend on external apps not in test environment
MIGRATION_MODULES = {
    'django_fusion': None,
    'accounts': None,  # Fake accounts app - no migrations needed
}
