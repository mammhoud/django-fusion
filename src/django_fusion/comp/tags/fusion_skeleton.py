"""Fusion skeleton template tags.

Provides the ``{% fusion_page_skeleton %}`` tag that embeds a per-page
skeleton manifest as ``window.__FUSION_SKELETON_MANIFEST__``.

Usage::

    {% load fusion_skeleton %}

    {% fusion_page_skeleton template_path="pages/home.html" %}
"""

from __future__ import annotations

import json

from django import template
from django.utils.html import format_html, mark_safe

from django_fusion.fragments.skeleton.resolver import SkeletonResolver

register = template.Library()


@register.simple_tag
def fusion_page_skeleton(template_path: str = "") -> str:
    """Emit the skeleton manifest for *template_path* as a JSON ``<script>`` block.

    The frontend reads ``window.__FUSION_SKELETON_MANIFEST__`` to render
    skeleton placeholders for every ``{% comp %}`` on the page **before**
    real content arrives.

    Args:
        template_path: Django template path, e.g. ``"pages/home.html"``.
            For Wagtail pages, pass ``page.get_template()``.  For static
            templates, use the value of ``TemplateView.template_name``.

    Returns:
        An HTML ``<script>`` element, or an empty string when the skeleton
        system is disabled (``FUSION_ANALYZER['ENABLED']`` is ``False``).

    Example::

        <head>
          {% load fusion_skeleton %}
          {% fusion_page_skeleton template_path="pages/home.html" %}
        </head>
    """
    if not template_path:
        return ""

    resolver = SkeletonResolver()
    entries = resolver.resolve_page_skeleton(template_path)

    if not entries:
        return ""

    payload = resolver.to_json(entries)
    json_str = json.dumps(payload, default=str)
    return format_html(
        "<script>window.__FUSION_SKELETON_MANIFEST__ = {};</script>",
        mark_safe(json_str),
    )
