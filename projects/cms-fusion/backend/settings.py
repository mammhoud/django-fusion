"""Website-local Django settings for cms-fusion."""
import os
import sys
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"
_APPS_DIR = _SITE_DIR / "apps"

# Ensure correct import paths.
# Iteration order is REVERSED so `sys.path.insert(0, …)` puts the per-site
# `apps/` and `www/` at the front of sys.path[0], ahead of the workspace
# `/app` whose `/app/www` only contains the shared `ci/` and `worker/`
# subpackages — without `projects/`.
for _path in (str(_WORKSPACE_DIR), str(_SITE_DIR), str(_SITE_APP_DIR), str(_APPS_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)


# ============================================================
# Site Configuration
# ============================================================
from configs.site import configure_site_environment, WORKSPACE_DIR

# Force the correct WEBSITE_DIR and WEBSITE before importing shared settings.
# The cms-fusion name isn't in sites.yml, so configure_site_environment
# would fall back to the default 'lms' site, resolving BASE_DIR to
# /app/websites/lms instead of /app/cms-fusion. Explicitly set them here
# to keep all env vars consistent.
_cms_site_dir = str(WORKSPACE_DIR / "cms-fusion")
if "WEBSITE_DIR" not in os.environ:
    os.environ["WEBSITE_DIR"] = _cms_site_dir
if "DJANGO_WEBSITE_DIR" not in os.environ:
    os.environ["DJANGO_WEBSITE_DIR"] = _cms_site_dir
if "WEBSITE" not in os.environ:
    os.environ["WEBSITE"] = "cms-fusion"
if "WEBSITE_NAME" not in os.environ:
    os.environ["WEBSITE_NAME"] = "cms-fusion"
if "DJANGO_WEBSITE" not in os.environ:
    os.environ["DJANGO_WEBSITE"] = "cms-fusion"

configure_site_environment("cms-fusion", module="FUSION", default_port=5070)

# ============================================================
# Internal Dependency Handling
# ============================================================
# django_fusion is the real workspace framework. Do not install
# fake sys.modules shims here; dependency failures should surface during checks.

# ============================================================
# Import Shared Django Settings
# ============================================================
from configs.settings import *  # noqa: E402,F401,F403

# ============================================================
# URL and Application Configuration
# ============================================================
ROOT_URLCONF = "www.urls"

# ASGI/WSGI applications live in the site-local server.py.
# The start script places this site directory on PYTHONPATH and launches
# server:application, so Django can keep the same import path.
ASGI_APPLICATION = "server.asgi_application"
WSGI_APPLICATION = "server.application"

# ============================================================
# Website-Specific Settings
# ============================================================
WEBSITE_NAME = "cms-fusion"
WEBSITE_IDENTIFIER = "cms-fusion"
SITE_ID = 1

# ── Wagtail admin branding ──
WAGTAIL_SITE_NAME = "Fusion CMS"

# ── Local apps (site-specific plugins, www packages, and page apps) ──
# NOTE: `www.worker` is NOT listed here because `core.configs.base.apps`
# already registers it globally as a shared worker module — including it
# here would register the same app label twice and Django would raise
# `ImproperlyConfigured: Application labels aren't unique`.
LOCAL_APPS = [
    "apps.domain",
    "apps.core",
    "apps.content.apps.ContentConfig",
    "apps.pages.pages.apps.PagesConfig",
    "apps.handlers.apps.AccountsConfig",
    "apps.pages.accounts.apps.AccountsConfig",
    "apps.pages.lms.apps.LmsConfig",
    "apps.pages.blog.apps.BlogConfig",
    "apps.pages.products.apps.ProductsConfig",
    "apps.pages.profile.apps.ProfileConfig",
    "django_fusion.fragments.analyzer.apps.AnalyzerAppConfig",
    "apps.pages.branding.apps.BrandingConfig",
]
INSTALLED_APPS += LOCAL_APPS

# The shared `www.worker` app is registered globally in `configs.base.apps`,
# but the fusion projects have their own site-local `www` package that shadows
# the workspace one, so `www.worker` cannot be imported here. Remove it from
# the fusion app registry; the fusion sites run their own task/worker stack
# through django-fusion and do not need the legacy shared worker.
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "www.worker"]

