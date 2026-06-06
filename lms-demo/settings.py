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

configure_site_environment("lms-demo", module="CMS", default_port=5071)

# ============================================================
# Import Shared Django Settings
# ============================================================
from configs.settings import *  # noqa: E402,F401,F403

# ============================================================
# URL and Application Configuration
# ============================================================
ROOT_URLCONF = "www.urls"

# ASGI/WSGI applications are now in server.py
# This is referenced by the start script as: lms-demo.server:application
ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

# ============================================================
# Website-Specific Settings
# ============================================================
WEBSITE_NAME = "lms-demo"
WEBSITE_IDENTIFIER = "lms-demo"
SITE_ID = 2
# ============================================================
# django_rseal required settings
# ============================================================
# PROFILE_MODEL is a required ForeignKey target in django_rseal models.
# Point it to Django's built-in User model since this project
# does not have a separate profile model.
PROFILE_MODEL = "auth.User"


# Third-party django_rseal currently declares an invalid TeamMembership ordering.
SILENCED_SYSTEM_CHECKS = ["models.E015"]
