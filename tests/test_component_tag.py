from pathlib import Path
from types import SimpleNamespace

import pytest
from django.template import Context, TemplateSyntaxError, engines
from django.template.exceptions import TemplateDoesNotExist
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


def test_false_values_are_preserved_for_literal_and_bound_props():
    assert Value(False).resolve(Context({})) is False
    assert Value("False").resolve(Context({})) is False

    prop = PropNode("enabled", "True", [])
    component = SimpleNamespace(nodelist=[prop])
    params = Params(attrs=[Param("enabled", Value(False))])

    assert params.render_props(component, Context({})) == {"enabled": False}


@override_settings(TEMPLATES=TEMPLATES)
def test_static_component_name_renders_standalone_tag():
    output = render('{% load components %}{% comp "components/static.html" %}')

    assert output == "static:static"


@override_settings(TEMPLATES=TEMPLATES)
def test_context_and_metadata_arguments_are_exposed_to_component_context():
    request = SimpleNamespace(path="/pages/about/")
    page = SimpleNamespace(title="About")

    output = render(
        '{% load components %}'
        '{% comp "components/cards/page.html" page=page source="pages" '
        'requested_by=request.path fragment_name="page_card" %}',
        {"page": page, "request": request},
    )

    assert output == "card:About|pages|/pages/about/|page_card"
    assert components.get_render_history()[-1].source == "pages"
    assert components.get_render_history()[-1].requested_by == "/pages/about/"
    assert components.get_render_history()[-1].fragment_name == "page_card"


@override_settings(TEMPLATES=TEMPLATES)
def test_repeated_component_renders_keep_props_isolated_per_context():
    first = render(
        '{% load components %}'
        '{% comp "components/cards/page.html" page=page source="first" %}',
        {"page": SimpleNamespace(title="First")},
    )
    second = render(
        '{% load components %}'
        '{% comp "components/cards/page.html" page=page source="second" %}',
        {"page": SimpleNamespace(title="Second")},
    )

    assert "card:First|first" in first
    assert "card:Second|second" in second
    assert "First" not in second
    assert "Second" not in first


@override_settings(TEMPLATES=TEMPLATES)
def test_htmx_fragment_component_exposes_fragment_name():
    output = render(
        '{% load components %}'
        '{% comp "components/fragments/messages.html" messages=messages '
        'fragment_name="messages" %}',
        {"messages": ["saved", "queued"]},
    )

    assert output == "fragment:saved,queued|messages"


@override_settings(TEMPLATES=TEMPLATES)
def test_missing_component_raises_template_does_not_exist():
    with pytest.raises(TemplateDoesNotExist):
        render('{% load components %}{% comp "components/missing.html" %}')


@override_settings(TEMPLATES=TEMPLATES)
def test_fragment_name_rejects_aliases_and_invalid_names():
    with pytest.raises(TemplateSyntaxError, match="Use fragment_name"):
        render('{% load components %}{% comp "components/static.html" fragment="x" %}')

    with pytest.raises(TemplateSyntaxError, match="fragment_name must"):
        render(
            '{% load components %}'
            '{% comp "components/static.html" fragment_name="Bad-Name" %}'
        )