# Register fusion_layout template tag library as both a builtin and library.
# - builtin:  allows {% fusion_layout %} and {% fusion_render_first_flag %} without {% load %}
# - library:  allows {% load fusion_layout %} in templates like base.html
# The shared configs/base/templates.py should have both, but /app/configs/ is
# read-only in the container, so we duplicate the registration here.
TEMPLATES[0]["OPTIONS"]["builtins"].append(
    "django_fusion.comp.templatetags.fusion_layout"
)
TEMPLATES[0]["OPTIONS"]["libraries"]["fusion_layout"] = (
    "django_fusion.comp.templatetags.fusion_layout"
)

# Dynamic branding context processor
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "apps.pages.branding.context_processors.fusion_branding_context"
)

# ============================================================
# Domain model settings
# ============================================================
# PROFILE_MODEL is a required ForeignKey target in domain models.
# Point it to Django's built-in User model since this project
# does not have a separate profile model.
PROFILE_MODEL = "auth.User"

# ============================================================
# Silenced system checks
# ============================================================
# Keep only legacy duplicated app/model checks silenced; the previous
# TeamMembership ordering check is fixed in domain models.
SILENCED_SYSTEM_CHECKS = [
    "treebeard.E001",
    # Legacy duplicated app/model clashes from removed framework apps
    "models.E028",  # db_table clashes
    "models.E030",  # index name clashes
    "models.E032",  # constraint name clashes
    "fields.E300",   # relation with uninstalled models
    "fields.E304",   # reverse accessor clashes
    "fields.E305",   # reverse query name clashes
    "fields.E307",   # lazy reference to uninstalled model
    "fields.E340",   # intermediary table name clashes
]
WAGTAIL_WORKFLOW_ENABLED = False

# ═══════════════════════════════════════════════════════════════════
# Fusion Branding (override defaults)
# ═══════════════════════════════════════════════════════════════════
FUSION_SITE_NAME = os.environ.get("FUSION_SITE_NAME", "Fusion CMS")
FUSION_COMPANY_NAME = os.environ.get("FUSION_COMPANY_NAME", "Fusion Inc.")
FUSION_CREATOR_NAME = os.environ.get("FUSION_CREATOR_NAME", "Fusion Team")
FUSION_PRIMARY_COLOR = os.environ.get("FUSION_PRIMARY_COLOR", "#7c3aed")
FUSION_SECONDARY_COLOR = os.environ.get("FUSION_SECONDARY_COLOR", "#5b21b6")

# ═══════════════════════════════════════════════════════════════════
# Fusion Layouts
# ═══════════════════════════════════════════════════════════════════
FUSION_LAYOUTS = {
    "default": "fusion/layouts/default.html",
    "full_width": "fusion/layouts/full_width.html",
    "sidebar": "fusion/layouts/sidebar.html",
    "blank": "fusion/layouts/blank.html",
}
FUSION_DEFAULT_LAYOUT = "default"

# ═══════════════════════════════════════════════════════════════════
# Fusion Features (toggle individual CMS features)
# ═══════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════
# Fusion Render-First
# ═══════════════════════════════════════════════════════════════════
FUSION_RENDER_FIRST_DEFAULT = True

# ═══════════════════════════════════════════════════════════════════
# Fusion Assets — top/bottom asset manifest served to Next.js frontend
# ═══════════════════════════════════════════════════════════════════
FUSION_ASSETS = {
    "top": {
        "css": [
            "/static/css/fusion.css",
        ],
        "fonts": [
            "/static/fonts/remixicon/remixicon.css",
            "/static/fonts/fontawesome-free/css/all.min.css",
        ],
        "preconnect": [
            "https://fonts.googleapis.com",
        ],
        "inline_css": [],
    },
    "bottom": {
        "js": [
            "/static/js/fusion-bridge.js",
        ],
        "inline_js": [],
    },
}

# ═══════════════════════════════════════════════════════════════════
# CORS — allow frontend origins to access the API
# ═══════════════════════════════════════════════════════════════════
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]
CORS_ALLOW_CREDENTIALS = True

# ═══════════════════════════════════════════════════════════════════
# CORS — force-enable cortheaders since configs/base may be read-only
# ═══════════════════════════════════════════════════════════════════
if "corsheaders" not in INSTALLED_APPS:
    INSTALLED_APPS.append("corsheaders")
if "corsheaders.middleware.CorsMiddleware" not in MIDDLEWARE:
    idx = next((i for i, m in enumerate(MIDDLEWARE) if m.startswith("django.middleware.security")), 0) + 1
    MIDDLEWARE.insert(idx, "corsheaders.middleware.CorsMiddleware")
