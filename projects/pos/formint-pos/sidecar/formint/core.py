"""
FormintSite — navigation configuration backed by django-fusion's Site class.

Mirrors ``projects/landing-fusion/backend/apps/core/site.py`` so the POS
package has the same dual-source contract: the Site class provides the
navigation context consumed by:

- ``formint.fusion.navigation_api``  → GET /api/v1/navigation/ (JSON)
- ``formint.handlers`` views         → template context for rendered pages

The ``NAV_ITEMS`` list is the single source of truth for the main POS
navigation structure (Home / Data / Admin).
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.core.sites import Site


class FormintSite(Site):
    """Top-level site for the formint-pos package.

    Extends django-fusion's ``Site`` to provide structured navigation context
    consumed by both the Django backend (rendered templates) and the Astro
    frontend (via ``/api/v1/navigation/``).
    """

    title = "Formint POS"
    app_name = "formint_site"

    # ── Navigation ──────────────────────────────────────────────────────────

    # Ordered list of (slug, display_label, href, show_in_nav). The Astro
    # shell renders the main nav from this; admin is footer/sidebar-only.
    NAV_ITEMS: list[tuple[str, str, str, bool]] = [
        ("home", "Home", "/", True),
        ("data", "Data", "/data/", True),
        ("admin", "Admin", "/admin/", True),
    ]

    def get_navigation_context(self, request: Any = None) -> list[dict[str, Any]]:
        """Return navigation items for the frontend.

        Each item is a dict with ``label``, ``href``, ``show_in_nav`` and
        ``active`` (whether it is the current page).
        """
        items: list[dict[str, Any]] = []
        current_path = getattr(request, "path", "") if request else ""

        for slug, label, href, show_in_nav in self.NAV_ITEMS:
            items.append(
                {
                    "label": label,
                    "href": href,
                    "show_in_nav": show_in_nav,
                    "active": current_path.rstrip("/") == href.rstrip("/"),
                }
            )

        return items


# Singleton instance — used by the API and view handlers.
formint_site = FormintSite()
