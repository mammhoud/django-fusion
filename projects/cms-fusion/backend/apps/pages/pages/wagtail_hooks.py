"""Wagtail hooks for CMS Fusion pages."""

from __future__ import annotations

from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_global_admin_css")
def fusion_admin_css():
    return format_html("""<style>
        .fusion-layout-badge { display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;text-transform:uppercase; }
        .fusion-layout-full_width { background:#d1fae5;color:#065f46; }
        .fusion-layout-sidebar { background:#dbeafe;color:#1e40af; }
        .fusion-layout-blank { background:#f3f4f6;color:#374151; }
        .fusion-layout-default { background:#fef3c7;color:#92400e; }
    </style>""")


@hooks.register("before_serve_page")
def fusion_before_serve(page, request, serve_args, serve_kwargs):
    from apps.pages.pages.models import FusionPage

    if isinstance(page, FusionPage):
        if "fusion_render_first" not in request.session:
            request.session["fusion_render_first"] = page.fusion_render_first
    return None
