"""
Shop — django-fusion fragment components (dual-mode).

Each component owns a storefront fragment and knows how to build both the
template context (``get_fragment_context``) and the JSON data payload
(``get_fragment_data``), so the same endpoint can serve the HTMX HTML
fragment or the fusion-render-first JSON envelope.
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.components.dual_mode import FusionDualModeMixin
from django_fusion.routes.components.fragments import FragmentComponent

from . import services
from .models import Product

__all__ = [
    "ProductGridFragment",
    "CartCountFragment",
    "CartDrawerFragment",
]


class ProductGridFragment(FusionDualModeMixin, FragmentComponent):
    """Product card grid — the menu surface, filterable by category slug."""

    fragment_name = "shop.fragments.product_grid"
    template_name = "shop/fragments/product_grid.html"
    htmx_only = True

    def get_queryset(self):
        qs = Product.objects.filter(
            is_available=True, category__is_active=True
        ).select_related("category")
        slug = self.request.GET.get("category") if getattr(self, "request", None) else None
        if slug:
            qs = qs.filter(category__slug=slug)
        return qs

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        context["products"] = list(self.get_queryset())
        return context

    def get_fragment_data(self) -> dict[str, Any]:
        """JSON payload for the data-mode envelope (Astro build client)."""
        return {
            "products": [
                {
                    "id": p.pk,
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "price": str(p.price),
                    "compare_at_price": str(p.compare_at_price) if p.compare_at_price else None,
                    "image_url": p.image_url,
                    "unit": p.unit,
                    "category": p.category.slug,
                    "tags": p.tags,
                    "is_featured": p.is_featured,
                }
                for p in self.get_queryset()
            ]
        }


class CartCountFragment(FragmentComponent):
    """Cart badge — the item-count chip swapped on every ``cartUpdated`` event."""

    fragment_name = "shop.fragments.cart_count"
    template_name = "shop/fragments/cart_count.html"
    htmx_only = True

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        cart = services.get_or_create_cart(self.request)
        context.update({"cart": cart, "cart_payload": services.cart_payload(cart)})
        return context


class CartDrawerFragment(FragmentComponent):
    """Cart drawer body — items, quantities, totals and the checkout link."""

    fragment_name = "shop.fragments.cart_drawer"
    template_name = "shop/fragments/cart_drawer.html"
    htmx_only = True

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        cart = services.get_or_create_cart(self.request)
        context.update({"cart": cart, "cart_payload": services.cart_payload(cart)})
        return context
