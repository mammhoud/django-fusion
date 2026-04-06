# ====================================
# 🚀 Production Environment Settings
# ====================================
import os

from .core import *
from ..conf import settings

# ---- Core ----
DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

# ---- Wagtail ----
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "Alliance")
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "https://structa.cloud")
WAGTAILSEARCH_BACKENDS = {
    "default": {"BACKEND": "wagtail.search.backends.database"}
}
WAGTAILIMAGES_SERVE_METHOD = "direct"
WAGTAIL_CACHE = True
WAGTAIL_CACHE_BACKEND = "default"
WAGTAILEMBEDS_RESPONSIVE_HTML = True

# ---- Admin ----
ADMIN_SITE_HEADER = settings.get("ADMIN_SITE_HEADER", "Alliance Administration")
ADMIN_SITE_TITLE = settings.get("ADMIN_SITE_TITLE", "Alliance Admin")
ADMIN_INDEX_TITLE = settings.get("ADMIN_INDEX_TITLE", "Site Management")

# ---- Timing ----
TIME_ZONE = settings.get("TIME_ZONE", "UTC")
USE_TZ = True
SESSION_COOKIE_AGE = settings.get("SESSION_COOKIE_AGE", 604800)       # 1 week
SECURE_HSTS_SECONDS = settings.get("SECURE_HSTS_SECONDS", 31536000)   # 1 year
PASSWORD_RESET_TIMEOUT = settings.get("PASSWORD_RESET_TIMEOUT", 259200)  # 3 days
EMAIL_TIMEOUT = settings.get("EMAIL_TIMEOUT", 60)

# ---- Cache middleware ----
CACHE_MIDDLEWARE_SECONDS = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_SECONDS", 600)
CACHE_MIDDLEWARE_KEY_PREFIX = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_KEY_PREFIX", "prod")
CACHE_MIDDLEWARE_ALIAS = "default"
MIDDLEWARE += [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

# ---- i18n ----
USE_I18N = settings.get("USE_I18N", True)
USE_L10N = settings.get("USE_L10N", True)
LANGUAGE_CODE = settings.get("LANGUAGE_CODE", "en-us")

# ---- Templates (cached loader) ----
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]

# ---- Logging (JSON stdout — container friendly) ----
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
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "django.request": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "wagtail": {"level": "INFO", "handlers": ["console"], "propagate": False},
    },
}

# ---- Optional services ----
from .services import *
