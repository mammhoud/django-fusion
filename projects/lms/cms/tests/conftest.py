"""
pytest configuration for LMS data API endpoint tests.

Configures Django, sets up the database, and creates test data inside a
session-scoped fixture (``django_db_setup``) that uses
``django_db_blocker.unblock()`` for all database operations.
All individual fixtures return module-level variables — zero DB access
at fixture-evaluation time.
"""

from __future__ import annotations

import hashlib
import importlib
import os
import sys
from pathlib import Path

import pytest

# ── Path setup ──────────────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent.parent  # projects/lms/cms
_WORKSPACE_DIR = _SITE_DIR.parent  # projects/lms
_PROJECTS_DIR = _SITE_DIR.parents[1]  # projects/

for _path in (str(_WORKSPACE_DIR), str(_SITE_DIR), str(_SITE_DIR / "www"), str(_PROJECTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("DJANGO_SITE", "ctc-research")
os.environ.setdefault("WEBSITE", "ctc-research")

_TEST_DB = "/tmp/lms_bolt_test.sqlite3"
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
        SECRET_KEY="test-secret-key-bolt-lms",
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "django.contrib.sites",
            "wagtail",
            "wagtail.admin",
            "wagtail.snippets",
            "wagtail.contrib.settings",
            "wagtail.users",
            "wagtail.images",
            "wagtail.documents",
            "wagtail.search",
            "wagtail.contrib.redirects",
            "modelcluster",
            "taggit",
            "www.core",
            "www.content",
            "plugins.accounts",
            "django_bolt",
        ],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            "wagtail.contrib.redirects.middleware.RedirectMiddleware",
        ],
        ROOT_URLCONF="www.urls",
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
        BOLT_API={
            "prefix": "/apis",
            "namespace": "ctc-research-bolt",
            "title": "CTC Research API",
            "version": "1.0.0",
            "auth": {"token_header": "Authorization", "token_prefix": "Bearer"},
        },
        PROFILE_MODEL="auth.User",
        CORS_ALLOWED_ORIGINS=["http://testserver.local"],
        CORS_ALLOW_CREDENTIALS=True,
    )
    django.setup()

# ── Give all test functions database access (same file, TEST dict above) ──
pytestmark = pytest.mark.django_db

# ═══════════════════════════════════════════════════════════════════════════
# Module-level holders — populated by django_db_setup fixture (session scope)
# ═══════════════════════════════════════════════════════════════════════════

_AUTH_TOKEN_RAW = "test-access-token-12345"
_STAFF_TOKEN_RAW = "admin-access-token-67890"

_test_user = None
_staff_user = None


@pytest.fixture(scope="session", autouse=True)
def django_db_setup(django_db_blocker):
    """Create all tables + seed data once per session, inside unblocked context."""
    global _test_user, _staff_user

    with django_db_blocker.unblock():
        from django.core.management import call_command

        call_command("migrate", "--run-syncdb", verbosity=0)

        from django.contrib.auth.models import User

        _test_user, _ = User.objects.get_or_create(
            username="testuser",
            defaults={"email": "test@example.com", "first_name": "Test", "last_name": "User", "is_active": True},
        )
        _test_user.set_password("password123")
        _test_user.save(update_fields=["password"])

        _staff_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        _staff_user.set_password("adminpass123")
        _staff_user.save(update_fields=["password"])

        from www.content.models.others import Token as TokenModel

        TokenModel.objects.get_or_create(
            token_hash=hashlib.sha256(_AUTH_TOKEN_RAW.encode()).hexdigest(),
            defaults={"user": _test_user, "token_type": "access", "category": ""},
        )
        TokenModel.objects.get_or_create(
            token_hash=hashlib.sha256(_STAFF_TOKEN_RAW.encode()).hexdigest(),
            defaults={"user": _staff_user, "token_type": "access", "category": ""},
        )


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures — return module-level references (zero DB access)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def test_user():
    return _test_user


@pytest.fixture()
def staff_user():
    return _staff_user


@pytest.fixture()
def test_api(django_db_blocker):
    """Return a combined BoltAPI instance with core + extras routes.

    Mirrors the pattern in ``verify_endpoints.py``:
      1. Patch BoltAPI to accept extra kwargs (needed by ``apis.py``)
      2. Import ``apis`` to get the core bolt instance
      3. Copy core routes onto a fresh BoltAPI
      4. Register extras from ``www.api.data.router.register_all_handlers()``
    """
    with django_db_blocker.unblock():
        from django_bolt import BoltAPI

        # Patch to accept kwargs that apis.py passes but the installed bolt
        # version doesn't support (namespace, title, version, description)
        _orig_init = BoltAPI.__init__

        def _patched_init(self, *args, **kwargs):
            kwargs.pop("namespace", None)
            kwargs.pop("title", None)
            kwargs.pop("version", None)
            kwargs.pop("description", None)
            return _orig_init(self, *args, **kwargs)

        BoltAPI.__init__ = _patched_init

        # Import core apis.py (triggers route registration on its ``bolt`` instance)
        import apis
        importlib.reload(apis)
        core_bolt = apis.bolt

        # Restore original __init__
        BoltAPI.__init__ = _orig_init

        # Build a fresh bolt instance and copy core routes
        api = BoltAPI(prefix="/apis")
        api._routes.extend(core_bolt._routes)
        api._handlers.update(core_bolt._handlers)
        api._handler_meta.update(core_bolt._handler_meta)
        api._handler_middleware.update(core_bolt._handler_middleware)
        api._next_handler_id = core_bolt._next_handler_id

        # Register extras
        from www.api.data.router import register_all_handlers
        register_all_handlers(api)

        return api


@pytest.fixture()
def auth_token() -> str:
    return _AUTH_TOKEN_RAW


@pytest.fixture()
def staff_auth_token() -> str:
    return _STAFF_TOKEN_RAW
