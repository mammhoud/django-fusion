"""``{% pagination %}`` — HTMX pagination inclusion tag.

Usage::

    {% load ui_tags %}

    {% pagination page_obj=page_obj query_string=query_string hx_target="#list-container" %}
"""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.inclusion_tag("components/pagination.html", takes_context=False)
def pagination(
    page_obj: Any = None,
    query_string: str = "",
    hx_target: str = "",
) -> dict[str, Any]:
    """Render Bootstrap 5 pagination with optional HTMX and search preservation.

    Args:
        page_obj: A Django ``Page`` object.
        query_string: Pre-computed query string (``request.GET`` sans ``page``)
                      to preserve across page navigation.
        hx_target: HTMX target selector for fragment-based pagination.
    """
    return {
        "page_obj": page_obj,
        "query_string": query_string,
        "hx_target": hx_target,
    }
