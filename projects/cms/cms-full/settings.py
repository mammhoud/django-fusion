"""Website-local Django settings for cms-full (merged CTC Research + LMS)."""
import os
import sys
from pathlib import Path

_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"

# lms/cms provides comprehensive API views, schemas, and plugins.research
_LMS_CMS_DIR = _SITE_DIR.parents[1] / "lms" / "cms"

# Priority: lms/cms first (comprehensive API), then self (local plugins+templates)
for _path in reversed((
    str(_LMS_CMS_DIR),
    str(_LMS_CMS_DIR / "www"),
    str(_SITE_DIR),
    str(_SITE_APP_DIR),
    str(_WORKSPACE_DIR),
)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

from configs.site import configure_site_environment

configure_site_environment("cms-full", module="LMS", default_port=5080)

from configs.settings import *  # noqa: E402,F401,F403

ROOT_URLCONF = "www.urls"
ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

WEBSITE_NAME = "cms-full"
WEBSITE_IDENTIFIER = "cms-full"
SITE_ID = 3
WAGTAIL_SITE_NAME = "Structa CMS Full"

LOCAL_APPS = [
    # Core — from lms/cms (on sys.path)
    "www.core",
    "www.core.content.apps.ContentConfig",
    "www.core.handlers.apps.AccountsConfig",
    "www.schemas.apps.SchemaConfig",
    # Plugins — copied from ctc-research into local plugins/
    "plugins.accounts.apps.AccountsConfig",
    "plugins.lms.apps.LmsConfig",
    "plugins.blog.apps.BlogConfig",
    "plugins.products.apps.ProductsConfig",
    "plugins.profile.apps.ProfileConfig",
    "plugins.pages",
    # Plugins — from lms/cms (on sys.path)
    "plugins.research.apps.ResearchConfig",
    # Shared
    "ceptor_ai",
    "django_fusion.fragments.analyzer.apps.AnalyzerAppConfig",
]

_OPTIONAL_APPS = [
    "django_bolt",
    "corsheaders",
]
for _app in _OPTIONAL_APPS:
    try:
        __import__(_app)
        LOCAL_APPS.append(_app)
    except ImportError:
        pass

_SHARED_APPS_TO_REMOVE = {"www.worker"}
INSTALLED_APPS = [a for a in INSTALLED_APPS if a not in _SHARED_APPS_TO_REMOVE]
INSTALLED_APPS += LOCAL_APPS

# ── django-bolt ──
BOLT_API = {
    "prefix": "/apis",
    "namespace": "cms-full-bolt",
    "title": "Structa CMS Full API",
    "version": "1.0.0",
    "description": "High-performance bolt API for the unified CMS frontend",
    "auth": {
        "enabled": True,
        "token_header": "Authorization",
        "token_prefix": "Bearer",
        "token_model": "django.contrib.auth.models.User",
    },
}

# ── CORS ──
_CORS_AVAILABLE = False
try:
    __import__("corsheaders")
    _CORS_AVAILABLE = True
except ImportError:
    pass

if _CORS_AVAILABLE:
    MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:1420",
    "http://structa.cloud",
    "https://structa.cloud",
]
CORS_ALLOW_CREDENTIALS = True

PROFILE_MODEL = "auth.User"

SILENCED_SYSTEM_CHECKS = [
    "models.E028",
    "models.E030",
    "models.E032",
    "fields.E304",
    "fields.E305",
    "fields.E340",
]

WAGTAIL_WORKFLOW_ENABLED = False
