"""Site-specific Django settings for ctc-research.

Imports shared Fusion defaults from configs.default, then applies
CTC Research-specific branding, CORS origins, and feature flags.
"""

import os
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# Path Configuration — ensure correct import resolution
# ═══════════════════════════════════════════════════════════════════
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_PROJECTS_DIR = _WORKSPACE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"
_APPS_DIR = _SITE_DIR / "apps"

for _path in (str(_PROJECTS_DIR), str(_WORKSPACE_DIR), str(_SITE_DIR),
              str(_SITE_APP_DIR), str(_APPS_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# The canonical shared settings package lives at projects/precis/configs (not
# backend/configs). Prefer projects/precis for `import configs` so every site
# resolves one shared source; the site-local backend dir stays on the path for
# `apps`, `settings`, and `manage.py`.
sys.path.insert(0, str(_PROJECTS_DIR))


# ═══════════════════════════════════════════════════════════════════
# Site Environment — seed env vars before importing shared settings
# ═══════════════════════════════════════════════════════════════════
from configs.site import configure_site_environment  # noqa: E402

configure_site_environment("precis-ctc", module="FUSION", default_port=5070)


# ═══════════════════════════════════════════════════════════════════
# Shared Fusion Settings — CD layer, base Django, common FUSION_*
# Also provides the ``cfg()`` helper for resolving site settings
# from env vars, Dynaconf YAML (Env/_site.yml), or Python fallback.
# ═══════════════════════════════════════════════════════════════════
from configs.default import *  # noqa: E402,F401,F403

# ═══════════════════════════════════════════════════════════════════
# ALLOWED_HOSTS — the Django test client connects as ``testserver``
# ═══════════════════════════════════════════════════════════════════
if "testserver" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, "testserver"]

# TLS terminates at Traefik in production. Tell Django which forwarded scheme
# is authoritative, enforce HTTPS for normal requests, and keep the internal
# container health probes reachable over plain HTTP.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = (r"^health/$", r"^assets/health/$")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ── APPEND_SLASH — kept at the Django default (True).
#
#    Note: the allauth headless URL patterns (e.g. /api/auth/browser/v1/auth/login)
#    are registered WITHOUT trailing slashes, and CommonMiddleware only appends
#    a slash when the slash-less URL does not match. Exact headless requests
#    therefore resolve directly with no redirect (verified in tests); disabling
#    APPEND_SLASH here would turn the public /api/* 301 redirects into 404s.


# ═══════════════════════════════════════════════════════════════════
# Auth — django-allauth headless API (precis-landing parity)
# ═══════════════════════════════════════════════════════════════════
# The Alpine login modal (frontend + Django templates) consumes the
# headless API at /api/auth/browser/v1/auth/* — the same contract as
# precis-landing. Server-rendered /accounts/* pages remain as fallback.
if "allauth.headless" not in INSTALLED_APPS:
    INSTALLED_APPS.append("allauth.headless")
if "apps.auth.apps.PrecisAuthConfig" not in INSTALLED_APPS:
    INSTALLED_APPS.append("apps.auth.apps.PrecisAuthConfig")
if "apps.tasks" not in INSTALLED_APPS:
    INSTALLED_APPS.append("apps.tasks")

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = cfg("ACCOUNT_EMAIL_VERIFICATION", "optional")
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_ADAPTER = "apps.auth.adapters.PrecisAuthAdapter"
SOCIALACCOUNT_ADAPTER = "apps.auth.adapters.PrecisSocialAccountAdapter"
MFA_PASSKEY_LOGIN_ENABLED = cfg("MFA_PASSKEY_LOGIN_ENABLED", True)
MFA_SUPPORTED_TYPES = ["recovery_codes", "totp", "webauthn"]
ACCOUNT_LOGIN_URL = "/accounts/login/"
ACCOUNT_SIGNUP_URL = "/accounts/signup/"
ACCOUNT_EMAIL_URL = "/accounts/email/"


# ═══════════════════════════════════════════════════════════════════
# Site Identity
# ═══════════════════════════════════════════════════════════════════
WEBSITE_NAME = "precis-ctc"
WEBSITE_IDENTIFIER = "precis-ctc"
WAGTAIL_SITE_NAME = cfg("WAGTAIL_SITE_NAME", "CTC Research")

# ── Task Center (website-record contract) ──────────────────────────
# The shared worker writes django_fusion's BackgroundTaskLog; the authenticated
# /tasks/ page (and the scheduled sync_task_history job) mirror it into
# apps.tasks.TaskExecution filtered by this site so the website record stays
# fresh without a Task Center page view.
FUSION_TASK_SITE_NAME = cfg("FUSION_TASK_SITE_NAME", WEBSITE_NAME)
FUSION_TASK_EXECUTION_MODEL = cfg("FUSION_TASK_EXECUTION_MODEL", "tasks.TaskExecution")
FUSION_TASK_MODULES = [
    "plugins.workers.email_tasks",
    "plugins.workers.course_tasks",
    "plugins.workers.content_tasks",
    "plugins.workers.legacy_email_tasks",
    "plugins.workers.campaign_tasks",
]


# ═══════════════════════════════════════════════════════════════════
# Branding — teal theme (env var > _site.yml > fallback)
# ═══════════════════════════════════════════════════════════════════
FUSION_SITE_NAME = cfg("FUSION_SITE_NAME", "CTC Research")
FUSION_COMPANY_NAME = cfg("FUSION_COMPANY_NAME", "CTC Research")
FUSION_CREATOR_NAME = cfg("FUSION_CREATOR_NAME", "CTC Research Team")
FUSION_PRIMARY_COLOR = cfg("FUSION_PRIMARY_COLOR", "#00a1b3")
FUSION_SECONDARY_COLOR = cfg("FUSION_SECONDARY_COLOR", "#008080")


# ═══════════════════════════════════════════════════════════════════
# Render-First — disabled by default for LMS
# ═══════════════════════════════════════════════════════════════════
# Astro is the active document renderer after the cms-fusion consolidation.
# Requests may still override this with X-Fusion-Render-First for compatibility.
# The same flag drives asset loading: with ``render_first_gates_assets`` on in
# FUSION_PIPELINE, webpack/skeleton links are only served while render-first
# is active (see django-fusion ``AssetPipelineOptions``).
FUSION_RENDER_FIRST = cfg("FUSION_RENDER_FIRST", True)

# Keep the Wagtail locale contract aligned with dump-data.json. In particular,
# pt-br is an existing public fixture locale and must not be normalized to pt.
# The shared CD settings provide the Wagtail switches; these explicit values
# make this site's supported content languages unambiguous.
LANGUAGES = [
    ("en", "English"),
    ("sv", "Swedish"),
    ("fr", "French"),
    ("de", "German"),
    ("es", "Spanish"),
    ("ar", "Arabic"),
    ("pt-br", "Portuguese (Brazil)"),
]
# Unified catalog currency — one setting drives products + courses + editions
# pricing across both websites (precis-landing parity). Products and courses
# fall back to it when no per-record currency is set.
FUSION_DEFAULT_CURRENCY = cfg("FUSION_DEFAULT_CURRENCY", "USD")
LANGUAGES_BIDI = ["ar"]
# The Docker image consolidates the project asset tree at /app/assets while
# local development keeps it at <site>/assets. Resolve both from the shared
# asset root so gettext loads the same catalogs in local, test, and container
# processes instead of silently falling back to English.
_LOCALE_DIR = _WORKSPACE_DIR / "assets" / "locale"
_LOCALE_FALLBACK_DIR = _SITE_DIR / "assets" / "locale"
LOCALE_PATHS = [
    str(path)
    for path in (_LOCALE_DIR, _LOCALE_FALLBACK_DIR)
    if path.exists()
]
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES
WAGTAIL_I18N_LOCALE_MODEL = "wagtailcore.Locale"


# ═══════════════════════════════════════════════════════════════════
# Branding Context Processor — resolved from _site.yml
# ═══════════════════════════════════════════════════════════════════
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    cfg("FUSION_BRANDING_BACKEND",
        "django_fusion.contrib.branding.context_processors.fusion_branding_context")
)


