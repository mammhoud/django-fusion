"""django-fusion UI template tags.

Provides reusable inclusion tags for tables, pagination, search, and forms.

Load all at once::

    {% load ui_tags %}

    {% table headers=headers rows=rows hx_target="#list" %}
    {% pagination page_obj=page_obj query_string=query_string %}
    {% search search_query=q hx_target="#list" %}
    {% form form=my_form hx_post="/api/" submit_label="Save" %}

Load individually::

    {% load table from ui_tags %}
    {% load pagination from ui_tags %}
"""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


# ── {% table %} ───────────────────────────────────────────────────────────

@register.inclusion_tag("components/table.html", takes_context=False)
def table(
    headers: list[dict[str, Any]] | None = None,
    rows: list[list[Any]] | None = None,
    table_obj: Any = None,
    hx_target: str = "#table-container",
    table_class: str = "",
    empty_message: str = "",
) -> dict[str, Any]:
    """Render a sortable HTMX table."""
    return {
        "headers": headers or [],
        "rows": rows or [],
        "table": table_obj,
        "hx_target": hx_target,
        "table_class": table_class,
        "empty_message": empty_message,
    }


# ── {% pagination %} ──────────────────────────────────────────────────────

@register.inclusion_tag("components/pagination.html", takes_context=False)
def pagination(
    page_obj: Any = None,
    query_string: str = "",
    hx_target: str = "",
) -> dict[str, Any]:
    """Render Bootstrap 5 pagination with optional HTMX."""
    return {
        "page_obj": page_obj,
        "query_string": query_string,
        "hx_target": hx_target,
    }


# ── {% search %} ──────────────────────────────────────────────────────────

@register.inclusion_tag("components/search.html", takes_context=False)
def search(
    search_query: str = "",
    search_placeholder: str = "",
    hx_target: str = "",
    hx_get: str = "",
    extra_filters: dict[str, str] | None = None,
    max_width: str = "320px",
) -> dict[str, Any]:
    """Render a search input bar with optional HTMX."""
    return {
        "search_query": search_query,
        "search_placeholder": search_placeholder,
        "hx_target": hx_target,
        "hx_get": hx_get,
        "extra_filters": extra_filters or {},
        "max_width": max_width,
    }


# ── {% form %} ────────────────────────────────────────────────────────────

@register.inclusion_tag("components/form.html", takes_context=False)
def form(
    form: Any = None,
    hx_post: str = "",
    hx_url: str = "",
    hx_target: str = "",
    hx_swap: str = "",
    hx_indicator: str = "",
    is_multipart: bool = False,
    form_class: str = "",
    form_id: str = "",
    form_action: str = "",
    form_method: str = "",
    form_extra_attrs: str = "",
    submit_label: str = "",
    submit_attrs: str = "",
    show_cancel: bool = False,
    cancel_label: str = "",
    cancel_onclick: str = "",
    cancel_hx_get: str = "",
    cancel_hx_target: str = "",
    cancel_hx_swap: str = "",
    field_success: str = "",
    success_message: str = "",
) -> dict[str, Any]:
    """Render a unified Django form with HTMX support."""
    return {
        "form": form,
        "hx_post": hx_post,
        "hx_url": hx_url,
        "hx_target": hx_target,
        "hx_swap": hx_swap,
        "hx_indicator": hx_indicator,
        "is_multipart": is_multipart,
        "form_class": form_class,
        "form_id": form_id,
        "form_action": form_action,
        "form_method": form_method,
        "form_extra_attrs": form_extra_attrs,
        "submit_label": submit_label,
        "submit_attrs": submit_attrs,
        "show_cancel": show_cancel,
        "cancel_label": cancel_label,
        "cancel_onclick": cancel_onclick,
        "cancel_hx_get": cancel_hx_get,
        "cancel_hx_target": cancel_hx_target,
        "cancel_hx_swap": cancel_hx_swap,
        "field_success": field_success,
        "success_message": success_message,
    }


__all__ = [
    "form",
    "pagination",
    "search",
    "table",
]
