# ====================================
# 📦 Storage Configuration — Local Only
# ====================================
# VResume uses local filesystem storage for both media and static files.
# No S3, boto3, or django-storages dependency is required.
# NOTE: This file is deprecated. Use configs/base/assets.py instead.
# ====================================

import os

from core.config import BASE_DIR

from ..settings.setup import settings

# ── Storage Backends ─────────────────────────────────────────────────────────
# Django built-ins — no third-party packages needed.
DEFAULT_FILE_STORAGE = settings.get(
    "DEFAULT_FILE_STORAGE",
    "django.core.files.storage.FileSystemStorage",
    block="STORAGE",
)
STATICFILES_STORAGE = settings.get(
    "STATICFILES_STORAGE",
    "django.contrib.staticfiles.storage.StaticFilesStorage",
    block="STORAGE",
)

# ── URL Prefixes ──────────────────────────────────────────────────────────────
MEDIA_URL = settings.get("MEDIA_URL", "/media/", block="STORAGE")
STATIC_URL = settings.get("STATIC_URL", "/static/", block="STORAGE")

# ── Filesystem Paths (Media & Static) ──────────────────────────────────────────
# NOTE: MEDIA_ROOT and STATIC_ROOT are now defined in configs/base/assets.py
# These definitions are kept for backward compatibility only.
# If you're configuring storage, use configs/base/assets.py instead.
MEDIA_ROOT = os.path.join(BASE_DIR, settings.get("MEDIA_ROOT", "assets/media", block="STORAGE"))
STATIC_ROOT = os.path.join(BASE_DIR, settings.get("STATIC_ROOT", "staticfiles", block="STORAGE"))

# ── Static File Finders ───────────────────────────────────────────────────────
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# ── File Upload Limits ────────────────────────────────────────────────────────
# FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
# FILE_UPLOAD_PERMISSIONS = 0o644
# FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
# DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB
# DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ── Allowed File Types ────────────────────────────────────────────────────────
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".csv", ".xls", ".xlsx"]
ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

MAX_UPLOAD_SIZE = {
    "image": 10 * 1024 * 1024,  # 10 MB
    "document": 50 * 1024 * 1024,  # 50 MB
    "video": 100 * 1024 * 1024,  # 100 MB
}
