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
import copy
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


# 4. Global template-state guard.
#
# Several modules need a custom `TEMPLATES` configuration and replace
# `settings.TEMPLATES` (or the cached backend's `dirs`) to get it:
# `analyzer/test_views.py`, `test_component_tags.py`, `test_comp_registry.py`,
# `test_form_components.py`, and
# `test_register_include_path_render_equivalence.py`. None of them restored the
# original value, so a module that had already run left the engine pointing at
# a deleted `tmp_path` and every later module that resolved a real component
# template failed with `TemplateDoesNotExist`. That made the suite
# order-dependent: identical tests passed in isolation and failed in a full
# run.
#
# The pristine value is captured HERE, at import time, for two reasons:
#
# - A ``scope="module"`` fixture that configures templates (e.g.
#   ``analyzer/test_views.py::shared_e2e_dir``) runs BEFORE the first
#   function-scoped fixture in its module. A per-test snapshot would therefore
#   capture the already-polluted value and faithfully restore the pollution.
# - Capturing per test also lets a polluting fixture leak into the *next*
#   module when the polluter is module-scoped rather than function-scoped.
#
# Import time is the only point that is guaranteed to precede every fixture.
# The (cheap) deepcopy comparison runs for each test; the engine rebuild is
# paid only by the handful of tests that actually mutate the value.
_PRISTINE_TEMPLATES = copy.deepcopy(getattr(settings, "TEMPLATES", None))


# Scope is MODULE, not function, on purpose: several modules configure templates
# for the whole module from a `scope="module"` fixture
# (`test_comp_registry.py::_boot_django_for_module`,
# `analyzer/test_views.py::shared_e2e_dir`). Restoring after every test would
# undo that configuration mid-module and break the tests it was written for.
# Restoring between modules is what isolation actually requires.
def _reset_template_engine_cache() -> None:
    """Discard Django's cached template-engine state.

    Three pieces of state matter, and clearing only the first is not enough:

    - ``engines._engines`` holds the instantiated backends.
    - ``engines.templates`` is a ``cached_property`` mapping alias to backend.
    - ``engines._templates`` is the list ``Handler.templates`` captured on its
      first access -- ``if self._templates is None: self._templates =
      settings.TEMPLATES``. It is a *reference to the old settings list*, so as
      long as it is set, rebuilding re-reads the previous ``TEMPLATES`` value
      and the restore appears to do nothing.

    Dropping all three is what makes the next ``engines["django"]`` lookup read
    the current ``settings.TEMPLATES``. Omitting ``_templates`` is the subtle one
    -- ``engines._engines.clear()`` alone looks sufficient and is not.
    """
    from django.template import engines

    engines._engines.clear()
    engines._templates = None
    engines.__dict__.pop("templates", None)


@pytest.fixture(scope="module", autouse=True)
def _restore_django_template_state():
    yield
    if copy.deepcopy(getattr(settings, "TEMPLATES", None)) != _PRISTINE_TEMPLATES:
        settings.TEMPLATES = copy.deepcopy(_PRISTINE_TEMPLATES)
        _reset_template_engine_cache()


# 5. Global component-registry guard.
#
# `components` (django_fusion.comp._init) is a process-global singleton holding
# the include-path registry and the render history. Several modules mutate it:
# `test_comp_registry.py` (which resets it per test but deliberately does not
# reset on teardown), the analyzer views, and the registry/asset tests. Two
# failure modes followed:
#
# - `_render_history` accumulates for the whole session, so
#   `assert len(history) == 1` failed as soon as anything rendered a component
#   earlier in the run.
# - Include paths registered by an earlier module changed how
#   `{% comp "partials/auth_buttons.html" %}` resolved later.
#
# `ComponentRegistry.reset()` plus `_register_builtin_component_paths()` restores
# exactly what `AppConfig.ready()` produced at startup, so that pair is the
# pristine state for this suite. Restore only when a test actually changed the
# registry.
def _registry_fingerprint() -> tuple[frozenset, int]:
    from django_fusion.comp._init import components

    return (frozenset(components._components), len(components._render_history))


@pytest.fixture(scope="module", autouse=True)
def _restore_component_registry():
    before = _registry_fingerprint()
    yield
    if _registry_fingerprint() != before:
        from django_fusion.comp._init import components
        from django_fusion.comp.apps import _register_builtin_component_paths

        components.reset()
        _register_builtin_component_paths()
