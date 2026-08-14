"""
FormintC purchase-app backend settings.

A self-contained Django configuration for the FormintC client purchase app
(restaurant / coffee-shop storefront). Mirrors the landing-fusion backend
layout (standalone settings.py — no shared-config dependency) and the
django-allauth headless auth contract the AHA stack consumes:

    POST /api/auth/browser/v1/auth/login     { email, password }
    GET  /api/auth/browser/v1/auth/session
    DELETE /api/auth/browser/v1/auth/session (logout)
    GET  /accounts/login/                    server-rendered fallback
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "formintc-purchase-dev-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "corsheaders",
    # django-fusion — unified fragment/layout rendering pipeline (replaces
    # django_htmx): HTMX request detection, FragmentComponent / PageHandler
    # views, dual-mode render contract, and the fusion asset pipeline.
    "django_fusion",
    # Auth — django-allauth headless API (login/signup/session/logout)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.headless",
    "allauth.mfa",
    # Wagtail CMS
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
    # Shop + employee apps
    "shop",
    "employee",
    "cms",  # Wagtail page models, blocks (badges/stars), and site settings
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # CORS — the Vue POS client (:1420) and Astro storefront (:4322) fetch
    # the Django portal cross-origin; must sit above CommonMiddleware.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "urls"

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
                "shop.context_processors.shop_branding",
                "wagtail.contrib.settings.context_processors.settings",
            ],
            "libraries": {
                "components": "django_fusion.comp.templatetags.components",
            },
        },
    },
]

WSGI_APPLICATION = "wsgi.application"

# allauth headless URL patterns carry no trailing slash; disable slash
# appending so POST bodies are not 301-redirected.
APPEND_SLASH = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3"))),
    }
}

SITE_ID = 1

# ── Auth (django-allauth headless) ────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
# Dev-friendly: no email verification so signup flows are instant. Flip to
# "mandatory" for production (console email backend already configured).
ACCOUNT_EMAIL_VERIFICATION = os.environ.get("ACCOUNT_EMAIL_VERIFICATION", "none")
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

ACCOUNT_ADAPTER = "shop.auth_adapters.FormintCPurchaseAccountAdapter"

# Two-factor: TOTP + recovery codes (WebAuthn needs a secure context; passkeys
# are available in production HTTPS deploys).
MFA_SUPPORTED_TYPES = ["recovery_codes", "totp"]
MFA_PASSKEY_LOGIN_ENABLED = False

# Dual-mode auth: headless API (Alpine modal) AND server-rendered allauth pages.
HEADLESS_ONLY = False

ACCOUNT_LOGIN_URL = "/accounts/login/"
ACCOUNT_SIGNUP_URL = "/accounts/signup/"
ACCOUNT_EMAIL_URL = "/accounts/email/"
ACCOUNT_PASSWORD_CHANGE_URL = "/accounts/password/change/"
ACCOUNT_PASSWORD_RESET_URL = "/accounts/password/reset/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "Formint Café <orders@formintcafe.example>"
)
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Astro dev server proxies /api, /accounts, /shop and /employee to this
# backend — those Astro origins must be CSRF-trusted for POST forms.
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8075",
    "http://127.0.0.1:8075",
    "http://localhost:4322",
    "http://127.0.0.1:4322",
    "http://localhost:1420",
    "http://127.0.0.1:1420",
    *[o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()],
]

# Credentialed reads from the Astro origin to the headless API.
ALLAUTH_CORS_ORIGIN_WHITELIST = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:4322,http://localhost:1420",
    ).split(",")
    if o.strip()
]

# ── CORS (django-cors-headers) ───────────────────────────────────────
# The Vue POS client (:1420) and the storefront/dev previews (:4322/:4173)
# call the portal cross-origin; credentials are needed for the fusion
# session-mode POST/DELETE. Extend via CORS_ALLOWED_ORIGINS env (comma list).
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:1420",
    "http://127.0.0.1:1420",
    "http://localhost:4322",
    "http://127.0.0.1:4322",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:8075",
    *[o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()],
]

# ── Shop / storefront branding ────────────────────────────────────────
SHOP_NAME = os.environ.get("SHOP_NAME", "Formint Café")
SHOP_TAGLINE = os.environ.get(
    "SHOP_TAGLINE", "Roasted to order. Brewed to the table."
)
# Order types offered at checkout.
SHOP_ORDER_TYPES = [
    ("dine_in", "Dine in"),
    ("takeaway", "Takeaway"),
    ("delivery", "Delivery"),
]

# ── Wagtail CMS ────────────────────────────────────────────────────────
WAGTAIL_SITE_NAME = os.environ.get("WAGTAIL_SITE_NAME", "Formint Café")
WAGTAILADMIN_BASE_URL = os.environ.get(
    "WAGTAILADMIN_BASE_URL", "http://localhost:8075"
)
# The shop storefront owns the site root (/, /menu, /orders …); Wagtail pages
# live at their own slugs under Wagtail routes (e.g. /about/).

# ── i18n ───────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en"
TIME_ZONE = os.environ.get("DJANGO_TZ", "UTC")
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("ar", "Arabic"),
    ("fr", "French"),
]

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.contrib.sessions.middleware.SessionMiddleware") + 1,
    "django.middleware.locale.LocaleMiddleware",
)

LOCALE_PATHS = [BASE_DIR / "locale"]
USE_I18N_URL_PATTERNS = False

# ── Static / media ─────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Fusion Asset Pipeline (django-fusion) ─────────────────────────────
# Mirrors the Astro frontend bundler output so Django template tags and the
# Astro build emit the same URLs (served via GET /fusion/assets/).
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
    "bottom": {"js": []},
}

FUSION_ASSET_PIPELINE = {
    "enabled": True,
    "webpack": {"enabled": False},
    "components": {
        "enabled": True,
        "manifest_path": str(BASE_DIR / "static" / "components" / "manifest.json"),
    },
    "static_url": STATIC_URL,
}

# ── Fusion Render Mode (django-fusion dual-mode contract) ──────────────
#   True  → "fusion render first" — Django serves finished server-rendered
#           HTML as the source of truth.
#   False → "data APIs" — the Astro client renders from /api/* JSON and
#           /shop/fragments/* HTML fragments.
# Override per request with the ``X-Fusion-Render-First: true|false`` header.
# Env: FUSION_RENDER_FIRST=1|0
FUSION_RENDER_FIRST = os.environ.get("FUSION_RENDER_FIRST", "0") == "1"
# Legacy alias — the canonical resolver reads ``FUSION_RENDER_FIRST`` first.
FUSION_RENDER_FIRST_DEFAULT = FUSION_RENDER_FIRST

# django-fusion component registry — template subdirectories whose *.html
# files become registered include-path components.
COMPONENTS_DIR_NAMES = ("components", "partials", "tags")
COMPONENTS_ENABLE_BLOCK_ATTRS = True
