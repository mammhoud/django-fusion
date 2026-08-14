"""
LandingFusion navigation — configured django-fusion Landing module.

Provides navigation context consumed by:
- ``apps.pages.api.navigation_api`` → GET /apis/navigation/
- Django page handlers → template context for server-rendered pages

The generic navigation logic lives in ``django_fusion.routes.core.landing.Landing``;
this module supplies the landing-fusion ``nav_items``, curated dropdown
children, and the Wagtail page-tree hooks (delivery phases, hidden products).
"""

from __future__ import annotations

import logging
from typing import Any

from django_fusion.routes.core.landing import Landing

logger = logging.getLogger(__name__)

# ── Navigation ──────────────────────────────────────────────────────────────

# Ordered list of page routes that appear in the main nav.
# Each tuple is (slug, display_label, show_in_nav).
# FAQ + Privacy are intentionally NOT in the main nav — they are linked
# from the footer only (legal/support pages don't belong in the header).
NAV_ITEMS: tuple[tuple[str, str, bool], ...] = (
    ("home", "Home", True),
    ("about", "About", True),
    ("services", "Services", True),
    ("products", "Products", True),
    # Learning remains directly reachable at /learning/ and available from
    # authenticated profile/dashboard surfaces, but is intentionally not a
    # primary marketing-header destination.
    ("learning", "Learn", False),
    ("features", "Benefits", True),        # benefits and switching guide
    ("blog", "Blog", True),
    ("pricing", "Pricing", True),
    ("contact", "Contact", True),
    # Task Center is an authenticated tools route — registered in the
    # navigation contract so every surface can link to it, but not shown
    # in the public marketing header.
    ("tasks", "Tasks", False),
    # Brand, FAQ + Privacy are footer-only (legal/support identity links
    # don't belong in the header).
    ("brand", "Brand", False),
    ("faq", "FAQ", False),                 # footer only
    ("privacy", "Privacy Policy", False),  # footer only
)
# NOTE: Projects is intentionally NOT in the nav — the Projects page was
# merged into Products (/products/ carries the repo project grid and
# /projects/ redirects permanently to /products/).

# Dropdown children for nav items whose subpages are NOT all real Wagtail
# children (e.g. About → founder/startup are Astro/view-backed routes, not
# seeded pages). Merged with tree-derived children; ``href`` keys dedupe.
NAV_CHILDREN_CURATED: dict[str, list[dict[str, str]]] = {
    "about": [
        {"label": "Team", "href": "/about/team/"},
        {"label": "Founder", "href": "/about/founder/"},
        {"label": "Startup", "href": "/about/startup/"},
    ],
}


class LandingModule(Landing):
    """Landing-fusion marketing navigation module (django-fusion Landing)."""

    title = "StructAI Softwares"
    app_name = "landing_module"
    nav_items = NAV_ITEMS
    nav_children_curated = NAV_CHILDREN_CURATED

    def tree_children(self, current_path: str) -> dict[str, list[dict[str, Any]]]:
        """Map every top-level nav slug to its dropdown children in ONE pass.

        Walks the home page's direct children (the top-level pages) once and
        collects each one's live children. Hidden products (ceptor-ai) are
        excluded; delivery phases get their canonical /services/phases/<slug>/
        href. Returns ``{}`` (or a partial map) on error — never raises, so
        navigation keeps rendering.
        """
        result: dict[str, list[dict[str, Any]]] = {}
        try:
            from apps.pages.models import HomePage

            home = HomePage.objects.first()
            if home is None:
                return result
            for top in home.get_children().live().specific():
                # NOTE: sorting happens in Python — ``nav_order`` only exists
                # on specific subclasses, so ordering the generic Page queryset
                # would raise FieldError. ``nav_order`` defaults to 100; phases
                # sort by their seeded ``phase_number``.
                children_pages = sorted(
                    top.get_children().live().specific(),
                    key=self.child_sort_key,
                )
                children: list[dict[str, Any]] = []
                for child in children_pages:
                    # ``hidden`` excludes e.g. ceptor-ai from the Products
                    # dropdown; ``show_on_home=False`` excludes subproducts
                    # (vResume) from the top-level dropdown — both stay
                    # reachable from the /products/ catalog and pricing tabs.
                    # ``show_in_nav`` is NOT consulted (it defaults to False on
                    # ProductPage/BlogPostPage and only governs the top-level
                    # nav, never dropdown children).
                    if getattr(child, "hidden", False):
                        continue
                    if getattr(child, "show_on_home", True) is False:
                        continue
                    child_href = self.child_href(child)
                    children.append(
                        {
                            "label": child.title,
                            "href": child_href,
                            "active": current_path.rstrip("/") == child_href.rstrip("/"),
                        }
                    )
                if children:
                    result[top.slug] = children
        except Exception:
            logger.exception("navigation tree children failed — degrading to curated")
        return result

    @staticmethod
    def child_sort_key(child) -> tuple:
        """Stable sort for dropdown children.

        Delivery phases keep their seeded sequence (Discover → Build → Launch →
        Enhance) via ``phase_number``; everything else sorts by ``nav_order``
        then title.
        """
        from apps.pages.models import PhasePage

        if isinstance(child, PhasePage):
            return (0, getattr(child, "phase_number", 1), child.title)
        return (1, getattr(child, "nav_order", 100), child.title)

    @staticmethod
    def child_href(child) -> str:
        """Canonical public href for a dropdown child page.

        Most children use ``page.url`` (site-root relative). Delivery phases
        live at /services/phases/<slug>/ (handler route) while the Wagtail
        tree keeps them at /services/<slug>/, so their public URL is rebuilt
        to match every other link the site exposes.
        """
        from apps.pages.models import PhasePage

        if isinstance(child, PhasePage):
            return f"/services/phases/{child.slug}/"
        return child.url


# Singleton instance — used by the API and page handlers.
landing_module = LandingModule()
