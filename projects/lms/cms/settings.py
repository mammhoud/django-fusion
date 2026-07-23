"""
Structa LMS — Django settings (django-bolt exclusive, no DRF).

Serves the Structa Cloud LMS site on port 5071 and exposes the
django-bolt API under ``/apis`` for the LMS frontend. Follows the
monorepo pattern: configs.site + configs.settings base.
"""

import os
import sys
from pathlib import Path

_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_PROJECTS_DIR = _SITE_DIR.parents[2] / "projects"  # projects/configs/
_SITE_APP_DIR = _SITE_DIR / "www"

for _path in (str(_PROJECTS_DIR), str(_WORKSPACE_DIR), str(_SITE_DIR), str(_SITE_APP_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ── Site configuration (monorepo pattern) ──
from configs.site import configure_site_environment
configure_site_environment("lms", module="LMS", default_port=5071)

from configs.settings import *

# ── URL & Application ──
ROOT_URLCONF = "www.urls"
ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

# ── Site identity ──
WEBSITE_NAME = "lms"
WEBSITE_IDENTIFIER = "lms"
SITE_ID = 2

# ── Wagtail admin branding ──
WAGTAIL_SITE_NAME = "Structa LMS"

# ── Local apps ──
LOCAL_APPS = [
    "www.core",
    "www.schemas.apps.SchemaConfig",
    "www.content.apps.ContentConfig",
    "plugins.accounts.apps.AccountsConfig",
    "plugins.research.apps.ResearchConfig",
    "plugins.lms",
    "plugins.blog",
]
# ── Optional packages (may not be installed in all environments) ──
_OPTIONAL_APPS = [
    "ceptor_ai",
    "django_bolt",
    "corsheaders",
]
for _app in _OPTIONAL_APPS:
    try:
        __import__(_app)
        LOCAL_APPS.append(_app)
    except ImportError:
        pass
# Filter out shared apps that do not exist in the LMS site
_SHARED_APPS_TO_REMOVE = {"www.worker"}
INSTALLED_APPS = [a for a in INSTALLED_APPS if a not in _SHARED_APPS_TO_REMOVE]
INSTALLED_APPS += LOCAL_APPS

# ── django-bolt configuration (exclusive API layer) ──
BOLT_API = {
    "prefix": "/apis",
    "namespace": "lms-bolt",
    "title": "Structa LMS API",
    "version": "1.0.0",
    "description": "High-performance bolt API for the Structa LMS frontend",
    "auth": {
        "enabled": True,
        "token_header": "Authorization",
        "token_prefix": "Bearer",
        "token_model": "django.contrib.auth.models.User",
    },
}

# ── CORS for Structa LMS frontend (only if corsheaders is installed) ──
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
    "http://www.structa.cloud",
    "https://www.structa.cloud",
    "http://core.structa.cloud",
    "https://core.structa.cloud",
]
CORS_ALLOW_CREDENTIALS = True

# ── Profile model for ceptor_ai ──
PROFILE_MODEL = "auth.User"
