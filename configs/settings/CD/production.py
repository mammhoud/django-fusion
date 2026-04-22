# =======================================================
# 🚀 Production Environment Settings
# =======================================================
import os
import secrets
from pathlib import Path

from ..conf import settings
from .core import *  # common settings


# -------------------------------------------------------------------
# 🔑 Secret Key — read from secret.key.txt, generate if missing
# -------------------------------------------------------------------
def _get_or_create_secret_key() -> str:
    """
    Load SECRET_KEY from secret.key.txt (project root).
    If the file doesn't exist or is empty, generate a new key,
    persist it to the file, and return it.
    Never reads from or writes to .env.
    """
    key_file = Path(__file__).resolve().parent.parent.parent.parent / "secret.key.txt"
    # 1. Try the file
    if key_file.exists():
        try:
            line = key_file.read_text(encoding="utf-8").splitlines()[0].strip()
            if line and not line.startswith("#"):
                os.environ.setdefault("DJANGO_SECRET_KEY", line)
                return line
        except Exception:
            pass
    # 2. Try env var (set by conf.py _load_secret_key or Docker env)
    env_key = os.environ.get("DJANGO_SECRET_KEY", "")
    if env_key and env_key not in ("change-this-in-production-with-environment-variable",):
        return env_key
    # 3. Generate a new key and persist it
    new_key = "django-" + secrets.token_urlsafe(50)
    try:
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_text(new_key + "\n", encoding="utf-8")
    except Exception:
        pass
    os.environ["DJANGO_SECRET_KEY"] = new_key
    return new_key


SECRET_KEY = _get_or_create_secret_key()

# -------------------------------------------------------------------
# 🎛️ Main Switches
# -------------------------------------------------------------------
DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# -------------------------------------------------------------------
# 🔐 Production Security (Requirements: 9.6, 9.7, 9.8)
# -------------------------------------------------------------------
# SSL redirect is handled by Traefik — Django must NOT redirect or
# Traefik's health check gets a 301 and marks the backend as unhealthy.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# -------------------------------------------------------------------
# 🏷️ Titling
# -------------------------------------------------------------------
# WAGTAIL_SITE_NAME, ADMIN_SITE_HEADER, ADMIN_SITE_TITLE, ADMIN_INDEX_TITLE
# are defined in configs/base/admin_site.py and configs/base/wagtail.py.
# Override here only if production needs a different value.

# -------------------------------------------------------------------
# ⏱️ Timing
# -------------------------------------------------------------------
TIME_ZONE = settings.get("TIME_ZONE", "UTC")
USE_TZ = settings.get("USE_TZ", True)
SESSION_COOKIE_AGE = settings.get("SESSION_COOKIE_AGE", 604800)           # 1 week
CACHE_MIDDLEWARE_SECONDS = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_SECONDS", 600)
CACHE_MIDDLEWARE_KEY_PREFIX = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_KEY_PREFIX", "prod")
PASSWORD_RESET_TIMEOUT = settings.get("PASSWORD_RESET_TIMEOUT", 259200)  # 3 days
EMAIL_TIMEOUT = settings.get("EMAIL_TIMEOUT", 60)                        # 1 minute

# -------------------------------------------------------------------
# 🎛️ Wagtail Core (production overrides only)
# -------------------------------------------------------------------
# Base Wagtail settings live in configs/base/wagtail.py.
# Only override what differs in production:
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "https://structa.cloud")
WAGTAIL_CACHE = True

# -------------------------------------------------------------------
# 📝 Logging (JSON to stdout – container friendly)
# -------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "django.request": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "wagtail": {"level": "INFO", "handlers": ["console"], "propagate": False},
    },
}

# -------------------------------------------------------------------
# 🧪 Caching Middleware (Django core)
# -------------------------------------------------------------------
MIDDLEWARE += [  # appended to base MIDDLEWARE
    "django.middleware.cache.UpdateCacheMiddleware",
    # ... your other middleware ...
    "django.middleware.cache.FetchFromCacheMiddleware",
]
CACHE_MIDDLEWARE_ALIAS = "default"

# -------------------------------------------------------------------
# 🌍 Internationalisation
# -------------------------------------------------------------------
USE_I18N = settings.get("USE_I18N", True)
USE_L10N = settings.get("USE_L10N", True)
LANGUAGE_CODE = settings.get("LANGUAGE_CODE", "en-us")

# -------------------------------------------------------------------
# 🧰 Templates (cached loader)
# -------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]

# -------------------------------------------------------------------
# ✅ Reminders
# -------------------------------------------------------------------
# 1. Run `python manage.py migrate` to create session table.
# 2. Run `python manage.py collectstatic --noinput`.
# 3. Set all required environment variables.


# -------------------------------------------------------------------
# 📦 Optional Services
# -------------------------------------------------------------------
from .services import *
