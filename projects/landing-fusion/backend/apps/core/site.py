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

import logging
from typing import Any

from django_fusion.routes.core.sites import Site

logger = logging.getLogger(__name__)


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
        # Learning remains directly reachable at /learning/ and available from
        # authenticated profile/dashboard surfaces, but is intentionally not a
        # primary marketing-header destination.
        ("learning", "Learn", False),
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

    # Dropdown children for nav items whose subpages are NOT all real Wagtail
    # children (e.g. About → founder/startup are Astro/view-backed routes, not
    # seeded pages). Merged with tree-derived children; ``href`` keys dedupe.
    NAV_CHILDREN_CURATED: dict[str, list[dict[str, str]]] = {            "about": [
            {"label": "Team", "href": "/about/team/"},
            {"label": "Founder", "href": "/about/founder/"},
            {"label": "Startup", "href": "/about/startup/"},
        ],
    }

    def get_navigation_context(self, request: Any = None) -> list[dict[str, Any]]:
        """Return navigation items for the frontend.

        Each item is a dict with:
        - ``label`` (str): Display label
        - ``href`` (str): URL path
        - ``show_in_nav`` (bool): Whether to show in the main nav bar
        - ``active`` (bool): Whether this is the current page
        - ``children`` (list): Live subpages shown in the hover dropdown
          (``{label, href, active}``) — empty for pages with no subpages.

        Children are derived from the Wagtail tree (live children, hidden
        products excluded) merged with ``NAV_CHILDREN_CURATED`` for routes
        that are not seeded pages. Pages without subpages get ``[]`` so the
        header renders a plain link (no dropdown affordance).
        """
        items: list[dict[str, Any]] = []
        current_path = getattr(request, "path", "") if request else ""
        # One pass over the home subtree → {nav_slug: [child dicts]} so the
        # whole header costs two queries (home + subtree), not one per item.
        tree_children = self._tree_children(current_path)

        for slug, label, show_in_nav in self.NAV_ITEMS:
            href = "/" if slug == "home" else f"/{slug}/"
            items.append(
                {
                    "label": label,
                    "href": href,
                    "show_in_nav": show_in_nav,
                    "active": current_path.rstrip("/") == href.rstrip("/"),
                    "children": self._nav_children(slug, current_path, tree_children),
                }
            )

        return items

    def _tree_children(self, current_path: str) -> dict[str, list[dict[str, Any]]]:
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
                    key=self._child_sort_key,
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
                    child_href = self._child_href(child)
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
    def _child_sort_key(child) -> tuple:
        """Stable sort for dropdown children.

        Delivery phases keep their seeded sequence (Discover → Build → Launch →
        Enhance) via ``phase_number``; everything else sorts by ``nav_order``
        then title.
        """
        from apps.pages.models import PhasePage

        if isinstance(child, PhasePage):
            return (0, getattr(child, "phase_number", 1), child.title)
        return (1, getattr(child, "nav_order", 100), child.title)

    def _nav_children(
        self,
        slug: str,
        current_path: str,
        tree_children: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """Return the dropdown children for one nav item (``[]`` when none).

        Merges curated entries (view-backed routes such as About → founder/
        startup) with the tree-derived children. ``home`` is always a leaf —
        its tree children ARE the top-level nav pages themselves, not subpages.
        """
        if slug == "home":
            return []

        children: list[dict[str, Any]] = []
        seen: set[str] = set()

        for entry in self.NAV_CHILDREN_CURATED.get(slug, []):
            if entry["href"] in seen:
                continue
            seen.add(entry["href"])
            children.append(
                {
                    "label": entry["label"],
                    "href": entry["href"],
                    "active": current_path.rstrip("/") == entry["href"].rstrip("/"),
                }
            )

        for child in tree_children.get(slug, []):
            if child["href"] in seen:
                continue
            seen.add(child["href"])
            children.append(child)

        return children

    @staticmethod
    def _child_href(child) -> str:
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
landing_site = LandingSite()
