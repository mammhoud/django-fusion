# =======================================================
# 📦 Production – Optional Services (by use case)
# =======================================================
# Import this file *after* production.py and merge settings.
# Example:
#   from .production import *
#   from .services import *
#
import os
from ..conf import settings

# -------------------------------------------------------------------
# ☁️  USE CASE: Static & Media Files (Cloud Storage)
# -------------------------------------------------------------------
if settings.get("STORAGE.USE_S3", False):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = settings.get("STORAGE.AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = settings.get("STORAGE.AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = settings.get("STORAGE.AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = settings.get("STORAGE.AWS_S3_REGION_NAME", "us-east-1")
    AWS_S3_CUSTOM_DOMAIN = settings.get("STORAGE.AWS_S3_CUSTOM_DOMAIN") or os.environ.get("AWS_CLOUDFRONT_DOMAIN", f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com")
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400, public",
        "ContentDisposition": "inline",
    }
    AWS_DEFAULT_ACL = "public-read"
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_USE_SSL = True
    AWS_S3_VERIFY = True
    AWS_S3_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
    AWS_S3_ADDRESSING_STYLE = "virtual"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

# -------------------------------------------------------------------
# 📊 USE CASE: Monitoring & Error Tracking (Sentry)
# -------------------------------------------------------------------
sentry_dsn = settings.get("SENTRY.DSN")
if settings.get("SENTRY.ENABLED", False) and sentry_dsn and str(sentry_dsn).strip():
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[DjangoIntegration(), RedisIntegration()],
        traces_sample_rate=float(settings.get("SENTRY.TRACES_SAMPLE_RATE", 0.1)),
        send_default_pii=False,
        environment=settings.get("SENTRY.ENVIRONMENT", "production"),
        release=settings.get("SENTRY.RELEASE", ""),
    )

# -------------------------------------------------------------------
# 🥬 USE CASE: Background Tasks (Celery + Redis)
# -------------------------------------------------------------------
# Check if Celery is configured via its broker URL
if settings.get("CELERY.BROKER_URL"):
    CELERY_BROKER_URL = settings.get("CELERY.BROKER_URL")
    CELERY_RESULT_BACKEND = settings.get("CELERY.RESULT_BACKEND")
    CELERY_ACCEPT_CONTENT = settings.get("CELERY.ACCEPT_CONTENT", ["json"])
    CELERY_TASK_SERIALIZER = settings.get("CELERY.TASK_SERIALIZER", "json")
    CELERY_RESULT_SERIALIZER = settings.get("CELERY.RESULT_SERIALIZER", "json")
    CELERY_TIMEZONE = settings.get("CELERY.TIMEZONE", "UTC")
    CELERY_TASK_TRACK_STARTED = settings.get("CELERY.TASK_TRACK_STARTED", True)
    CELERY_TASK_TIME_LIMIT = settings.get("CELERY.TASK_TIME_LIMIT", 30 * 60)
    CELERY_TASK_SOFT_TIME_LIMIT = settings.get("CELERY.TASK_SOFT_TIME_LIMIT", 20 * 60)
    CELERY_WORKER_MAX_TASKS_PER_CHILD = settings.get("CELERY.WORKER_MAX_TASKS_PER_CHILD", 100)
    CELERY_WORKER_CONCURRENCY = settings.get("CELERY.WORKER_CONCURRENCY", 4)
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = settings.get("CELERY.BROKER_CONNECTION_RETRY_ON_STARTUP", True)
    CELERY_BROKER_HEARTBEAT = settings.get("CELERY.BROKER_HEARTBEAT", 10)
    CELERY_BROKER_POOL_LIMIT = settings.get("CELERY.BROKER_POOL_LIMIT", 10)

# -------------------------------------------------------------------
# 🚦 USE CASE: Rate Limiting (Django Ratelimit)
# -------------------------------------------------------------------
if settings.get("SECURITY.RATE_LIMIT_ENABLED", False):
    RATELIMIT_ENABLE = True
    RATELIMIT_USE_CACHE = "default"
    RATELIMIT_KEY_PREFIX = settings.get("SECURITY.RATE_LIMIT_CACHE_PREFIX", "rl_prod")
    # Example: '100/h' for anonymous, '1000/h' for authenticated
    RATELIMIT_VIEW = "core.views.ratelimit_view"

# -------------------------------------------------------------------
# 🔄 USE CASE: Wagtail Frontend Cache (Varnish / Cloudflare)
# -------------------------------------------------------------------
if settings.get("WAGTAIL.FRONTEND_CACHE_ENABLED", False):
    WAGTAIL_FRONTEND_CACHE = {
        "default": {
            "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
            "LOCATION": os.environ.get("CACHE_PURGE_URL"),
        }
    }

# -------------------------------------------------------------------
# 📈 USE CASE: Performance Monitoring (django-silk) – Debug only
# -------------------------------------------------------------------
if settings.get("ENABLE_SILK_PROFILING", False) and DEBUG:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE += ["silk.middleware.SilkyMiddleware"]

# -------------------------------------------------------------------
# 🛡️ USE CASE: Content Security Policy (django-csp)
# -------------------------------------------------------------------
if settings.get("CSP_ENABLED", False):
    INSTALLED_APPS += ["csp"]
    MIDDLEWARE += ["csp.middleware.CSPMiddleware"]
    CSP_DEFAULT_SRC = ["'self'"]
    CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
    CSP_SCRIPT_SRC = ["'self'"]
    CSP_FONT_SRC = ["'self'"]
    CSP_IMG_SRC = ["'self'", "data:"]
    CSP_CONNECT_SRC = ["'self'"]
    CSP_FRAME_SRC = ["'none'"]
    CSP_OBJECT_SRC = ["'none'"]
    CSP_BASE_URI = ["'self'"]
    CSP_FORM_ACTION = ["'self'"]
    CSP_FRAME_ANCESTORS = ["'none'"]
    CSP_BLOCK_ALL_MIXED_CONTENT = True
    CSP_UPGRADE_INSECURE_REQUESTS = True

# -------------------------------------------------------------------
# 🐕 USE CASE: Background Tasks (Django-RQ + Redis)
# -------------------------------------------------------------------
RQ_QUEUES = settings.get("RQ_QUEUES", {})

# -------------------------------------------------------------------
# 🧩 Add other service configurations here, each behind an env flag.
# -------------------------------------------------------------------
