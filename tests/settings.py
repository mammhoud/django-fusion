"""
Test settings for the websites test suite.

This file is loaded by pytest-django via DJANGO_SETTINGS_MODULE.
All sys.path manipulation and module aliasing happens here, before
Django's app registry loads any models.
"""
import importlib
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_tests_dir = Path(__file__).parent
_websites_dir = _tests_dir.parent
_workspace_root = _websites_dir.parent

_lms_path = _websites_dir / "projects" / "lms" / "cms"
_portfolio_path = _websites_dir / "projects" / "cms" / "portfolio"
_lms_full_path = _websites_dir / "projects" / "cms" / "lms-full"
_ceptor_tests = _workspace_root / "libs" / "ceptor-ai" / "tests"

# Support both monorepo layout (projects/<site>/cms) and single-site layout.
_repo_root = _websites_dir

# Map old site names to their new paths under projects/:
# - "ctc-research" and "lms" (old core/) → projects/lms/cms/
# - "VResume" (old core/)               → projects/cms/portfolio/
# - lms-full                             → projects/cms/lms-full/
_ctc_path = _lms_path
_structa_path = _lms_path
_vresume_path = _portfolio_path

_plugin_roots = [
    _lms_path / "plugins",
    _portfolio_path / "plugins",
    _lms_full_path / "plugins",
]
_www_roots = [
    _lms_path / "www",
    _portfolio_path / "www",
    _lms_full_path / "www",
    _websites_dir / "projects" / "www",
]
_core_roots = [
    _lms_path / "www" / "core",
    _portfolio_path / "www" / "core",
    _lms_full_path / "www" / "core",
]

_sys_paths = [
    # Inserted with sys.path.insert(0), so lower-priority roots come first.
    _repo_root,
    _portfolio_path,
    _portfolio_path / "plugins",
    _lms_full_path,
    _lms_full_path / "plugins",
    _lms_path,
    _lms_path / "plugins",
    _ceptor_tests,
]
for _p in _sys_paths:
    if _p.exists() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# Keep only directories that actually exist to avoid invalid import roots.
# Use only CTC Research's plugins for the `www.apps` namespace to avoid
# app_label conflicts when multiple sites define apps with the same name
# (e.g. blog). Tests that need a specific site's app should import it
# directly from that site's path.
_plugin_paths = [str(_lms_path / "plugins")] if (_lms_path / "plugins").exists() else []
_www_paths = [str(p) for p in _www_roots if p.exists()]
_core_paths = [str(p) for p in _core_roots if p.exists()]

# ---------------------------------------------------------------------------
# Module stubs — must happen before INSTALLED_APPS are loaded
# ---------------------------------------------------------------------------

# Stub out optional heavy dependencies that may not be installed in test env
import types as _types

for _stub_name in ["twilio", "twilio.rest"]:
    if _stub_name not in sys.modules:
        _m = _types.ModuleType(_stub_name)
        _m.Client = type("Client", (), {})
        sys.modules[_stub_name] = _m

# Stub attrs if not installed
if "attrs" not in sys.modules:
    _attrs = _types.ModuleType("attrs")
    _attrs.define = lambda *a, **kw: (lambda cls: cls)
    _attrs.field = lambda *a, **kw: None
    sys.modules["attrs"] = _attrs
    sys.modules["attr"] = _attrs

# 1. `www` / `www.apps` namespace stubs
# www needs to point to www/core for Django imports
if "www" not in sys.modules:
    _www_mod = types.ModuleType("www")
    _www_mod.__path__ = _www_paths
    _www_mod.__package__ = "www"
    sys.modules["www"] = _www_mod

# www.core → structa.cloud/www/core (and ctc)
if "www.core" not in sys.modules:
    _www_core = types.ModuleType("www.core")
    _www_core.__path__ = _core_paths
    _www_core.__package__ = "www.core"
    sys.modules["www.core"] = _www_core

# www.apps needs to point to plugins for accounts/content imports
# We need to set up the full hierarchy as direct aliases
if "www.apps" not in sys.modules:
    _www_apps_mod = types.ModuleType("www.apps")
    _www_apps_mod.__path__ = _plugin_paths
    _www_apps_mod.__package__ = "www.apps"
    sys.modules["www.apps"] = _www_apps_mod

# Set up www.apps.accounts as an alias to accounts
if "www.apps.accounts" not in sys.modules:
    try:
        import accounts as _real_accounts
        sys.modules["www.apps.accounts"] = _real_accounts
    except Exception:
        pass

# Set up www.apps.accounts.models as an alias to accounts.models
if "www.apps.accounts.models" not in sys.modules:
    try:
        import accounts.models as _real_models
        sys.modules["www.apps.accounts.models"] = _real_models
    except Exception:
        pass

