"""
POS Solo — Branch Device Django Settings.

Centralized configuration for the pos-solo sidecar server.
pos-solo is a branch device that connects to the pos-full master.
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR.parent / "unified.db"

# ── Django Core ──
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "pos-solo-branch-device-key")
DEBUG = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Database ──
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DB_PATH),
    }
}

# ── Installed Apps ──
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "models.PosSoloConfig",  # Managed models (pos_unified) — migrations + CRUD
]

# ── Server Config ──
HOST = os.environ.get("POS_HOST", "0.0.0.0")
PORT = int(os.environ.get("POS_PORT", "8765"))
API_KEY = os.environ.get("POS_API_KEY", None)

# ── Master/Full Connection (single source of truth) ──
MASTER_URL = os.environ.get("POS_MASTER_URL", "http://localhost:8766")
MASTER_API_KEY = os.environ.get("POS_MASTER_API_KEY", None)

# ── Cloud CRM ──
CLOUD_CRM_URL = os.environ.get("CLOUD_CRM_URL", "http://127.0.0.1:8767")
CLOUD_API_KEY = os.environ.get("CLOUD_API_KEY", None)
