"""
Landing-fusion backend settings.

A self-contained Django + Wagtail configuration for the landing-only slice of
the ASTRO migration. Unlike the shared ``configs.default`` layer used by the
full CMS sites, this module keeps the landing backend standalone so it can be
deployed side-by-side with the Astro frontend without wiring the entire Fusion
workspace.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "precis-landing-dev-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
# Default to backend + localhost only (secure fallback). Production
# docker-compose.yml sets DJANGO_ALLOWED_HOSTS explicitly with the public
# domains appended, so this default never tightens a deployed site.
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,precis-landing-backend,precis-landing-frontend").split(",") if host.strip()]

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
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serve /static/ from STATIC_ROOT in production (traefik routes /static
    # to Django; staticfiles_urlpatterns() is debug-only). whitenoise is a
    # declared dependency — wire it here so backend-rendered pages get their
    # compiled fusion.css after `make css` + collectstatic.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "apps.handlers.middleware.LandingCorsMiddleware",
]

ROOT_URLCONF = "urls"

_PROJECT_DIR = BASE_DIR.parent  # projects/
# Landing-fusion owns a colocated assets directory at
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
# Local dev defaults to SQLite. Set DJANGO_DB_ENGINE=django.db.backends.postgresql
# (or USE_POSTGRES=1) to connect to the shared ``postgres`` container
# (applications/databases) with this site's own database (DB_NAME_LANDING →
# db_precis_landing), matching the other Precis/Fusion sites on the shared cluster.
if os.environ.get("DJANGO_DB_ENGINE", "") == "django.db.backends.postgresql" or os.environ.get("USE_POSTGRES", "0") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DJANGO_DB_NAME", "db_precis_landing"),
            "USER": os.environ.get("DJANGO_DB_USER", "admin"),
            "PASSWORD": os.environ.get("DJANGO_DB_PASSWORD", ""),
            "HOST": os.environ.get("DJANGO_DB_HOST", "postgres"),
            "PORT": os.environ.get("DJANGO_DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3"))),
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
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Structa Cloud <structa.cloud@gmail.com>")
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
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

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

# Locale middleware — detects the user's language preference from the
# ``django_language`` cookie (set by the Astro language switcher) or the
# Accept-Language header, and activates it for the request.
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.contrib.sessions.middleware.SessionMiddleware") + 1,
    "django.middleware.locale.LocaleMiddleware",
)
# After LocaleMiddleware: activate the locale from the landing ?lang= / cookie
# resolver so {% translate %} tags on server-rendered pages and fragments
# follow the same language the content-overlay API uses.
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.locale.LocaleMiddleware") + 1,
    "apps.handlers.middleware.LandingLocaleMiddleware",
)

# i18n URL pattern — when True, Django prefixes URLs with the language code
# (e.g. /en/about/, /ar/about/). The landing site uses cookie-based switching
# so all routes stay at root; set False for single-domain cookie switching.
USE_I18N_URL_PATTERNS = False

# ── Static / Media ─────────────────────────────────────────────────
STATIC_URL = "/static/"
# Static files are owned by this standalone landing backend. Keep source and
# collected paths beside settings.py so local Django, the Docker image, and
# the proxy all resolve the same product screenshots and compiled CSS.
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
WAGTAIL_SITE_NAME = "StructAI Softwares"
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8074")

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
FUSION_TASK_SITE_NAME = os.environ.get("FUSION_TASK_SITE_NAME", "precis-landing")
FUSION_TASK_EXECUTION_MODEL = os.environ.get("FUSION_TASK_EXECUTION_MODEL", "tasks.TaskExecution")
FUSION_TASK_MODULES = [
    "plugins.workers.email_tasks",
    "plugins.workers.content_tasks",
]
