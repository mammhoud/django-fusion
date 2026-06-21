"""
Minimal Django settings for django-rseal tests.
"""
import os
import sys
from pathlib import Path

# Add tests directory to path so fake_accounts can be found
sys.path.insert(0, str(Path(__file__).parent))

SECRET_KEY = "django-rseal-test-secret-key"
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
    "wagtail",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.snippets",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.contrib.settings",
    "taggit",
    "modelcluster",
    "fake_accounts.apps.FakeAccountsConfig",  # Stub for accounts app
    "crafts_ai",
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
WAGTAIL_SITE_NAME = "Test"
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

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@example.com"

# Root URL configuration for testing
ROOT_URLCONF = "tests.urls"

# Django-rseal specific settings
DJANGO_RSEAL = {
    "EMAIL_TEMPLATE_CACHE_TIMEOUT": 3600,
}

# Profile model setting for django-rseal
PROFILE_MODEL = 'auth.User'

# Skip migrations that depend on external apps not in test environment
MIGRATION_MODULES = {
    'crafts_ai': None,  # Use in-memory schema creation instead
    'pipelines': None,     # Use in-memory schema creation instead
    'accounts': None,      # Fake accounts app - no migrations needed
}
