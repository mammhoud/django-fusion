# ====================================
# 📦 Storage Configuration
# ====================================
import os

from ..settings.conf import settings
from ..settings.conf import settings as tracker
from .paths import BASE_DIR

# -------------------------------
# Storage Backend Selection
# -------------------------------
USE_S3 = getattr(settings, "USE_S3", False)
if hasattr(settings, "STORAGE"):
    USE_S3 = settings.STORAGE.get("USE_S3", False)

# -------------------------------
# AWS S3 / Local Storage Configuration
# -------------------------------
if USE_S3:
    # AWS Credentials
    AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID", os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin"))
    AWS_SECRET_ACCESS_KEY = getattr(settings, "AWS_SECRET_ACCESS_KEY", os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin"))

    # S3 Bucket Configuration
    AWS_STORAGE_BUCKET_NAME = getattr(settings, "AWS_STORAGE_BUCKET_NAME", os.environ.get("AWS_STORAGE_BUCKET_NAME", "static"))
    AWS_S3_ENDPOINT_URL = getattr(settings, "AWS_S3_ENDPOINT_URL", os.environ.get("AWS_S3_ENDPOINT_URL", "http://ctc-minio:9000"))
    AWS_S3_REGION_NAME = getattr(settings, "AWS_S3_REGION_NAME", os.environ.get("AWS_S3_REGION_NAME", "us-east-1"))

    # For local MinIO (without HTTPS)
    AWS_S3_USE_SSL = False
    AWS_S3_VERIFY = False

    # Optional: make files publicly readable (no query string auth)
    AWS_QUERYSTRING_AUTH = False

    # Static files storage
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"

    # Media files storage
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/media/"

    # S3 Performance & Security
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400, public",
        "ContentDisposition": "inline",
    }

    # S3 Transfer Acceleration (optional)
    AWS_S3_ACCELERATE = tracker.is_production

else:
    # Local File Storage
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

    # Local Paths
    MEDIA_URL = "/media/"
    STATIC_URL = "/static/"

    MEDIA_ROOT = os.path.join(BASE_DIR, "assets", "media")
    STATIC_ROOT = os.path.join(BASE_DIR, "assets", "staticfiles")

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# -------------------------------
# File Upload Configuration
# -------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# -------------------------------
# Media File Types & Validation
# -------------------------------
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".csv", ".xls", ".xlsx"]
ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

MAX_UPLOAD_SIZE = {
    "image": 10 * 1024 * 1024,  # 10 MB
    "document": 50 * 1024 * 1024,  # 50 MB
    "video": 100 * 1024 * 1024,  # 100 MB
}

# -------------------------------
# Storage Backend Health Check
# -------------------------------
STORAGE_HEALTH_CHECK = {
    "enabled": tracker.is_production,
    "timeout": 10,
    "retries": 2,
}

# -------------------------------
# CDN Configuration (if using)
# -------------------------------
CDN_CONFIG = {
    "enabled": USE_S3 and tracker.is_production,
    "static_url": STATIC_URL,
    "media_url": MEDIA_URL,
    "cache_ttl": 86400,  # 24 hours
}
