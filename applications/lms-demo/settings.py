"""Website-local Django settings for lms-demo."""
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

configure_site_environment("lms-demo", module="LMS", default_port=5071)

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
WEBSITE_NAME = "lms-demo"
WEBSITE_IDENTIFIER = "lms-demo"
SITE_ID = 2

# ── Local apps (site-specific plugins, www packages, and page apps) ──
# Uses the shared LMS_LOCAL_APPS constant from configs.base.apps (already
# imported via `from configs.settings import *` above).
# ctc-research and lms-demo share the same plugin/www structure.
LOCAL_APPS = LMS_LOCAL_APPS
INSTALLED_APPS += LOCAL_APPS
# ============================================================
# crafts_ai required settings
# ============================================================
# PROFILE_MODEL is a required ForeignKey target in crafts_ai models.
# Point it to Django's built-in User model since this project
# does not have a separate profile model.
PROFILE_MODEL = "auth.User"


# Keep only legacy duplicated app/model checks silenced; the previous
# TeamMembership ordering check is fixed in crafts_ai.
SILENCED_SYSTEM_CHECKS = [
    "models.E028",  # legacy accounts/handlers shared service table during migration
    "models.E030",  # legacy accounts/handlers shared indexes during migration
    "models.E032",  # legacy accounts/handlers shared constraints during migration
    "fields.E304",  # legacy duplicated profile reverse accessors
    "fields.E305",  # legacy duplicated profile reverse query names
    "fields.E340",  # legacy duplicated many-to-many intermediary tables
]

# Disable workflows until legacy imported Wagtail tasks are cleaned.
WAGTAIL_WORKFLOW_ENABLED = False
