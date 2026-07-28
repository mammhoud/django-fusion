"""Single source of truth for lms-demo test Django settings.

This module owns `TEST_SETTINGS` and the idempotent `configure()` callable
used by `tests/conftest.py`. The same pattern is mirrored across
`django-fusion/tests/_django_settings.py`, `ctc-research/tests/_django_settings.py`,
and `VResume/tests/_django_settings.py` — the contract test
`tests/test_django_settings_configure_contract.py` locks in idempotency.

Extraction rationale (mirrors `applications/libs/django-fusion/tests/_django_settings.py`):

  - Centralize lms-demo test settings in one discoverable module so
    `grep -n "SECRET_KEY\|INSTALLED_APPS" tests/` points here.
  - Keep the docs/why-comments near the data they explain.
  - Reduce `tests/conftest.py` to a thin bootstrap (no settings data).

`configure()` is idempotent by default — won't override an existing
Django settings from an inherited `DJANGO_SETTINGS_MODULE`. Pass
`only_if_unconfigured=False` to force a reset.

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
import django
from django.conf import settings


def configure(*, only_if_unconfigured: bool = True) -> None:
    """Apply `TEST_SETTINGS` to Django.

    Idempotent unless `only_if_unconfigured=False`. Calls
    `django.setup()` so template engines (if any) initialize.

    See module docstring for full idempotency contract.
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


# ── Test settings ────────────────────────────────────────────────────────────
# Minimal Django settings so the contract test runs isolated (no site-
# specific apps). Sites that need richer test settings can override this
# dict at the call site OR fork `_django_settings.configure()` to a
# site-specific variant.
#
# `lms-demo` is the source-of-truth test settings file for ITS test
# suite. `ctc-research` and `VResume` carry their own copies mirroring
# this one — the duplication is intentional (each site's test infra is
# independent so a regression in one site doesn't propagate to the others).
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
    ],
    "MIDDLEWARE": [],
    "ROOT_URLCONF": "",
    "SECRET_KEY": "lms-demo-test-secret-key",
    "STATIC_URL": "/static/",
    "USE_TZ": True,
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [],
                "libraries": {},
                "builtins": [],
            },
        },
    ],
}
