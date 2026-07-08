"""
Template tags for routable components.

Usage::

    {% load routable_components %}

    {% site_menu site request.user %}
    {% app_menu app request.user %}
    {% breadcrumbs component %}
    {% component_url component %}
    {% is_active_menu request component as active %}
"""

from __future__ import annotations

from typing import Any

from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# Site menu
# ---------------------------------------------------------------------------

@register.inclusion_tag(
    "components/menu/site_menu.html",
    takes_context=True,
)
def site_menu(context: dict[str, Any], site: Any, user: Any) -> dict[str, Any]:
    """
    Render the full site navigation menu.

    Usage::

        {% site_menu site request.user %}

    Template: ``components/menu/site_menu.html``
    """
    apps = []
    for app in site.menu_items():
        if hasattr(app, "has_view_permission") and not app.has_view_permission(user):
            continue
        apps.append(app)

    return {
        "site": site,
        "apps": apps,
        "user": user,
        "request": context.get("request"),
    }


# ---------------------------------------------------------------------------
# Application menu
# ---------------------------------------------------------------------------

@register.inclusion_tag(
    "components/menu/app_menu.html",
    takes_context=True,
)
def app_menu(context: dict[str, Any], app: Any, user: Any) -> dict[str, Any]:
    """
    Render a single application's navigation menu.

    Usage::

        {% app_menu app request.user %}

    Template: ``components/menu/app_menu.html``
    """
    items = []
    for item in app.menu_items():
        if hasattr(item, "has_view_permission") and not item.has_view_permission(user):
            continue
        items.append(item)

    return {
        "app": app,
        "items": items,
        "user": user,
        "request": context.get("request"),
    }


# ---------------------------------------------------------------------------
# Breadcrumbs
# ---------------------------------------------------------------------------

@register.inclusion_tag("components/breadcrumbs.html")
def breadcrumbs(component: Any) -> dict[str, Any]:
    """
    Render breadcrumb trail for a routable component.

    Usage::

        {% breadcrumbs component %}

    Template: ``components/breadcrumbs.html``
    """
    crumbs = []
    if hasattr(component, "get_breadcrumbs"):
        crumbs = component.get_breadcrumbs()
    return {"breadcrumbs": crumbs}


# ---------------------------------------------------------------------------
# Component URL
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Active menu detection
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Pagination fragment
# ---------------------------------------------------------------------------

@register.inclusion_tag("components/pagination.html")
def fragment_pagination(page_obj: Any, url: str = "") -> dict[str, Any]:
    """
    Render Unpoly + HTMX-aware pagination controls.

    Usage::

        {% fragment_pagination page_obj url=request.path %}

    Template: ``components/pagination.html``
    """
    return {
        "page_obj": page_obj,
        "paginator": getattr(page_obj, "paginator", None),
        "url": url,
    }