# Set up www.apps.accounts.models.tags as an alias to accounts.models.tags
if "www.apps.accounts.models.tags" not in sys.modules:
    try:
        import accounts.models.tags as _real_tags
        sys.modules["www.apps.accounts.models.tags"] = _real_tags
    except Exception:
        pass

# 3. Mock heavy Wagtail page deps so blog models import cleanly
class _MockBasePage:
    content_panels = []
    search_fields = []
    class Meta:
        abstract = True

_page_mock = MagicMock()
_page_mock.BasePage = _MockBasePage
_page_mock.BaseFormPage = _MockBasePage
_page_mock.BaseIndexPage = _MockBasePage

# 4. Create proper namespace packages for www.apps.accounts hierarchy
# www.apps.accounts.* → accounts.* (from structa.cloud/plugins/accounts)
# We make www.apps.accounts a real namespace pointing to the accounts package path
if "www.apps.accounts" not in sys.modules:
    try:
        import accounts as _real_accounts
        # Create a namespace that mirrors the real accounts package
        _www_accounts = types.ModuleType("www.apps.accounts")
        _www_accounts.__path__ = list(getattr(_real_accounts, "__path__", []))
        _www_accounts.__package__ = "www.apps.accounts"
        sys.modules["www.apps.accounts"] = _www_accounts
    except Exception:
        _m = types.ModuleType("www.apps.accounts")
        _m.__path__ = []
        _m.__package__ = "www.apps.accounts"
        sys.modules["www.apps.accounts"] = _m

# Make www.apps.accounts.models a namespace package (not mock) so tags can be imported
if "www.apps.accounts.models" not in sys.modules:
    try:
        import accounts.models as _real_models
        _ns = types.ModuleType("www.apps.accounts.models")
        _ns.__path__ = list(getattr(_real_models, "__path__", []))
        _ns.__package__ = "www.apps.accounts.models"
        sys.modules["www.apps.accounts.models"] = _ns
    except Exception:
        pass

# www.apps.accounts.renderers → real module at structa.cloud/plugins/accounts/renderers.py
if "www.apps.accounts.renderers" not in sys.modules:
    try:
        import importlib as _il
        _real = _il.import_module("accounts.renderers")
        sys.modules["www.apps.accounts.renderers"] = _real
    except Exception:
        _stub = types.ModuleType("www.apps.accounts.renderers")
        _stub.dynamic_renderer = MagicMock()
        sys.modules["www.apps.accounts.renderers"] = _stub

# Registration modules moved under accounts.*; keep django-fusion/ceptor and
# legacy tests that import www.apps.accounts.registration.* working.
def _register_registration_aliases():
    _alias_targets = {
        "www.apps.accounts.registration": "accounts.registration",
        "www.apps.accounts.registration.tokens": "accounts.registration.tokens",
        "apps.accounts": "accounts",
        "apps.accounts.registration": "accounts.registration",
        "apps.accounts.registration.tokens": "accounts.registration.tokens",
    }
    for _alias, _target in _alias_targets.items():
        if _alias in sys.modules:
            continue
        try:
            sys.modules[_alias] = importlib.import_module(_target)
        except Exception:
            # Non-token registration modules can require Django's app registry;
            # pytest_configure registers those after django.setup().
            pass

_register_registration_aliases()

# www.apps.accounts.models.tags → real module (must be before the mock loop)
# This must be set up as a direct alias so the import works
if "www.apps.accounts.models.tags" not in sys.modules:
    try:
        import importlib as _il
        _real = _il.import_module("accounts.models.tags")
        sys.modules["www.apps.accounts.models.tags"] = _real
    except Exception:
        pass  # Keep the mock if import fails

# Also set up www.apps.accounts.models.manage.service
if "www.apps.accounts.models.manage" not in sys.modules:
    try:
        import accounts.models.manage as _real_manage
        _ns = types.ModuleType("www.apps.accounts.models.manage")
        _ns.__path__ = list(getattr(_real_manage, "__path__", []))
        _ns.__package__ = "www.apps.accounts.models.manage"
        sys.modules["www.apps.accounts.models.manage"] = _ns
    except Exception:
        pass

# Modules that need to be proper namespace packages (not MagicMock)
# so that sub-imports like `www.apps.accounts.renderers` work
# Note: www.apps.accounts.models must be a namespace package for tags to work
for _mod_path in [
    "www.apps.content",
    "www.apps.content.models",
    "www.apps.content.models.pages",
    "www.apps.content.models.pages.base",
    "www.apps.content.models.contact",
    "apps.content",
    "apps.content.models",
    "apps.content.models.pages",
    "apps.content.models.pages.base",
    "apps.content.models.contact",
    # apps.content.tasks is registered separately via _register_tasks_aliases()
    "apps.pages",
    "www.apps.accounts.models.manage.service",
    # Missing sub-modules referenced by accounts models
    "ceptor_ai.pipelines.models.tags",
    "ceptor_ai.pipelines.models.users.role",
    # Missing generic.search module
    "django_fusion.comp.generic.search",
    # www.core.content.models — stub to avoid pulling in ceptor_ai models
    "www.core.content",
    "www.core.content.models",
    "www.core.content.models.pages",
    "www.core.content.models.pages.base",
    "www.core.content.models.contact",
]:
    if _mod_path not in sys.modules:
        sys.modules[_mod_path] = _page_mock

