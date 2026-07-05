"""Website-local Django settings for TemplateTinker."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent

for _path in (
    _WORKSPACE_DIR,
    _WORKSPACE_DIR / "libs" / "ceptor-ai" / "src",
    _WORKSPACE_DIR / "libs" / "django-fusion" / "src",
):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

# ============================================================
# Site Configuration
# ============================================================
from configs.site import configure_site_environment

configure_site_environment("templatetinker", module="CMS", default_port=5073)

# ============================================================
# Import Shared Django Settings
# ============================================================
from configs.settings import *  # noqa: E402,F401,F403

# ============================================================
# URL and Application Configuration
# ============================================================
ROOT_URLCONF = "urls"
WSGI_APPLICATION = "server.application"
ASGI_APPLICATION = "server.asgi_application"

# ============================================================
# Website-Specific Settings
# ============================================================
WEBSITE_NAME = "templatetinker"
WEBSITE_IDENTIFIER = "templatetinker"
SITE_ID = 4

# ── Preserve backwards compatibility with CUSTOMIZER_SECRET_KEY ──
SECRET_KEY = os.environ.get("TINKER_SECRET_KEY", SECRET_KEY)

# ── Keep UTC timezone (shared i18n.py switches to Africa/Cairo in dev) ──
TIME_ZONE = "UTC"

# ── Local apps ───────────────────────────────────────────────
# Override the Wagtail-heavy shared INSTALLED_APPS with the
# customizer's minimal set.
LOCAL_APPS = [
    "chat.apps.ChatConfig",
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "webpack_loader",
    *LOCAL_APPS,
]

# ── Middleware ───────────────────────────────────────────────
# Override the Wagtail/allauth-heavy shared middleware with the
# customizer's minimal set.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ── Templates ───────────────────────────────────────────────
# Override the Wagtail-oriented shared template config with the
# customizer's own template directories.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [_SITE_DIR / "templates", _WORKSPACE_DIR / "assets" / "templates"],
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

# ── Database ────────────────────────────────────────────────
# Override shared databases (which may reference Postgres) with
# the customizer's local SQLite.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _SITE_DIR / "db.sqlite3",
    }
}

# ── Static files ────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = _SITE_DIR / "staticfiles"

STATICFILES_DIRS = []
_customizer_static = _SITE_DIR / "assets" / "static"
if _customizer_static.exists():
    STATICFILES_DIRS.append(str(_customizer_static))
_customizer_bundles = _SITE_DIR / "assets" / "bundles"
if _customizer_bundles.exists():
    STATICFILES_DIRS.append(str(_customizer_bundles))
if (_SITE_DIR / "static").exists():
    STATICFILES_DIRS.append(str(_SITE_DIR / "static"))

# ── Media ───────────────────────────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = _SITE_DIR / "assets" / "media"

# ── Webpack Loader ──────────────────────────────────────────
_site_bundles_dir = _SITE_DIR / "assets" / "bundles" / "customizer"
_bundles_json = _site_bundles_dir / "bundles.json"

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "customizer/",
        "STATS_FILE": str(_bundles_json),
        "POLL_INTERVAL": 0.1 if DEBUG else 300,
        "TIMEOUT": None if DEBUG else 120,
        "IGNORE": [r".+\.hot-update\.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
    }
}

# ── End Django defaults ─────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# Customizer-Specific Settings
# ============================================================
CUSTOMIZER_APPS = [
    {
        "slug": "ctc-research",
        "name": "CTC Research",
        "template_root": _WORKSPACE_DIR / "ctc-research" / "templates",
    },
    {
        "slug": "lms-demo",
        "name": "Structa LMS Demo",
        "template_root": _WORKSPACE_DIR / "lms-demo" / "templates",
    },
    {
        "slug": "VResume",
        "name": "VResume",
        "template_root": _WORKSPACE_DIR / "VResume" / "www" / "pages" / "templates",
    },
]

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
