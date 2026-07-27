"""Context processor that injects Fusion branding settings into
every template context.

Usage::

    TEMPLATES[0]["OPTIONS"]["context_processors"].append(
        "django_fusion.contrib.branding.context_processors.fusion_branding_context"
    )

Then in templates::

    {{ fusion_branding.site_name }}
    {{ fusion_branding.primary_color }}
"""

import os

from django.conf import settings


def fusion_branding_context(request):
    """Return a ``fusion_branding`` dict for template use.

    Reads from the ``FusionBranding`` Wagtail snippet (site-scoped)
    and falls back to Django settings/environment variables.
    """
    try:
        branding = request.site.fusionbranding_set.first()
    except Exception:
        branding = None
    return {
        "fusion_branding": {
            "site_name": getattr(branding, "site_name", None)
            or os.environ.get("FUSION_SITE_NAME", "Fusion"),
            "company_name": getattr(branding, "company_name", None)
            or os.environ.get("FUSION_COMPANY_NAME", "Fusion Inc."),
            "creator_name": getattr(branding, "creator_name", None)
            or os.environ.get("FUSION_CREATOR_NAME", "Fusion Team"),
            "primary_color": getattr(branding, "primary_color", None)
            or os.environ.get("FUSION_PRIMARY_COLOR", "#00a1b3"),
        },
    }
