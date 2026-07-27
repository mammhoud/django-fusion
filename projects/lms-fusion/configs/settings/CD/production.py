# =======================================================
# 🚀 Production Environment Settings
# =======================================================
import os

from ..conf import settings
from .core import *  # common settings

# -------------------------------------------------------------------
# 🎛️ Main Switches
# -------------------------------------------------------------------
DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", settings.DJANGO_SECRET_KEY)
# Keep production host validation sourced from configs/settings/ENV/security.yml.
# An ALLOWED_HOSTS env var may still override it when explicitly set.
ALLOWED_HOSTS = globals().get("ALLOWED_HOSTS", [])

# -------------------------------------------------------------------
# 🏷️ Titling
# -------------------------------------------------------------------
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "VResume")
ADMIN_SITE_HEADER = settings.get("ADMIN_SITE_HEADER", "VResume Administration")
ADMIN_SITE_TITLE = settings.get("ADMIN_SITE_TITLE", "VResume Admin")
ADMIN_INDEX_TITLE = settings.get("ADMIN_INDEX_TITLE", "Site Management")

# -------------------------------------------------------------------
# ⏱️ Timing
# -------------------------------------------------------------------
TIME_ZONE = settings.get("TIME_ZONE", "UTC")
USE_TZ = settings.get("USE_TZ", True)
SESSION_COOKIE_AGE = settings.get("SESSION_COOKIE_AGE", 604800)  # 1 week
SECURE_HSTS_SECONDS = settings.get("SECURE_HSTS_SECONDS", 31536000)  # 1 year
CACHE_MIDDLEWARE_SECONDS = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_SECONDS", 600)
CACHE_MIDDLEWARE_KEY_PREFIX = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_KEY_PREFIX", "prod")
PASSWORD_RESET_TIMEOUT = settings.get("PASSWORD_RESET_TIMEOUT", 259200)  # 3 days
EMAIL_TIMEOUT = settings.get("EMAIL_TIMEOUT", 60)  # 1 minute

# -------------------------------------------------------------------
# 🎛️ Wagtail Core
# -------------------------------------------------------------------
WAGTAILADMIN_BASE_URL = (
    os.environ.get("WAGTAILADMIN_BASE_URL")
    or os.environ.get("DJANGO_HOST")
    or f"https://{os.environ.get('SITE_DOMAIN', 'example.com')}"
)
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",  # PostgreSQL full‑text
    }
}
# Default to Django serving Wagtail image renditions directly when no
# dedicated media server / X-Accel proxy is present.
WAGTAILIMAGES_SERVE_METHOD = os.environ.get("WAGTAILIMAGES_SERVE_METHOD", "serve")
WAGTAIL_CACHE = True
# Use the shared `redis` alias (matches CACHE_MIDDLEWARE_ALIAS below) so that
# `cache.clear()` flushes the Wagtail page cache across all 4 gunicorn workers
# in one call. The previous value `"default"` was LocMemCache (per-process),
# which is why full container restarts were required to invalidate cached pages
# from EventPage and other Wagtail Page models.
WAGTAIL_CACHE_BACKEND = "redis"
WAGTAILEMBEDS_RESPONSIVE_HTML = True

# -------------------------------------------------------------------
# 🧪 Caching Middleware (Django core)
# -------------------------------------------------------------------
if "MIDDLEWARE" in dir():  # noqa: F821
    MIDDLEWARE += [  # noqa: F821
        "django.middleware.cache.UpdateCacheMiddleware",
        # ... your other middleware ...
        "django.middleware.cache.FetchFromCacheMiddleware",
    ]
# ---- Cache Middleware: Shared Redis (faster than FileBasedCache, survives restarts) ----
# Add a `redis` alias to CACHES that uses django_redis with a no-password URL.
# REDIS_URL has a password but Redis has no `requirepass` configured, so we
# strip the password here. `cache.clear()` affects all 4 gunicorn workers
# in one call and the cache survives container restarts. Faster than the
# `file` alias (FileBasedCache) because Redis is in-memory.
import os
import re as _re_cache

_redis_env = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
# Strip :password@ from the URL (keeps @host:port/db intact)
_redis_url_no_password = _re_cache.sub(r"://[^@]+@", "://", _redis_env)

CACHES["redis"] = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": _redis_url_no_password,
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
        "SOCKET_CONNECT_TIMEOUT": 5,
        "SOCKET_TIMEOUT": 5,
        "IGNORE_EXCEPTIONS": True,
    },
    "KEY_PREFIX": "django_cache",
    "TIMEOUT": CACHE_MIDDLEWARE_SECONDS,
}

# Re-declare the `session` alias that `projects/configs/base/cache.py` defines
# via `from configs.base import *`, but is then wiped out by `from .core import *`
# in CD/core.py (which overwrites CACHES with {default, file} keys only).
# Without `session`, `SESSION_ENGINE = django.contrib.sessions.backends.cache`
# fails with `InvalidCacheBackendError: The connection 'session' doesn't exist.`
_session_db = (_redis_url_no_password.rsplit("/", 1)[0]) + "/1"
CACHES["session"] = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": _session_db,
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
        "IGNORE_EXCEPTIONS": True,
    },
    "KEY_PREFIX": "django_session",
}

CACHE_MIDDLEWARE_ALIAS = "redis"

# -------------------------------------------------------------------
# 🌍 Internationalisation
# -------------------------------------------------------------------
USE_I18N = settings.get("USE_I18N", True)
USE_L10N = settings.get("USE_L10N", True)
