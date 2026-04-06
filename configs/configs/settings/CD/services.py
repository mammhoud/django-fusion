# ====================================
# 📦 Optional Production Services
# Each block activates only when its env flag is set.
# ====================================
import os

from ..conf import settings

# ---- S3 / Cloud Storage ----
if settings.get("STORAGE.USE_S3", False):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = settings.get("STORAGE.AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = settings.get("STORAGE.AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME = settings.get("STORAGE.AWS_STORAGE_BUCKET_NAME", "")
    AWS_S3_REGION_NAME = settings.get("STORAGE.AWS_S3_REGION_NAME", "us-east-1")
    _cdn = settings.get("STORAGE.AWS_S3_CUSTOM_DOMAIN") or os.environ.get(
        "AWS_CLOUDFRONT_DOMAIN", f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    )
    AWS_S3_CUSTOM_DOMAIN = _cdn
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400, public", "ContentDisposition": "inline"}
    AWS_DEFAULT_ACL = "public-read"
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_USE_SSL = True
    AWS_S3_VERIFY = True
    AWS_S3_MAX_MEMORY_SIZE = 100 * 1024 * 1024
    AWS_S3_ADDRESSING_STYLE = "virtual"
    STATIC_URL = f"https://{_cdn}/static/"
    MEDIA_URL = f"https://{_cdn}/media/"

# ---- Sentry ----
_sentry_dsn = settings.get("SENTRY.DSN", "")
if settings.get("SENTRY.ENABLED", False) and _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[DjangoIntegration(), RedisIntegration()],
        traces_sample_rate=float(settings.get("SENTRY.TRACES_SAMPLE_RATE", 0.1)),
        send_default_pii=False,
        environment=settings.get("SENTRY.ENVIRONMENT", "production"),
        release=settings.get("SENTRY.RELEASE", ""),
    )

# ---- Celery ----
if settings.get("CELERY.BROKER_URL", ""):
    CELERY_BROKER_URL = settings.get("CELERY.BROKER_URL")
    CELERY_RESULT_BACKEND = settings.get("CELERY.RESULT_BACKEND", "")
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = "UTC"
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60
    CELERY_TASK_SOFT_TIME_LIMIT = 20 * 60
    CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
    CELERY_WORKER_CONCURRENCY = settings.get("CELERY.WORKER_CONCURRENCY", 4)
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
    CELERY_BROKER_HEARTBEAT = 10
    CELERY_BROKER_POOL_LIMIT = 10

# ---- Rate Limiting ----
if settings.get("SECURITY.RATE_LIMIT_ENABLED", False):
    RATELIMIT_ENABLE = True
    RATELIMIT_USE_CACHE = "default"
    RATELIMIT_KEY_PREFIX = settings.get("SECURITY.RATE_LIMIT_CACHE_PREFIX", "rl_prod")

# ---- Wagtail Frontend Cache ----
if settings.get("WAGTAIL.FRONTEND_CACHE_ENABLED", False):
    WAGTAIL_FRONTEND_CACHE = {
        "default": {
            "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
            "LOCATION": os.environ.get("CACHE_PURGE_URL", ""),
        }
    }

# ---- Django Silk (profiling, debug only) ----
if settings.get("ENABLE_SILK_PROFILING", False) and DEBUG:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE += ["silk.middleware.SilkyMiddleware"]

# ---- Content Security Policy ----
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

# ---- Django-RQ ----
RQ_QUEUES = settings.get("RQ_QUEUES", {})
