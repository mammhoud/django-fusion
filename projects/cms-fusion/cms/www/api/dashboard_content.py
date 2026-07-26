"""
Dashboard Content API — Serves CMS-managed dashboard content blocks.

The dashboard page uses FusionPage to fetch CMS-backed blocks
(welcome messages, tips, quick links, announcements) that content
editors manage through Wagtail admin.
"""

import logging

from www.api.data_adapter import bolt_view

logger = logging.getLogger(__name__)


def _get_cms_dashboard_blocks() -> list[dict]:
    """Fetch dashboard-specific content blocks from Wagtail.

    Returns compiled JSON matching the PageBlock format used by
    the frontend FusionPage decoder. Falls back to sensible defaults
    when no CMS page exists.
    """
    try:
        from wagtail.models import Page
        from www.content.models.pages import (
            page_to_dict,
            ContentPageMixin,
        )

        page = (
            Page.objects.live()
            .filter(slug="dashboard")
            .first()
        )
        if page is not None and hasattr(page.specific, "body"):
            return page_to_dict(page.specific)

    except Exception:
        logger.debug("Wagtail dashboard page not found — using default blocks")

    # Fallback: default dashboard content blocks
    return {
        "slug": "dashboard",
        "title": "Dashboard",
        "seo": {
            "title": "Dashboard",
            "description": "Your learning dashboard",
        },
        "blocks": [
            {
                "type": "dashboard_welcome",
                "heading": "Welcome back!",
                "intro": "Here's your learning progress at a glance.",
            },
        ],
    }


@bolt_view
def dashboard_content(request):
    """GET /apis/dashboard/content/ — Serve CMS-managed dashboard content blocks.

    Returns the same block format as the page_data endpoint so the frontend
    can use FusionDecoder to decode the content.
    """
    from django_fusion.routes import FusionCodec

    page_data = _get_cms_dashboard_blocks()
    encoded = FusionCodec.encode(page_data)

    return {
        "slug": "dashboard",
        "title": page_data.get("title", "Dashboard"),
        "encoded": encoded,
        "language": getattr(request, "LANGUAGE_CODE", "en"),
    }
