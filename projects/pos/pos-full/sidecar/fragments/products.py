"""
POS Full — Product fragments.

Product statistics grouped by category, and per-product detail views.

Fragment names:
- ``pos.products`` — aggregate stats, category breakdown, top sellers
- ``pos.product_detail`` — single product details by PK

Template contexts::

    # ProductListFragment (pos.products)
    {
        "total_products": 150,
        "active_products": 120,
        "by_category": [{"name": "Beverages", "count": 30}, ...],
        "average_price": "12.50",
        "top_selling": [{"name": "...", "sold": 100}, ...],
        "categories": ["Beverages", "Food", ...],
    }

    # ProductDetailFragment (pos.product_detail)
    {
        "product": { ... },  # Serialized product fields
        "in_stock": true,
        "total_sold": 42,
    }
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, Sum

from fragments import FragmentComponent, register


@register
class ProductListFragment(FragmentComponent):
    """Product aggregate stats and category breakdown."""

    fragment_name = "pos.products"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        from models.pos import Product, Category, SaleItem

        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()

        category_counts = list(
            Category.objects.annotate(product_count=Count("products"))
            .order_by("-product_count")
            .values("name", "product_count")
        )

        price_agg = Product.objects.filter(is_active=True).aggregate(
            avg=Sum("price") / Count("id")
        )
        average_price = price_agg["avg"] or Decimal("0.00")

        top_selling = list(
            SaleItem.objects.values("product_name")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:5]
        )

        return {
            "total_products": total_products,
            "active_products": active_products,
            "by_category": [
                {"name": c["name"], "count": c["product_count"]}
                for c in category_counts
            ],
            "average_price": str(average_price),
            "top_selling": [
                {"name": t["product_name"], "sold": t["total_sold"]}
                for t in top_selling
            ],
            "categories": list(Category.objects.filter(is_active=True).values_list("name", flat=True)),
        }


@register
class ProductDetailFragment(FragmentComponent):
    """Single product detail view with sales summary."""

    fragment_name = "pos.product_detail"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        pk = kwargs.get("pk")
        if pk is None:
            return {"product": None, "in_stock": False, "total_sold": 0}
        from models.pos import Product, SaleItem

        try:
            product = Product.objects.get(pk=pk)
        except (Product.DoesNotExist, ValueError):
            return {"product": None, "in_stock": False, "total_sold": 0}

        # Total units sold across all sales
        sold_agg = SaleItem.objects.filter(product=product).aggregate(
            total=Sum("quantity")
        )
        total_sold = sold_agg["total"] or 0

        return {
            "product": {
                "id": product.id,
                "name": product.name,
                "sku": product.sku or "",
                "price": str(product.price),
                "cost_price": str(product.cost_price),
                "tax_rate": product.tax_rate,
                "stock_quantity": product.stock_quantity,
                "low_stock_threshold": product.low_stock_threshold,
                "description": product.description,
                "category_id": product.category_id,
                "is_active": product.is_active,
                "barcode": product.barcode or "",
                "image_url": product.image_url or "",
                "created_at": product.created_at.isoformat() if product.created_at else "",
            },
            "in_stock": product.stock_quantity > 0,
            "total_sold": total_sold,
        }
