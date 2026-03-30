# ====================================
# 🎪 Demo Environment Settings
# ====================================
from .core import *
from ..conf import settings

# -------------------------------------------------------------------
# 🎛️ Main Switches
# -------------------------------------------------------------------
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# -------------------------------------------------------------------
# 🏷️ Titling
# -------------------------------------------------------------------
WAGTAIL_SITE_NAME = settings.get("WAGTAIL_SITE_NAME", "Alliance (Demo)")
ADMIN_SITE_HEADER = settings.get("ADMIN_SITE_HEADER", "Alliance Demo Administration")
ADMIN_SITE_TITLE = settings.get("ADMIN_SITE_TITLE", "Alliance Demo Admin")
ADMIN_INDEX_TITLE = settings.get("ADMIN_INDEX_TITLE", "Demo Management")

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
