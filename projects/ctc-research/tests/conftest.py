"""
pytest configuration for CTC Research fusion integration tests.

Configures a minimal Django environment so that ``RequestFactory``,
``django_fusion.routes.session.FusionCodec``, and template rendering all
work without needing the full site settings (which depend on Docker
infrastructure for ``www.worker``, ``configs.site``, etc.).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# ── Path setup ──────────────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent.parent  # projects/cms/ctc-research

_paths_to_add = (
    str(_SITE_DIR),
    str(_SITE_DIR / "www"),
    str(_SITE_DIR.parent),
    str(_SITE_DIR.parents[1]),
)
for _path in reversed(_paths_to_add):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

_TEST_DB = "/tmp/ctc_research_test.sqlite3"
try:
    os.remove(_TEST_DB)
except FileNotFoundError:
    pass

# ── Django settings bootstrap ───────────────────────────────────────────────
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key-ctc-research",
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "django.contrib.staticfiles",
            "django.contrib.admin",
            "django.contrib.messages",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],

        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [str(_SITE_DIR / "templates")],
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                    "loaders": [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                },
            },
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": _TEST_DB,
                "TEST": {"NAME": _TEST_DB},
            },
        },
        USE_TZ=True,
        LANGUAGE_CODE="en-us",
        TIME_ZONE="UTC",
        USE_I18N=True,
        STATIC_URL="/static/",
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    )
    django.setup()

# Force-reload the plugins.pages.content module from the correct path to ensure
# CTC Research STATIC_PAGES is used, not the LMS one (pytest can cache modules
# from other projects in sys.modules due to earlier test discovery).
_ppc_keys = ["plugins", "plugins.pages", "plugins.pages.content"]
for _key in _ppc_keys:
    sys.modules.pop(_key, None)

# Pre-import from the correct site so test modules see the CTC version.
from plugins.pages.content import STATIC_PAGES  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════════
# Mark all tests as django_db (they don't actually use the DB, but some
# Django internals like TemplateResponse require it)
# ═══════════════════════════════════════════════════════════════════════════
pytestmark = pytest.mark.django_db
