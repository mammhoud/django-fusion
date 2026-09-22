"""
components_field — bakerydemo-style helpers for Wagtail block templates.

Provides ``render_unhandled_fields`` (renders block fields the template did
not explicitly handle) plus the ``get_table_config`` / ``get_table_classes``
filters used by the enhanced-table block template.
"""

from __future__ import annotations

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def render_unhandled_fields(context, unhandled_fields=None):
    """
    Render a small debug block listing block fields the template did not
    handle explicitly. Renders nothing when ``unhandled_fields`` is empty.
    """
    fields = unhandled_fields or []
    if not fields:
        return ""

    rows = "".join(
        format_html(
            "<tr><th>{name}</th><td>{value}</td></tr>",
            name=name,
            value=value,
        )
        for name, value in fields
    )
    return mark_safe(
        '<div class="unhandled-fields"><strong>Unhandled fields</strong>'
        f'<table class="table table-sm">{rows}</table></div>'
    )


def _call_block_method(value, method_name):
    """Call ``method_name`` on a StructValue or its owning block, if present."""
    for target in (value, getattr(value, "block", None)):
        method = getattr(target, method_name, None)
        if callable(method):
            try:
                return method(value)
            except (TypeError, ValueError, KeyError):
                return None
    return None


@register.filter
def get_table_config(value):
    """Return the JS table configuration from the owning table block."""
    return _call_block_method(value, "get_table_config")


@register.filter
def get_table_classes(value):
    """Return the CSS classes from the owning table block."""
    return _call_block_method(value, "get_table_classes")
