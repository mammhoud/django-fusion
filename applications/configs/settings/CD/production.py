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
WAGTAIL_CACHE_BACKEND = "default"
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
CACHE_MIDDLEWARE_ALIAS = "default"

# -------------------------------------------------------------------
# 🌍 Internationalisation
# -------------------------------------------------------------------
USE_I18N = settings.get("USE_I18N", True)
USE_L10N = settings.get("USE_L10N", True)
