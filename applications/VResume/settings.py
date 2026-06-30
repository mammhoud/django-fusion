"""Website-local Django settings for vresume."""
import os
import sys
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"

# Ensure correct import paths
for _path in (str(_SITE_APP_DIR), str(_SITE_DIR), str(_WORKSPACE_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ============================================================
# Site Configuration
# ============================================================
from configs.site import configure_site_environment

configure_site_environment("vresume", module="CMS", default_port=5072)

# ============================================================
# Internal Dependency Handling
# ============================================================
# django_osoul and crafts_ai are real workspace dependencies. Do not install
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
ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

# ============================================================
# Website-Specific Settings
# ============================================================
WEBSITE_NAME = "vresume"
WEBSITE_IDENTIFIER = "vresume"
SITE_ID = 3

# ── Local apps (site-specific plugins, www packages, and page apps) ──
# Each website ships its own set of plugins and www sub-packages.
# These are appended to the shared INSTALLED_APPS built by configs.base.apps.
LOCAL_APPS = [
    "www.core",
    "plugins.accounts.apps.AccountsConfig",
    "crafts_ai",
    "django_osoul.analyzer.apps.AnalyzerAppConfig",
    "pages.home",
    "pages.about",
    "pages.cv",
    "pages.connect",
    "pages.portfolio",
    "pages.blog",
    "pages.events",
]
INSTALLED_APPS += LOCAL_APPS

# ============================================================
# crafts_ai required settings
# ============================================================
# PROFILE_MODEL is a required ForeignKey target in crafts_ai models.
# Point it to Django's built-in User model since this project
# does not have a separate profile model.
PROFILE_MODEL = "auth.User"

# ============================================================
# Silenced system checks
# ============================================================
# The previous TeamMembership ordering check is fixed in crafts_ai.
SILENCED_SYSTEM_CHECKS = []

# Disable workflows until legacy imported Wagtail tasks are cleaned.
WAGTAIL_WORKFLOW_ENABLED = False

