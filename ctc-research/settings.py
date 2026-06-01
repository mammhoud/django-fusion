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
