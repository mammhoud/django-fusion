# ====================================
# 🎨 Assets & Static Files Configuration
# ====================================
import os
from pathlib import Path

from ..settings.conf import settings
from ..settings.conf import settings as tracker
from .paths import BASE_DIR

# ── Workspace root (websites/) ────────────────────────────────────────────────
WORKSPACE_DIR = BASE_DIR.parent          # websites/
SITE_NAME = BASE_DIR.name                # ctc-research.com or structa.cloud

# ── Per-site asset directories ────────────────────────────────────────────────
ASSETS_DIR   = BASE_DIR / "assets"
STATIC_DIR   = ASSETS_DIR / "static"
FIXTURES_DIR = ASSETS_DIR / "fixtures"

# ── Workspace-level shared directories ───────────────────────────────────────
# In Docker, bundles are inside the app directory, not at workspace level
import os

if os.getenv('RUNNING_ENV') == 'docker':
    BUNDLES_DIR = ASSETS_DIR / "bundles"           # /app/assets/bundles
    SHARED_STATIC_DIR = BASE_DIR / "shared" / "assets" / "static"  # /app/shared/assets/static
else:
    BUNDLES_DIR = WORKSPACE_DIR / "bundles" / SITE_NAME  # compiled webpack output
    SHARED_STATIC_DIR = WORKSPACE_DIR / "assets" / "static"  # websites/assets/static

STATICFILES_DIR  = ASSETS_DIR / "staticfiles"             # collectstatic output
SITE_STATIC_DIR  = STATIC_DIR                              # per-site assets/static/ (styles only)
MEDIA_DIR        = WORKSPACE_DIR / "assets" / "media"      # shared media
LOCALE_DIRS      = WORKSPACE_DIR / "assets" / "locale"     # shared locale

# Ensure directories exist
for directory in [ASSETS_DIR, STATIC_DIR, BUNDLES_DIR, STATICFILES_DIR,
                  FIXTURES_DIR, SHARED_STATIC_DIR, MEDIA_DIR, LOCALE_DIRS]:
    directory.mkdir(exist_ok=True, parents=True)

# ── Media ─────────────────────────────────────────────────────────────────────
MEDIA_ROOT = str(MEDIA_DIR)
MEDIA_URL  = settings.get("MEDIA_URL", "/media/")

FILE_UPLOAD_PERMISSIONS           = settings.get("FILE_UPLOAD_PERMISSIONS", 0o644)
FILE_UPLOAD_DIRECTORY_PERMISSIONS = settings.get("FILE_UPLOAD_DIRECTORY_PERMISSIONS", 0o755)
FILE_UPLOAD_MAX_MEMORY_SIZE       = settings.get("FILE_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024)
DATA_UPLOAD_MAX_MEMORY_SIZE       = settings.get("DATA_UPLOAD_MAX_MEMORY_SIZE", 50 * 1024 * 1024)
DATA_UPLOAD_MAX_NUMBER_FIELDS     = settings.get("DATA_UPLOAD_MAX_NUMBER_FIELDS", 10000)

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_ROOT = str(STATICFILES_DIR)
STATIC_URL  = settings.get("STATIC_URL", "/static/")

STATICFILES_DIRS = [
    str(BUNDLES_DIR),        # compiled webpack bundles
    str(SHARED_STATIC_DIR),  # shared assets (fonts, images, js, styles)
    str(SITE_STATIC_DIR),    # per-site assets (site-specific styles)
]

STATICFILES_FINDERS = settings.get("STATICFILES_FINDERS", [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
])

# ── Webpack Loader ────────────────────────────────────────────────────────────
_bundles_json = BUNDLES_DIR / "bundles.json"

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE":           not tracker.is_debug,
        "BUNDLE_DIR_NAME": f"bundles/{SITE_NAME}/",
        "STATS_FILE":      str(_bundles_json),
        "POLL_INTERVAL":   0.1 if tracker.is_debug else 300,
        "TIMEOUT":         None if tracker.is_debug else 120,
        "IGNORE":          [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": (
            "webpack_loader.loader.WebpackLoader"
            if _bundles_json.exists()
            else "webpack_loader.loaders.FakeWebpackLoader"
        ),
    }
}

# ── Locale ────────────────────────────────────────────────────────────────────
LOCALE_PATHS = [str(LOCALE_DIRS)]

# ── Fixtures ──────────────────────────────────────────────────────────────────
FIXTURE_DIRS = [str(FIXTURES_DIR)]

# ── Image processing ──────────────────────────────────────────────────────────
WAGTAILIMAGES_IMAGE_MODEL      = settings.get("WAGTAILIMAGES_IMAGE_MODEL", "wagtailimages.Image")
WAGTAILIMAGES_MAX_UPLOAD_SIZE  = settings.get("WAGTAILIMAGES_MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
WAGTAILIMAGES_MAX_IMAGE_PIXELS = settings.get("WAGTAILIMAGES_MAX_IMAGE_PIXELS", 128 * 1024 * 1024)
WAGTAILIMAGES_JPEG_QUALITY     = settings.get("WAGTAILIMAGES_JPEG_QUALITY", 85)
WAGTAILIMAGES_WEBP_QUALITY     = settings.get("WAGTAILIMAGES_WEBP_QUALITY", 85)

WAGTAILDOCS_EXTENSIONS   = settings.get("WAGTAILDOCS_EXTENSIONS", [
    "csv", "docx", "key", "odt", "pdf", "pptx", "rtf", "txt", "xlsx", "zip"
])
WAGTAILDOCS_SERVE_METHOD = settings.get("WAGTAILDOCS_SERVE_METHOD", "direct")

# ── Third-party API keys ──────────────────────────────────────────────────────
GOOGLE_MAP_API_KEY          = settings.get("GOOGLE_MAP_API_KEY", "")
GOOGLE_ANALYTICS_ID         = settings.get("GOOGLE_ANALYTICS_ID", "")
GOOGLE_RECAPTCHA_SITE_KEY   = settings.get("GOOGLE_RECAPTCHA_SITE_KEY", "")
GOOGLE_RECAPTCHA_SECRET_KEY = settings.get("GOOGLE_RECAPTCHA_SECRET_KEY", "")
