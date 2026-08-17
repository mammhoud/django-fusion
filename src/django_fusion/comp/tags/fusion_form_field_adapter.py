"""
fusion_form_field_adapter
=========================

Synthesizes a Wagtail-block-shaped context from a flat per-field render
context so legacy plugin templates (lms / precis-ctc form_field
partials) can include the canonical
``applications/assets/templates/components/form/form_field.html``.

Usage inside a duplicate form_field template ::

    {% load fusion_form_field_adapter %}
    {% as_form_block field
       show_icons=show_icons
       show_labels=show_labels
       show_placeholders=show_placeholders
       icon_style=icon_style as synthetic_block %}
    {% include "components/form/form_field.html"
       with block=synthetic_block field_config=field %}

Why this exists
---------------
The canonical form_field dereferences ``block.id`` and
``block.value.{layout, show_icons, icon_style, show_labels,
show_placeholders, allowed_file_types}``. django_fusion was originally
written for Wagtail StreamField child blocks that always carry this
context. The two plugin duplicates predate that convention and pass a
flat ``field`` plus a few top-level flags. This adapter bridges the
two by building a stable, attribute-accessible SimpleNamespace that the
canonical can dereference safely.

Stability / uniqueness
----------------------
``block.id`` is set to a stable ``legacy-`` prefix combined with the
field name so element ids remain deterministic across renders (which
matters for label-for and inline error hydration). Callers that have
a real Wagtail block SHOULD keep using ``form_block.html`` directly and
bypass this adapter.
"""
from types import SimpleNamespace

from django import template

register = template.Library()


def _get(field, key, default=None):
    """Read ``key`` from a dict OR an object, returning ``default`` if absent."""
    if field is None:
        return default
    if isinstance(field, dict):
        return field.get(key, default)
    return getattr(field, key, default)


@register.simple_tag
def as_form_block(
    field,
    show_icons=False,
    show_labels=True,
    show_placeholders=True,
    icon_style="inside",
    block_id="",
):
    """Build a synthetic Wagtail-block shape from a flat per-field context.

    Returns a SimpleNamespace that exposes:

    * ``block.id`` -- stable string for unique element ids
    * ``block.value.layout`` -- 'two-column' for ``field_width`` in
      (``half``, ``quarter``); else ``None``
    * ``block.value.show_icons`` ``show_labels`` ``show_placeholders``
      -- booleans forwarded from caller
    * ``block.value.icon_style`` -- 'inside' default
    * ``block.value.allowed_file_types`` -- empty list (canonical's loop
      is guarded by ``{% if %}``)
    """
    width = _get(field, "field_width", "full") or "full"
    if width in ("half", "quarter"):
        layout = "two-column"
    else:
        layout = None

    name = _get(field, "name", "") or "field"
    if not block_id:
        block_id = f"legacy-{name}"

    return SimpleNamespace(
        id=block_id,
        value=SimpleNamespace(
            layout=layout,
            show_icons=bool(show_icons),
            show_labels=bool(show_labels),
            show_placeholders=bool(show_placeholders),
            icon_style=icon_style or "inside",
            allowed_file_types=[],
        ),
    )
