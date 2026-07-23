"""Smoke tests for django-fusion form component templates.

Pins that the canonical form component templates in
``django_fusion/comp/templates/components/form/`` are discoverable
by Django's template loader AND by the django-fusion ``{% comp %}``
tag after the templates were consolidated into the django-fusion
package.
"""
import pytest
from django.template.loader import get_template
from django_fusion.comp.core._init import components


@pytest.fixture(autouse=True)
def _ensure_builtin_components_registered():
    """Make sure built-in component paths are registered before each test.

    Other tests may reset the registry, so re-populate it here without
    re-running ``AppConfig.ready()``.
    """
    from django_fusion.comp.apps import _register_builtin_component_paths

    if "components/form/form_block.html" not in components._components:
        _register_builtin_component_paths()
    yield


def test_form_block_loads_via_template_loader():
    """``components/form/form_block.html`` must load via ``get_template``.

    Pins the canonical path of the form_block template after it
    was moved from
    ``applications/assets/templates/components/form/form_block.html``
    to
    ``applications/libs/django-fusion/src/django_fusion/comp/templates/components/form/form_block.html``.
    """
    template = get_template("components/form/form_block.html")
    assert template is not None


def test_form_field_loads_via_template_loader():
    """``components/form/form_field.html`` must load (regression guard)."""
    template = get_template("components/form/form_field.html")
    assert template is not None


def test_form_simple_loads_via_template_loader():
    """``components/form/form_simple.html`` must load (regression guard).

    Previously failed with ``TemplateSyntaxError: 'block' tag with
    name 'actions' appears more than once`` because the multi-line
    ``{# #}`` comment at the top of the file contained ``{% block actions %}``
    references that Django tried to parse as actual block tags. Fixed
    by wrapping the comment in ``{% comment %}{% endcomment %}``.
    """
    template = get_template("components/form/form_simple.html")
    assert template is not None


def test_form_loads_via_template_loader():
    """``components/form/form.html`` must load (regression guard).

    Previously failed with ``TemplateSyntaxError: Invalid block tag
    on line 40: 'comp'`` because the multi-line ``{# #}`` comment at
    the top of the file contained ``{% comp %}`` examples that Django
    tried to parse as actual comp tags. Fixed by wrapping the comment
    in ``{% comment %}{% endcomment %}``.
    """
    template = get_template("components/form/form.html")
    assert template is not None


def test_form_block_registered_as_comp_path():
    """``components/form/form_block.html`` must be in the component registry.

    Pins that the template is discoverable via ``{% comp %}`` so
    callers don't need to know the full package-internal path.
    """
    assert "components/form/form_block.html" in components._components, (
        f"components/form/form_block.html missing from component registry. "
        f"Registered: {sorted(components._components.keys())}"
    )
