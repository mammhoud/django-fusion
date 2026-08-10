"""Regression tests for the skeleton/page-render fixes:

1. Slot content is rendered exactly once (no double-render of template syntax).
2. ``{% prop name default=X %}`` kwarg-style defaults resolve (LMS component syntax).
3. Resolved props are exposed as bare context variables, not only via ``props.*``.

Fixtures live under ``tests/test_templates/components/{slottest,proptest,bareprops}/``.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest
from django.template import Context, engines
from django.test import override_settings

from django_fusion.comp._init import components
from django_fusion.comp.tags.tags.prop import PropNode
from django_fusion.config.params import Param, Params, Value

_test_templates_dir = Path(__file__).resolve().parent / "test_templates"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(_test_templates_dir)],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
            "libraries": {"components": "django_fusion.comp.tags.components"},
        },
    }
]


@pytest.fixture(autouse=True)
def reset_components():
    components.reset()
    yield
    components.reset()


def render(source, context=None):
    return engines["django"].from_string(source).render(context or {}).strip()


# ---------------------------------------------------------------------------
# Slot double-render
# ---------------------------------------------------------------------------


@override_settings(TEMPLATES=TEMPLATES)
def test_slot_with_variable_renders_value_not_double_template():
    """A slot containing ``{{ var }}`` must output the value exactly once.

    Regression: ``fill_slots`` eagerly rendered the nodelist to a string and
    ``SlotNode.render`` then re-parsed that string as a new template, so any
    ``{{ }}`` / ``{% %}`` sequences in the caller's content evaluated twice.
    """
    output = render(
        '{% load components %}'
        '{% comp "components/slottest/panel.html" name="panel-a" %}'
        '{% slot header %}{{ greeting }} world{% endslot %}'
        '{% endcomp %}',
        {"greeting": "hello"},
    )

    assert output.count("hello") == 1
    assert "hello world" in output
    assert "hello fallback" not in output
    assert output.count("data-panel") == 1
    # The component's own attribute interpolation still evaluates normally.
    assert 'data-name="panel-a"' in output


@override_settings(TEMPLATES=TEMPLATES)
def test_slot_default_fallback_rendered_once():
    """When the caller passes no slot content, the component's fallback body
    renders exactly once (previously also double-rendered)."""
    output = render(
        '{% load components %}'
        '{% comp "components/slottest/fallback.html" %}'
        '{% slot header %}{% endslot %}'
        '{% endcomp %}',
        {"fallback": "FALLBACK"},
    )

    assert output.count("FALLBACK") == 1
    assert "FALLBACK default" in output
    assert output.count("data-fallback") == 1


# ---------------------------------------------------------------------------
# {% prop name default=X %} kwarg syntax
# ---------------------------------------------------------------------------


def test_prop_node_parses_kwarg_style_default():
    """``{% prop show_icons default=True %}`` keeps the kwarg default."""
    from django.template.base import Parser, Token, TokenType

    from django_fusion.comp.tags.tags.prop import do_prop

    token = Token(
        TokenType.BLOCK,
        "prop show_icons default=True",
    )
    node = do_prop(Parser([]), token)

    assert node.name == "show_icons"
    assert node.default == "True"


@override_settings(TEMPLATES=TEMPLATES)
def test_prop_kwarg_default_resolves_to_bool():
    """A prop declared ``{% prop show_icons default=True %}`` resolves True when
    the caller passes no value, and keeps the passed value otherwise."""
    default_output = render(
        '{% load components %}{% comp "components/proptest/flags.html" / %}'
    )
    assert default_output == "icons=True|labels=True|style=inside"

    overridden = render(
        '{% load components %}'
        '{% comp "components/proptest/flags.html" show_icons=False show_labels=False '
        'icon_style="outside" / %}'
    )
    assert overridden == "icons=False|labels=False|style=outside"


@override_settings(TEMPLATES=TEMPLATES)
def test_prop_kwarg_default_passes_none_for_plain_declaration():
    """``{% prop field %}`` (no default) resolves None when the caller omits it."""
    output = render(
        '{% load components %}{% comp "components/proptest/required.html" / %}'
    )
    assert output == "MISSING"


# ---------------------------------------------------------------------------
# Bare-context-var prop exposure
# ---------------------------------------------------------------------------


@override_settings(TEMPLATES=TEMPLATES)
def test_props_exposed_as_bare_context_vars():
    """Component templates can reference props as bare variables
    (django-cotton style), not only via ``{{ props.name }}``."""
    output = render(
        '{% load components %}'
        '{% comp "components/bareprops/card.html" title="Hello" / %}',
        {},
    )

    assert '<h3 data-bare-title>Hello</h3>' in output
    assert '<span data-bare-badge>new</span>' in output


@override_settings(TEMPLATES=TEMPLATES)
def test_props_and_bare_vars_stay_in_sync():
    """``props.*`` mapping and bare vars expose the same resolved values."""
    output = render(
        '{% load components %}'
        '{% comp "components/bareprops/sync.html" name="Fusion" / %}',
        {},
    )

    assert output == "bare=Fusion|mapping=Fusion"


def test_render_props_uses_kwarg_default_when_passed_value_is_none():
    """A caller passing ``show_labels=None`` falls back to the declared default."""
    prop = PropNode("show_labels", "True", [])
    component = SimpleNamespace(nodelist=[prop])
    params = Params(attrs=[Param("show_labels", Value("None"))])

    assert params.render_props(component, Context({})) == {"show_labels": True}
