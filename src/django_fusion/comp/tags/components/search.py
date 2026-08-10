"""``{% search %}`` — search bar inclusion tag.

Usage::

    {% load components %}

    {% search search_query=search_query hx_target="#list-container" %}
"""

from __future__ import annotations

from typing import Any

from django_fusion.comp.tags.components import register


@register.inclusion_tag("fusion/components/search.html", takes_context=False)
def search(
    search_query: str = "",
    search_placeholder: str = "",
    hx_target: str = "",
    hx_get: str = "",
    extra_filters: dict[str, str] | None = None,
    max_width: str = "320px",
) -> dict[str, Any]:
    """Render a search input bar with optional HTMX fragment submission.

    Args:
        search_query: Current search term value.
        search_placeholder: Placeholder text override.
        hx_target: HTMX target for fragment-based search.
        hx_get: Override HTMX GET URL (defaults to ``request.path``).
        extra_filters: Additional filter name→value pairs to preserve as
                       hidden inputs.
        max_width: CSS max-width on the search input group.
    """
    return {
        "search_query": search_query,
        "search_placeholder": search_placeholder,
        "hx_target": hx_target,
        "hx_get": hx_get,
        "extra_filters": extra_filters or {},
        "max_width": max_width,
    }
