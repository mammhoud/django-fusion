"""
Precis Landing backend settings.

A self-contained Django + Wagtail configuration for the landing-only slice of
the ASTRO migration. Unlike the shared ``configs.default`` layer used by the
full CMS sites, this module keeps the landing backend standalone so it can be
deployed side-by-side with the Astro frontend without wiring the entire Fusion
workspace.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Layered config cascade ───────────────────────────────────────────────────
# Sources env-read *defaults* from the project configs dir (configs/README.md):
# shared Env YAML → configs/*.yml → Env/_site.yml → .env, with environment
# variables always winning. The cascade is optional sugar — a container or
# checkout without configs/ behaves exactly as before (env-only).
# See libs/django-fusion/src/django_fusion/config/project.py.
try:
    from django_fusion.config.project import load_config

    _cascade = load_config(BASE_DIR)
except Exception:  # pragma: no cover — cascade is optional; never break boot
    _cascade = None


def _cfg(key: str, default=None):
    """Return a cascade value (env already wins inside the cascade) or default."""
    if _cascade is None:
        return default
    value = _cascade.get(key, default)
    return default if value is None else value


def _cfg_list(key: str, default: str) -> str:
    """Return a cascade list/string as a comma-joined string or default."""
    value = _cfg(key, None)
    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)
    if value:
        return str(value)
    return default


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "precis-dev-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# ── Multi-tenancy (django-tenants — schema-per-tenant) ──────────────────────
# Schema-based multi-tenancy is PostgreSQL-only. The full django-tenants stack
# (SHARED/TENANT app split, tenant router, PathTenantMiddleware, Postgres
# backend, public URLconf) activates ONLY when DB_ENGINE is set to the
# django_tenants backend. Under SQLite (dev default) everything runs exactly
# as before — the tenant middleware and router are simply absent.
#
# TENANT_MODEL / TENANT_DOMAIN_MODEL must be set BEFORE INSTALLED_APPS because
# django-tenants' DomainMixin references settings.TENANT_MODEL at class
# definition time (module load), not lazily at runtime.
TENANCY_ENABLED = os.environ.get("DB_ENGINE", "").startswith("django_tenants")
TENANT_MODEL = "tenants.CourseCenter"
TENANT_DOMAIN_MODEL = "tenants.CourseDomain"
TENANT_BASE_URL = os.environ.get("TENANT_BASE_URL", "https://dev.structa.cloud")
# Default to backend + localhost only (secure fallback). Production
# docker-compose.yml sets DJANGO_ALLOWED_HOSTS explicitly with the public
# domains appended, so this default never tightens a deployed site.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        _cfg_list("SITE.allowed_hosts", "localhost,127.0.0.1,precis-dev-backend,precis-dev-frontend"),
    ).split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # mfa/webauthn authenticator list uses |naturaltime
    # HTMX
    "django_htmx",
    # Auth — django-allauth (headless API + social providers). The React
    # reference (cms-fusion frontend) used /auth/login JSON endpoints; here
    # allauth's headless API serves the same shape: POST /api/auth/login,
    # /api/auth/session, /api/auth/logout + provider redirects, consumed by
    # the Alpine login modal on both render roads.
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    # MFA — TOTP authenticator app + WebAuthn passkeys/security keys (the
    # ``allauth.mfa.webauthn`` module is part of allauth.mfa; fido2 is the
    # only extra dependency and it is installed). ``allauth.headless`` mounts
    # the same 2FA flows through the /api/auth/* endpoints the Alpine login
    # modal consumes (gated on allauth.mfa being installed), so both render
    # roads cover the journey.
    "allauth.mfa",
    "allauth.headless",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    # django-fusion — unified fragment/layout rendering pipeline
    "django_fusion",
    # django-dramatiq — background workers (rundramatiq) consuming the Redis
    # task broker; powers queued email delivery via plugins.workers.*
    "django_dramatiq",
    # django-webpack-loader — serves versioned bundles (webpack/precis-landing.config.js)
    "webpack_loader",
    # Landing apps (precis-lms-style organization)
    "apps.content",  # StreamField blocks + block templates
    "apps.pages",  # Wagtail page models + page templates + seed
    "apps.handlers",  # PageHandler views (HTMX fragment rendering)
    "apps.auth",  # Allauth auth adapters + templates (LandingAuthAdapter + social)
    "apps.learning",  # Commercial LMS catalog, enrollment, progress, and learner profile
    # TaskExecution remains in apps.tasks; worker implementations live in
    # plugins.workers and are loaded explicitly below.
    "apps.tasks",
    # Merged LMS apps (from precis-lms) — components templatetag helpers and
    # the shared domain model layer (contacts, locations, newsletter, teams).
    "apps.components",
    "apps.domain",
    "apps.tenants",  # Multi-tenant registry (Plan, Tenant, Domain, TenantRegistration)
]

# ── Multi-tenancy: shared vs tenant app split ────────────────────────────────
# When TENANCY_ENABLED is True (PostgreSQL), django-tenants splits the database
# into a shared ``public`` schema (SHARED_APPS) and per-center schemas
# (TENANT_APPS).  Under SQLite every app stays in the flat list; the split is
# purely declarative until the tenancy backend activates.
#
# Rules:
#   SHARED_APPS  — one copy in public schema (admin, Wagtail UI, tenant registry)
#   TENANT_APPS  — replicated into each CourseCenter's schema (users, pages, courses)
#   INSTALLED_APPS = SHARED_APPS + (TENANT_APPS - SHARED_APPS) — deduped, order preserved
#
# Pattern lifted from Formint Cloud (formint-cloud/backend/configs/__init__.py).

SHARED_APPS = [
    # Django core (admin stays in public — one Django admin for all staff)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # HTMX
    "django_htmx",
    # Allauth — headless API + social providers (public schema)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.mfa",
    "allauth.headless",
    # Wagtail admin + contrib (shared admin UI; page models are per-tenant)
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    # django-fusion + task infra
    "django_fusion",
    "django_dramatiq",
    "webpack_loader",
    # Shared-app modules (no per-tenant data)
    "apps.tenants",       # CourseCenter registry + plans (public schema)
    "apps.handlers",      # PageHandler views + middleware (routing)
    "apps.auth",          # Allauth adapters (one adapter, tenant-aware)
    "apps.components",    # Templatetag helpers (no models)
    "apps.tasks",         # Background task tracking
]

TENANT_APPS = [
    # Django core (duplicated per schema → isolated users, sessions, content)
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # HTMX
    "django_htmx",
    # Allauth (per-tenant users, social connections, MFA devices)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    # django-fusion (per-tenant component trees)
    "django_fusion",
    # Per-center data apps
    "apps.pages",         # Wagtail page trees + site config
    "apps.content",       # StreamField blocks
    "apps.learning",      # Courses, enrollments, progress, certificates
    "apps.domain",        # Shared domain models (contacts, newsletter, teams)
]

if TENANCY_ENABLED:
    SHARED_APPS.insert(0, "django_tenants")

# Build the effective app list: shared first, then tenant-only apps.
# Under SQLite this is identical to the old flat INSTALLED_APPS because
# every entry is already in SHARED_APPS.  Under PostgreSQL the router
# splits shared → public, tenant → per-center schemas.
INSTALLED_APPS = list(SHARED_APPS) + [
    a for a in TENANT_APPS if a not in SHARED_APPS
]

# ── Dramatiq worker broker ───────────────────────────────────────────────────
# django-dramatiq must be told to use the Redis broker explicitly; without
# this it imports every dramatiq broker module (incl. RabbitMQ, which needs
# the optional `pika` dependency) at AppConfig.ready() and crashes. Mirror of
# projects/precis/configs/base/cache.py for the standalone landing settings.
_REDIS_BROKER_URL = os.environ.get(
    "DRAMATIQ_BROKER_URL",
    os.environ.get("REDIS_URL", "redis://localhost:6379/1"),
)
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": _REDIS_BROKER_URL,
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.AdminMiddleware",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
    ],
}
FUSION_TASKS = {
    "BACKEND": "django_fusion.tasks.backends.dramatiq.DramatiqBackend",
    "BROKER_URL": _REDIS_BROKER_URL,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serve /static/ from STATIC_ROOT in production (traefik routes /static
    # to Django; staticfiles_urlpatterns() is debug-only). whitenoise is a
    # declared dependency — wire it here so backend-rendered pages get their
    # compiled fusion.css after `make css` + collectstatic.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    # Shared django-fusion language contract: query → session → cookie →
    # negotiated/default language, with the configured Django cookie settings.
    "django_fusion.core.middlewares.language.DefaultLanguageMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "apps.handlers.middleware.LandingCorsMiddleware",
]

ROOT_URLCONF = "urls"

_PROJECT_DIR = BASE_DIR.parent  # projects/
# Precis Landing owns a colocated assets directory at
# projects/precis/precis-landing/assets (not the monorepo-level projects/assets).
_ASSETS_DIR = BASE_DIR.parent / "assets"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # Project-level consolidated assets/templates/ (all templates live here)
            _ASSETS_DIR / "templates",
            _ASSETS_DIR / "templates" / "pages",
            _ASSETS_DIR / "templates" / "content",
            _ASSETS_DIR / "templates" / "content" / "blocks",
            # Landing-specific shared templates (phase/prompt and future
            # Wagtail-managed documents).
            BASE_DIR.parent / "templates",
            BASE_DIR.parent / "templates" / "pages",
            # Backend-local templates (for backward compatibility).
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # Exposes LANGUAGE_CODE / LANGUAGE_BIDI so base.html can render
                # <html lang> + dir from the active (cookie-selected) language.
                "django.template.context_processors.i18n",
                # Exposes fusion_languages / fusion_languages_json /
                # fusion_language_dirs_json — the seeded SiteLanguage catalog,
                # so templates never hardcode codes, flags, or directions.
                "apps.content.context_processors.fusion_languages",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
            "libraries": {
                # django-fusion component tags (comp, slot, prop, var) — registered
                # so `{% load components %}` works, mirroring configs/base/templates.py.
                "components": "django_fusion.comp.tags.components",
            },
        },
    },
]

WSGI_APPLICATION = "wsgi.application"

# allauth headless URL patterns carry no trailing slash (e.g.
# /api/auth/browser/v1/auth/login). With APPEND_SLASH=True the common
# middleware tries to 301-redirect POST bodies — a RuntimeError — so slash
# appending is disabled. All landing routes declare their slashes explicitly
# and Wagtail serves its own tree without relying on APPEND_SLASH.
APPEND_SLASH = False

# ── Database ───────────────────────────────────────────────────────
# Database selection is wired by *type* through the project config cascade
# (configs/database.yml — DATABASE.type: sqlite | postgres), with environment
# variables always winning:
#
#   DB_TYPE=sqlite|postgres   → authoritative shortcut (used by Compose/CI)
#   DJANGO_DB_ENGINE          → django.db.backends.postgresql forces postgres
#   USE_POSTGRES=1            → legacy flag, forces postgres
#   DATABASE.type (cascade)   → fallback when no env var is set
#
# The active type picks its connection map from the cascade
# (DATABASE.sqlite / DATABASE.postgres), so forcing a type via env always
# resolves the right name/user/host/port. Postgres connects to the shared
# ``postgres`` container (application/databases) with this site's own database
# (DB_NAME_LANDING → db_precis_landing); the password comes from .env
# (POSTGRES_PASSWORD / DJANGO_DB_PASSWORD) — never from YAML.
_db_type = os.environ.get("DB_TYPE", "").strip().lower()
if _db_type == "sqlite":
    _use_postgres = False
elif _db_type in ("postgres", "postgresql"):
    _use_postgres = True
else:
    _use_postgres = (
        os.environ.get("DJANGO_DB_ENGINE", "") == "django.db.backends.postgresql"
        or os.environ.get("USE_POSTGRES", "0") == "1"
        or str(_cfg("DATABASE.type", "sqlite")).lower() in {"postgres", "postgresql"}
    )

if _use_postgres:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DJANGO_DB_NAME") or _cfg("DATABASE.postgres.name", "db_precis_dev"),
            "USER": os.environ.get("DJANGO_DB_USER") or _cfg("DATABASE.postgres.user", "admin"),
            "PASSWORD": os.environ.get("DJANGO_DB_PASSWORD") or _cfg("DATABASE.postgres.password", ""),
            "HOST": os.environ.get("DJANGO_DB_HOST") or _cfg("DATABASE.postgres.host", "postgres"),
            "PORT": os.environ.get("DJANGO_DB_PORT") or str(_cfg("DATABASE.postgres.port", "5432")),
        }
    }
else:
    _db_sqlite_name = os.environ.get("DJANGO_DB_PATH")
    if _db_sqlite_name:
        _db_sqlite_path = Path(_db_sqlite_name)
    else:
        _db_sqlite_path = Path(_cfg("DATABASE.sqlite.name", "")) if _cfg("DATABASE.sqlite.name", "") else BASE_DIR / "db.sqlite3"
        if not _db_sqlite_path.is_absolute():
            _db_sqlite_path = BASE_DIR / _db_sqlite_path
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": _db_sqlite_path,
        }
    }

SITE_ID = 1

# ── Auth (django-allauth headless) ────────────────────────────────
AUTHENTICATION_BACKENDS = [
    # Needed to log in by username in Django admin, regardless of allauth
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
# Mandatory email verification: signups must confirm their address before
# they can log in (the branded confirmation email + /accounts/confirm-email/
# flow carry that step). Production behaviour, on by default.
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_BY_CODE_ENABLED = False
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Adapters — custom precis-landing adapters for HTMX/Alpine templates
ACCOUNT_ADAPTER = "apps.auth.adapters.LandingAuthAdapter"
SOCIALACCOUNT_ADAPTER = "apps.auth.adapters.LandingSocialAccountAdapter"

# ── Two-factor authentication (allauth.mfa) ───────────────────────
# TOTP authenticator app + recovery codes + WebAuthn passkeys/security keys.
# Passkeys use the WebAuthn browser flow (fido2 installed); in dev they need
# the insecure-origin escape hatch because localhost is not a secure context.
MFA_SUPPORTED_TYPES = ["recovery_codes", "totp", "webauthn"]
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = DEBUG

# Dual-mode auth: the headless API (/api/auth/*, consumed by the Alpine login
# modal on both render roads) AND server-rendered allauth pages (/accounts/*,
# login / signup / password reset / email management / confirmation). Keeping
# HEADLESS_ONLY=False lets both coexist — pages for no-JS/progressive flows,
# JSON endpoints for the modal.
HEADLESS_ONLY = False

# Server-rendered allauth page URLs (fallback for non-JS + full-page flows).
# The modal posts to /api/auth/browser/v1/auth/login directly; these URLs are
# used by login_required redirects and the account management pages.
ACCOUNT_LOGIN_URL = "/accounts/login/"
ACCOUNT_SIGNUP_URL = "/accounts/signup/"
ACCOUNT_EMAIL_URL = "/accounts/email/"
ACCOUNT_PASSWORD_CHANGE_URL = "/accounts/password/change/"
ACCOUNT_PASSWORD_RESET_URL = "/accounts/password/reset/"

# Branded transactional email. Console backend in dev so the messages render to
# the server log (visible in the preview run); swap to SMTP in production via
# EMAIL_BACKEND/EMAIL_HOST/… env vars (see .env.example — Gmail SMTP for
# structa.cloud@gmail.com).
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    _cfg("SITE.default_email", "Structa Cloud <structa.cloud@gmail.com>"),
)
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_SUBJECT_PREFIX = ""  # subjects already carry the brand via templates

# Gmail SMTP (structa.cloud@gmail.com) — populated from env so no secrets live
# in the repo. The values only take effect once EMAIL_BACKEND is set to the SMTP
# backend; they stay inert while the console backend is the dev default.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

# ── Newsletter provider (Mailchimp / Brevo / webhook) ─────────────
# NEWSLETTER_PROVIDER selects the sync target for NewsletterSubscriber
# signups: "" (off), "mailchimp", "brevo", or "webhook". The subscribe API
# pushes every signup to the provider (idempotent) and the
# sync_newsletter_provider management command bulk-exports the whole list.
# All values come from env so no secrets live in the repo.
NEWSLETTER_PROVIDER = os.environ.get("NEWSLETTER_PROVIDER", "")
NEWSLETTER_MAILCHIMP_API_KEY = os.environ.get("NEWSLETTER_MAILCHIMP_API_KEY", "")
NEWSLETTER_MAILCHIMP_LIST_ID = os.environ.get("NEWSLETTER_MAILCHIMP_LIST_ID", "")
NEWSLETTER_MAILCHIMP_SERVER_PREFIX = os.environ.get("NEWSLETTER_MAILCHIMP_SERVER_PREFIX", "us1")
NEWSLETTER_BREVO_API_KEY = os.environ.get("NEWSLETTER_BREVO_API_KEY", "")
NEWSLETTER_BREVO_LIST_ID = os.environ.get("NEWSLETTER_BREVO_LIST_ID", "")
NEWSLETTER_WEBHOOK_URL = os.environ.get("NEWSLETTER_WEBHOOK_URL", "")

# CORS: the Astro frontend (:4321) posts credentials to the headless API.
# The LandingCorsMiddleware already allows credentialed reads on the landing
# routes; the allauth headless API answers on /api/auth/* so we permit that
# origin list there too.
ALLAUTH_CORS_ORIGIN_WHITELIST = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:4321,http://localhost:3000").split(",")
    if o.strip()
]

# CSRF: the Astro dev server proxies /accounts/* to this backend, so the
# browser's Origin header on form POSTs is the Astro origin (:3000) while the
# proxied Host is :8074. Those Astro origins must be trusted or every auth
# form 403s with "Origin checking failed". The backend's own origins are
# included too (same-host form posts), plus any env-provided entries.
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8074",
    "http://127.0.0.1:8074",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    *[o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()],
]

# Social providers — GitHub + Google. Client IDs/secrets come from env vars;
# in dev both accept the login flow and redirect back to the callback.
# Values are read at request time so empty IDs simply disable the button.
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

# The login URL drives redirect-after-login targets. For headless mode the
# modal handles redirects itself; LOGIN_REDIRECT_URL is used by the Django
# admin fallback.
LOGIN_REDIRECT_URL = "/"

# ── Learning commerce ─────────────────────────────────────────────
# The learning core owns entitlements independently of payment providers.
# Checkout stays disabled until a provider is explicitly configured, avoiding
# false-positive commercial flows in local/dev environments.
LEARNING_PAYMENT_PROVIDER = os.environ.get("LEARNING_PAYMENT_PROVIDER", "")
LEARNING_PAYMENT_ENABLED = bool(LEARNING_PAYMENT_PROVIDER)
LEARNING_COURSE_CURRENCY = os.environ.get("LEARNING_COURSE_CURRENCY", "USD")
# Unified catalog currency — one setting drives products + courses + editions
# pricing across both websites. Products fall back to it when no per-record
# currency is set (see apps/content/models/products.py).
FUSION_DEFAULT_CURRENCY = os.environ.get("FUSION_DEFAULT_CURRENCY", "USD")
# login_required redirects land on the server-rendered page (browser flow);
# the headless API is still consumed directly by the Alpine modal.
LOGIN_URL = "/accounts/login/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── i18n ───────────────────────────────────────────────────────────
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en")
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Shared Django/Wagtail language catalog. The Wagtail SiteLanguage snippet
# controls editorial visibility; these settings validate requests and provide
# the default catalog before snippets are seeded.
FUSION_LANGUAGES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
    ("sv", _("Swedish")),
    ("fr", _("French")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("pt", _("Portuguese")),
]
LANGUAGES = FUSION_LANGUAGES
LANGUAGE_SESSION_KEY = os.environ.get("LANGUAGE_SESSION_KEY", "_language")
LANGUAGE_COOKIE_NAME = os.environ.get("LANGUAGE_COOKIE_NAME", "django_language")
LANGUAGE_COOKIE_AGE = int(os.environ.get("LANGUAGE_COOKIE_AGE", str(60 * 60 * 24 * 365)))
LANGUAGE_COOKIE_DOMAIN = os.environ.get("LANGUAGE_COOKIE_DOMAIN") or None
LANGUAGE_COOKIE_PATH = os.environ.get("LANGUAGE_COOKIE_PATH", "/")
LANGUAGE_COOKIE_SECURE = os.environ.get("LANGUAGE_COOKIE_SECURE", "0").lower() in {"1", "true", "yes", "on"}
LANGUAGE_COOKIE_HTTPONLY = os.environ.get("LANGUAGE_COOKIE_HTTPONLY", "0").lower() in {"1", "true", "yes", "on"}
LANGUAGE_COOKIE_SAMESITE = os.environ.get("LANGUAGE_COOKIE_SAMESITE", "Lax")

# Supported languages — mirrors the Astro frontend translations module.
# Swedish (sv) added per request; Arabic (ar) has full RTL support.
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
    ("sv", _("Swedish")),
    ("fr", _("French")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("pt", _("Portuguese")),
]
LANGUAGES_BIDI = ["ar"]

# Wagtail's native locale model is enabled alongside the landing overlay
# contract. The page tree remains English-canonical, while editors can add
# native Wagtail translations and the Astro road can use PageTranslation.
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES
WAGTAIL_I18N_LOCALE_MODEL = "wagtailcore.Locale"

# Locale paths — Django scans these for .po translation files.
# The catalogs live beside settings.py in backend/locale (BASE_DIR is the
# precis-landing project root, so the backend subdir is explicit).
LOCALE_PATHS = [
    BASE_DIR / "backend" / "locale",
]

# The shared django-fusion middleware above owns query/session/cookie/header
# negotiation for both full documents and HTMX fragments. Keep this settings
# module free of a second locale resolver.

# i18n URL pattern — when True, Django prefixes URLs with the language code
# (e.g. /en/about/, /ar/about/). The landing site uses cookie-based switching
# so all routes stay at root; set False for single-domain cookie switching.
USE_I18N_URL_PATTERNS = False

# ── Static / Media ─────────────────────────────────────────────────
STATIC_URL = "/static/"
# Static files are owned by this standalone landing backend. Keep source and
# collected paths beside settings.py so local Django, the Docker image, and
# the proxy all resolve the same product screenshots and compiled CSS.
# The full read → output → deploy reference (STATICFILES_DIRS / STATIC_ROOT /
# MEDIA_ROOT / bundles / fusion.css / Docker volumes) lives in
# configs/defaults.yml under ``STATIC:`` and is printed by `make config-show`.
_BACKEND_DIR = Path(__file__).resolve().parent
STATIC_ROOT = _BACKEND_DIR / "assets" / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = _BACKEND_DIR / "assets" / "media"

# Source assets are split between the backend-owned preview captures and the
# shared landing assets. Keep both directories separate from STATIC_ROOT so
# Django's development finder and collectstatic see the same CSS, favicon, and
# product media used by the Astro and Wagtail roads.
_BACKEND_STATIC_DIR = _BACKEND_DIR / "assets" / "static"
_SHARED_STATIC_DIR = BASE_DIR / "assets" / "static"
STATICFILES_DIRS = [
    path for path in (_BACKEND_STATIC_DIR, _SHARED_STATIC_DIR) if path.exists()
]

# ── Wagtail ────────────────────────────────────────────────────────
# Identity defaults come from the project config cascade (configs/admin.yml +
# configs/site.yml) so the admin panel and domains stay in one place; env vars
# still win. Proxy contract: /admin → Wagtail login, /django-admin → Django
# admin login (see application/proxy/README.md).
WAGTAIL_SITE_NAME = os.environ.get(
    "WAGTAIL_SITE_NAME",
    _cfg("SITE.wagtail_site_name", _cfg("ADMIN.wagtail_site_name", "StructAI Softwares")),
)
WAGTAILADMIN_BASE_URL = os.environ.get(
    "WAGTAILADMIN_BASE_URL",
    _cfg("ADMIN.wagtailadmin_base_url", "http://localhost:8074"),
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Webpack Loader (django-webpack-loader) ────────────────────────
# Reads the bundles.json produced by webpack/precis-landing.config.js.
# Templates use {% render_bundle 'landing' 'css' %} / 'js' %}.
WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": str(BASE_DIR / "backend" / "assets" / "static" / "bundles" / "bundles.json"),
    }
}

# ── Fusion Asset Pipeline ──────────────────────────────────────────
# Mirrors the Astro frontend bundler output so both Django template tags
# ({% fusion_top_assets %}) and the Astro build (vite) emit the same URLs.
# Served via: GET /apis/assets/
FUSION_ASSETS = {
    "top": {
        "preconnect": [
            "https://fonts.googleapis.com",
            "https://fonts.gstatic.com",
        ],
        "fonts": [
            "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Public+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap",
        ],
        "css": [],
    },
    "bottom": {
        "js": [],
    },
}

FUSION_PIPELINE = {
    "enabled": True,
    # Webpack bundles (webpack/precis-landing.config.js →
    # backend/assets/static/bundles/bundles.json) are merged into the
    # unified asset manifest served at GET /apis/assets/ so the Astro road
    # preloads the same Django-road bundles (single bundle source).
    # ``render_first_gates_assets`` ties asset loading to the render-first
    # flag: in data-api mode (FUSION_RENDER_FIRST=0) the webpack/skeleton
    # links are trimmed from the manifest; render-first serves them.
    "render_first_gates_assets": True,
    "webpack": {
        "enabled": True,
        "stats_file": str(BASE_DIR / "backend" / "assets" / "static" / "bundles" / "bundles.json"),
        "bundle_dir": "bundles/",
    },
    "components": {
        "enabled": True,
        "manifest_path": str(_ASSETS_DIR / "static" / "components" / "manifest.json"),
    },
    "static_url": STATIC_URL,
}

# ── Fusion Render Mode (django-fusion settings config) ─────────────
# The dual-mode contract used across django-fusion
# (``RoutableComponent.get_fusion_render_first()`` / ``FusionDualModeMixin``
# read ``FUSION_RENDER_FIRST``):
#
#   True  → "fusion render first" — Django serves finished server-rendered
#           HTML as the source of truth (SEO friendly, no client render).
#   False → "data APIs" — the client (Astro build) renders from /apis/* JSON.
#
# The same flag is surfaced on /apis/assets/ as ``fusion_render_first`` and
# (with ``render_first_gates_assets``) decides whether webpack/skeleton
# bundles are served — one variable checks both render mode and asset loading.
# Override per request with the ``X-Fusion-Render-First: true|false`` header.
# Env: FUSION_RENDER_FIRST=1|0
FUSION_RENDER_FIRST = os.environ.get("FUSION_RENDER_FIRST", "0") == "1"

# ── Task Center (website-record contract) ──────────────────────────
# The shared worker writes django_fusion's BackgroundTaskLog; the authenticated
# /tasks/ page mirrors it into apps.tasks.TaskExecution filtered by this site.
FUSION_TASK_SITE_NAME = os.environ.get("FUSION_TASK_SITE_NAME", "precis-dev")
FUSION_TASK_EXECUTION_MODEL = os.environ.get("FUSION_TASK_EXECUTION_MODEL", "tasks.TaskExecution")
FUSION_TASK_MODULES = [
    "plugins.workers.email_tasks",
    "plugins.workers.legacy_email_tasks",
    "plugins.workers.content_tasks",
]

if TENANCY_ENABLED:
    # Switch to the django-tenants PostgreSQL backend (schema-aware)
    DATABASES["default"]["ENGINE"] = "django_tenants.postgresql_backend"
    DATABASE_ROUTERS = ["django_tenants.routers.TenantSyncRouter"]
    # Path-based center middleware (replaces host-based TenantMainMiddleware)
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.contrib.sessions.middleware.SessionMiddleware") + 1,
        "apps.tenants.middleware.PathCenterMiddleware",
    )
    PUBLIC_SCHEMA_URLCONF = "configs.urls_public"
    SHOW_PUBLIC_IF_NO_TENANT_FOUND = True
