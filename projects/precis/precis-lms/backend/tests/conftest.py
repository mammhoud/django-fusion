"""pytest configuration for precis-lms.

Uses the real project settings (inherited via tests.test_settings) with
SQLite override so domain models and Wagtail-dependent apps work in tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import django

# ── Path setup ──────────────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent.parent  # projects/precis-lms/backend

for _path in (
    str(_SITE_DIR),          # backend/
    str(_SITE_DIR / "www"),  # backend/www/
    str(_SITE_DIR.parent),   # precis-lms/
):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ── Use test settings (real INSTALLED_APPS + SQLite) ────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

# ── Bootstrap Django ────────────────────────────────────────────────────────
django.setup()
