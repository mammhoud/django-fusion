"""Conftest for the lms-demo test suite.

Two responsibilities, in order:

1. **sys.path bootstrap** — add `tests/` to `sys.path` so
   `_django_settings` (in `tests/_django_settings.py`) can be imported
   by both this conftest and any `test_*.py` that imports it.
2. **Hand off to `_django_settings`** — call
   `_django_settings.configure()` to apply Django settings and run
   `django.setup()`. The actual `TEST_SETTINGS` lives in
   `tests/_django_settings.py` as the single source of truth.

The same conftest structure is mirrored across
`django-fusion/tests/conftest.py`, `ctc-research/tests/conftest.py`,
and `VResume/tests/conftest.py` for parity.
"""
import os
import sys


# 1. sys.path bootstrap.
#
# `tests/` must be on sys.path so `import _django_settings` resolves.
_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)


# 2. Hand off to `_django_settings`.
#
# `import _django_settings` adds `tests/_django_settings.py` to
# `sys.modules`. `configure()` applies `TEST_SETTINGS` to Django and
# runs `django.setup()`. Idempotent unless `only_if_unconfigured=False`.
import _django_settings  # noqa: E402
_django_settings.configure()
