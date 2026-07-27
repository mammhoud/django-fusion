"""Django REST views for Fusion LMS products API.

Mount: /api/products
"""

from __future__ import annotations

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def _qp_int(request, key: str, default: int = 1) -> int:
    try:
        return int(request.GET.get(key, str(default)))
    except (TypeError, ValueError):
        return default


def list_products(request):
    """GET /api/products — Product listing from models or STATIC_PAGES fallback."""
    try:
        from apps.pages.products.models.cart import Product
        qs = Product.objects.filter(is_active=True).order_by("title")
        page = _qp_int(request, "page", 1)
        per_page = _qp_int(request, "per_page", 12)
        total = qs.count()
        products = qs[(page - 1) * per_page : page * per_page]
        return JsonResponse({
            "data": [
                {
                    "id": p.pk, "title": p.title, "slug": getattr(p, "slug", ""),
                    "description": getattr(p, "description", ""),
                    "price": str(getattr(p, "price", 0)),
                    "image_url": p.image.url if getattr(p, "image", None) else None,
                }
                for p in products
            ],
            "pagination": {
                "page": page, "per_page": per_page, "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
        })
    except Exception:
        # Fall back to STATIC_PAGES products section
        try:
            from apps.pages.pages.content import STATIC_PAGES
            products_page = STATIC_PAGES.get("products", {})
            blocks = products_page.get("blocks", [])
            items = []
            for block in blocks:
                if block.get("type") == "rich_section":
                    for item in block.get("items", []):
                        items.append({
                            "id": hash(item.get("heading", "")),
                            "title": item.get("heading", ""),
                            "description": item.get("text", ""),
                            "slug": item.get("heading", "").lower().replace(" ", "-"),
                        })
            return JsonResponse({
                "data": items,
                "pagination": {"page": 1, "per_page": 24, "total": len(items), "total_pages": 1},
            })
        except Exception:
            return JsonResponse({
                "data": [],
                "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0},
            })
