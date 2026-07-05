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
    from django_fusion.comp.core._init import components  # imports after settings

    components.reset()
    yield
    components.reset()


def _render(source: str) -> str:
    from django.template import engines  # imports after settings

    return engines["django"].from_string(source).render().strip()


def test_comp_path_renders_same_as_include():
    via_include = _render('{% include "partials/auth_buttons.html" %}')
    via_comp = _render('{% comp "partials/auth_buttons.html" /%}')
    assert via_include == via_comp == '<span class="auth">auth</span>'


def test_comp_path_records_render_history_with_full_path_as_name():
    _render('{% comp "partials/auth_buttons.html" /%}')
    from django_fusion.comp.core._init import components

    history = components.get_render_history()
    assert len(history) == 1
    assert history[0].name == "partials/auth_buttons.html"


def test_register_include_path_under_root_returns_list():
    from django_fusion.comp.registry import register_include_paths

    cached = register_include_paths(["partials/auth_buttons.html"])
    assert cached == ["partials/auth_buttons.html"]
    from django_fusion.comp.core._init import components

    assert "partials/auth_buttons.html" in components._components


def test_register_include_path_idempotent():
    from django_fusion.comp.registry import register_include_path
    from django_fusion.comp.core._init import components

    register_include_path("partials/auth_buttons.html")
    first_id = id(components._components["partials/auth_buttons.html"])
    register_include_path("partials/auth_buttons.html")
    second_id = id(components._components["partials/auth_buttons.html"])
    assert first_id == second_id


def test_parse_include_contents_all_shapes():
    """Pure-Python classification covers ALL realistic include shapes.

    Specifically tests the previously-failing ``only with foo=bar``
    shape (only-before-with).
    """
    import importlib.util
    import sys

    scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
    spec = importlib.util.spec_from_file_location(
        "convert_includes", scripts_dir / "convert_includes.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["convert_includes"] = mod
    spec.loader.exec_module(mod)
    mod._configure_django_minimal()

    cases = [
        ('include "partials/auth_buttons.html"', None, False),
        ("include partials/foo.html", "variable-path", False),
        ('include "p.html" as alias', "as-alias", False),
        ('include "p.html" only', None, True),
        ('include "p.html" with foo=bar', None, False),
        ('include "p.html" with foo=bar only', None, True),
        ('include "p.html" only with foo=bar', None, True),
        ('include "p.html" with foo=bar only as alias', "as-alias", True),
    ]
    for contents, expected_skip, expected_only in cases:
        m = mod._parse_include_contents(contents)
        assert m.skip_reason == expected_skip, (
            f"contents={contents!r}: skip_reason={m.skip_reason!r}, expected={expected_skip!r}"
        )
        assert m.only == expected_only, (
            f"contents={contents!r}: only={m.only}, expected={expected_only}"
        )


def test_rewrite_template_byte_exact_replacement():
    """Splice is byte-exact; the original whitespace pattern survives."""
    import importlib.util
    import sys

    scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
    spec = importlib.util.spec_from_file_location(
        "convert_includes", scripts_dir / "convert_includes.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["convert_includes"] = mod
    spec.loader.exec_module(mod)
    mod._configure_django_minimal()

    src = (
        '<div>\n'
        '    {% include "partials/auth_buttons.html" %}\n'  # normal padding
        '{%   include   "partials/auth_buttons.html"   %}\n'  # extra padding
        '{% include var %}\n'  # variable-path skipped
        '{% include "x.html" as saved %}\n'  # as-alias skipped
        '{% include "y.html" only %}\n'  # only-tag preserved
        '</div>'
    )
    new, converted, skipped = mod.rewrite_template(src)
    # Tighter form-based assertions: regex-pin the EXACT produced comp token
    # so a regression that changes whitespace / quoting / kwarg shape would
    # be caught instead of slipping past a length count.
    expected_comp_calls = {
        # Two distinct occurrences of the same comp call (normal + extra padding).
        '{% comp "partials/auth_buttons.html" /%}': 2,
        '{% comp "y.html" only /%}': 1,
    }
    import re  # local import so the test stays self-contained.

    for token, expected_count in expected_comp_calls.items():
        actual_count = len(re.findall(re.escape(token), new))
        assert (
            actual_count == expected_count
        ), f"{token!r}: expected to appear {expected_count}×, found {actual_count}×"
    # Variable-path and as-alias left untouched
    assert "{% include var %}" in new
    assert '{% include "x.html" as saved %}' in new
    # Sanity: no double-conversion or accidental regeneration
    total_comp = len(re.findall(r"\{%\s*comp\s+", new))
    assert total_comp == sum(expected_comp_calls.values())
