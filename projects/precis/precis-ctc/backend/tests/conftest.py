"""pytest configuration for precis-lms.

Uses the real project settings (inherited via tests.test_settings) with
SQLite override so domain models and Wagtail-dependent apps work in tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

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
# Override a production container's DJANGO_SETTINGS_MODULE instead of letting
# pytest accidentally point its database tests at PostgreSQL.
os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"

# ── Bootstrap Django ────────────────────────────────────────────────────────
import django  # noqa: E402

django.setup()
