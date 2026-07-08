"""
Navigation template tags for django-fusion.

Provides ``{% nav_link %}`` and ``{% nav_panel %}`` template tags that
generate the correct attributes for **Unpoly** (``up-follow`` / ``up-target``)
with an automatic **HTMX** (``hx-get`` / ``hx-target``) fallback.

Template tag usage::

    {% load components %}

    {% nav_link url="..." label="..." icon="..." target="#panel-content" %}
    {% nav_panel links=nav_items target="#panel-content" %}

The nav_link tag renders an ``<a>`` element with:
  - Unpoly: ``up-follow``, ``up-target``, ``up-layer`` (optional)
  - HTMX:   ``hx-get``, ``hx-target``, ``hx-trigger``
  - Both:   ``href`` (static fallback)

Set ``UNPOLY_ENABLED = False`` in Django settings to disable Unpoly output
and use only HTMX attributes.
"""

from __future__ import annotations

from typing import Any

from django import template
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unpoly_enabled() -> bool:
    """Return True when Unpoly is the primary navigation engine."""
    return getattr(settings, "UNPOLY_ENABLED", True)


def _resolve_url(url_or_name: str, *args: Any, **kwargs: Any) -> str:
    """Resolve a URL name via reverse() or return the literal URL."""
    if url_or_name.startswith("/") or url_or_name.startswith("http"):
        return url_or_name
    try:
        return reverse(url_or_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return url_or_name


def _build_attrs(
    url: str,
    target: str = "#panel-content",
    layer: str | None = None,
    extra_classes: str = "",
    **extra: Any,
) -> dict[str, str]:
    """Build HTML attributes dict with Unpoly-first + HTMX fallback."""
    attrs: dict[str, str] = {
        "href": url,
        "class": extra_classes.strip() or "nav-link",
    }

    if _unpoly_enabled():
        # Unpoly — primary navigation engine
        attrs["up-follow"] = ""
        attrs["up-target"] = target
        if layer:
            attrs["up-layer"] = layer
    else:
        # HTMX — fallback
        attrs["hx-get"] = url
        attrs["hx-target"] = target
        attrs["hx-trigger"] = "click"

    return attrs


def _render_attrs(attrs: dict[str, str]) -> str:
    """Render a dict of HTML attributes to a string."""
    parts = []
    for key, value in attrs.items():
        if value == "":
            parts.append(key)
        else:
            parts.append(f'{key}="{value}"')
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Inclusion tags
# ---------------------------------------------------------------------------


@register.inclusion_tag("components/navigation/nav_link.html", takes_context=True)
def nav_link(
    context: dict[str, Any],
    url: str = "",
    label: str = "",
    icon: str = "",
    target: str = "#panel-content",
    layer: str | None = None,
    css_class: str = "",
    *,
    request: Any = None,
) -> dict[str, Any]:
    """
    Render a single navigation link.

    Usage::

        {% nav_link url="plugins:profile:dashboard" label="Dashboard" icon="home" %}

    Or with explicit attributes::

        {% nav_link url="/blog/" label="Blog" target="#main-content" layer="modal" %}
    """
    resolved_url = _resolve_url(url)
    link_attrs = _build_attrs(resolved_url, target=target, layer=layer, extra_classes=css_class)

    is_active = False
    if request or context.get("request"):
        req = request or context["request"]
        current_path = req.path
        is_active = (
            current_path == resolved_url
            or (url and current_path.startswith(resolved_url) and resolved_url != "/")
        )

    return {
        "url": resolved_url,
        "label": label,
        "icon": icon,
        "attrs": mark_safe(_render_attrs(link_attrs)),
        "is_active": is_active,
        "target": target,
        "layer": layer,
        "unpoly_enabled": _unpoly_enabled(),
    }


@register.inclusion_tag("components/navigation/nav_panel.html", takes_context=True)
def nav_panel(
    context: dict[str, Any],
    links: list[dict[str, Any]] | None = None,
    target: str = "#panel-content",
    title: str = "",
    css_class: str = "card",
    *,
    request: Any = None,
) -> dict[str, Any]:
    """
    Render a vertical navigation panel with multiple links.

    Each link dict supports::

        {"url": "...", "label": "...", "icon": "...", "layer": "modal"}

    Usage::

        {% nav_panel links=nav_items title="Profile" %}
    """
    resolved_links = []
    for link in links or []:
        resolved_url = _resolve_url(link.get("url", ""))
        link_attrs = _build_attrs(
            resolved_url,
            target=link.get("target", target),
            layer=link.get("layer"),
            extra_classes=link.get("css_class", ""),
        )

        req = request or context.get("request")
        is_active = False
        if req:
            is_active = req.path == resolved_url

        resolved_links.append({
            "url": resolved_url,
            "label": link.get("label", ""),
            "icon": link.get("icon", ""),
            "attrs": mark_safe(_render_attrs(link_attrs)),
            "is_active": is_active,
            "target": link.get("target", target),
            "layer": link.get("layer"),
        })

    return {
        "links": resolved_links,
        "title": title,
        "css_class": css_class,
        "unpoly_enabled": _unpoly_enabled(),
    }
