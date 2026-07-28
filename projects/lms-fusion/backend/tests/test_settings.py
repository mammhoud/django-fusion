"""Test settings for cms-fusion — inherits real settings, overrides DB to SQLite.

Uses the real INSTALLED_APPS (Wagtail, django_fusion, domain models, etc.)
but replaces the database with an in-memory SQLite backend so tests run
without Docker/Postgres.

Migrations are disabled via MIGRATION_MODULES — Django creates tables
from model metadata instead of running migration files, which is much
faster and avoids SQLite/Postgres migration incompatibilities.
"""

import os

# Force development profile so configs.settings picks up the right base
os.environ.setdefault("SERVER_ENV", "development")
os.environ.setdefault("DJANGO_SERVER_ENV", "development")
os.environ.setdefault("WEBSITE", "cms-fusion")
os.environ.setdefault("WEBSITE_NAME", "cms-fusion")

# Import ALL real settings (Wagtail, domain apps, middleware, etc.)
# pylint: disable=wildcard-import,unused-wildcard-import
from settings import *  # noqa: E402, F403

# ── Override database to in-memory SQLite ───────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ── Disable migrations for speed ────────────────────────────────────────
# Return None for ALL apps — Django creates tables from model metadata
# instead of running migration files. This is much faster and avoids
# SQLite/Postgres migration file incompatibilities. Tables are still
# created for all models (Wagtail, Django, domain, project apps) via
# schema introspection.
class _DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = _DisableMigrations()

# ── Silence noisy checks in tests ───────────────────────────────────────
SILENCED_SYSTEM_CHECKS = [
    "treebeard.E001",        # Wagtail upstream — managers don't subclass MP_NodeManager
    "models.W001",           # PostgreSQL-specific field not needed on SQLite
    "wagtailsearch.W004",    # No search backend configured in test
]
