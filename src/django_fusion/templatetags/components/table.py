"""``{% table %}`` — unified table component inclusion tag.

Usage::

    {% load ui_tags %}

    {% table headers=headers rows=rows hx_target="#list-container" %}
    {% table table=table %}
"""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.inclusion_tag("components/table.html", takes_context=False)
def table(
    headers: list[dict[str, Any]] | None = None,
    rows: list[list[Any]] | None = None,
    table: Any = None,
    hx_target: str = "#table-container",
    table_class: str = "",
    empty_message: str = "",
) -> dict[str, Any]:
    """Render a sortable HTMX table.

    Accepts either ``headers``/``rows`` (explicit mode) or a
    ``django_tables2.Table`` object in ``table``.

    Args:
        headers: List of column dicts with ``label``, optional ``sort_url``,
                 ``is_sorted``, ``direction``.
        rows: List of row lists (each cell rendered as safe HTML).
        table: A ``django_tables2.Table`` object (alternative to headers/rows).
        hx_target: HTMX target for sort link clicks.
        table_class: Extra CSS classes on the ``<table>`` element.
        empty_message: Message shown when ``rows`` is empty.
    """
    return {
        "headers": headers or [],
        "rows": rows or [],
        "table": table,
        "hx_target": hx_target,
        "table_class": table_class,
        "empty_message": empty_message,
    }
