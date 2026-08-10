"""``{% pagination %}`` — HTMX pagination inclusion tag.

Usage::

    {% load components %}

    {% pagination page_obj=page_obj query_string=query_string hx_target="#list-container" %}
"""

from __future__ import annotations

from typing import Any

from django_fusion.comp.tags.components import register


@register.inclusion_tag("fusion/components/pagination/pagination.html", takes_context=False)
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


@register.inclusion_tag("fusion/components/pagination/pagination.html")
def fragment_pagination(page_obj: Any, url: str = "") -> dict[str, Any]:
    """
    Render Unpoly + HTMX-aware pagination controls.

    Usage::

        {% fragment_pagination page_obj url=request.path %}

    Template: ``fusion/components/pagination/pagination.html``
    """
    return {
        "page_obj": page_obj,
        "paginator": getattr(page_obj, "paginator", None),
        "url": url,
    }
