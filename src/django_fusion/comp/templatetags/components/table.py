from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.inclusion_tag("components/table.html", takes_context=False)
def table(
    headers: list[Any] | None = None,
    rows: list[list[Any]] | None = None,
    *,
    table: Any | None = None,
    hx_target: str = "#table-container",
    table_class: str = "",
    empty_message: str = "",
) -> dict[str, Any]:
    """Render a data table inclusion tag.

    Usage::

        {% load ui_tags %}
        {% table headers=headers rows=rows hx_target="#list" %}
    """
    return {
        "headers": headers or [],
        "rows": rows or [],
        "hx_target": hx_target,
        "table": table,
        "table_class": table_class,
        "empty_message": empty_message,
    }


@register.inclusion_tag("components/table.html")
def generate_table(columns, rows):
    """
    Template tag to generate a table with dynamic columns and rows.

    Usage:
        {% generate_table columns=columns rows=rows %}
    """
    return {"columns": columns, "rows": rows}


@register.inclusion_tag("table.html")
def generate_table_rows(fields, qs, *args, **kwargs):
    """
    Template tag to generate table rows based on the provided fields and queryset.

    Usage:
        {% generate_table_rows fields qs %}
    """
    context = {"fields": fields, "qs": qs}
    return context
