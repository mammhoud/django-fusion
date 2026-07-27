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
# Only disable migrations for our project apps — third-party apps
# (Wagtail, Django, allauth, taggit, treebeard, modelcluster) MUST run
# their migrations so Wagtail's root page and content types are created.
_PROJECT_APP_PREFIXES = (
    "apps.",      # apps.core, apps.pages, etc.
    "www.",       # www sub-packages
    "pages.",     # legacy direct app labels
    "core.",      # legacy core app labels
    "accounts.",
    "blog.",
    "branding.",
    "lms.",
    "products.",
    "profile.",
)

class _DisableMigrations:
    """Only disable migrations for our project apps. Third-party
    apps (Wagtail, Django, allauth, etc.) are NOT in __contains__
    so Django falls back to their built-in migration modules."""
    def __contains__(self, item):
        return item.startswith(_PROJECT_APP_PREFIXES)

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = _DisableMigrations()

# ── Silence noisy checks in tests ───────────────────────────────────────
SILENCED_SYSTEM_CHECKS = [
    "treebeard.E001",        # Wagtail upstream — managers don't subclass MP_NodeManager
    "models.W001",           # PostgreSQL-specific field not needed on SQLite
    "wagtailsearch.W004",    # No search backend configured in test
]

# ── Fixture directories — point to project assets/fixtures ──────────────
from pathlib import Path
FIXTURE_DIRS = [
    str(Path(__file__).resolve().parents[2] / "assets" / "fixtures"),  # projects/cms-fusion/
]
