"""
Menu template tags used by the shared header partials.

Classic Wagtail bakerydemo-style tags:

- ``{% get_site_root as site_root %}`` — the root page of the site serving
  the current request.
- ``{% top_menu parent=site_root calling_page=self %}`` — renders the
  live, in-menu children of ``parent`` as ``<li>`` nav items.

These were historically provided by a per-project ``menu_tags`` library;
they are implemented here so the header partials
(``partials/header_links.html``, ``layout/*/header/hyperLinks.html``,
``partials/header/pagesLinks.html``) can ``{% load menu_tags %}``.
"""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context: dict[str, Any]):
    """
    Return the root page of the site for the current request.

    Usage::

        {% load menu_tags %}
        {% get_site_root as site_root %}
    """
    request = context.get("request")
    if request is None:
        return None
    try:
        from wagtail.models import Site

        return Site.find_for_request(request).root_page
    except (AttributeError, Site.DoesNotExist):
        return None


@register.inclusion_tag("partials/header/top_menu.html", takes_context=True)
def top_menu(context: dict[str, Any], parent, calling_page=None) -> dict[str, Any]:
    """
    Render the live, in-menu children of ``parent`` as ``<li>`` nav items.

    Usage::

        {% load menu_tags %}
        {% top_menu parent=site_root calling_page=self %}
    """
    menuitems = []
    if parent is not None:
        try:
            menuitems = parent.get_children().live().in_menu()
        except (AttributeError, TypeError):
            menuitems = []

    return {
        "menuitems": menuitems,
        "calling_page": calling_page
        or context.get("page")
        or context.get("self"),
    }
