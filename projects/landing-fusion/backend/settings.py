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

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "landing-fusion-dev-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") if host.strip()]

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
    # Landing apps (lms-fusion-style organization)
    "apps.content",  # StreamField blocks + block templates
    "apps.pages",  # Wagtail page models + page templates + seed
    "apps.handlers",  # PageHandler views (HTMX fragment rendering)
    "apps.auth",  # Allauth auth adapters + templates (LandingAuthAdapter + social)
    "apps.learning",  # Commercial LMS catalog, enrollment, progress, and learner profile
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
_ASSETS_DIR = _PROJECT_DIR / "assets"

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
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
            "libraries": {
                # django-fusion component tags (comp, slot, prop, var) — registered
                # so `{% load components %}` works, mirroring configs/base/templates.py.
                "components": "django_fusion.comp.templatetags.components",
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

# Adapters — custom landing-fusion adapters for HTMX/Alpine templates
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
# EMAIL_BACKEND/EMAIL_HOST/… env vars.
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Structa Cloud <structa.cloud@gmail.com>")
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_SUBJECT_PREFIX = ""  # subjects already carry the brand via templates

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

# Locale paths — Django scans these for .po translation files.
# The first entry is the project-level locale directory.
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Locale middleware — detects the user's language preference from the
# ``django_language`` cookie (set by the Astro language switcher) or the
# Accept-Language header, and activates it for the request.
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.contrib.sessions.middleware.SessionMiddleware") + 1,
    "django.middleware.locale.LocaleMiddleware",
)

# i18n URL pattern — when True, Django prefixes URLs with the language code
# (e.g. /en/about/, /ar/about/). The landing site uses cookie-based switching
# so all routes stay at root; set False for single-domain cookie switching.
USE_I18N_URL_PATTERNS = False

# ── Static / Media ─────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = _ASSETS_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = _ASSETS_DIR / "media"

# STATICFILES_DIRS: the landing project's own assets/static/ (compiled
# fusion.css from `make css`). Note: _ASSETS_DIR resolves to the shared
# projects/assets/ (a legacy path that does not exist here), so we point at
# BASE_DIR/assets/static — the real location of the compiled stylesheet.
_PROJECT_STATIC_DIR = BASE_DIR / "assets" / "static"
STATICFILES_DIRS = [
    _PROJECT_STATIC_DIR,
] if _PROJECT_STATIC_DIR.exists() else []

# ── Wagtail ────────────────────────────────────────────────────────
WAGTAIL_SITE_NAME = "StructAI Softwares"
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8074")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

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

FUSION_ASSET_PIPELINE = {
    "enabled": True,
    "webpack": {"enabled": False},
    "components": {
        "enabled": True,
        "manifest_path": str(_ASSETS_DIR / "static" / "components" / "manifest.json"),
    },
    "static_url": STATIC_URL,
}

# ── Fusion Render Mode (django-fusion settings config) ─────────────
# The dual-mode contract used across django-fusion
# (``RoutableComponent.get_fusion_render_first()`` / ``FusionDualModeMixin``
# read ``FUSION_RENDER_FIRST_DEFAULT`` or ``COMPONENTS_FUSION_RENDER_FIRST_DEFAULT``):
#
#   True  → "fusion render first" — Django serves finished server-rendered
#           HTML as the source of truth (SEO friendly, no client render).
#   False → "data APIs" — the client (Astro build) renders from /apis/* JSON.
#
# Override per request with the ``X-Fusion-Render-First: true|false`` header.
# Env: FUSION_RENDER_FIRST=1|0
FUSION_RENDER_FIRST_DEFAULT = os.environ.get("FUSION_RENDER_FIRST", "0") == "1"
