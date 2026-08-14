"""Landing navigation module for django-fusion routes.

``Landing`` is a reusable ``Module`` that renders a marketing/landing-header
navigation contract (``label`` / ``href`` / ``show_in_nav`` / ``active`` /
``children``) from a declarative ``nav_items`` list, optionally merged with
children derived from a content tree via overridable hooks.

Products subclass ``Landing`` (or instantiate it directly) and set
``nav_items`` / ``nav_children_curated``. They override ``tree_children``,
``child_sort_key``, and ``child_href`` when their content tree needs custom
handling (e.g. Wagtail delivery phases that live at a different public URL
than their tree path).
"""

from __future__ import annotations

import logging
from typing import Any

from django_fusion.routes.core.sites import Module

logger = logging.getLogger(__name__)


class Landing(Module):
    """Marketing-site navigation module.

    Each item in ``nav_items`` is ``(slug, label, show_in_nav)``. Dropdown
    children come from ``nav_children_curated`` (view-backed routes) merged
    with ``tree_children()`` (content-tree-derived routes); ``href`` keys
    dedupe across the two sources.
    """

    title = "Landing"
    app_name = "landing"

    #: Ordered nav entries — ``(slug, display_label, show_in_nav)``.
    nav_items: tuple[tuple[str, str, bool], ...] = ()

    #: Curated dropdown children ``{slug: [{label, href}]}`` merged with the
    #: tree-derived children. ``href`` keys dedupe.
    nav_children_curated: dict[str, list[dict[str, str]]] = {}

    def __init__(
        self,
        *,
        nav_items: Any = None,
        nav_children_curated: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if nav_items is not None:
            self.nav_items = tuple(nav_items)
        if nav_children_curated is not None:
            self.nav_children_curated = dict(nav_children_curated)

    def get_navigation_context(self, request: Any = None) -> list[dict[str, Any]]:
        """Return navigation items for the frontend.

        Each item carries ``label``, ``href``, ``show_in_nav``, ``active`` and
        ``children`` (a list of ``{label, href, active}``). Children are
        derived once from the content tree (``tree_children``) and merged with
        ``nav_children_curated``.
        """
        current_path = getattr(request, "path", "") if request else ""
        tree_children = self.tree_children(current_path)

        items: list[dict[str, Any]] = []
        for slug, label, show_in_nav in self.nav_items:
            href = "/" if slug == "home" else f"/{slug}/"
            items.append(
                {
                    "label": label,
                    "href": href,
                    "show_in_nav": show_in_nav,
                    "active": current_path.rstrip("/") == href.rstrip("/"),
                    "children": self.nav_children(slug, current_path, tree_children),
                }
            )
        return items

    # ── overridable content-tree hooks ─────────────────────────────

    def tree_children(self, current_path: str) -> dict[str, list[dict[str, Any]]]:
        """Map every top-level nav slug to its dropdown children in ONE pass.

        The default has no content-tree coupling. Override to walk the
        product's content tree. Must never raise — return ``{}`` (or a partial
        map) on error so navigation keeps rendering.
        """
        return {}

    def child_sort_key(self, child) -> tuple:
        """Stable sort key for tree-derived children."""
        return (getattr(child, "nav_order", 100), getattr(child, "title", ""))

    def child_href(self, child) -> str:
        """Canonical public href for a tree-derived child."""
        return getattr(child, "url", "")

    # ── shared child merging ───────────────────────────────────────

    def nav_children(
        self,
        slug: str,
        current_path: str,
        tree_children: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """Return the dropdown children for one nav item (``[]`` when none).

        Merges curated entries (view-backed routes) with the tree-derived
        children. ``home`` is always a leaf — its tree children ARE the
        top-level nav pages themselves, not subpages.
        """
        if slug == "home":
            return []

        children: list[dict[str, Any]] = []
        seen: set[str] = set()

        for entry in self.nav_children_curated.get(slug, []):
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


__all__ = ["Landing"]
