"""Website-local Django settings for Cypercloud (AI Chat Customizer).

This settings module uses Dynaconf for multi-environment configuration management.
"""

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
    _WORKSPACE_DIR / "libs" / "django-fusion" / "src",
):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

# ============================================================
# Basic Django Settings
# ============================================================

# SECRET_KEY
SECRET_KEY = os.environ.get(
    "CYPERCLOUD_SECRET_KEY",
    "django-insecure-cypercloud-dev-change-in-production"
)

# DEBUG Mode
DEBUG = os.environ.get("CYPERCLOUD_DEBUG", "true").lower() in ("true", "1", "yes", "on")

# ALLOWED_HOSTS
_hosts_env = os.environ.get("CYPERCLOUD_ALLOWED_HOSTS", "localhost,127.0.0.1,cypercloud.localhost")
ALLOWED_HOSTS = [h.strip() for h in _hosts_env.split(",")]

# Site Configuration
WEBSITE_NAME = "cypercloud"
WEBSITE_IDENTIFIER = "cypercloud"
SITE_ID = 4

TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

# ============================================================
# Django Core Apps
# ============================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "webpack_loader",
    "chat.apps.ChatConfig",
]

# ============================================================
# Middleware
# ============================================================
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

# ============================================================
# URL and Application Configuration
# ============================================================
ROOT_URLCONF = "urls"
WSGI_APPLICATION = "server.application"
ASGI_APPLICATION = "server.asgi_application"

# ============================================================
# Templates
# ============================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            _SITE_DIR / "templates",
            _WORKSPACE_DIR / "assets" / "templates",
        ],
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

# ============================================================
# Database
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _SITE_DIR / "db.sqlite3",
    }
}

# ============================================================
# Static Files
# ============================================================
STATIC_URL = "/static/"
STATIC_ROOT = _SITE_DIR / "staticfiles"

STATICFILES_DIRS = []
for _legacy_path in [
    _SITE_DIR / "assets" / "static",
    _SITE_DIR / "assets" / "bundles",
    _SITE_DIR / "static",
]:
    if _legacy_path.exists() and str(_legacy_path) not in STATICFILES_DIRS:
        STATICFILES_DIRS.append(str(_legacy_path))

# ============================================================
# Media Files
# ============================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = _SITE_DIR / "assets" / "media"

# ============================================================
# Webpack Loader
# ============================================================
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

# ============================================================
# Security Settings
# ============================================================
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True

# ============================================================
# Logging Configuration
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(message)s"},
        "verbose": {
            "format": "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple" if DEBUG else "verbose",
            "level": "DEBUG" if DEBUG else "INFO",
        }
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "cypercloud": {"handlers": ["console"], "level": "DEBUG"},
    },
}

# ============================================================
# Cache Configuration
# ============================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "cypercloud-cache",
        "TIMEOUT": 300,
    }
}

# ============================================================
# Email Configuration
# ============================================================
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend" if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() in ("true", "1")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@cypercloud.local")

# ============================================================
# REST Framework
# ============================================================
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour"},
}

# ============================================================
# AI Model Configuration
# ============================================================
MODELS_REGISTRY_FILE = "configs/models.yml"
MODELS_DEFAULT_PROVIDER = "ollama"
MODELS_TIMEOUT = 60

# Lazily initialize registries
def _get_dynaconf_settings():
    """Lazy-load Dynaconf settings on first access."""
    try:
        from django_fusion.config.loader import (
            DynaconfSettings,
            ModelsRegistry,
            TemplateRegistry,
        )
        
        _dynaconf = DynaconfSettings(
            config_dir=str(_SITE_DIR / "configs"),
            load_dotenv=True,
        ).load()
        
        return {
            "dynaconf": _dynaconf,
            "models": ModelsRegistry(_dynaconf),
            "templates": TemplateRegistry(_dynaconf),
        }
    except Exception as e:
        # If Dynaconf fails, return None - registries will use defaults
        import logging
        logging.warning(f"Dynaconf initialization failed: {e}")
        return None

_dynaconf_data = None

def get_dynaconf_data():
    global _dynaconf_data
    if _dynaconf_data is None:
        _dynaconf_data = _get_dynaconf_settings()
    return _dynaconf_data or {}

def get_models_registry():
    """Get models registry (with Dynaconf fallback)."""
    data = get_dynaconf_data()
    return data.get("models")

def get_templates_registry():
    """Get templates registry (with Dynaconf fallback)."""
    data = get_dynaconf_data()
    return data.get("templates")

def get_models():
    """Get all configured AI models."""
    reg = get_models_registry()
    if reg:
        return reg.list_models()
    return []

def get_model(model_id: str):
    """Get a specific model by ID."""
    reg = get_models_registry()
    if reg:
        return reg.get_model(model_id)
    return None

def get_default_model(provider: str = None):
    """Get default model, optionally filtered by provider."""
    reg = get_models_registry()
    if reg:
        return reg.get_default_model(provider)
    return None

# ============================================================
# Ollama Configuration
# ============================================================
OLLAMA_ENABLED = True
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT = 60

# ============================================================
# Ceptor-AI Configuration
# ============================================================
CEPTOR_AI_ENABLED = True
CEPTOR_AI_AGENTS_DIR = "../../application/kilo/agent/"
CEPTOR_AI_MODELS_FILE = "../../application/kilo/models.yml"

# ============================================================
# Template Sites Configuration
# ============================================================
CUSTOMIZER_APPS = [
    {
        "slug": "precis-ctc",
        "name": "CTC Research",
        "template_root": _WORKSPACE_DIR / "precis-ctc" / "templates",
    },
    {
        "slug": "lms",
        "name": "Structa LMS Demo",
        "template_root": _WORKSPACE_DIR / "lms" / "templates",
    },
    {
        "slug": "VResume",
        "name": "VResume",
        "template_root": _WORKSPACE_DIR / "VResume" / "www" / "pages" / "templates",
    },
]

# ============================================================
# Django Defaults
# ============================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