# apps.content.tasks and apps.pages.tasks → real module at www/projects/content/tasks.py
# (the test_tasks_recovery tests import from these paths)
def _register_tasks_aliases():
    import importlib as _il
    _task_candidates = [
        _lms_path / "www" / "core" / "content" / "tasks.py",
        _portfolio_path / "www" / "core" / "content" / "tasks.py",
        _lms_full_path / "www" / "core" / "content" / "tasks.py",
    ]
    _content_tasks_file = next((p for p in _task_candidates if p.exists()), None)
    if _content_tasks_file is None:
        return
    _content_tasks_path = str(_content_tasks_file)
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("_content_tasks_real", _content_tasks_path)
    if _spec:
        _mod = _ilu.module_from_spec(_spec)
        try:
            _spec.loader.exec_module(_mod)
            for _alias in ("apps.content.tasks", "apps.pages.tasks"):
                if _alias not in sys.modules:
                    sys.modules[_alias] = _mod
        except Exception:
            pass

_register_tasks_aliases()

# ---------------------------------------------------------------------------
# Django settings
# ---------------------------------------------------------------------------
SECRET_KEY = "test-secret-key-for-testing-only-at-least-50-chars-long!!"
DEBUG = True
USE_TZ = True
SITE_ID = 1
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Use file-based database to avoid test isolation issues
import os

TEST_DB_NAME = os.environ.get("TEST_DB_NAME", "test_db.sqlite3")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": TEST_DB_NAME,
        "TEST": {
            "NAME": TEST_DB_NAME,
        },
    }
}

# Force pytest-django to use the file-based database
TEST_RUNNER = "django.test.runner.DiscoverRunner"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.sites",
    "wagtail",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.snippets",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.contrib.settings",
    "taggit",
    "modelcluster",
    "django_fusion",
    "django_fusion.comp",
    # allauth — needed for adapter tests
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Remove ceptor_ai to avoid table conflicts with email_log
    # Blog app only — accounts/ceptor have complex deps needing full project setup
    "plugins.blog",
    # Skip apps.accounts to avoid admin autodiscover issues with www.apps.accounts.models.tags
]


import importlib.util as _importlib_util

def _installed(app: str) -> bool:
    try:
        return _importlib_util.find_spec(app) is not None
    except ModuleNotFoundError:
        return False

_OPTIONAL_TEST_APPS = {
    "wagtail", "wagtail.images", "wagtail.documents", "wagtail.snippets",
    "wagtail.search", "wagtail.admin", "wagtail.contrib.settings",
    "taggit", "modelcluster", "django_fusion", "django_fusion.comp", "allauth",
    "allauth.account", "allauth.socialaccount", "apps.blog",
}
INSTALLED_APPS = [
    app for app in INSTALLED_APPS
    if app not in _OPTIONAL_TEST_APPS or _installed(app)
]
if not _installed("wagtail"):
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "apps.blog"]

# Disable admin autodiscover to prevent import errors from accounts admin
# We'll manually register needed models in conftest.py instead
import sys

# Patch admin.autodiscover to do nothing
from django.contrib import admin

original_autodiscover = admin.autodiscover_modules
def no_autodiscover(*args, **kwargs):
    pass
admin.autodiscover = no_autodiscover

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
if _installed("allauth.account"):
    MIDDLEWARE.append("allauth.account.middleware.AccountMiddleware")

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [
        # Test-specific templates override app templates (e.g. base_page.html stub)
        str(_tests_dir / "assets" / "templates"),
    ],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
        "builtins": [
            "django_fusion.comp.templatetags.components",
        ],
        "libraries": {
            "components": "django_fusion.comp.templatetags.components",
        },
    },
}]

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
ROOT_URLCONF = "tests.urls"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@example.com"
WAGTAIL_SITE_NAME = "Test"
PROFILE_MODEL = "auth.User"

# Disable migrations for test apps to speed up test DB creation
MIGRATION_MODULES = {
    # Main apps
    "ceptor_ai": None,
    "django_fusion": None,
    "pipelines": None,
    "accounts": None,
    "blog": None,
    # All ceptor sub-apps
    "email": None,
    "chat": None,
    "mcp_designer": None,
    "handlers": None,
    "newsletter": None,
    "workflows": None,
    "temporal": None,
    "services": None,
    "site": None,
    "blocks": None,
    "contrib": None,
    "forms": None,
    "middlewares": None,
    "signals": None,
    "tasks": None,
    "templatetags": None,
}
