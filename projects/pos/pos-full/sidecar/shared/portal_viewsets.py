"""
Canonical portal viewsets using django-fusion component system.
Shared across all editions (vresume, solo, minimal, full).

Pulls menu data from database (MenuItem, Category models).
No Wagtail dependencies — pure django-fusion viewsets.

@tested pos-portal/shared - Portal viewsets for all editions
"""

from __future__ import annotations

from django.db.models import Count, Q

from django_fusion.comp.routes import Viewset, route
from .models import Category, MenuItem


class PortalDashboard(Viewset):
    """Portal dashboard showing menu overview and stats from database."""

    @route(path="", methods=["GET"])
    def dashboard(self, request):
        """Render portal dashboard with menu stats from database."""
        total_items = MenuItem.objects.filter(is_available=True).count()
        total_categories = Category.objects.filter(is_active=True).count()
        featured = MenuItem.objects.filter(is_featured=True, is_available=True)

        categories = (
            Category.objects
            .filter(is_active=True)
            .annotate(item_count=Count("items", filter=Q(items__is_available=True)))
            .order_by("display_order")
        )

        recent_items = (
            MenuItem.objects
            .select_related("category")
            .order_by("-created_at")[:5]
        )

        return self.render_template("portal/dashboard.html", {
            "total_items": total_items,
            "total_categories": total_categories,
            "featured_items": featured[:6],
            "categories": categories,
            "recent_items": recent_items,
        })


class PortalMenuItems(Viewset):
    """Menu items listing — grouped by category, fetched from database."""

    @route(path="", methods=["GET"])
    def menu_list(self, request):
        """Render all available menu items grouped by category."""
        items = (
            MenuItem.objects
            .filter(is_available=True)
            .select_related("category")
            .order_by("category__display_order", "display_order")
        )

        grouped = {}
        for item in items:
            cat_name = item.category.name
            if cat_name not in grouped:
                grouped[cat_name] = {
                    "category": item.category,
                    "items": [],
                }
            grouped[cat_name]["items"].append(item)

        return self.render_template("portal/menu_list.html", {
            "grouped_items": grouped,
            "total_count": len(items),
        })


class PortalMenuView(Viewset):
    """Single menu item detail view."""

    @route(path="<slug:slug>/", methods=["GET"])
    def item_detail(self, request, slug):
        """Render a single menu item's details."""
        item = (
            MenuItem.objects
            .select_related("category")
            .filter(slug=slug, is_available=True)
            .first()
        )
        if not item:
            return self.render_template("portal/404.html", status=404)

        related = (
            MenuItem.objects
            .filter(category=item.category, is_available=True)
            .exclude(id=item.id)[:4]
        )

        return self.render_template("portal/menu_item_detail.html", {
            "item": item,
            "related_items": related,
        })
