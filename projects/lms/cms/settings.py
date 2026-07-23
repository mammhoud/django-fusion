"""
CTC Research — Django settings (django-bolt exclusive, no DRF).

Serves Wagtail CMS on port 8086 + django-bolt API on port 8087.
Connected to next-LMS Next.js frontend via bolt API.
Follows monorepo pattern: configs.site + configs.settings base.
"""

import os
import sys
from pathlib import Path

_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_PROJECTS_DIR = _SITE_DIR.parents[2] / "projects"  # projects/configs/
_SITE_APP_DIR = _SITE_DIR / "www"

for _path in (str(_WORKSPACE_DIR), str(_SITE_DIR), str(_SITE_APP_DIR), str(_PROJECTS_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ── Site configuration (monorepo pattern) ──
from configs.site import configure_site_environment
configure_site_environment("ctc-research", module="CTC Research", default_port=8086)

from configs.settings import *

# ── URL & Application ──
ROOT_URLCONF = "www.urls"
ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

# ── Site identity ──
WEBSITE_NAME = "ctc-research"
WEBSITE_IDENTIFIER = "ctc-research"
SITE_ID = 3

# ── Wagtail admin branding ──
WAGTAIL_SITE_NAME = "CTC Hub"

# ── Local apps ──
LOCAL_APPS = [
    "www.core",
    "www.schemas.apps.SchemaConfig",
    "www.content.apps.ContentConfig",
    "plugins.accounts.apps.AccountsConfig",
    "plugins.research.apps.ResearchConfig",
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
# Filter out shared apps that don't exist in ctc-research
_SHARED_APPS_TO_REMOVE = {"www.worker"}
INSTALLED_APPS = [a for a in INSTALLED_APPS if a not in _SHARED_APPS_TO_REMOVE]
INSTALLED_APPS += LOCAL_APPS

# ── django-bolt configuration (exclusive API layer) ──
BOLT_API = {
    "prefix": "/apis",
    "namespace": "ctc-research-bolt",
    "title": "CTC Research API",
    "version": "1.0.0",
    "description": "High-performance bolt API for CTC Research — serves next-LMS frontend",
    "auth": {
        "enabled": True,
        "token_header": "Authorization",
        "token_prefix": "Bearer",
        "token_model": "django.contrib.auth.models.User",
    },
}

# ── CORS for next-LMS frontend (only if corsheaders is installed) ──
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
    "https://lms.structa.cloud",
]
CORS_ALLOW_CREDENTIALS = True

# ── Profile model for ceptor_ai ──
PROFILE_MODEL = "auth.User"
