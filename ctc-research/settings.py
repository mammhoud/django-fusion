"""Website-local Django settings for ctc-research."""
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

configure_site_environment("ctc-research", module="LMS", default_port=5070)

# ============================================================
# Internal Dependency Handling
# ============================================================
# django_osoul and django_rseal are real workspace dependencies. Do not install
# fake sys.modules shims here; dependency failures should surface during checks.

# ============================================================
# Import Shared Django Settings
# ============================================================
from configs.settings import *  # noqa: E402,F401,F403

# ============================================================
# URL and Application Configuration
# ============================================================
ROOT_URLCONF = "www.urls"

# ASGI/WSGI applications are now in server.py
# This is referenced by the start script as: ctc-research.server:application
ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

# ============================================================
# Website-Specific Settings
# ============================================================
WEBSITE_NAME = "ctc-research"
WEBSITE_IDENTIFIER = "ctc-research"
SITE_ID = 1

# ============================================================
# django_rseal required settings
# ============================================================
# PROFILE_MODEL is a required ForeignKey target in django_rseal models.
# Point it to Django's built-in User model since this project
# does not have a separate profile model.
PROFILE_MODEL = "auth.User"

# ============================================================
# Silenced system checks
# ============================================================
# models.E015: django_rseal.TeamMembership.ordering references person__full_name
# which is a valid cross-model lookup at query time but Django's static check
# cannot verify related-field traversal. Safe to silence.
SILENCED_SYSTEM_CHECKS = ["models.E015"]