# ═══════════════════════════════════════════════════════════════════
# CORS Origins — resolved from _site.yml (YAML key: CORS_ORIGINS)
# ═══════════════════════════════════════════════════════════════════
CORS_ALLOWED_ORIGINS = cfg("CORS_ORIGINS", [
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://localhost:3458",
    "http://127.0.0.1:3458",
    "https://ctc-research.com",
    "https://www.ctc-research.com",
    "https://arch.ctc-research.com",
    "https://precis-lms.com",
    "https://www.precis-lms.com",
])

# Allow custom fusion headers for render-first negotiation.
from corsheaders.defaults import default_headers  # noqa: E402

CORS_ALLOW_HEADERS = [*default_headers, "x-fusion-render-first"]


# ═══════════════════════════════════════════════════════════════════
# Bolt API — complex nested config, kept inline (not in YAML)
# ═══════════════════════════════════════════════════════════════════
FUSION_BOLT = {
    "enabled": True,
    "prefix": "/api",
    "openapi_title": "CTC Research API",
    "openapi_version": "1.0.0",
    "auth_backends": ["jwt"],
    "serializer_format": "dict",
    "cors_origins": [
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "https://ctc-research.com",
        "https://www.ctc-research.com",
        "https://arch.ctc-research.com",
        "https://precis-lms.com",
        "https://www.precis-lms.com",
    ],
    "component_auto_register": True,
}


