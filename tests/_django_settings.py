"""Single source of truth for django-fusion test Django settings.

This module owns the Django settings dict (`TEST_SETTINGS`) used by
`tests/conftest.py` to configure Django via `settings.configure(...)`.

Extracted from conftest.py to:
  - Reduce conftest.py from ~115 lines → ~50 lines (focus on
    pytest bootstrapping + opt-in debug logging, not Django data).
  - Centralize Django settings in one discoverable module so
    `grep -n "SECRET_KEY\|DEBUG\|INSTALLED_APPS" tests/` points here.
  - Keep the docs/why-comments near the data they explain.

`configure()` is idempotent by default — won't override an existing
Django settings from an inherited `DJANGO_SETTINGS_MODULE`. Pass
`only_if_unconfigured=False` to force a reset (useful for tests
that need a clean slate).
"""
import os

import django
import django_fusion
from django.conf import settings


def configure(*, only_if_unconfigured: bool = True) -> None:
    """Apply `TEST_SETTINGS` to Django.

    Idempotent unless `only_if_unconfigured=False`. Calls
    `django.setup()` so template engines initialize.

    Idempotency contract (locked in by
    `tests/test_django_settings_configure_contract.py`):

      - `only_if_unconfigured=True` (default) + Django already
        configured → no-op (caller's settings survive).
      - `only_if_unconfigured=True` (default) + Django not yet
        configured → apply `TEST_SETTINGS` + `django.setup()`.
      - `only_if_unconfigured=False` + Django already configured →
        reset `LazySettings._wrapped` (drops any auto-loaded parent
        module's attrs), then apply `TEST_SETTINGS` + `django.setup()`.
        Without the explicit reset, Django would raise
        `RuntimeError("Settings already configured.")`.
      - `only_if_unconfigured=False` + Django not yet configured →
        still applies `TEST_SETTINGS` + `django.setup()` (the reset
        is a no-op when `_wrapped is empty`).
    """
    if only_if_unconfigured and settings.configured:
        return

    if settings.configured:
        # Django's `LazySettings.configure()` raises
        # `RuntimeError("Settings already configured.")` if `_wrapped`
        # is anything other than the `empty` sentinel. To honor a
        # `only_if_unconfigured=False` request against an already-
        # configured Django state (e.g., a `DJANGO_SETTINGS_MODULE`
        # auto-load), reset `_wrapped` BEFORE calling `configure()`.
        from django.utils.functional import empty as _empty
        settings._wrapped = _empty

    settings.configure(**TEST_SETTINGS)
    django.setup()


# `tests/conftest.py` adds tests/ to `sys.path` (so `stubs.X` libraries
# resolve). Imports here resolve via pyproject.toml's `pythonpath = ["src"]`.
TEST_SETTINGS: dict = {
    "DEBUG": True,
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    "INSTALLED_APPS": [
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django.contrib.sessions",
        "django.contrib.messages",
        # `django_fusion.comp` is the sub-app that owns
        # CoreExtAppConfig. Without it, `ready()` never runs and the
        # component registry stays empty.
        "django_fusion.comp",
    ],
    "MIDDLEWARE": [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ],
    # ``tests/`` is added to ``sys.path`` by ``tests/conftest.py``,
    # so the urlconf module is importable as ``urls`` directly.
    "ROOT_URLCONF": "urls",
    "SECRET_KEY": "test-secret-key",
    "STATIC_URL": "/static/",
    "USE_TZ": True,
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            # Django's `APP_DIRS` only scans `<app>/templates/` (top
            # level). django-fusion ships canonical templates under
            # `django_fusion/templates/` (the new `fusion/` component
            # namespace) and also keeps some backward-compatible stubs
            # under `django_fusion/comp/templates/`. Add both explicitly
            # so `get_template()` can resolve paths like
            # "components/form/form_block.html" and
            # "fusion/components/form/form_block.html".
            "DIRS": [
                os.path.join(os.path.dirname(django_fusion.__file__), "templates"),
                os.path.join(os.path.dirname(django_fusion.__file__), "comp", "templates"),
            ],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
                "libraries": {
                    # Real django-fusion component tag library
                    # ({% prop %}, {% slot %}, {% var %}, etc.).
                    "components": "django_fusion.comp.templatetags.components",
                    # Stub libraries at tests/stubs/*.py — see those
                    # files for what each provides.
                    "wagtailcore_tags": "stubs.wagtailcore_tags",
                    "wagtailimages_tags": "stubs.wagtailimages_tags",
                    "laces": "stubs.laces",
                },
                "builtins": [
                    "django.templatetags.static",
                    "django_fusion.comp.templatetags.components",
                ],
            },
        },
    ],
}
