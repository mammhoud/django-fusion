# ====================================
# 🎨 Assets & Static Files Configuration
# ====================================
from pathlib import Path

from ..settings.conf import settings as tracker
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
MEDIA_URL = settings.get("MEDIA_URL", "/media/")

# Media file permissions
FILE_UPLOAD_PERMISSIONS = settings.get("FILE_UPLOAD_PERMISSIONS", 0o644)
FILE_UPLOAD_DIRECTORY_PERMISSIONS = settings.get("FILE_UPLOAD_DIRECTORY_PERMISSIONS", 0o755)

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = settings.get("FILE_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024)  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = settings.get("DATA_UPLOAD_MAX_MEMORY_SIZE", 50 * 1024 * 1024)  # 50MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings.get("DATA_UPLOAD_MAX_NUMBER_FIELDS", 10000)

# -------------------------------
# Static Files Configuration
# -------------------------------
STATIC_ROOT = str(ASSETS_DIR / "staticfiles")
STATIC_URL = settings.get("STATIC_URL", "/static/")

# Static files directories
STATICFILES_DIRS = [
    str(BUNDLES_DIR),
    str(STATIC_DIR),
    # str(MEDIA_DIR / "images"),
]

# Static files finders
STATICFILES_FINDERS = settings.get("STATICFILES_FINDERS", [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # "compressor.finders.CompressorFinder",
    # "pipeline.finders.PipelineFinder",
])

# -------------------------------
# Webpack Loader Configuration
# -------------------------------
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not tracker.is_debug,
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": str(BUNDLES_DIR / "bundles.json"),
        "POLL_INTERVAL": 0.1 if tracker.is_debug else 300,
        "TIMEOUT": None if tracker.is_debug else 120,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
    }
}

# -------------------------------
# Django Compressor Configuration
# -------------------------------
COMPRESS_ENABLED = settings.get("COMPRESS_ENABLED", not tracker.is_debug)
COMPRESS_OFFLINE = settings.get("COMPRESS_OFFLINE", tracker.is_production)
COMPRESS_CSS_HASHING_METHOD = settings.get("COMPRESS_CSS_HASHING_METHOD", "content")
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
COMPRESS_STORAGE = settings.get("COMPRESS_STORAGE", "compressor.storage.CompressorFileStorage")

# Compressor filters
COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
    ],
    "js": [
        "compressor.filters.jsmin.JSMinFilter",
    ],
}

# Compressor precompilers
COMPRESS_PRECOMPILERS = settings.get("COMPRESS_PRECOMPILERS", [
    ("text/x-scss", "django_libsass.SassCompiler"),
    ("text/x-sass", "django_libsass.SassCompiler"),
    ("text/less", "lessc {infile} {outfile}"),
])

# -------------------------------
# Django Pipeline Configuration
# -------------------------------
PIPELINE = {
    "PIPELINE_ENABLED": settings.get("PIPELINE_ENABLED", tracker.is_production),
    "JS_COMPRESSOR": settings.get("PIPELINE_JS_COMPRESSOR", "pipeline.compressors.uglifyjs.UglifyJSCompressor"),
    "CSS_COMPRESSOR": settings.get("PIPELINE_CSS_COMPRESSOR", "pipeline.compressors.cssmin.CSSMinCompressor"),
    "STYLESHEETS": settings.get("PIPELINE_STYLESHEETS", {
        "main": {
            "source_filenames": [
                "css/vendors.css",
                "css/app.css",
            ],
            "output_filename": "css/styles.min.css",
            "extra_context": {
                "media": "screen,projection",
            },
        },
    }),
    "JAVASCRIPT": settings.get("PIPELINE_JAVASCRIPT", {
        "main": {
            "source_filenames": [
                "js/vendors.js",
                "js/app.js",
            ],
            "output_filename": "js/app.min.js",
            "extra_context": {
                "async": True,
            },
        },
    }),
}