# ═══════════════════════════════════════════════════════════════════
# Asset Consolidation — all templates, static, media, and styles
# live under the workspace-level assets/ directory.
# ═══════════════════════════════════════════════════════════════════

# Templates: ensure the consolidated assets/templates/ is in DIRS.
# The shared configs already include this path via BASE_DIR.parent, but
# we add it explicitly so it takes priority over scattered app dirs.
_ASSETS_TEMPLATES = _WORKSPACE_DIR / "assets" / "templates"
if str(_ASSETS_TEMPLATES) not in [str(d) for d in TEMPLATES[0]["DIRS"]]:
    TEMPLATES[0]["DIRS"].insert(0, str(_ASSETS_TEMPLATES))

# Sub-paths that app templates were scattered across — now under assets/templates/.
for _sub in ("blog", "lms", "profile", "products", "pages", "accounts",
             "blocks", "emails", "events", "layout", "plugins"):
    _sub_path = _ASSETS_TEMPLATES / _sub
    if _sub_path.exists() and str(_sub_path) not in [str(d) for d in TEMPLATES[0]["DIRS"]]:
        TEMPLATES[0]["DIRS"].append(str(_sub_path))

# Media: serve from the monorepo-shared media tree, project-named so the
# shared Nginx proxy can map ctc-research.com → /var/www/media/ctc-research
# (see applications/proxy/docker-compose.nginx.yml + nginx/default.conf.template).
# The runtime container overrides this via the MEDIA_ROOT env var (/app/media).
MEDIA_ROOT = os.environ.get(
    "MEDIA_ROOT", str(_PROJECTS_DIR / "assets" / "media" / "ctc-research")
)

# CTC archive/media pack. The attached backup is kept under the same
# project-named shared media root; ``prepare_ctc_media`` creates a clean
# ``ctc-content/`` website copy and dump-compatible ``original_images/``
# aliases without loading or mutating database data.
_CTC_MEDIA_ROOT = Path(MEDIA_ROOT)
CTC_MEDIA_SOURCE_DIR = Path(os.environ.get("CTC_MEDIA_SOURCE_DIR", str(_CTC_MEDIA_ROOT / "media")))
CTC_MEDIA_CONTENT_DIR = Path(os.environ.get("CTC_MEDIA_CONTENT_DIR", str(_CTC_MEDIA_ROOT / "ctc-content")))
CTC_MEDIA_DUMP_IMAGE_DIR = Path(os.environ.get("CTC_MEDIA_DUMP_IMAGE_DIR", str(_CTC_MEDIA_ROOT / "original_images")))
CTC_MEDIA_MANIFEST_PATH = Path(os.environ.get(
    "CTC_MEDIA_MANIFEST_PATH",
    str(_SITE_DIR / "assets" / "fixtures" / "ctc-research-media.json"),
))
CTC_MEDIA_CONTENT_URL = os.environ.get("CTC_MEDIA_CONTENT_URL", f"{MEDIA_URL}ctc-content/")

