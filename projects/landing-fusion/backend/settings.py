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
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # HTMX
    "django_htmx",
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
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "apps.handlers.middleware.LandingCorsMiddleware",
]

ROOT_URLCONF = "urls"

_PROJECT_DIR = BASE_DIR.parent  # projects/landing-fusion/
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
            # Legacy — backend-level templates (for backward compat)
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── Auth ───────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── i18n ───────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── Static / Media ─────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = _ASSETS_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = _ASSETS_DIR / "media"

# STATICFILES_DIRS: include project-level assets/static/
STATICFILES_DIRS = [
    _ASSETS_DIR / "static",
] if (_ASSETS_DIR / "static").exists() else []

# ── Wagtail ────────────────────────────────────────────────────────
WAGTAIL_SITE_NAME = "Fusion Landing"
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
