"""Conftest for the django-fusion test suite.

Three responsibilities, in order:

1. **sys.path bootstrap** + opt-in `DJANGO_FUSION_QUIET_DEPRECATION`
   env var — silences the 2 documented DeprecationWarnings from the
   deprecated stub modules `django_fusion/comp/forms/{__init__,layout}.py`
   in this regression suite only. Production users never see this
   env var, so the warnings surface normally there.
2. **Hand off to `_django_settings`** — import + call
   `_django_settings.configure()` to apply Django settings and run
   `django.setup()`. The actual `INSTALLED_APPS`, `TEMPLATES`, etc.
   live in `tests/_django_settings.py` as the single source of truth.
3. **Opt-in debug logging** — `DJANGO_DEBUG_CONFTEST=1` prints the
   active settings via `pytest_configure` hook (avoids module-load
   ordering issues; gives the smoke tests a stable signal source).
"""
import os
import sys

import pytest
from django.conf import settings


# 1. sys.path bootstrap + opt-in deprecation-warning gate.
#
# `tests/` must be on sys.path so the `stubs.X` library paths declared
# in `_django_settings.TEST_SETTINGS` can be imported. We also set the
# `DJANGO_FUSION_QUIET_DEPRECATION` env var BEFORE any code that might
# import `django_fusion.comp.forms`. The deprecated stub modules at
# `comp/forms/__init__.py:20` and `comp/forms/layout.py:11` gate their
# `warnings.warn(..., DeprecationWarning, stacklevel=2)` calls on this
# env var. Setting it here means pytest invocations of the regression
# suite run silent; production users (no env var) keep seeing the
# signal. This sidesteps the catch_warnings / pytest_configure-ordering
# footguns we ran into on prior iterations.
_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)
os.environ.setdefault("DJANGO_FUSION_QUIET_DEPRECATION", "1")


# 2. Hand off to `_django_settings` (no noqa needed for inline import).
#
# `import _django_settings` adds `tests/_django_settings.py` to
# `sys.modules`. `configure()` applies `TEST_SETTINGS` to Django and
# runs `django.setup()`. Idempotent unless `only_if_unconfigured=False`.
import _django_settings  # noqa: E402
_django_settings.configure()


# 3. Opt-in debug logging via a `pytest_configure` hook.
#
# Why a hook instead of module-level `print()`? Module-level `print()`
# runs BEFORE pytest's capture setup is complete, which:
# - Bypasses pytest's terminal writer (colorization discipline lost).
# - On TTY, pytest's later re-emit of captured output can produce
#   malformed ANSI escape sequences (mid-banner `^[[31m` gets converted
#   to literal text or scrambled colors).
#
# `@pytest.hookimpl()` makes the hook intent explicit and protects
# against future pytest hookspec validation. The hook fires after
# plugin dispatch but BEFORE per-test fd-level capture begins, so
# raw `print(..., flush=True)` writes reach real stdout immediately
# (and are visible to subprocess tests). We deliberately avoid
# `terminal_writer.line()` here — it buffers to pytest's internal line
# buffer that isn't flushed during `--collect-only`, making the
# banner invisible to subprocess greps.
#
# The banner content itself contains no ANSI escape sequences, so
# pytest's colorization wrapping (which adds codes around content,
# not inside it) doesn't visually change the output.
#
# DO NOT change `== "1"` to a truthy check — `tests/test_conftest_debug_is_quiet.py`
# (negative + positive control) will fail.
@pytest.hookimpl()
def pytest_configure(config):
    if os.environ.get("DJANGO_DEBUG_CONFTEST") == "1":
        print("\n====== CONFTEST DEBUG: Django template configuration ======", flush=True)
        print(f"  env DJANGO_DEBUG_CONFTEST:        {os.environ.get('DJANGO_DEBUG_CONFTEST')!r}", flush=True)
        print(f"  settings.SETTINGS_MODULE:          {settings.SETTINGS_MODULE!r}", flush=True)
        print(f"  settings.configured:               {settings.configured!r}", flush=True)
        print(
            f"  settings.INSTALLED_APPS ({len(settings.INSTALLED_APPS)}): "
            f"{', '.join(settings.INSTALLED_APPS)}",
            flush=True,
        )
        print(f"  settings.TEMPLATES count:          {len(settings.TEMPLATES)}", flush=True)
        for i, tpl in enumerate(settings.TEMPLATES):
            opts = tpl.get("OPTIONS", {})
            print(f"  TEMPLATES[{i}].BACKEND:            {tpl['BACKEND']!r}", flush=True)
            print(f"  TEMPLATES[{i}].DIRS:               {tpl.get('DIRS', [])!r}", flush=True)
            print(f"  TEMPLATES[{i}].APP_DIRS:           {tpl.get('APP_DIRS', False)!r}", flush=True)
            print(f"  TEMPLATES[{i}].builtins:           {opts.get('builtins', [])!r}", flush=True)
            print(
                f"  TEMPLATES[{i}].libraries:          {sorted(opts.get('libraries', {}).keys())!r}",
                flush=True,
            )
            print(
                f"  TEMPLATES[{i}].context_processors: {opts.get('context_processors', [])!r}",
                flush=True,
            )