# Pipeline storage
STATICFILES_STORAGE = settings.get(
    "STATICFILES_STORAGE",
    "pipeline.storage.PipelineManifestStorage" if PIPELINE["PIPELINE_ENABLED"] else "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)

# -------------------------------
# File Type Configuration
# -------------------------------
MIMETYPES = settings.get("MIMETYPES", (
    ("text/javascript", ".js"),
    ("text/css", ".css"),
    ("text/x-scss", ".scss"),
    ("text/x-sass", ".sass"),
    ("text/less", ".less"),
    ("text/coffeescript", ".coffee"),
    ("application/json", ".json"),
    ("image/svg+xml", ".svg"),
))

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = settings.get("ALLOWED_IMAGE_EXTENSIONS", [
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"
])

ALLOWED_DOCUMENT_EXTENSIONS = settings.get("ALLOWED_DOCUMENT_EXTENSIONS", [
    ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
    ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".zip", ".tar", ".gz"
])

ALLOWED_VIDEO_EXTENSIONS = settings.get("ALLOWED_VIDEO_EXTENSIONS", [
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"
])

ALLOWED_AUDIO_EXTENSIONS = settings.get("ALLOWED_AUDIO_EXTENSIONS", [
    ".mp3", ".wav", ".ogg", ".m4a", ".flac"
])

# -------------------------------
# Image Processing Configuration
# -------------------------------
WAGTAILIMAGES_IMAGE_MODEL = settings.get("WAGTAILIMAGES_IMAGE_MODEL", "wagtailimages.Image")
WAGTAILIMAGES_MAX_UPLOAD_SIZE = settings.get("WAGTAILIMAGES_MAX_UPLOAD_SIZE", 10 * 1024 * 1024)  # 10MB
WAGTAILIMAGES_MAX_IMAGE_PIXELS = settings.get("WAGTAILIMAGES_MAX_IMAGE_PIXELS", 128 * 1024 * 1024)  # 128MP

# Image quality settings
WAGTAILIMAGES_JPEG_QUALITY = settings.get("WAGTAILIMAGES_JPEG_QUALITY", 85)
WAGTAILIMAGES_WEBP_QUALITY = settings.get("WAGTAILIMAGES_WEBP_QUALITY", 85)
WAGTAILIMAGES_AVIF_QUALITY = settings.get("WAGTAILIMAGES_AVIF_QUALITY", 75)
WAGTAILIMAGES_PNG_QUALITY = settings.get("WAGTAILIMAGES_PNG_QUALITY", 85)
WAGTAILIMAGES_GIF_QUALITY = settings.get("WAGTAILIMAGES_GIF_QUALITY", 85)

# Image format settings
WAGTAILIMAGES_FORMAT_CONVERSIONS = settings.get("WAGTAILIMAGES_FORMAT_CONVERSIONS", {
    "bmp": "jpeg",
    "webp": "webp",
    "avif": "avif",
})

# -------------------------------
# Document Configuration
# -------------------------------
WAGTAILDOCS_EXTENSIONS = settings.get("WAGTAILDOCS_EXTENSIONS", [
    "csv", "docx", "key", "odt", "pdf", "pptx", "rtf", "txt", "xlsx", "zip"
])

WAGTAILDOCS_SERVE_METHOD = settings.get("WAGTAILDOCS_SERVE_METHOD", "direct")
WAGTAILDOCS_MAX_UPLOAD_SIZE = settings.get("WAGTAILDOCS_MAX_UPLOAD_SIZE", 50 * 1024 * 1024)  # 50MB

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

# -------------------------------
# CDN Configuration
# -------------------------------
CDN_ENABLED = settings.get("CDN_ENABLED", tracker.is_production)
CDN_DOMAIN = settings.get("CDN_DOMAIN", "")

if CDN_ENABLED and CDN_DOMAIN:
    STATIC_URL = f"https://{CDN_DOMAIN}{STATIC_URL}"
    MEDIA_URL = f"https://{CDN_DOMAIN}{MEDIA_URL}"

# -------------------------------
# Asset Compression
# -------------------------------
ASSET_COMPRESSION = {
    "ENABLED": settings.get("ASSET_COMPRESSION_ENABLED", tracker.is_production),
    "CSS_MINIFY": True,
    "JS_MINIFY": True,
    "HTML_MINIFY": True,
    "IMAGE_OPTIMIZATION": True,
    "BROTLI_COMPRESSION": True,
    "GZIP_COMPRESSION": True,
}

# -------------------------------
# Cache Busting
# -------------------------------
CACHE_BUSTING = {
    "ENABLED": settings.get("CACHE_BUSTING_ENABLED", tracker.is_production),
    "STRATEGY": "content-hash",  # content-hash, version, timestamp
    "MANIFEST_FILE": str(Path(STATIC_ROOT) / "staticfiles.json"),
}

# -------------------------------
# Development Server Configuration
# -------------------------------
if tracker.is_debug:
    # Disable compression and caching in development
    COMPRESS_ENABLED = False
    PIPELINE["PIPELINE_ENABLED"] = False
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
