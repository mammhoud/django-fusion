# ====================================
# 🎨 Assets & Static Files Configuration
# ====================================

from ..settings.conf import settings as conf_settings
from ..settings.setup import settings
from .paths import BASE_DIR

# -------------------------------
# Assets Directory Configuration
# -------------------------------
ASSETS_DIR = BASE_DIR / "assets"
MEDIA_DIR = ASSETS_DIR / "media"
STATIC_DIR = ASSETS_DIR / "static"
BUNDLES_DIR = ASSETS_DIR / "bundles"
FIXTURES_DIR = ASSETS_DIR / "fixtures"
LOCALE_DIRS = ASSETS_DIR / "locale"

# Ensure directories exist
for directory in [ASSETS_DIR, MEDIA_DIR, STATIC_DIR, BUNDLES_DIR, FIXTURES_DIR, LOCALE_DIRS]:
    directory.mkdir(exist_ok=True, parents=True)

# -------------------------------
# Media Files Configuration
# -------------------------------
MEDIA_ROOT = str(MEDIA_DIR)
MEDIA_URL = settings.get("MEDIA_URL", "/media/", block="STORAGE")

# -------------------------------
# Static Files Configuration
# -------------------------------
STATIC_ROOT = str(ASSETS_DIR / "staticfiles")
STATIC_URL = settings.get("STATIC_URL", "/static/", block="STORAGE")

# Static files directories
STATICFILES_DIRS = [
    str(BUNDLES_DIR),
    str(STATIC_DIR),
]

# Static files finders
STATICFILES_FINDERS = settings.get(
    "STATICFILES_FINDERS",
    [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ],
)

# ------------------------------
# Webpack Loader Configuration
# ------------------------------
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not conf_settings.is_debug,
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": str(BUNDLES_DIR / "bundles.json"),
        "POLL_INTERVAL": 0.1 if conf_settings.is_debug else 300,
        "TIMEOUT": None if conf_settings.is_debug else 120,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
        "IGNORE_MISSING_BUNDLES": True,
    }
}

# -------------------------------
# Fixtures Configuration
# -------------------------------
FIXTURE_DIRS = [str(FIXTURES_DIR)]

# -------------------------------
# Third-Party API Keys
# -------------------------------
GOOGLE_MAP_API_KEY = settings.get("GOOGLE_MAP_API_KEY", "")
GOOGLE_ANALYTICS_ID = settings.get("GOOGLE_ANALYTICS_ID", "")
GOOGLE_RECAPTCHA_SITE_KEY = settings.get("GOOGLE_RECAPTCHA_SITE_KEY", "")
GOOGLE_RECAPTCHA_SECRET_KEY = settings.get("GOOGLE_RECAPTCHA_SECRET_KEY", "")
