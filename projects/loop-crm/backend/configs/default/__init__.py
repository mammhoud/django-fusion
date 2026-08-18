"""Loop-CRM Django settings — the unified sales + marketing platform.

A modular monolith on django-fusion: one Django project, several focused apps
(core, crm, marketing, attribution), a single PostgreSQL database, Redis for
cache/queues, and Dramatiq for background work (replacing both Temporal and
BullMQ from the Twenty/Postiz sources).

This is the project-local ``configs.default`` layer (Loop-CRM's own settings,
not the LMS/Wagtail ``configs`` package). ``backend/settings.py`` seeds the
site environment and re-exports everything here.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

# backend/ = configs/default/__init__.py → parents[0]=default, parents[1]=configs,
# parents[2]=backend. This keeps BASE_DIR identical to the old flat settings.py.
BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "loop-crm-dev-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") if h]

# Demo state — when enabled, the login page surfaces the seeded demo
# credentials and the container entrypoint seeds the demo workspace on boot.
# NEVER enable on a production deployment with real data: the demo password
# is intentionally public.
DEMO_MODE = os.environ.get("DEMO_MODE", "0") == "1"

INSTALLED_APPS = [
    # daphne must precede django.contrib.staticfiles so ``runserver`` serves
    # the Channels ASGI stack instead of Django's sync dev server.
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Channels provides the channel layer + consumers backing the realtime
    # SSE/WebSocket road (see apps.core.realtime).
    "channels",
    # django-fusion is the shared component/routing/fragment layer — it
    # replaces django-cotton: components, ``{% comp %}``, fragments and the
    # dual render-first / data-API pipeline come from here.
    "django_fusion",
    # django-fusion component system: registers the built-in {% comp %}
    # templates (table, form, pagination, modal, …) so project-level
    # templates/fusion/components/*.html overrides can shadow them.
    "django_fusion.comp",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Social providers (precis-landing parity): GitHub + Google OAuth. Client
    # IDs/secrets come from env; empty values disable the buttons in the login
    # template through allauth's SOCIALACCOUNT_ENABLED context flag.
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "django_tables2",
    # django-dramatiq wires Dramatiq into Django (provides `rundramatiq`).
    "django_dramatiq",
    # Loop-CRM domain apps.
    "apps.core",
    "apps.crm",
    "apps.marketing",
    "apps.attribution",
    "apps.finance",
    "apps.pos",
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
# After sign-in the user belongs inside the workspace, not on the marketing
# landing (which still shows "Sign in" / "Start free").
LOGIN_REDIRECT_URL = "/overview/"
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

# allauth adapters — thin wrappers over allauth defaults (precis-landing
# parity). Social signup follows the same open-registration policy as email.
ACCOUNT_ADAPTER = "apps.core.adapters.LoopAuthAdapter"
SOCIALACCOUNT_ADAPTER = "apps.core.adapters.LoopSocialAccountAdapter"

# Social providers — GitHub + Google. Client IDs/secrets come from env vars;
# values are read at request time so empty IDs simply disable the button.
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": os.environ.get("GITHUB_CLIENT_ID", ""),
            "secret": os.environ.get("GITHUB_CLIENT_SECRET", ""),
        },
        "SCOPE": ["read:user", "user:email"],
    },
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        },
        "SCOPE": ["profile", "email"],
    },
}

# Social connector OAuth clients (LinkedIn + X). Empty values keep the
# adapters honest: publishing requires a token, refresh requires these.
LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
X_CLIENT_ID = os.environ.get("X_CLIENT_ID", "")
X_CLIENT_SECRET = os.environ.get("X_CLIENT_SECRET", "")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Loop CRM <noreply@structa.cloud>")
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Secure defaults are enabled in production without breaking local HTTP tests.
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "0") == "1"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
_csrf_trusted_origins = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if DEBUG:
    # The Astro shell proxies /accounts to Django; the browser sees the Astro
    # origin (and the direct backend port), so both must be trusted in dev for
    # the landing's Start free signup POST to pass the CSRF origin check.
    _csrf_trusted_origins += [
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:4321",
        "http://127.0.0.1:4323",
        "http://localhost:8000",
        "http://localhost:4321",
    ]
CSRF_TRUSTED_ORIGINS = _csrf_trusted_origins
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
                "apps.core.context_processors.workspace_id",
                "apps.core.context_processors.demo_state",
            ],
            "builtins": [
                "django_fusion.comp.tags.components",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"
ASGI_APPLICATION = "asgi.application"


def _redis_db_offset() -> int:
    """Base Redis DB offset for Loop-CRM's private index block.

    The shared ``default-redis`` cluster serves every product. Legacy stacks
    pin the relative indexes 0 (cache), 1 (Dramatiq), 2 (channels), so
    Loop-CRM shifts them by ``REDIS_DB`` to own a private block (compose sets
    8 → 8/9/10) and avoid queue/session collisions with other projects.
    """
    try:
        return int(os.environ.get("REDIS_DB", "0"))
    except (TypeError, ValueError):
        return 0


def _redis_url(db: int = 0) -> str:
    """Build a Redis URL, honoring REDIS_URL and an optional REDIS_PASSWORD.

    Compose deployments run passwordless Redis and pass REDIS_URL directly.
    Local development may run a password-protected Redis; REDIS_HOST/PORT/
    PASSWORD then compose the URL so allauth's login rate-limiter, the
    Dramatiq broker, and the channel layer can connect.

    ``db`` is a *relative* index (0=cache, 1=Dramatiq, 2=channels) offset by
    ``REDIS_DB`` (see :func:`_redis_db_offset`).
    """
    url = os.environ.get("REDIS_URL")
    if url:
        return url
    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = os.environ.get("REDIS_PORT", "6379")
    password = os.environ.get("REDIS_PASSWORD", "")
    auth = f":{password}@" if password else ""
    return f"redis://{auth}{host}:{port}/{_redis_db_offset() + db}"


def _redis_reachable(timeout: float = 0.4) -> bool:
    """Probe whether a Redis server answers on the configured dev defaults.

    Dependency-free socket check so ``make dev`` and the browser suite work
    without a Redis process. Explicit REDIS_URL/REDIS_HOST configuration
    always requires a real server (production behavior unchanged).
    """
    try:
        import socket

        host = os.environ.get("REDIS_HOST", "127.0.0.1")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# Realtime channel layer. Redis-backed in composed/prod environments; an
# in-process layer keeps local dev + the test suite working without Redis.
# ``_redis_url(2)`` keeps the channel layer off the cache (0) and Dramatiq (1)
# relative indexes (all shifted by REDIS_DB).
if os.environ.get("REDIS_URL") or os.environ.get("REDIS_HOST"):
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [_redis_url(2)]},
        }
    }
elif DEBUG and not _redis_reachable():
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [_redis_url(2)]},
        }
    }

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
    # SQLite tests default to an in-memory shared-cache database (fast, and the
    # right choice for the unit suite). ``LOOP_TEST_DB_NAME`` opts into a
    # file-backed test database so subprocess tests (the daphne SSE/WebSocket
    # smoke tests) can share the same SQLite file across processes — the
    # in-memory DB cannot cross a process boundary.
    _test_db_name = os.environ.get("LOOP_TEST_DB_NAME", "").strip()
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    if _test_db_name:
        DATABASES["default"]["TEST"] = {"NAME": _test_db_name}

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

# Machine-to-machine POS ingest key (Formint POS → Loop-CRM finance). Empty
# disables the ingest road; production must set a shared secret with Formint.
POS_INGEST_API_KEY = os.environ.get("POS_INGEST_API_KEY", "")

# Optional Slack incoming-webhook URL for the ``send_slack`` workflow action.
# Empty keeps the action honest (it reports ``deferred`` until configured).
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# Optional email-sync OAuth client credentials (Gmail + Outlook). Empty values
# keep the connectors honest: an account can be registered but sync reports
# ``unconfigured`` and token refresh is a no-op until these are set.
GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
OUTLOOK_CLIENT_ID = os.environ.get("OUTLOOK_CLIENT_ID", "")
OUTLOOK_CLIENT_SECRET = os.environ.get("OUTLOOK_CLIENT_SECRET", "")
# Override the email OAuth callback host; falls back to SOCIAL_REDIRECT_BASE
# and then to the request host.
EMAIL_REDIRECT_BASE = os.environ.get("EMAIL_REDIRECT_BASE", "")
FUSION_BOLT_AUTH_HEADER = os.environ.get("FUSION_BOLT_AUTH_HEADER", "Authorization")
FUSION_BOLT_JWT_ISSUER = os.environ.get("FUSION_BOLT_JWT_ISSUER", "loop-crm")
FUSION_BOLT_JWT_AUDIENCE = os.environ.get("FUSION_BOLT_JWT_AUDIENCE", "")

# Redis-backed cache + Dramatiq broker (defaults for local dev).
if os.environ.get("REDIS_URL") or os.environ.get("REDIS_HOST"):
    # Explicit configuration: Redis is required (compose, prod, CI).
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _redis_url(0),
        }
    }
elif DEBUG and not _redis_reachable():
    # Unconfigured local dev with no Redis running: fall back to an in-process
    # cache so allauth's login rate-limiter and session flows never 500.
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "loop-crm-dev",
        }
    }
else:
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
