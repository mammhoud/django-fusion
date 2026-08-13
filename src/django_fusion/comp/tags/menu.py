"""
Menu template tags for django-fusion.

Usage::

    {% load menu %}

    {% site_menu site request.user %}
    {% app_menu app request.user %}
    {% if submenu|filter_by_url:request %}...{% endif %}
"""

from __future__ import annotations

from typing import Any

from django import template
from django.urls import NoReverseMatch

from django_fusion.comp.tags.navigation import _resolve_url

register = template.Library()


@register.filter
def filter_by_url(submenu, url):
    """
    Recursively filters a submenu structure to determine if the URL matches any item's URL.

    Usage:
        {% if submenu|filter_by_url:request %}
    """
    if submenu:
        for subitem in submenu:
            subitem_url = subitem.get("url")
            if subitem_url in [url.path, url.resolver_match.url_name]:
                return True
            if subitem.get("submenu") and filter_by_url(subitem["submenu"], url):
                return True
    return False


@register.inclusion_tag(
    "fusion/menu/site_menu.html",
    takes_context=True,
)
def site_menu(context: dict[str, Any], site: Any, user: Any) -> dict[str, Any]:
    """
    Render the full site navigation menu.

    Usage::

        {% site_menu site request.user %}

    Template: ``fusion/menu/site_menu.html``
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


@register.inclusion_tag(
    "fusion/menu/app_menu.html",
    takes_context=True,
)
def app_menu(context: dict[str, Any], app: Any, user: Any) -> dict[str, Any]:
    """
    Render a single application's navigation menu.

    Usage::

        {% app_menu app request.user %}

    Template: ``fusion/menu/app_menu.html``
    """
    items = []
    for item in app.menu_items():
        if hasattr(item, "has_view_permission") and not item.has_view_permission(user):
            continue
        if isinstance(item, dict) and item.get("is_url_pattern"):
            # ``menu_path`` stores the route metadata on the URLPattern. Resolve
            # the named route through the owning Application so menu links are
            # real links instead of the old ``href="#"`` placeholder.
            item = dict(item)
            name = item.get("name")
            try:
                item["url"] = app.reverse(name) if name else "#"
            except (NoReverseMatch, AttributeError, ValueError):
                item["url"] = _resolve_url(name or "#")
        items.append(item)

    return {
        "app": app,
        "items": items,
        "user": user,
        "request": context.get("request"),
    }
