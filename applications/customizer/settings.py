"""Django settings for the Structa template customizer."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APPLICATIONS_DIR = BASE_DIR.parent
REPO_ROOT = APPLICATIONS_DIR.parent

for path in (
    REPO_ROOT,
    APPLICATIONS_DIR,
    APPLICATIONS_DIR / "libs" / "crafts-ai" / "src",
    APPLICATIONS_DIR / "libs" / "django-osoul" / "src",
):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

SECRET_KEY = os.environ.get("CUSTOMIZER_SECRET_KEY", "django-insecure-customizer-dev")
DEBUG = os.environ.get("CUSTOMIZER_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("CUSTOMIZER_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chat.apps.ChatConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"
WSGI_APPLICATION = "server.application"
ASGI_APPLICATION = "server.asgi_application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", APPLICATIONS_DIR / "assets" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CUSTOMIZER_APPS = [
    {
        "slug": "ctc-research",
        "name": "CTC Research",
        "template_root": APPLICATIONS_DIR / "ctc-research" / "templates",
    },
    {
        "slug": "lms-demo",
        "name": "Structa LMS Demo",
        "template_root": APPLICATIONS_DIR / "lms-demo" / "templates",
    },
    {
        "slug": "VResume",
        "name": "VResume",
        "template_root": APPLICATIONS_DIR / "VResume" / "www" / "pages" / "templates",
    },
]

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
