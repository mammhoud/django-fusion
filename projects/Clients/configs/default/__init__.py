"""Precis-local default settings for the LMS backend.

Import this after site environment configuration to get:
- CD environment layer selection (from configs.settings)
- Shared Django base settings (from configs.base)
- Common Precis/Fusion settings (layouts, features, assets, apps, templates, CORS)
- The ``cfg()`` helper that resolves site settings from env vars,
  Dynaconf YAML, or a Python fallback.

Site-specific settings.py files then override branding, domain, colors, etc.
"""

import os

from configs.settings import *  # noqa: F401,F403 — CD env layer + base settings


# ═══════════════════════════════════════════════════════════════════
# Dynaconf bridge — resolve settings: env var → YAML → fallback
# ═══════════════════════════════════════════════════════════════════
from configs.settings.conf import settings as _dynaconf  # noqa: E402


def cfg(key: str, default=None):
    """Resolve a site setting: environment variable → Dynaconf YAML → default.

    Uses explicit ``key in os.environ`` rather than ``os.environ.get(key) or …``
    so that falsy-but-valid values (empty strings, ``"0"``, ``"false"``) are
    honoured as explicit overrides.
    """
    if key in os.environ:
        return os.environ[key]
    return _dynaconf.get(key, default)


# ═══════════════════════════════════════════════════════════════════
# URL / ASGI / WSGI (same for all fusion sites)
# ═══════════════════════════════════════════════════════════════════
ROOT_URLCONF = "apps.urls"
ASGI_APPLICATION = "server.asgi_application"
WSGI_APPLICATION = "server.application"
SITE_ID = 1


# ═══════════════════════════════════════════════════════════════════
# Common Local Apps (same for both LMS and CMS)
# ═══════════════════════════════════════════════════════════════════
LOCAL_APPS = [
    "apps.domain",
    "apps.core",
    "apps.content.apps.ContentConfig",
    "apps.pages.pages.apps.PagesConfig",
    "apps.handlers.apps.AccountsConfig",
    "apps.pages.accounts.apps.AccountsConfig",
    "apps.learning.apps.LearningConfig",
    "apps.pages.blog.apps.BlogConfig",
    "apps.pages.products.apps.ProductsConfig",
    "apps.pages.profile.apps.ProfileConfig",
    "django_fusion.fragments.analyzer.apps.AnalyzerAppConfig",
    "apps.pages.branding.apps.BrandingConfig",
]
INSTALLED_APPS += LOCAL_APPS
# The shared worker is now the canonical plugins.workers Dramatiq app.


# ═══════════════════════════════════════════════════════════════════
# Template Extensions (fusion_layout builtins + libraries)
# ═══════════════════════════════════════════════════════════════════
TEMPLATES[0]["OPTIONS"]["builtins"].append(
    "django_fusion.comp.templatetags.fusion_layout"
)
TEMPLATES[0]["OPTIONS"]["libraries"]["fusion_layout"] = (
    "django_fusion.comp.templatetags.fusion_layout"
)


# ═══════════════════════════════════════════════════════════════════
# Domain / Profile / Wagtail (same for both)
# ═══════════════════════════════════════════════════════════════════
PROFILE_MODEL = "auth.User"
WAGTAIL_WORKFLOW_ENABLED = False


# ═══════════════════════════════════════════════════════════════════
# Fusion Shared Settings
# ═══════════════════════════════════════════════════════════════════
FUSION_LAYOUTS = {
    "default": "fusion/layouts/default.html",
    "full_width": "fusion/layouts/full_width.html",
    "sidebar": "fusion/layouts/sidebar.html",
    "blank": "fusion/layouts/blank.html",
}
FUSION_DEFAULT_LAYOUT = "default"

FUSION_FEATURES = {
    "blog": True,
    "courses": True,
    "products": True,
    "pages": True,
    "auth": True,
    "profile": True,
    "branding": True,
    "search": True,
}

FUSION_ASSETS = {
    "top": {
        "css": ["/static/css/fusion.css"],
        "fonts": [
            "/static/fonts/remixicon/remixicon.css",
            "/static/fonts/fontawesome-free/css/all.min.css",
        ],
        "preconnect": ["https://fonts.googleapis.com"],
        "inline_css": [],
    },
    "bottom": {
        "js": ["/static/js/fusion-bridge.js"],
        "inline_js": [],
    },
}


# ═══════════════════════════════════════════════════════════════════
# CORS — shared defaults
# ═══════════════════════════════════════════════════════════════════
CORS_ALLOW_CREDENTIALS = True

if "corsheaders" not in INSTALLED_APPS:
    INSTALLED_APPS.append("corsheaders")
if "corsheaders.middleware.CorsMiddleware" not in MIDDLEWARE:
    idx = next(
        (i for i, m in enumerate(MIDDLEWARE) if m.startswith("django.middleware.security")),
        0,
    ) + 1
    MIDDLEWARE.insert(idx, "corsheaders.middleware.CorsMiddleware")
