"""
Template tags for routable components.

Usage::

    {% load routable_components %}

    {% component_url component %}
    {% active_menu component %}
"""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.simple_tag
def component_url(component: Any, *args: Any, **kwargs: Any) -> str:
    """
    Return the URL for a routable component.

    Usage::

        {% component_url component %}
        {% component_url component pk=42 %}
    """
    if hasattr(component, "get_route_url"):
        try:
            return component.get_route_url(*args, **kwargs)
        except Exception:
            return "#"
    return "#"


@register.simple_tag(takes_context=True)
def active_menu(context: dict[str, Any], component: Any) -> str:
    """
    Return ``"active"`` if the current request path matches the component URL.

    Usage::

        <a class="{% active_menu component %}" href="...">...</a>
    """
    request = context.get("request")
    if request is None:
        return ""
    try:
        url = component.get_route_url() if hasattr(component, "get_route_url") else "#"
        if request.path.startswith(url) and url != "#":
            return "active"
    except Exception:
        pass
    return ""
