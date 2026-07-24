"""
pytest configuration for LMS data API endpoint tests.

Configures Django conditionally:
- Default (LMS_TEST_FULL not set): Minimal apps for fusion/page/adapter tests.
  No Wagtail, no www.content — uses signed-cookie sessions, no DB access.
- LMS_TEST_FULL=1: Full apps (Wagtail, www.content, django_bolt) for
  bolt/data/contract test suites. Requires database migration.
"""
from __future__ import annotations

import hashlib
import importlib
import os
import sys
from pathlib import Path

import pytest

_SITE_DIR = Path(__file__).resolve().parent.parent
_WORKSPACE_DIR = _SITE_DIR.parent
_PROJECTS_DIR = _SITE_DIR.parents[1]
_WORKSPACE_ROOT = _SITE_DIR.parents[3]  # /home/structa.cloud

for _path in (
    str(_WORKSPACE_DIR),
    str(_SITE_DIR),
    str(_SITE_DIR / "www"),
    str(_PROJECTS_DIR),
    str(_WORKSPACE_ROOT / "libs" / "django-fusion" / "src"),
    str(_WORKSPACE_ROOT / "libs" / "ceptor-ai" / "src"),
):
    if _path not in sys.path:
        sys.path.insert(0, _path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("DJANGO_SITE", "ctc-research")
os.environ.setdefault("WEBSITE", "ctc-research")

_FULL_MODE = os.environ.get("LMS_TEST_FULL") == "1"

_TEST_DB = "/tmp/lms_bolt_test.sqlite3"
if _FULL_MODE:
    try:
        os.remove(_TEST_DB)
    except FileNotFoundError:
        pass

import django
from django.conf import settings

# ── Minimal apps (fusion/page/adapter tests — no DB required) ──
_MINIMAL_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

if not settings.configured:
    if _FULL_MODE:
        _installed_apps = [
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
            "plugins.lms.apps.LmsConfig",
            "django_bolt",
        ]
    else:
        _installed_apps = _MINIMAL_APPS

    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key-bolt-lms",
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=_installed_apps,
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
        STATIC_URL="/static/",
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
        PROFILE_MODEL="auth.User",
    )
    django.setup()

# Force-reload plugins.pages.content from the correct path.
# Only clear specific sub-modules — NOT the parent 'plugins' package
# which would remove plugins.lms and other apps registered during setup.
_ppc_keys = ["plugins.pages", "plugins.pages.content"]
for _key in _ppc_keys:
    sys.modules.pop(_key, None)
from plugins.pages.content import STATIC_PAGES  # noqa: E402

# ── Full-mode database fixtures ───────────────────────────────────────────
if _FULL_MODE:
    pytestmark = pytest.mark.django_db

    _AUTH_TOKEN_RAW = "test-access-token-12345"
    _STAFF_TOKEN_RAW = "admin-access-token-67890"
    _test_user = None
    _staff_user = None

    @pytest.fixture(scope="session", autouse=True)
    def django_db_setup(django_db_blocker):
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
                defaults={"email": "admin@example.com", "first_name": "Admin", "last_name": "User", "is_staff": True, "is_superuser": True, "is_active": True},
            )
            _staff_user.set_password("adminpass123")
            _staff_user.save(update_fields=["password"])
            # Token creation may fail if content_token table is missing
            # (e.g. when running fixture tests without full migrations).
            # We swallow the error so that tests not requiring tokens can still run.
            try:
                from www.content.models.others import Token as TokenModel
                TokenModel.objects.get_or_create(
                    token_hash=hashlib.sha256(_AUTH_TOKEN_RAW.encode()).hexdigest(),
                    defaults={"user": _test_user, "token_type": "access", "category": ""},
                )
                TokenModel.objects.get_or_create(
                    token_hash=hashlib.sha256(_STAFF_TOKEN_RAW.encode()).hexdigest(),
                    defaults={"user": _staff_user, "token_type": "access", "category": ""},
                )
            except Exception:
                pass

    @pytest.fixture()
    def test_user():
        return _test_user

    @pytest.fixture()
    def staff_user():
        return _staff_user

    @pytest.fixture()
    def test_api(django_db_blocker):
        with django_db_blocker.unblock():
            from django_bolt import BoltAPI
            _orig_init = BoltAPI.__init__
            def _patched_init(self, *args, **kwargs):
                kwargs.pop("namespace", None)
                kwargs.pop("title", None)
                kwargs.pop("version", None)
                kwargs.pop("description", None)
                return _orig_init(self, *args, **kwargs)
            BoltAPI.__init__ = _patched_init
            import apis
            importlib.reload(apis)
            core_bolt = apis.bolt
            BoltAPI.__init__ = _orig_init
            api = BoltAPI(prefix="/apis")
            api._routes.extend(core_bolt._routes)
            api._handlers.update(core_bolt._handlers)
            api._handler_meta.update(core_bolt._handler_meta)
            api._handler_middleware.update(core_bolt._handler_middleware)
            api._next_handler_id = core_bolt._next_handler_id
            from www.api.data.router import register_all_handlers
            register_all_handlers(api)
            return api

    @pytest.fixture()
    def auth_token() -> str:
        return _AUTH_TOKEN_RAW

    @pytest.fixture()
    def staff_auth_token() -> str:
        return _STAFF_TOKEN_RAW
