from __future__ import annotations

from typing import Any

from django_fusion.comp.templatetags.components import register


def _context(
    *,
    headers: list[Any] | None = None,
    rows: list[Any] | None = None,
    table: Any | None = None,
    hx_target: str = "#table-container",
    table_class: str = "",
    empty_message: str = "",
    resource: str = "",
    count_label: str = "records",
    new_url: str = "",
    new_label: str = "New record",
    form_target: str = "",
    fragment_attr: str = "",
) -> dict[str, Any]:
    """Build the normalized context shared by every table tag."""
    resolved_headers = headers or []
    resolved_rows = rows or []
    values: dict[str, Any] = {
        "headers": resolved_headers,
        "rows": resolved_rows,
        "table": table,
        "table_data": resolved_rows,
        "hx_target": hx_target,
        "table_class": table_class,
        "empty_message": empty_message,
        "resource": resource,
        "count_label": count_label,
        "new_url": new_url,
        "new_label": new_label,
        "form_target": form_target,
        "fragment_attr": fragment_attr,
    }
    # Keep inclusion-tag rendering on the same normalized prop surface as
    # {% comp %}; this avoids repeated fallback lookups in table.html.
    values["props"] = values.copy()
    return values


@register.inclusion_tag("fusion/components/table.html", takes_context=False)
def table(
    headers: list[Any] | None = None,
    rows: list[list[Any]] | None = None,
    *,
    table: Any | None = None,
    hx_target: str = "#table-container",
    table_class: str = "",
    empty_message: str = "",
    resource: str = "",
    count_label: str = "records",
    new_url: str = "",
    new_label: str = "New record",
    form_target: str = "",
    fragment_attr: str = "",
) -> dict[str, Any]:
    """Render a data table inclusion tag.

    Usage::

        {% load components %}
        {% table headers=headers rows=rows hx_target="#list" %}
    """
    return _context(
        headers=headers,
        rows=rows,
        table=table,
        hx_target=hx_target,
        table_class=table_class,
        empty_message=empty_message,
        resource=resource,
        count_label=count_label,
        new_url=new_url,
        new_label=new_label,
        form_target=form_target,
        fragment_attr=fragment_attr,
    )


@register.inclusion_tag("fusion/components/table.html")
def generate_table(columns, rows):
    """Render a legacy dynamic-column table through the canonical component."""
    headers = [
        column if isinstance(column, dict)
        else {"label": str(column), "key": str(column)}
        for column in (columns or [])
    ]
    return _context(headers=headers, rows=rows)


@register.inclusion_tag("fusion/components/table.html")
def generate_table_rows(fields, qs, *args, **kwargs):
    """Render legacy queryset rows through the canonical component."""
    rows = list(qs or [])
    if fields:
        rows = [
            [getattr(row, field, "") for field in fields]
            if not isinstance(row, (list, tuple, dict)) else row
            for row in rows
        ]
    headers = [
        field if isinstance(field, dict)
        else {"label": str(field), "key": str(field)}
        for field in (fields or [])
    ]
    return _context(headers=headers, rows=rows)
