"""
Fusion page component views — Re-exports from django_fusion.routes.pages
for backward compatibility.

Usage::

    from apps.pages.pages.components import FusionHomePageView, FusionContentPageView

    # Register in Site → Application routing tree
    site.add_view(FusionHomePageView)
"""

from django_fusion.routes.pages import (  # noqa: F401
    FusionContentPageView,
    FusionHomePageView,
    FusionPageView,
)
