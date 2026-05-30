# ====================================
# 🎨 Assets & Static Files Configuration
# ====================================
from ..settings.conf import settings
from ..settings.conf import settings as tracker
from .paths import BASE_DIR

# ── Workspace and asset directories ─────────────────────────────────────────
WORKSPACE_DIR = BASE_DIR.parent
SITE_NAME = BASE_DIR.name

# Shared repository-level assets. npm installs live here so every website uses
# one dependency tree: ``assets/node_modules``.
BASE_ASSETS_DIR = WORKSPACE_DIR / "assets"
BASE_NODE_MODULES_DIR = BASE_ASSETS_DIR / "node_modules"
SHARED_STATIC_DIR = BASE_ASSETS_DIR / "static"
SHARED_BUNDLES_DIR = BASE_ASSETS_DIR / "bundles" / "shared"
MEDIA_DIR = BASE_ASSETS_DIR / "media"
LOCALE_DIRS = BASE_ASSETS_DIR / "locale"

# Per-site assets and build outputs. Webpack writes selected website bundles to
# ``<site>/assets/bundles/<site-name>`` so collectstatic can preserve a stable
# URL namespace: ``/static/bundles/<site-name>/...``.
ASSETS_DIR = BASE_DIR / "assets"
STATIC_DIR = ASSETS_DIR / "static"
FIXTURES_DIR = ASSETS_DIR / "fixtures"
SITE_STATIC_DIR = STATIC_DIR
SITE_BUNDLES_DIR = ASSETS_DIR / "bundles" / SITE_NAME
BUNDLES_DIR = SITE_BUNDLES_DIR
STATICFILES_DIR = ASSETS_DIR / "staticfiles"

# Ensure directories exist
for directory in [
    BASE_ASSETS_DIR,
    BASE_NODE_MODULES_DIR,
    SHARED_STATIC_DIR,
    SHARED_BUNDLES_DIR,
    ASSETS_DIR,
    STATIC_DIR,
    SITE_BUNDLES_DIR,
    STATICFILES_DIR,
    FIXTURES_DIR,
    MEDIA_DIR,
    LOCALE_DIRS,
]:
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
    (f"bundles/{SITE_NAME}", str(SITE_BUNDLES_DIR)),
    ("bundles/shared", str(SHARED_BUNDLES_DIR)),
    str(SHARED_STATIC_DIR),
    (f"site/{SITE_NAME}", str(SITE_STATIC_DIR)),
]

STATICFILES_FINDERS = settings.get("STATICFILES_FINDERS", [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
])

# ── Webpack Loader ────────────────────────────────────────────────────────────
_bundles_json = SITE_BUNDLES_DIR / "bundles.json"

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
