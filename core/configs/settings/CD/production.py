# =======================================================
# 🚀 Production Environment Settings
# =======================================================
from .core import *   # common settings
import os
from ..conf import settings

# -------------------------------------------------------------------
# 🎛️ Main Switches
# -------------------------------------------------------------------
DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# -------------------------------------------------------------------
# 🏷️ Titling
# -------------------------------------------------------------------
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "Alliance")
ADMIN_SITE_HEADER = settings.get("ADMIN_SITE_HEADER", "Alliance Administration")
ADMIN_SITE_TITLE = settings.get("ADMIN_SITE_TITLE", "Alliance Admin")
ADMIN_INDEX_TITLE = settings.get("ADMIN_INDEX_TITLE", "Site Management")

# -------------------------------------------------------------------
# ⏱️ Timing
# -------------------------------------------------------------------
TIME_ZONE = settings.get("TIME_ZONE", "UTC")
USE_TZ = settings.get("USE_TZ", True)
SESSION_COOKIE_AGE = settings.get("SESSION_COOKIE_AGE", 604800)           # 1 week
SECURE_HSTS_SECONDS = settings.get("SECURE_HSTS_SECONDS", 31536000)      # 1 year
CACHE_MIDDLEWARE_SECONDS = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_SECONDS", 600)
CACHE_MIDDLEWARE_KEY_PREFIX = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_KEY_PREFIX", "prod")
PASSWORD_RESET_TIMEOUT = settings.get("PASSWORD_RESET_TIMEOUT", 259200)  # 3 days
EMAIL_TIMEOUT = settings.get("EMAIL_TIMEOUT", 60)                        # 1 minute

# -------------------------------------------------------------------
# 🎛️ Wagtail Core
# -------------------------------------------------------------------
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "https://example.com")
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",   # PostgreSQL full‑text
    }
}
WAGTAILIMAGES_SERVE_METHOD = "direct"                  # requires nginx X-Accel
WAGTAIL_CACHE = True
WAGTAIL_CACHE_BACKEND = "default"
WAGTAILEMBEDS_RESPONSIVE_HTML = True

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
