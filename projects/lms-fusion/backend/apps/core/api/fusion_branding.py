"""
Fusion LMS — Branding API endpoint.

Provides a ``/api/fusion/branding/`` endpoint that the Next.js frontend
can call to fetch dynamic site branding (site name, company name, creator,
colors) from Wagtail snippet or environment variables.
"""

from __future__ import annotations

import logging
import os

from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)


def fusion_branding(request: HttpRequest):
    """GET /api/fusion/branding/ — return dynamic site branding.

    Tries to read from Wagtail FusionBranding snippet first,
    falls back to environment variables.
    """
    try:
        from apps.pages.branding.context_processors import fusion_branding_context
        ctx = fusion_branding_context(request)
        branding = ctx.get("fusion_branding", {})
        if branding:
            return JsonResponse(branding)
    except Exception:
        logger.debug("Branding context processor unavailable, using env fallback")

    return JsonResponse({
        "site_name": os.environ.get("FUSION_SITE_NAME", "Fusion LMS"),
        "company_name": os.environ.get("FUSION_COMPANY_NAME", "Fusion Inc."),
        "creator_name": os.environ.get("FUSION_CREATOR_NAME", "Fusion Team"),
        "primary_color": os.environ.get("FUSION_PRIMARY_COLOR", "#00a1b3"),
    })


__all__ = ["fusion_branding"]