# Bundles: webpack writes to the site-local assets/bundles/ctc-research/ dir
# (mounted at /app/assets/bundles/ctc-research in the container). Register it
# under the bundles/ctc-research/ URL namespace so collectstatic copies it into
# STATIC_ROOT and the shared proxy serves it at /static/bundles/ctc-research/
# (nginx location already aliases that path).
_SHARED_BUNDLES = _WORKSPACE_DIR / "assets" / "bundles" / "ctc-research"
if _SHARED_BUNDLES.exists() and "STATICFILES_DIRS" in dir():
    # The runtime site root is /app/precis-ctc, while the shared asset tree is
    # mounted at /app/assets. Keep the webpack manifest and URL namespace
    # aligned with the actual shared bundle directory.
    SITE_BUNDLES_DIR = _SHARED_BUNDLES
    _bundle_entry = ("bundles/ctc-research", str(_SHARED_BUNDLES))
    if _bundle_entry not in STATICFILES_DIRS:
        STATICFILES_DIRS.append(_bundle_entry)
    if "WEBPACK_LOADER" in dir():
        _webpack_default = WEBPACK_LOADER.setdefault("DEFAULT", {})
        _webpack_default["BUNDLE_DIR_NAME"] = "bundles/ctc-research/"
        _webpack_default["STATS_FILE"] = str(_SHARED_BUNDLES / "bundles.json")
        if (_SHARED_BUNDLES / "bundles.json").is_file():
            _webpack_default["LOADER_CLASS"] = "webpack_loader.loader.WebpackLoader"
    if "FUSION_PIPELINE" in dir():
        FUSION_PIPELINE["webpack"].update(
            stats_file=str(_SHARED_BUNDLES / "bundles.json"),
            bundle_dir="bundles/ctc-research/",
        )

# Static: ensure workspace-level assets/static is in STATICFILES_DIRS.
# Use the CTC finder so Unfold's intentional admin overrides do not produce
# duplicate-destination warnings during collectstatic.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "apps.core.staticfiles.CtcAppDirectoriesFinder",
]
_ASSETS_STATIC = _WORKSPACE_DIR / "assets" / "static"
if _ASSETS_STATIC.exists() and "STATICFILES_DIRS" in dir():
    # Mount the site-local assets at the root namespace (/static/...) so the
    # fusion bundles (css/fusion.css, js/app.js) resolve from this site's own
    # assets/static/ — same convention as precis-landing. The shared configs
    # also register this same directory under a ``site/precis-ctc/`` namespace;
    # drop that alias because FileSystemFinder keys storages by root path, so a
    # second entry for the same dir overwrites the root prefix and makes every
    # file collect twice (the ``site/precis-ctc/...`` collectstatic duplicates).
    _root_entry = str(_ASSETS_STATIC)
    STATICFILES_DIRS[:] = [
        d for d in STATICFILES_DIRS
        if not (isinstance(d, tuple) and str(d[1]) == _root_entry)
    ]
    if _root_entry not in STATICFILES_DIRS:
        STATICFILES_DIRS.insert(0, _root_entry)

# FUSION_PIPELINE: point component manifest at the workspace static root.
if "FUSION_PIPELINE" in dir() and "components" in FUSION_PIPELINE:
    FUSION_PIPELINE["components"]["manifest_path"] = str(
        _ASSETS_STATIC / "components" / "manifest.json"
    )

# Legacy duplicate styles dir: remove assets/styles/ from STATICFILES_DIRS
# (content was merged into assets/static/styles/).
if "STATICFILES_DIRS" in dir():
    _styles_dup = _WORKSPACE_DIR / "assets" / "styles"
    STATICFILES_DIRS[:] = [
        d for d in STATICFILES_DIRS
        if not (isinstance(d, tuple) and str(d[1]) == str(_styles_dup))
    ]

# Component templates: the flat single-file tree under ``apps/components/``
# (contact.sections.field, contact.sections.method, blocks.partials.form_field,
# content.page_title, ...) only resolves when the apps root is a template dir,
# because django-fusion prefixes dotted names with ``components/``, ``partials/``
# or ``tags/`` when generating candidate names. Append it LAST so it never
# shadows the nested ``name/name.html`` trees already registered above.
_APPS_TEMPLATE_ROOT = _SITE_DIR / "apps"
if str(_APPS_TEMPLATE_ROOT) not in [str(d) for d in TEMPLATES[0]["DIRS"]]:
    TEMPLATES[0]["DIRS"].append(str(_APPS_TEMPLATE_ROOT))
