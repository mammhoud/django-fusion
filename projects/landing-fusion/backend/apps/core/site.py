"""
LandingFusion Site — navigation configuration backed by django-fusion's Site class.

Provides navigation context consumed by:
- ``apps.pages.api.navigation_api`` → GET /apis/navigation/
- Django page handlers → template context for server-rendered pages

The Site class inherits from ``django_fusion.routes.core.sites.Site`` so it plugs
into the django-fusion routing and menu system. The ``NAV_ITEMS`` list is the single
source of truth for the main navigation structure.
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.core.sites import Site


class LandingSite(Site):
    """Top-level site for the landing-fusion project.

    Extends django-fusion's Site to provide structured navigation context
    consumed by both the Django backend (template rendering) and the Astro
    frontend (via /apis/navigation/).
    """

    title = "StructAI Softwares"
    app_name = "landing_site"

    # ── Navigation ──────────────────────────────────────────────────────────

    # Ordered list of page routes that appear in the main nav.
    # Each tuple is (slug, display_label, show_in_nav).
    # FAQ + Privacy are intentionally NOT in the main nav — they are linked
    # from the footer only (legal/support pages don't belong in the header).
    NAV_ITEMS: list[tuple[str, str, bool]] = [
        ("home", "Home", True),
        ("about", "About", True),
        ("services", "Services", True),
        ("products", "Products", True),
        ("features", "Features", False),       # linked from /products
        ("blog", "Blog", True),
        ("pricing", "Pricing", True),
        ("contact", "Contact", True),
        # Brand, FAQ + Privacy are footer-only (legal/support identity links
        # don't belong in the header).
        ("brand", "Brand", False),
        ("faq", "FAQ", False),                 # footer only
        ("privacy", "Privacy Policy", False),  # footer only
    ]
    # NOTE: Projects is intentionally NOT in the nav — the Projects page was
    # merged into Products (/products/ carries the repo project grid and
    # /projects/ redirects permanently to /products/).

    def get_navigation_context(self, request: Any = None) -> list[dict[str, Any]]:
        """Return navigation items for the frontend.

        Each item is a dict with:
        - ``label`` (str): Display label
        - ``href`` (str): URL path
        - ``show_in_nav`` (bool): Whether to show in the main nav bar
        - ``active`` (bool): Whether this is the current page
        """
        items: list[dict[str, Any]] = []
        current_path = getattr(request, "path", "") if request else ""

        for slug, label, show_in_nav in self.NAV_ITEMS:
            href = "/" if slug == "home" else f"/{slug}/"
            items.append(
                {
                    "label": label,
                    "href": href,
                    "show_in_nav": show_in_nav,
                    "active": current_path.rstrip("/") == href.rstrip("/"),
                }
            )

        return items


# Singleton instance — used by the API and page handlers.
landing_site = LandingSite()
