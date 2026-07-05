"""
📦 Django + Wagtail Template Tags
=================================

Provides utilities for:
- 🌐 Site and page navigation (site roots, menus, breadcrumbs)
- 🧩 Form rendering via ComponentsFormRenderer
- 🔁 Viewset-based URL reversing
- 🎨 Theme variable injection (light/dark)
- 🧭 Wagtail layout utilities

Usage in templates:
-------------------
    {% load core_tags %}
    {% get_site_root as site_root %}
    {% top_menu site_root %}
    {% render_component_form form %}
    {% viewset_url my_viewset 'detail' pk=obj.pk %}
    {% get_theme_variables 'light' %}
"""

import logging

from django import template
from django.http import HttpRequest
from django.template.context import Context
from django.urls import NoReverseMatch


# Viewset belongs to rseal (routing concept) — keep pointing to ceptor_ai
# Lazy import to avoid circular imports during template tag loading
def _get_viewset():
    from django_fusion.comp.routes.base import Viewset
    return Viewset
from wagtail.models import Page, Site

logger = logging.getLogger(__name__)

register = template.Library()

# ---------------------------------------------------------------------
# 🌍 Site & Navigation Tags
# ---------------------------------------------------------------------
@register.simple_tag(takes_context=True)
def get_site_root(context: Context) -> Page | None:
    """
    Get the Wagtail root page for the current request.
    Works with or without Wagtail SiteMiddleware.
    """
    try:
        request = context.get("request")

        if not request:
            return context.get("site_root")

        site = getattr(request, "site", None)
        if not site:
            try:
                site = Site.find_for_request(request)
            except (Site.DoesNotExist, AttributeError):
                pass

        if site and hasattr(site, "root_page"):
            root = site.root_page
            if root and hasattr(root, 'get_translation_or_none'):
                from django.utils import translation
                from wagtail.models import Locale
                current_locale = Locale.objects.get(language_code=translation.get_language())
                translated_root = root.get_translation_or_none(current_locale)
                if translated_root:
                    return translated_root
            return root

        return context.get("site_root")

    except Exception:
        return None


@register.simple_tag
def has_children(page: Page) -> bool:
    """Check if a Wagtail page has live children."""
    return page.get_children().live().exists()


@register.simple_tag
def is_active(page: Page, current_page: Page | None) -> bool:
    """Determine whether a page is active (for menu highlighting)."""
    return current_page.url_path.startswith(page.url_path) if current_page else False

@register.inclusion_tag("landing/partials/navigations.html", takes_context=True)
def top_menu(
    context: Context,
    parent=None,
    calling_page: Page | None = None,
    max_depth: int = 1,
    show_root: bool = False
):
    """
    Render a top navigation menu from Wagtail live children.
    """
    request = context.get("request")

    if not parent:
        try:
            site = Site.find_for_request(request)
            parent = site.root_page if site else None
        except Exception:
            parent = None

    if not parent:
        return {
            "calling_page": calling_page,
            "menuitems": [],
            "request": request,
        }

    if show_root:
        menuitems = [parent]
        children = parent.get_children().live().in_menu()
        menuitems.extend(children)
    else:
        menuitems = parent.get_children().live().in_menu()

    for item in menuitems:
        if calling_page:
            item.active = (
                calling_page.url_path.startswith(item.url_path) or
                calling_page.id == item.id or
                (hasattr(item, 'specific') and
                 calling_page.id == getattr(item.specific, 'id', None))
            )
        else:
            item.active = False

    return {
        "calling_page": calling_page,
        "menuitems": menuitems,
        "request": request,
        "parent_page": parent,
    }

# ---------------------------------------------------------------------
# 🔁 Viewset-Based URL Utilities
# ---------------------------------------------------------------------

@register.simple_tag(takes_context=True)
def viewset_url(context: Context, viewset, view_name: str, *args, **kwargs) -> str:
    """
    Reverse a URL from a registered viewset.

    Usage:
        {% viewset_url viewset 'detail' pk=object.id %}
    """
    if not viewset:
        return ""

    Viewset = _get_viewset()
    if not isinstance(viewset, Viewset):
        raise template.TemplateSyntaxError(
            f"viewset_url: expected Viewset instance, got '{type(viewset)}'"
        )

    try:
        current_app = getattr(context.request, "current_app", None) or \
                      getattr(context.request.resolver_match, "namespace", None)
    except Exception:
        current_app = None

    try:
        return viewset.reverse(view_name, args=args, kwargs=kwargs, current_app=current_app)
    except NoReverseMatch:
        return ""

# ---------------------------------------------------------------------
# 🌐 Request URL Helpers
# ---------------------------------------------------------------------

@register.simple_tag
def absolute_request_url(request: HttpRequest) -> str:
    """Return the absolute URI of the current request."""
    return request.build_absolute_uri()


@register.inclusion_tag("layout/front/includes/breadcrumbs.html", takes_context=True)
def wagtail_breadcrumbs(context: Context):
    """
    Render Wagtail breadcrumbs with a front-end layout template.
    """
    self = context.get("self")
    if not self or self.depth <= 2:
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(self, inclusive=True).filter(depth__gt=1)
    return {
        "ancestors": ancestors,
        "request": context["request"],
    }


@register.filter
def multiply(value, arg):
    """Multiply the value by the arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """Add the arg to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value
