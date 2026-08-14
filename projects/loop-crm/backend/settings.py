"""Loop-CRM Django settings — the unified sales + marketing platform.

A modular monolith on django-fusion: one Django project, several focused apps
(core, crm, marketing, attribution), a single PostgreSQL database, Redis for
cache/queues, and Dramatiq for background work (replacing both Temporal and
BullMQ from the Twenty/Postiz sources). Mirrors the landing-fusion settings
layout so every loop-crm Makefile command resolves the same way.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "loop-crm-dev-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # django-fusion is the shared component/routing/fragment layer — it
    # replaces django-cotton: components, ``{% comp %}``, fragments and the
    # dual render-first / data-API pipeline come from here.
    "django_fusion",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_tables2",
    # django-dramatiq wires Dramatiq into Django (provides `rundramatiq`).
    "django_dramatiq",
    # Loop-CRM domain apps.
    "apps.core",
    "apps.crm",
    "apps.marketing",
    "apps.attribution",
    "apps.finance",
    # Worker implementations live in plugins.workers; no legacy task app is
    # needed because TaskExecution belongs to core in Loop-CRM.
]
if importlib.util.find_spec("django_bolt") is not None:
    # The real Bolt package is optional; the repository stub is harmless and
    # is rejected by the fusion bridge's capability check.
    INSTALLED_APPS.append("django_bolt")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

SITE_ID = int(os.environ.get("SITE_ID", "1"))
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = os.environ.get("ACCOUNT_EMAIL_VERIFICATION", "optional")
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_REAUTHENTICATION_TIMEOUT = 300
SOCIALACCOUNT_STORE_TOKENS = False

# allauth email login (ACCOUNT_LOGIN_METHODS = {"email"}) requires its
# AuthenticationBackend; ModelBackend keeps the Django admin username flow.
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Loop CRM <noreply@structa.cloud>")
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Secure defaults are enabled in production without breaking local HTTP tests.
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "0") == "1"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
if not DEBUG:
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "django_fusion.comp.tags.components",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"
ASGI_APPLICATION = "asgi.application"

# Local dev defaults to SQLite (frictionless scaffold); set USE_POSTGRES=1 to
# switch to the PostgreSQL cluster the merge plan targets for production.
if os.environ.get("USE_POSTGRES", "0") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "loop_crm"),
            "USER": os.environ.get("POSTGRES_USER", "loop_crm"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "loop_crm"),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# NOTE: AUTH_USER_MODEL is intentionally NOT swapped — django-fusion's models
# reference auth.User directly. Role/workspace live on core.UserProfile instead.

# Optional django-bolt API runtime. The Django JSON compatibility road remains
# available when the package is not installed. SECRET_KEY is only a local
# fallback; production deployments should set a dedicated signing secret.
FUSION_BOLT_ENABLED = os.environ.get("FUSION_BOLT_ENABLED", "1") == "1"
# Development may reuse SECRET_KEY; production must provide a dedicated JWT
# secret or Bolt will not expose a signing backend.
FUSION_BOLT_JWT_SECRET = os.environ.get("FUSION_BOLT_JWT_SECRET", SECRET_KEY if DEBUG else "")
FUSION_BOLT_JWT_ALGORITHM = os.environ.get("FUSION_BOLT_JWT_ALGORITHM", "HS256")
FUSION_BOLT_TOKEN_TTL = int(os.environ.get("FUSION_BOLT_TOKEN_TTL", "3600"))
FUSION_BOLT_REFRESH_TTL = int(os.environ.get("FUSION_BOLT_REFRESH_TTL", "2592000"))
FUSION_BOLT_API_KEY = os.environ.get("FUSION_BOLT_API_KEY", "")
FUSION_BOLT_API_KEY_HEADER = os.environ.get("FUSION_BOLT_API_KEY_HEADER", "X-API-Key")
FUSION_BOLT_AUTH_HEADER = os.environ.get("FUSION_BOLT_AUTH_HEADER", "Authorization")
FUSION_BOLT_JWT_ISSUER = os.environ.get("FUSION_BOLT_JWT_ISSUER", "loop-crm")
FUSION_BOLT_JWT_AUDIENCE = os.environ.get("FUSION_BOLT_JWT_AUDIENCE", "")

# Redis-backed cache + Dramatiq broker (defaults for local dev).
def _redis_url(db: int = 0) -> str:
    """Build a Redis URL, honoring REDIS_URL and an optional REDIS_PASSWORD.

    Compose deployments run passwordless Redis and pass REDIS_URL directly.
    Local development may run a password-protected Redis; REDIS_HOST/PORT/
    PASSWORD then compose the URL so allauth's login rate-limiter and the
    Dramatiq broker can connect.
    """
    url = os.environ.get("REDIS_URL")
    if url:
        return url
    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = os.environ.get("REDIS_PORT", "6379")
    password = os.environ.get("REDIS_PASSWORD", "")
    auth = f":{password}@" if password else ""
    return f"redis://{auth}{host}:{port}/{db}"


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": _redis_url(0),
    }
}

# Shared/website task-record contract for the Task Center page. The shared
# worker writes django_fusion's BackgroundTaskLog; the Task Center mirrors it
# into core.TaskExecution (the website-local record) filtered by this site name.
FUSION_TASK_SITE_NAME = os.environ.get("FUSION_TASK_SITE_NAME", "loop-crm")
FUSION_TASK_EXECUTION_MODEL = os.environ.get("FUSION_TASK_EXECUTION_MODEL", "core.TaskExecution")
FUSION_TASK_MODULES = ["plugins.workers.tasks"]

DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {"url": _redis_url(1)},
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
    ],
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
