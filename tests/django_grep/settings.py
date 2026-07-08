"""
Minimal Django settings for running centralized tests.
"""
import os
from pathlib import Path

SECRET_KEY = "django-grep-test-secret-key"
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
    "wagtail",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.snippets",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.contrib.settings",
    "taggit",
    "modelcluster",
    "django_fusion",
    "ceptor_ai",
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

# Health check configuration
SERVICE_NAME = "django-grep-test"
VERSION = "0.1.1"

# Profile model for django-fusion
PROFILE_MODEL = 'auth.User'

# Static and media files for health checks
STATIC_ROOT = os.path.join(Path(__file__).parent.parent, "static")
MEDIA_ROOT = os.path.join(Path(__file__).parent.parent, "media")
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Root URL configuration for testing
ROOT_URLCONF = "django_grep.urls"
