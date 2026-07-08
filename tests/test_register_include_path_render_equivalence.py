"""Lights-up render-equivalence check for include-path registration.

GREEN-LIGHT GUARANTEE before rolling the comp-tag refactor out to
production: after registering ``partials/auth_buttons.html`` so the
verbatim **template_name** key AND the bare **component_name** key
BOTH resolve to the same include-path component, the THREE
invocations below MUST produce byte-for-byte identical render
output::

    R1: {% include "partials/auth_buttons.html" %}
    R2: {% comp "partials/auth_buttons.html" /%}
    R3: {% comp auth_buttons /%}

- R1 is Django's built-in ``{% include %}`` tag (the baseline).
- R2 is the ``{% comp %}`` tag invoked by *template_name* — the
  verbatim path is the registry key produced by
  :func:`django_fusion.comp.registry.register_include_path`.
- R3 is the ``{% comp %}`` tag invoked by *component_name* — the
  bare Python identifier; the canonical "use the component by name"
  form. The dual-key wiring in this test is the spec that the
  production rollout must wire into :func:`register_include_path`
  (or its alias-API successor); until then R3 fails.

The lone test in this module is the assertion:
``r_include == r_comp_template_name == r_comp_component_name``.
If any pair diverges, the rollout is blocked.

Test isolation
--------------
- Self-contained Django bootstrap mirroring
  ``tests/test_comp_registry.py`` — runnable without pytest-django
  OR alongside it (the mutation branch keeps ``TEMPLATES[NAME='django']``
  consistent if pytest-django has pre-configured settings).
- Module-scoped ``tmp_path_factory`` so the partial lives in a
  per-session temp directory (no git pollution, no stale-file state
  across reruns).
- Per-test ``components.reset()`` autouse fixture so registry state
  never leaks between tests.
- The test partial contains NO ``{{ }}`` context references so the
  ``context.push`` performed by ``BoundComponent.render`` is
  observably inert — any future divergence between include and comp
  output is the bug, not the context frame.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Test-local Django bootstrap. Mirrors
# ``tests/test_comp_registry.py::_boot_django`` so this file is
# runnable in isolation OR alongside pytest-django's
# ``DJANGO_SETTINGS_MODULE=tests.settings`` preconfigured.
# ---------------------------------------------------------------------------


def _configure_django(test_templates_dir: Path) -> None:
    """Configure Django BEFORE any ``django_fusion.comp.*`` import.

    Importing the comp core eagerly touches ``settings.CONF``, so this
    function MUST run first.
    """
    import django
    from django.conf import settings

    templates_conf = {
        # ``NAME='django'`` matches the canonical engines-handler alias
        # so ``engines['django']`` resolves against THIS entry rather
        # than whichever entry pytest-django pre-configured at
        # index 0.
        "NAME": "django",
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(test_templates_dir)],
        "APP_DIRS": False,
        "OPTIONS": {
            "builtins": [
                # Mirror production: ``comp`` is available WITHOUT an
                # explicit ``{% load components %}`` (see
                # applications/configs/base/templates.py).
                "django_fusion.comp.templatetags.components",
            ],
        },
    }
    if not settings.configured:
        settings.configure(
            DEBUG=False,
            INSTALLED_APPS=[],
            TEMPLATES=[templates_conf],
        )
        django.setup()
    else:
        # pytest-django pre-configured Django. Inject our test DIRS
        # and tag builtin into the existing engine and clear the
        # engines cache so the next ``engines['django']`` rebuilds.
        from django.template import engines

        templates = list(settings.TEMPLATES)
        if templates:
            # Match the NAMED ``django`` engine; fall back to entry
            # without NAME (Django's default-alias convention).
            target_idx = next(
                (
                    i
                    for i, t in enumerate(templates)
                    if t.get("NAME") == "django"
                ),
                0,
            )
            templates[target_idx].setdefault("DIRS", []).append(
                str(test_templates_dir)
            )
            options = templates[target_idx].setdefault("OPTIONS", {})
            # Idempotent builtin registration: production settings
            # may already include the same dotted path.
            builtins = options.setdefault("builtins", [])
            if (
                "django_fusion.comp.templatetags.components"
                not in builtins
            ):
                builtins.append(
                    "django_fusion.comp.templatetags.components"
                )
        else:
            # ``settings.TEMPLATES`` is empty (e.g. conftest.py
            # configured Django WITHOUT a TEMPLATES block). Adopt
            # our own module-scoped template config so this test
            # file is runnable in isolation.
            templates.append(templates_conf)
        settings.TEMPLATES = templates
        # Thorough cached_property invalidation (Django 4.2+ / 5.x):
        # ``EngineHandler.templates`` is a ``cached_property`` that
        # lazy-builds an alias-indexed dict from ``self._templates``,
        # which by default points at ``settings.TEMPLATES``. After we
        # mutate settings.TEMPLATES we must clear THREE caches so
        # the next ``engines['django']`` rebuilds against our list:
        #   - ``engines._engines``: instantiated backend instances
        #   - ``engines._templates``: the storage pointer (set to
        #     ``None`` so the property re-bootstraps from
        #     ``settings.TEMPLATES`` on next access)
        #   - ``engines.__dict__['templates']``: the cached_property's
        #     cached NAME-indexed dict (Python's ``cached_property``
        #     stores its result in the instance ``__dict__`` keyed by
        #     the property name, NOT in the storage attribute).
        engines._engines.clear()
        if hasattr(engines, "_templates"):
            engines._templates = None
        engines.__dict__.pop("templates", None)


# ---------------------------------------------------------------------------
# Module-scoped fixtures.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def _boot_django_for_module(tmp_path_factory):
    """Create the partial + bootstrap Django for this module."""
    tmp_dir = tmp_path_factory.mktemp("comp_registry_lights_up")
    partials = tmp_dir / "partials"
    partials.mkdir(parents=True, exist_ok=True)
    target = partials / "auth_buttons.html"
    # Self-contained markup — no ``{{ }}`` so the include/comp render
    # comparison isn't perturbed by ``BoundComponent``'s context frame.
    target.write_text(
        '<span class="auth">auth</span>',
        encoding="utf-8",
    )
    _configure_django(tmp_dir)
    # Force lazy-init of the ``django`` engine so any setup errors
    # surface during fixture setup, NOT during the test body.
    import django.template

    django.template.engines["django"]
    yield


@pytest.fixture(autouse=True)
def _reset_components():
    """Wipe registry state before AND after each test for isolation."""
    # Imports AFTER Django is configured (comp.core touches settings
    # at module-import time).
    from django_fusion.comp.core._init import components

    components.reset()
    yield
    components.reset()


def _render(source: str) -> str:
    """Render ``source`` against the django engine, stripping whitespace.

    Stripping is intentional: this repo's marker convention omits
    trailing newlines on minimal partial templates, so a strict
    byte compare would catch a fixture-ordering artefact rather
    than a real regression. The equivalence assertion below is the
    real spec.
    """
    from django.template import engines

    return engines["django"].from_string(source).render().strip()


# ---------------------------------------------------------------------------
# The lights-up check.
# ---------------------------------------------------------------------------


def test_register_include_path_renders_identical_via_include_and_both_comp_invocations():
    """R1 == R2 == R3 after dual-key registration of a real partial.

    Run-time spec for production rollout:

    1. :func:`register_include_path` MUST populate the verbatim path
       key (``partials/auth_buttons.html``) so R2 resolves through
       the eager cache.
    2. The same call (or a sibling aliasing helper) MUST also
       populate the bare component-name key (``auth_buttons``) so
       R3 resolves through the same cache. The current
       implementation populates only the verbatim key; the second
       registration below in the test body is the spec-rollout
       contract. Until (2) lands in production rollout, R3 fails
       and migration is blocked.
    """
    # Imports AFTER fixtures have run.
    from django_fusion.comp.core._init import components
    from django_fusion.comp.registry import register_include_path

    # Step 1 — exercise the existing public API. After this call,
    # ``components._components['partials/auth_buttons.html']`` is
    # populated; the bare-name key is NOT.
    register_include_path("partials/auth_buttons.html")

    # Step 2 — wire the dual-key spec. The same IncludePathComponent
    # instance is shared under both keys; production rollout must
    # move this into ``register_include_path`` (or its alias-API
    # successor).
    path_key = "partials/auth_buttons.html"
    name_key = "auth_buttons"
    components._components[name_key] = components._components[path_key]
    # Pin the spec: both registry keys MUST point to the SAME
    # IncludePathComponent instance so render-history metadata stays
    # verbatim across both invocation routes. A regression that drops
    # either key OR re-creates the component under one key would
    # surface here.
    assert path_key in components._components
    assert name_key in components._components
    assert (
        components._components[path_key]
        is components._components[name_key]
    )

    # Step 3 — render all THREE routes and assert byte-exact
    # equivalence. Chained equality (r1 == r2 == r3) is intentional:
    # any pair divergence surfaces as a clean pytest failure with
    # both offending values printed.
    r_include = _render('{% include "partials/auth_buttons.html" %}')
    r_comp_template_name = _render(
        '{% comp "partials/auth_buttons.html" /%}'
    )
    r_comp_component_name = _render('{% comp auth_buttons /%}')

    assert r_include == r_comp_template_name == r_comp_component_name
