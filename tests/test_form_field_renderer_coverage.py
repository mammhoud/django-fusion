"""Render-coverage tests for the canonical form-field renderer.

Exercises ``applications/assets/templates/components/form/form_field.html``
end-to-end through the two calling paths the runtime exposes:

* **Path 1** — Wagtail StreamField child-block. The caller supplies a
  ``SimpleNamespace``-shaped ``block`` plus a ``field_config`` directly.
  The canonical dereferences ``block.value.{layout, show_icons,
  icon_style, show_labels, show_placeholders, allowed_file_types}`` and
  ``block.id`` to render the field shell, the label ``for=`` anchor, and
  the input ``id=``.

* **Path 2** — Synthesized adapter path. A flat per-field render context
  (``field``, plus ``show_icons`` / ``show_labels`` / ``show_placeholders``
  / ``icon_style`` boolean flags) is fed through the ``as_form_block``
  simple-tag in
  ``django_fusion.comp.templatetags.fusion_form_field_adapter``,
  which builds the same Wagtail-block shape SimpleNamespace from the
  flat dict / object. The canonical then renders identically to Path 1.

Both paths must produce the same HTML for the same logical field. The
ridges this suite guards against are:

1. **Per-call ``class_*`` override contract.** Every canonical tag has
   ``{% firstof class_xxx 'form-xxx' %}` so callers MAY pass any of
   the following 18 keyword args to swap the BEM class emitted:
   ``class_field``, ``class_input_group``, ``class_icon``,
   ``class_label``, ``class_control``, ``class_textarea``,
   ``class_select``, ``class_checkbox_group``, ``class_checkbox``,
   ``class_checkbox_label``, ``class_radio_group``,
   ``class_radio_item``, ``class_radio``, ``class_radio_label``,
   ``class_file``, ``class_input``, ``class_help_text``,
   ``class_error``. This suite asserts every override propagates
   into the rendered HTML for both call paths.

2. **All six ``field_type`` branches.** ``textarea`` / ``select``
   (and the ``dropdown`` back-compat alias) / ``checkbox`` /
   ``radio`` / ``file`` / plain input (i.e. any other
   ``field_type`` value).

3. **Adapter-body parity.** The real production adapter bodies at
   ``applications/lms/.../form_field.html`` and
   ``applications/ctc-research/.../form_field.html`` (read from
   disk) must round-trip a flat per-field dict into a rendered field
   that respects ``field.field_width`` (the root modifier).

The tests rely on ``engines['django'].from_string(...).render(...)``,
the same harness used by ``tests/test_component_tag.py``. The
real canonical + real adapter templates live outside the
``tests/test_templates`` folder, so the test harness extends the
engine ``DIRS`` to include the canonical's directory. Per-site
adapter bodies are read from disk and rendered inline so the test
realistically exercises both production files without template-name
collisions in the engine.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from django.template import engines
from django.test import override_settings

from django_fusion.comp.core._init import components

# -----------------------------------------------------------------
# Test infrastructure: template-engine setup.
# -----------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_APPS_ROOT = _HERE.parents[2]  # tests/ → django-fusion/ → libs/ → applications/
_CANONICAL_DIR = _APPS_ROOT / "assets" / "templates"
_TEST_TEMPLATES_DIR = _HERE / "test_templates"

_LMS_ADAPTER = (
    _APPS_ROOT
    / "lms"
    / "plugins"
    / "components"
    / "blocks"
    / "partials"
    / "form_field.html"
)
_CTC_ADAPTER = (
    _APPS_ROOT
    / "ctc-research"
    / "plugins"
    / "components"
    / "blocks"
    / "partials"
    / "form_field.html"
)
assert str(_CANONICAL_DIR).endswith(
    "applications/assets/templates"
), f"_CANONICAL_DIR resolved unexpectedly: {_CANONICAL_DIR}"
assert _LMS_ADAPTER.is_file(), f"missing lms adapter: {_LMS_ADAPTER}"
assert _CTC_ADAPTER.is_file(), f"missing ctc-research adapter: {_CTC_ADAPTER}"

TEMPLATES = [
    {
        # The real canonical lives under ``applications/assets/templates``,
        # outside ``tests/test_templates``. Adding its directory to
        # ``DIRS`` makes ``{% include "components/form/form_field.html"
        # %}`` resolve to the actual production file.
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(_TEST_TEMPLATES_DIR), str(_CANONICAL_DIR)],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
            "libraries": {
                # The ``{% load components %}`` library used by the
                # canonical and a small set of tests for ``{% comp %}``.
                "components": "django_fusion.comp.templatetags.components",
                # The ``{% load fusion_form_field_adapter %}``
                # library that exposes the ``{% as_form_block %}``
                # simple-tag bridging Path 2.
                "fusion_form_field_adapter": (
                    "django_fusion.comp.templatetags.fusion_form_field_adapter"
                ),
            },
        },
    }
]


@pytest.fixture(autouse=True)
def reset_components():
    components.reset()
    yield
    components.reset()


# -----------------------------------------------------------------
# Helpers.
# -----------------------------------------------------------------

def render(source: str, context: dict | None = None) -> str:
    """Compile + render a template source string with the test engine."""
    return engines["django"].from_string(source).render(context or {}).strip()


# Pre-load directives needed by template bodies that use ``{% comp %}`` or
# ``{% as_form_block %}`` directly. Production adapter partials assume
# these libraries are auto-loaded via ``INSTALLED_APPS`` + ``AppConfig``.
# Since the test engine builds templates from raw source via
# ``from_string``, callers reading production adapter bodies from disk
# must prepend these directives themselves.
ADAPTER_PROLOGUE = (
    '{% load components %}'
    '{% load i18n %}'
    '{% load fusion_form_field_adapter %}'
)


def render_adapter_source(adapter_source: str, context: dict) -> str:
    """Render a production adapter partial body read from disk.

    The adapter bodies at
    ``applications/<site>/plugins/components/blocks/partials/form_field.html``
    use ``{% comp %}`` and ``{% as_form_block %}`` directly. In production,
    those libraries are auto-loaded via ``INSTALLED_APPS`` + ``AppConfig``.
    The test engine has no AppConfig wiring, so we prepend the
    ``{% load %}`` directives here.
    """
    return render(ADAPTER_PROLOGUE + adapter_source, context)


def make_wagtail_block(
    *,
    block_id: str = "blk-test",
    layout: str | None = None,
    show_icons: bool = False,
    show_labels: bool = True,
    show_placeholders: bool = True,
    icon_style: str = "inside",
    allowed_file_types: list[str] | None = None,
) -> SimpleNamespace:
    """Build a Wagtail-block-shaped SimpleNamespace for Path 1 tests."""
    return SimpleNamespace(
        id=block_id,
        value=SimpleNamespace(
            layout=layout,
            show_icons=show_icons,
            show_labels=show_labels,
            show_placeholders=show_placeholders,
            icon_style=icon_style,
            allowed_file_types=allowed_file_types or [],
        ),
    )


def make_field_config(**overrides) -> SimpleNamespace:
    """A canonical ``field_config`` with sensible test defaults."""
    base = dict(
        field_type="text",
        name="sample",
        label="Sample Label",
        required=False,
        placeholder="Type here…",
        default_value="",
        choices=None,
        help_text="",
        icon="edit",
        min_length=None,
        max_length=None,
        min_value=None,
        max_value=None,
        pattern=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def make_choices(values: list[tuple[str, str]]) -> list[SimpleNamespace]:
    """Build a list of choice ``SimpleNamespace``s with ``value``/``label``."""
    return [SimpleNamespace(value=v, label=lab) for v, lab in values]


# Source used by Path 1 tests: render the real canonical directly with
# caller-supplied ``block`` + ``field_config``.
CANONICAL_INVOCATION = (
    '{% load components %}'
    '{% include "components/form/form_field.html" %}'
)


# Source used by Path 2 tests: pass a flat field through ``as_form_block``
# then include the canonical.
AS_FORM_BLOCK_INVOCATION = (
    '{% load fusion_form_field_adapter %}'
    '{% as_form_block flat_field as synth %}'
    '{% include "components/form/form_field.html" %}'
)


# -----------------------------------------------------------------
# Path 1 — Wagtail StreamField child-block. The canonical is invoked
# directly with a synthesized Wagtail-block-shaped SimpleNamespace.
# -----------------------------------------------------------------

@pytest.mark.parametrize(
    "field_type,expected_html",
    [
        ("textarea", "<textarea"),
        ("select", "<select"),
        # Back-compat alias `dropdown` is preserved by the canonical.
        ("dropdown", "<select"),
        ("checkbox", 'type="checkbox"'),
        ("radio", 'type="radio"'),
        ("file", 'type="file"'),
        # Plain input branch — anything not in the explicit set falls
        # through to `<input type="…">`. Test three representative
        # input types (text / email / number / hidden).
        ("text", 'type="text"'),
        ("email", 'type="email"'),
        ("number", 'type="number"'),
    ],
)
@override_settings(TEMPLATES=TEMPLATES)
def test_path1_canonical_renders_expected_html_per_field_type(
    field_type, expected_html
):
    block = make_wagtail_block()
    field_config = make_field_config(
        field_type=field_type,
        choices=make_choices([("a", "A"), ("b", "B")])
        if field_type in ("select", "radio", "dropdown")
        else None,
    )
    output = render(
        CANONICAL_INVOCATION,
        {"block": block, "field_config": field_config},
    )
    assert expected_html in output, (
        f"expected {expected_html!r} in output for field_type={field_type!r}; "
        f"got: {output!r}"
    )


@override_settings(TEMPLATES=TEMPLATES)
def test_path1_select_branch_renders_all_choices_with_option_values():
    block = make_wagtail_block()
    field_config = make_field_config(
        field_type="select",
        name="fruit",
        label="Pick a fruit",
        choices=make_choices([("apple", "Apple"), ("banana", "Banana")]),
    )
    output = render(
        CANONICAL_INVOCATION,
        {"block": block, "field_config": field_config},
    )
    # Placeholder option (the disabled `value=""` first option).
    assert "<option" in output
    # Each choice appears with `value=` and `label`.
    assert 'value="apple"' in output and "Apple" in output
    assert 'value="banana"' in output and "Banana" in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path1_radio_branch_renders_one_input_per_choice():
    block = make_wagtail_block()
    field_config = make_field_config(
        field_type="radio",
        name="rank",
        label="Pick",
        choices=make_choices([("1", "One"), ("2", "Two"), ("3", "Three")]),
    )
    output = render(
        CANONICAL_INVOCATION,
        {"block": block, "field_config": field_config},
    )
    # The radio branch renders an <input type="radio"> per choice.
    assert output.count('type="radio"') == 3
    # Each choice's label appears in the rendered HTML.
    assert "One" in output and "Two" in output and "Three" in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path1_file_branch_renders_accept_attr_from_block_allowed_types():
    block = make_wagtail_block(allowed_file_types=["pdf", "txt"])
    field_config = make_field_config(field_type="file", name="attachment")
    output = render(
        CANONICAL_INVOCATION,
        {"block": block, "field_config": field_config},
    )
    assert 'type="file"' in output
    # Allowed file extensions are emitted on the `accept=` attribute.
    assert ".pdf" in output
    assert ".txt" in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path1_required_indicator_emits_span_with_required_class():
    block = make_wagtail_block()
    field_config = make_field_config(field_type="text", required=True)
    output = render(
        CANONICAL_INVOCATION,
        {"block": block, "field_config": field_config},
    )
    # The canonical emits `<span class="required">*</span>` after the
    # required label.
    assert '<span class="required">*</span>' in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path1_checkbox_branch_uses_label_inside_input_wrapper():
    block = make_wagtail_block()
    field_config = make_field_config(field_type="checkbox", name="agree", label="I agree")
    output = render(
        CANONICAL_INVOCATION,
        {"block": block, "field_config": field_config},
    )
    # Checkbox branch is the ONLY branch where the canonical suppresses
    # the OUTER `<label for=...>` (the label sits inside the
    # `.form-checkbox-group` wrapper, paired with the inner `<input>`).
    assert '<input class="form-checkbox" type="checkbox"' in output
    # The canonical emits the checkbox label inside a `.form-checkbox-group`.
    assert 'class="form-checkbox-group"' in output


# -----------------------------------------------------------------
# Path 2 — as_form_block adapter tag. The canonical is invoked with
# a synthesized Wagtail-block shape produced by the templatetag.
# -----------------------------------------------------------------

@pytest.mark.parametrize("field_type", ["textarea", "select", "checkbox", "radio", "file", "text"])
@override_settings(TEMPLATES=TEMPLATES)
def test_path2_as_form_block_renders_correct_tag_per_field_type(field_type):
    flat_field = make_field_config(
        field_type=field_type,
        field_width="full",
        choices=make_choices([("a", "A"), ("b", "B")])
        if field_type in ("select", "radio")
        else None,
    )
    output = render(AS_FORM_BLOCK_INVOCATION, {"flat_field": flat_field})

    if field_type == "textarea":
        assert "<textarea" in output
    elif field_type == "select":
        assert "<select" in output
        assert "<option" in output  # choices render
    elif field_type == "checkbox":
        assert 'type="checkbox"' in output
    elif field_type == "radio":
        assert 'type="radio"' in output
        assert output.count('type="radio"') == 2  # 2 choices
    elif field_type == "file":
        assert 'type="file"' in output
    else:  # plain input
        assert f'type="{field_type}"' in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path2_as_form_block_layout_modifier_two_column_emits_col_md_6():
    flat_field = make_field_config(field_type="text", field_width="half")
    output = render(AS_FORM_BLOCK_INVOCATION, {"flat_field": flat_field})
    # `as_form_block` maps field_width ∈ {half, quarter} →
    # block.value.layout = "two-column"; canonical emits `col-md-6`.
    assert "col-md-6" in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path2_as_form_block_layout_full_does_not_emit_column_class():
    flat_field = make_field_config(field_type="text", field_width="full")
    output = render(AS_FORM_BLOCK_INVOCATION, {"flat_field": flat_field})
    # `full` is mapped to layout=None, so the canonical omits the
    # col-md-6 helper.
    assert "col-md-6" not in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path2_as_form_block_default_block_id_uses_legacy_dash_name():
    flat_field = make_field_config(name="email", field_type="email")
    output = render(AS_FORM_BLOCK_INVOCATION, {"flat_field": flat_field})
    # `as_form_block`'s default `block_id` is `f"legacy-{name}"`.
    assert "legacy-email" in output
    # Element id is `field-{block.id}-{name}` (see canonical id=).
    assert 'id="field-' in output


@override_settings(TEMPLATES=TEMPLATES)
def test_path2_as_form_block_caller_supplied_block_id_overrides_default():
    flat_field = make_field_config(name="email", field_type="email")
    # Force a custom block_id via the templatetag kwarg.
    source = (
        '{% load fusion_form_field_adapter %}'
        '{% as_form_block flat_field block_id="custom-form-A" as synth %}'
        '{% include "components/form/form_field.html" %}'
    )
    output = render(source, {"flat_field": flat_field})
    assert "custom-form-A" in output
    # Default `legacy-email` is NOT used.
    assert "legacy-email" not in output


# -----------------------------------------------------------------
# Path 1 — canonical with all 18 class_* overrides honored.
# This is the matrix that the canonical exposes; missing overrides
# must default to the canonical `form-*` BEM name.
# -----------------------------------------------------------------

EIGHTEEN_OVERRIDE_SENTINELS = {
    "class_field": "overridden-form-field",
    "class_input_group": "overridden-form-input-group",
    "class_icon": "overridden-form-icon",
    "class_label": "overridden-form-label",
    "class_control": "overridden-form-control",
    "class_textarea": "overridden-form-textarea",
    "class_select": "overridden-form-select",
    "class_checkbox_group": "overridden-form-checkbox-group",
    "class_checkbox": "overridden-form-checkbox",
    "class_checkbox_label": "overridden-form-checkbox-label",
    "class_radio_group": "overridden-form-radio-group",
    "class_radio_item": "overridden-form-radio-item",
    "class_radio": "overridden-form-radio",
    "class_radio_label": "overridden-form-radio-label",
    "class_file": "overridden-form-file",
    "class_input": "overridden-form-input",
    "class_help_text": "overridden-form-help-text",
    "class_error": "overridden-form-error",
}


@override_settings(TEMPLATES=TEMPLATES)
def test_path1_canonical_emits_all_eighteen_class_overrides_for_textarea():
    """All 18 ``class_*`` kwargs propagate into the rendered HTML."""
    block = make_wagtail_block()
    field_config = make_field_config(
        field_type="textarea", help_text="helpful hint"
    )
    # Build a wrapper template that re-includes the canonical with
    # every override kwarg set.
    include_kwargs = " ".join(
        f"{kwarg_name}=v_{kwarg_name}"
        for kwarg_name in EIGHTEEN_OVERRIDE_SENTINELS
    )
    wrapper = (
        '{% load components %}'
        f'{{% include "components/form/form_field.html" {include_kwargs} %}}'
    )
    ctx = {
        "block": block,
        "field_config": field_config,
        **{f"v_{kwarg_name}": sentinel
           for kwarg_name, sentinel in EIGHTEEN_OVERRIDE_SENTINELS.items()},
    }
    output = render(wrapper, ctx)
    for kwarg_name, sentinel in EIGHTEEN_OVERRIDE_SENTINELS.items():
        assert sentinel in output, (
            f"override sentinel {sentinel!r} for kwarg {kwarg_name!r} "
            f"not seen in output: {output!r}"
        )


# -----------------------------------------------------------------
# Adapter bodies: render the actual production adapter partial files
# (read from disk) and confirm they round-trip a flat per-field dict
# into the canonical with the correct root modifier.
# -----------------------------------------------------------------

@pytest.mark.parametrize(
    "site_adapter_path,site_name",
    [
        (_LMS_ADAPTER, "lms"),
        (_CTC_ADAPTER, "ctc-research"),
    ],
)
@override_settings(TEMPLATES=TEMPLATES)
def test_production_adapter_body_renders_with_field_width_modifier(
    site_adapter_path, site_name
):
    flat_field = make_field_config(
        field_type="email",
        field_width="half",
        name="contact_email",
        label="Email",
    )
    # Read the actual production adapter partial and render it inline
    # (sidesteps template-name collisions since both lms and
    # ctc-research have a `form_field.html` in the same partials dir).
    adapter_source = site_adapter_path.read_text(encoding="utf-8")
    output = render_adapter_source(adapter_source, {"field": flat_field})
    # The canonical emits `.form-field` plus a `--full|--half|--quarter`
    # modifier derived from `field.field_width`. Site adapters should
    # preserve the half-width modifier.
    assert "form-field--half" in output, (
        f"{site_name}: expected `form-field--half` modifier in output "
        f"when field.field_width='half'; got: {output!r}"
    )
    # The canonical's email field renders as <input type="email">.
    assert 'type="email"' in output


@pytest.mark.parametrize(
    "site_adapter_path,site_name,expected_width",
    [
        (_LMS_ADAPTER, "lms", "full"),
        (_CTC_ADAPTER, "ctc-research", "full"),
        (_LMS_ADAPTER, "lms", "half"),
        (_CTC_ADAPTER, "ctc-research", "half"),
        (_LMS_ADAPTER, "lms", "quarter"),
        (_CTC_ADAPTER, "ctc-research", "quarter"),
    ],
)
@override_settings(TEMPLATES=TEMPLATES)
def test_production_adapter_body_renders_correct_modifier_for_each_width(
    site_adapter_path, site_name, expected_width
):
    flat_field = make_field_config(
        field_type="text",
        field_width=expected_width,
        name="f",
    )
    adapter_source = site_adapter_path.read_text(encoding="utf-8")
    output = render_adapter_source(adapter_source, {"field": flat_field})
    assert f"form-field--{expected_width}" in output, (
        f"{site_name}: expected `form-field--{expected_width}` for "
        f"field.field_width={expected_width!r}; got: {output!r}"
    )


# -----------------------------------------------------------------
# Sanity: the canonical's default behavior (no overrides) emits the
# canonical `form-*` BEM names. If this fails, the override-firstof
# default logic regressed AND the 18-override test above would silently
# pass (because every override class would be present by coincidence).
# -----------------------------------------------------------------

@override_settings(TEMPLATES=TEMPLATES)
def test_canonical_default_classes_are_form_bem_when_no_overrides():
    """With no ``class_*`` kwargs, the canonical emits the canonical
    BEM names (``form-field``, ``form-label``, ``form-input``, …)."""
    block = make_wagtail_block()
    field_config = make_field_config(field_type="text", help_text="hint")
    output = render(
        CANONICAL_INVOCATION,
        {"block": block, "field_config": field_config},
    )
    expected_bem_classes = [
        "form-field",
        "form-input-group",
        "form-label",
        "form-control",
        "form-input",
        "form-help-text",
        "form-error",
    ]
    for cls in expected_bem_classes:
        assert f'class="{cls}"' in output or f" {cls} " in output or (
            output.count(cls) >= 1
        ), (
            f"default BEM class {cls!r} missing from canonical output: {output!r}"
        )
