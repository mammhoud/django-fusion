"""
Fusion layout template tags.

Provides template tags for the fusion layout system::

    {% load fusion_layout %}

    {% fusion_render_first_flag %}          → <meta> tag for Next.js hydration
    {% fusion_layout "sidebar" %}           → includes a layout template
    {% render_fusion_scripts %}             → frontend bridge scripts
    {% fusion_branding %}                   → inject branding CSS custom properties

These tags work with both server-rendered HTML (``fusion_render_first=True``)
and client-hydrated JSON responses (Next.js data fetching).
"""

from __future__ import annotations

import os
from typing import Any

from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()

LAYOUT_TEMPLATE_MAP = {
    "default": "fusion/layouts/default.html",
    "full": "fusion/layouts/full_width.html",
    "full_width": "fusion/layouts/full_width.html",
    "sidebar": "fusion/layouts/sidebar.html",
    "blank": "fusion/layouts/blank.html",
}


@register.simple_tag(takes_context=True)
def fusion_render_first_flag(context: dict[str, Any]) -> str:
    """Emit a ``<meta>`` tag with the ``fusion_render_first`` preference.

    Used inside ``<head>`` so Next.js ``FusionStore`` can hydrate the
    preference from the server-rendered HTML before any JavaScript runs.

    Output::

        <meta name="fusion-render-first" content="true">
    """
    render_first = _get_render_first(context)
    return format_html(
        '<meta name="fusion-render-first" content="{}">',
        "true" if render_first else "false",
    )


@register.simple_tag(takes_context=True)
def fusion_layout(context: dict[str, Any], layout_name: str = "default") -> str:
    """Render a fusion layout template.

    Includes the specified layout template from ``fusion/layouts/``.
    Falls back to ``default`` if the layout is not found.

    Usage::

        {% fusion_layout "sidebar" %}

    The layout name can also come from the component context::

        {% fusion_layout component.layout %}
    """
    template_path = LAYOUT_TEMPLATE_MAP.get(
        layout_name, LAYOUT_TEMPLATE_MAP["default"]
    )

    try:
        tpl = template.loader.get_template(template_path)
        return tpl.render(context.flatten() if hasattr(context, "flatten") else context)
    except template.TemplateDoesNotExist:
        # Fall back to default
        tpl = template.loader.get_template(LAYOUT_TEMPLATE_MAP["default"])
        return tpl.render(context.flatten() if hasattr(context, "flatten") else context)


@register.simple_tag(takes_context=True)
def render_fusion_scripts(context: dict[str, Any]) -> str:
    """Emit frontend bridge scripts for fusion protocol.

    Creates a ``<script>`` block that initializes the ``window.__FUSION__``
    global object with the current page's fragment pointer, render-first
    preference, and branding data.

    Usage::

        {% render_fusion_scripts %}
    """
    render_first = _get_render_first(context)
    fragment_name = context.get("fragment_name", "")
    component = context.get("component", "")

    branding = context.get("fusion_branding", {})
    site_name = branding.get("site_name", "Fusion")
    primary_color = branding.get("primary_color", "#00a1b3")

    # Build the fusion bridge object
    fusion_data = {
        "renderFirst": render_first,
        "fragmentName": fragment_name,
        "component": str(component),
        "branding": {
            "siteName": site_name,
            "primaryColor": primary_color,
        },
    }

    import json

    # Safely get component name
    if component is not None:
        component_name = getattr(component, "__class__", component)
        component_name = getattr(component_name, "__name__", str(component))
    else:
        component_name = ""

    json_str = json.dumps(fusion_data, default=str)

    return format_html(
        "<script>window.__FUSION__ = {};</script>",
        mark_safe(json_str),
    )


@register.simple_tag(takes_context=True)
def fusion_branding(context: dict[str, Any]) -> str:
    """Emit branding CSS custom properties as a ``<style>`` block.

    Reads ``fusion_branding`` from the template context and injects
    CSS custom properties so the frontend theme matches the backend
    Wagtail-managed branding snippet.

    Usage::

        {% fusion_branding %}
    """
    branding = context.get("fusion_branding", {})
    primary = branding.get("primary_color") or os.environ.get(
        "FUSION_PRIMARY_COLOR", "#00a1b3"
    )
    secondary = branding.get("secondary_color") or os.environ.get(
        "FUSION_SECONDARY_COLOR", "#008080"
    )
    site_name = branding.get("site_name") or os.environ.get(
        "FUSION_SITE_NAME", "Fusion"
    )

    return format_html(
        "<style>:root{{--fusion-primary-color:{primary};"
        "--fusion-secondary-color:{secondary};}}</style>",
        primary=primary,
        secondary=secondary,
    )


@register.simple_tag(takes_context=True)
def fusion_body_data(context: dict[str, Any]) -> str:
    """Emit ``data-fusion-*`` attributes on ``<body>`` for CSS/JS targeting.

    Usage::

        <body class="{% block body_class %}{% endblock %}" {% fusion_body_data %}>
    """
    render_first = _get_render_first(context)
    fragment_name = context.get("fragment_name", "")
    layout = context.get("layout", "default")

    return format_html(
        'data-fusion-render-first="{}"'
        ' data-fusion-fragment="{}"'
        ' data-fusion-layout="{}"',
        "true" if render_first else "false",
        str(fragment_name),
        str(layout),
    )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _get_render_first(context: dict[str, Any]) -> bool:
    """Extract ``fusion_render_first`` from context, session, or component."""
    # 1. Explicit context value
    rf = context.get("fusion_render_first")
    if rf is not None:
        return bool(rf)

    # 2. Component attribute
    component = context.get("component")
    if component is not None and hasattr(component, "get_fusion_render_first"):
        try:
            return component.get_fusion_render_first()
        except Exception:
            pass

    # 3. Request session
    request = context.get("request")
    if request is not None:
        session = getattr(request, "session", {})
        if "fusion_render_first" in session:
            return bool(session["fusion_render_first"])

    # Default: render client-side
    return False
