"""Fusion assets template tags.

Provides template tags for dynamic asset injection in Django/Wagtail templates.

Usage::

    {% load fusion_assets %}

    {% fusion_top_assets %}       → CSS links + font preloads in <head>
    {% fusion_bottom_assets %}    → JS scripts before </body>
    {% fusion_assets_manifest %}  → full manifest as JSON <script> block
"""

from __future__ import annotations

from django import template
from django.utils.html import format_html, mark_safe

# Use the canonical _get_assets_config() from the views module to avoid
# code duplication and keep template tags in sync with the API endpoints.
from django_fusion.core.assets.views import _get_assets_config

register = template.Library()


@register.simple_tag
def fusion_top_assets() -> str:
    """Emit CSS links, font preloads, and preconnect hints for ``<head>``.

    Output example::

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="stylesheet" href="/static/css/fusion.css">
        <link rel="stylesheet" href="/static/fonts/remixicon/remixicon.css">
        <style><!-- inline_css --></style>
    """
    config = _get_assets_config()
    top = config.get("top", {})
    parts: list[str] = []

    # Preconnect hints
    for url in top.get("preconnect", []):
        parts.append(format_html(
            '<link rel="preconnect" href="{}" crossorigin>', url
        ))

    # Font stylesheets
    for url in top.get("fonts", []):
        parts.append(format_html(
            '<link rel="stylesheet" href="{}" media="print" onload="this.media=\'all\'">', url
        ))

    # CSS stylesheets
    for url in top.get("css", []):
        parts.append(format_html(
            '<link rel="stylesheet" href="{}">', url
        ))

    # Inline CSS blocks
    for css in top.get("inline_css", []):
        parts.append(format_html("<style>{}</style>", mark_safe(css)))

    return mark_safe("\n".join(parts))


@register.simple_tag
def fusion_bottom_assets() -> str:
    """Emit JS scripts for before ``</body>``.

    Output example::

        <script src="/static/js/fusion-bridge.js" defer></script>
        <script><!-- inline_js --></script>
    """
    config = _get_assets_config()
    bottom = config.get("bottom", {})
    parts: list[str] = []

    # JS scripts
    for url in bottom.get("js", []):
        parts.append(format_html(
            '<script src="{}" defer></script>', url
        ))

    # Inline JS
    for js in bottom.get("inline_js", []):
        parts.append(format_html("<script>{}</script>", mark_safe(js)))

    return mark_safe("\n".join(parts))


@register.simple_tag
def fusion_assets_manifest() -> str:
    """Emit the full assets manifest as a JSON ``<script>`` block.

    The frontend reads ``window.__FUSION_ASSETS__`` to hydrate assets
    dynamically without a second API call.
    """
    import json

    config = _get_assets_config()
    json_str = json.dumps(config, default=str)
    return format_html(
        "<script>window.__FUSION_ASSETS__ = {};</script>",
        mark_safe(json_str),
    )
