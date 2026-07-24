"""Render-equivalence tests for path-style component registration.

These tests confirm that a template using ``{% comp "partials/auth_buttons.html" %}``
renders byte-for-byte identical to the equivalent ``{% include "partials/auth_buttons.html" %}``,
verifying that the dynamic registration in
``django_fusion.comp.registry`` produces the same render output as the
Django builtin include machinery.

NOTE on import order: ``django_fusion.comp.configuration.conf`` touches
``settings.DEBUG`` at MODULE IMPORT TIME (it's a dataclass field
default), so we must configure Django BEFORE importing any
``django_fusion.comp`` submodule. The fixture below enforces that.
``INSTALLED_APPS=[]`` is required so ``django.setup()`` populates the
apps registry deterministically across Django versions.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _boot_django(test_templates_dir: Path) -> None:
    """Configure Django settings BEFORE importing django_fusion registries.

    pytest-django (configured in pyproject.toml with
    ``DJANGO_SETTINGS_MODULE = "tests.settings"``) auto-configures Django
    at session start, so on entry to this fixture
    ``settings.configured`` may already be ``True``. In that case we
    **mutate** the existing ``TEMPLATES[0]`` to add our test directory
    and our comp tag library, then clear the engines cache so the next
    ``engines["django"]`` lookup rebuilds against the mutated settings.
    """
    import django
    from django.conf import settings

    templates_conf = {
        # Force the alias name to ``"django"`` so the engines.handler
        # resolves ``engines["django"]`` against THIS entry rather than
        # the (likely differently-configured) pytest-django index-0.
        # Without this, tests/settings.py pre-loading pytest-django
        # forces the lookup to skip our override.
        "NAME": "django",
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(test_templates_dir)],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [],
            "builtins": [
                # Mirror production: comp/wagtail/etc. should be
                # available WITHOUT an explicit {% load components %}
                # in the test sources. See
                # applications/configs/base/templates.py:59.
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
        # pytest-django pre-configured Django using DJANGO_SETTINGS_MODULE.
        # Inject our test DIRS and tag builtin into the existing engine
        # and clear the engines cache so the next lookup re-builds.
        from django.template import engines

        templates = list(settings.TEMPLATES)
        if templates:
            # Find the entry whose NAME is "django" (or default to index
            # 0). Mutating index 0 blindly can corrupt alternative engines
            # (e.g. JWT templates). Match by NAME first; fall back to
            # entry without NAME (the Django convention).
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
            templates[target_idx].setdefault("NAME", "django")
            options = templates[target_idx].setdefault("OPTIONS", {})
            # Guard against double-appending when production settings
            # (applications/configs/base/templates.py:59) already register
            # the same dotted path. Django's `import_library` is module-
            # cached so duplicates are functionally safe, but they grow
            # the list every fixture pass.
            _builtins = options.setdefault("builtins", [])
            if "django_fusion.comp.templatetags.components" not in _builtins:
                _builtins.append("django_fusion.comp.templatetags.components")
        else:
            templates.append(templates_conf)
        settings.TEMPLATES = templates
        engines._engines.clear()
        # Django 5.2+ uses @cached_property for templates; invalidate the
        # cached property so it re-reads from the mutated settings.TEMPLATES.
        engines.__dict__.pop("templates", None)


_test_templates_dir = Path(__file__).resolve().parent / "test_templates_comp_registry"


@pytest.fixture(scope="module", autouse=True)
def _boot_django_for_module():
    partials = _test_templates_dir / "partials"
    partials.mkdir(parents=True, exist_ok=True)
    target = partials / "auth_buttons.html"
    if not target.exists():
        target.write_text('<span class="auth">auth</span>', encoding="utf-8")
    _boot_django(_test_templates_dir)
    # Force ``django.template.engines`` to lazy-initialise the ``django``
    # backend via a probe. Several Django versions defer the
    # template-tag-modules enumeration until the first ``engines[alias]``
    # call; doing it here, inside the fixture, ensures any setup errors
    # surface during fixture setup rather than during test execution.
    import django.template  # noqa: PLC0415

    django.template.engines["django"]
    yield


@pytest.fixture(autouse=True)
def reset_components():
    from django_fusion.comp.apps import _register_builtin_component_paths
    from django_fusion.comp.fragment._init import components  # imports after settings

    # Reset and re-populate the component registry so each test in
    # this module starts with the same state Django built at startup.
    # We do not reset on teardown; otherwise later tests (e.g. in
    # test_form_components.py) would see an empty registry because
    # AppConfig.ready() only runs once.
    components.reset()
    _register_builtin_component_paths()
    yield


def _render(source: str) -> str:
    from django.template import engines  # imports after settings

    return engines["django"].from_string(source).render().strip()


def test_comp_path_renders_same_as_include():
    via_include = _render('{% include "partials/auth_buttons.html" %}')
    via_comp = _render('{% comp "partials/auth_buttons.html" /%}')
    assert via_include == via_comp == '<span class="auth">auth</span>'


def test_comp_path_records_render_history_with_full_path_as_name():
    _render('{% comp "partials/auth_buttons.html" /%}')
    from django_fusion.comp.fragment._init import components

    history = components.get_render_history()
    assert len(history) == 1
    assert history[0].name == "partials/auth_buttons.html"


def test_register_include_path_under_root_returns_list():
    from django_fusion.comp.registry import register_include_paths

    cached = register_include_paths(["partials/auth_buttons.html"])
    assert cached == ["partials/auth_buttons.html"]
    from django_fusion.comp.fragment._init import components

    assert "partials/auth_buttons.html" in components._components


def test_register_include_path_idempotent():
    from django_fusion.comp.registry import register_include_path
    from django_fusion.comp.fragment._init import components

    register_include_path("partials/auth_buttons.html")
    first_id = id(components._components["partials/auth_buttons.html"])
    register_include_path("partials/auth_buttons.html")
    second_id = id(components._components["partials/auth_buttons.html"])
    assert first_id == second_id


