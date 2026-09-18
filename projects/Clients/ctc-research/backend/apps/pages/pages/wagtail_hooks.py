"""
Wagtail hooks for FusionPage models.

Registers custom page types in the Wagtail admin and provides admin
customization for the fusion layout system.

Usage: Add ``"apps.pages.pages.wagtail_hooks"`` to your ``INSTALLED_APPS``
or ensure ``apps.pages.pages`` is loaded via ``AppConfig.ready()``.
"""

from __future__ import annotations

from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_global_admin_css")
def admin_css():
    """Inject fusion admin CSS for page layout previews in the Wagtail admin."""
    return format_html(
        """<style>
        /* Fusion layout badge in page listing */
        .fusion-layout-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .fusion-layout-full_width {{ background: #d1fae5; color: #065f46; }}
        .fusion-layout-sidebar {{ background: #dbeafe; color: #1e40af; }}
        .fusion-layout-blank {{ background: #f3f4f6; color: #374151; }}
        .fusion-layout-default {{ background: #fef3c7; color: #92400e; }}

        /* Render-first indicator */
        .fusion-render-first-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 4px;
        }}
        .fusion-render-first-on {{ background: #10b981; }}
        .fusion-render-first-off {{ background: #9ca3af; }}
    </style>"""
    )


@hooks.register("before_serve_page")
def before_serve(page, request, serve_args, serve_kwargs):
    """Inject fusion_context before serving any FusionPage.

    Ensures that ``fusion_branding`` and ``fusion_render_first`` are always
    available in the template context when serving a FusionPage.

    Gracefully degrades on non-default locale pages where FusionPage
    may not be available (e.g., Wagtail i18n /fr/ routes).
    """
    try:
        from apps.pages.pages.models import FusionPage

        if isinstance(page, FusionPage):
            # Ensure session has fusion_render_first set
            if "fusion_render_first" not in request.session:
                request.session["fusion_render_first"] = page.fusion_render_first
    except Exception:
        # Gracefully degrade for non-FusionPage types or locale variants
        # that may not have PageSubscription.route available.
        pass

    # ── SEO context for the Django render road ────────────────────────
    # Populates ``seo_context`` in the template context so base.html can
    # render meta description/keywords/OG/Twitter/canonical tags from
    # SiteSettings (Wagtail-managed) instead of hardcoded strings.
    try:
        from apps.content.models.settings import SiteSettings

        settings_obj = SiteSettings.for_request(request)
        if settings_obj is None:
            settings_obj = SiteSettings.load()
        seo_context = settings_obj.get_seo_context() if settings_obj else {}
    except Exception:
        seo_context = {}
    request.seo_context = seo_context

    return None  # Don't modify the response — just setting up context
