"""
Django settings for Solo POS Portal.
Extends VResume pattern with sync client for cloud CRM.

@tested pos-portal/solo - Portal settings with sync
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.environ.get("SOLO_PORTAL_SECRET_KEY", "solo-dev-secret-key")
DEBUG = os.environ.get("SOLO_PORTAL_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("SOLO_PORTAL_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_fusion.comp",
    "django_fusion.core",
    "shared",
    "portal",
    "node",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "portal" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "django_fusion.comp.templatetags.component_tags",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "solo_portal.db",
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Solo-specific: Cloud CRM sync configuration
CLOUD_CRM_URL = os.environ.get("CLOUD_CRM_URL", "http://localhost:8082")
CLOUD_CRM_API_KEY = os.environ.get("CLOUD_CRM_API_KEY", "")
SYNC_INTERVAL = int(os.environ.get("SYNC_INTERVAL", "60"))
