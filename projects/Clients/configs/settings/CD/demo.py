# ====================================
# 🎪 Demo Environment Settings
# ====================================
from ..conf import settings
from .core import *

# -------------------------------------------------------------------
# 🎛️ Main Switches
# -------------------------------------------------------------------
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# -------------------------------------------------------------------
# 🏷️ Titling
# -------------------------------------------------------------------
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "CTC Hub (Demo)")
# ADMIN_SITE_HEADER / ADMIN_SITE_TITLE / ADMIN_INDEX_TITLE removed 2026-09-21
# (deletion-manifest DOC-0033): no reader anywhere in the repository.

# -------------------------------------------------------------------
# ⏱️ Timing
# -------------------------------------------------------------------
TIME_ZONE = settings.get("LOCAL_TIME_ZONE", settings.get("TIME_ZONE", "Africa/Cairo"))
USE_TZ = settings.get("USE_TZ", True)
CACHE_MIDDLEWARE_SECONDS = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_SECONDS", 60)
CACHE_MIDDLEWARE_KEY_PREFIX = settings.get("PERFORMANCE.CACHE_MIDDLEWARE_KEY_PREFIX", "demo_middleware")
SESSION_COOKIE_AGE = settings.get("SESSION_COOKIE_AGE", 3600)             # 1 hour
PASSWORD_RESET_TIMEOUT = settings.get("PASSWORD_RESET_TIMEOUT", 3600)     # 1 hour
EMAIL_TIMEOUT = settings.get("EMAIL_TIMEOUT", 30)                         # 30 seconds

# -------------------------------------------------------------------
# 🔄 Database Fixtures
# -------------------------------------------------------------------
# Load demo data fixtures
FIXTURE_DIRS = [BASE_DIR / "fixtures" / "demo"]
LOAD_DEMO_DATA = True

# -------------------------------------------------------------------
# 📄 Template Configuration
# -------------------------------------------------------------------
# TEMPLATES[0]["OPTIONS"]["string_if_invalid"] = "NULL"  # Show errors

# -------------------------------------------------------------------
# 🎪 Demo Banner
# -------------------------------------------------------------------
# Add demo banner to all pages
DEMO_BANNER = {
    "ENABLED": True,
    "MESSAGE": "This is a demo environment. Data may be reset periodically.",
    "BACKGROUND_COLOR": "#F59E0B",  # Amber
    "TEXT_COLOR": "#1F2937",  # Gray 900
}

# -------------------------------------------------------------------
# 📦 Optional Services
# -------------------------------------------------------------------
from .services import *
