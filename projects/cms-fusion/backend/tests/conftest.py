"""pytest configuration for cms-fusion.

Uses the real project settings (inherited via tests.test_settings) with
SQLite override so domain models and Wagtail-dependent apps work in tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import django

# ── Path setup ──────────────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent.parent  # projects/cms-fusion/backend

for _path in (
    str(_SITE_DIR),          # backend/
    str(_SITE_DIR / "www"),  # backend/www/
    str(_SITE_DIR.parent),   # cms-fusion/
):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ── Use test settings (real INSTALLED_APPS + SQLite) ────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

# ── Bootstrap Django ────────────────────────────────────────────────────────
django.setup()

# Person is a legacy shared-table model.  The test settings disable migrations
# so Django builds the test schema from model metadata, but unmanaged models
# are otherwise skipped by the test database setup.  Enable it only in the
# test process; production keeps the model's managed=False contract.
from apps.domain.models.users.users import Person  # noqa: E402

Person._meta.managed = True
