# ====================================
# 🎨 Assets & Static Files Configuration
# ====================================
from ..settings.conf import settings
from .paths import BASE_DIR

# ── Workspace and asset directories ─────────────────────────────────────────
WORKSPACE_DIR = BASE_DIR.parent
# The directory on disk for VResume is capital-V "VResume" but webpack (see
# webpack/main.config.js) writes bundles to the lowercase "vresume"
# subdirectory.  The Nginx shared-media container also serves
# /static/bundles/vresume/ (lowercase).  Normalise so that
# STATS_FILE, BUNDLE_DIR_NAME, and STATICFILES_DIRS all point at the
# same directory webpack actually writes to.
BUNDLE_SITE_NAME = BASE_DIR.name
if BUNDLE_SITE_NAME == "VResume":
    BUNDLE_SITE_NAME = "vresume"

# Shared repository-level assets. npm installs live here so every website uses
# one dependency tree: ``assets/node_modules``.
BASE_ASSETS_DIR = WORKSPACE_DIR / "assets"
SHARED_STATIC_DIR = BASE_ASSETS_DIR / "static"
LOCALE_DIRS = BASE_ASSETS_DIR / "locale"

# Per-site assets and build outputs. Webpack writes selected website bundles to
# ``<site>/assets/bundles/<site-name>`` so collectstatic can preserve a stable
# URL namespace: ``/static/bundles/<site-name>/...``.
ASSETS_DIR = BASE_DIR / "assets"
MEDIA_DIR = ASSETS_DIR / "media"
STATIC_DIR = ASSETS_DIR / "static"
FIXTURES_DIR = ASSETS_DIR / "fixtures"
SITE_STATIC_DIR = STATIC_DIR
SITE_BUNDLES_DIR = ASSETS_DIR / "bundles" / BUNDLE_SITE_NAME
SHARED_BUNDLES_DIR = BASE_ASSETS_DIR / "bundles" / "shared"

# Ensure source/runtime directories exist. Generated webpack and collectstatic
# outputs (bundles/staticfiles) are intentionally not created here so empty build
# directories do not appear just from importing Django settings.
for directory in [
    BASE_ASSETS_DIR,
    SHARED_STATIC_DIR,
    ASSETS_DIR,
    STATIC_DIR,
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
STATIC_URL  = settings.get("STATIC_URL", "/static/")

# collectstatic must always have a filesystem destination. Keep generated
# files under the active website so both ctc-research and lms-demo can be
# collected independently while sharing the same workspace image.
STATIC_ROOT = str(settings.get("STATIC_ROOT", ASSETS_DIR / "staticfiles"))

_staticfiles_candidates = [
    (f"bundles/{BUNDLE_SITE_NAME}", SITE_BUNDLES_DIR),
    ("bundles/shared", SHARED_BUNDLES_DIR),
    (None, SHARED_STATIC_DIR),
    (f"site/{BUNDLE_SITE_NAME}", SITE_STATIC_DIR),
]
STATICFILES_DIRS = [
    (prefix, str(path)) if prefix else str(path)
    for prefix, path in _staticfiles_candidates
    if path.exists()
]

STATICFILES_FINDERS = settings.get("STATICFILES_FINDERS", [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
])

# ── Webpack Loader ────────────────────────────────────────────────────────────
_bundles_json = SITE_BUNDLES_DIR / "bundles.json"

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE":           not settings.is_debug,
        "BUNDLE_DIR_NAME": f"/static/bundles/{BUNDLE_SITE_NAME}/",
        "STATS_FILE":      str(_bundles_json),
        "POLL_INTERVAL":   0.1 if settings.is_debug else 300,
        "TIMEOUT":         None if settings.is_debug else 120,
        "IGNORE":          [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS":    "webpack_loader.loaders.WebpackLoader",
    }
}


# Webpack loader compatibility patch now lives in django-fusion
# (see ``django_fusion/comp/webpack_compat.py``). It is invoked
# from ``CoreExtAppConfig.ready()`` so every site that loads
# ``django_fusion`` auto-inherits the fix without duplicating it.

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
