"""Django REST views for the Wagtail-backed product catalog.

Mount: /api/products. Product records are the editor-managed ``Product``
snippet (apps/content/models/products.py) — the catalog-of-record for
language filtering and unified-currency pricing, mirroring the Course
snippet contract. Wagtail product child pages remain the rich product
documents linked from each snippet's ``href``.
"""

from __future__ import annotations

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def _qp(request, key: str, default: str = "") -> str:
    """Get a query parameter safely."""
    return request.GET.get(key, default)


def _qp_int(request, key: str, default: int = 1) -> int:
    try:
        return int(request.GET.get(key, str(default)))
    except (TypeError, ValueError):
        return default


def list_products(request):
    """GET /api/products — published Product snippets with filters + currency.

    Supports ``?language=`` and ``?category=`` filters plus pagination. An
    empty catalog is a valid response while fixtures have not been loaded;
    returning an empty result is safer than fabricating static products or
    masking DB errors.
    """
    try:
        from apps.content.models.products import Product
    except ImportError:
        return JsonResponse({"data": [], "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 1}})

    qs = Product.objects.filter(is_published=True)

    language = _qp(request, "language")
    if language:
        qs = qs.filter(language=language)
    category = _qp(request, "category")
    if category:
        qs = qs.filter(category=category)
    q = _qp(request, "q")
    if q:
        qs = qs.filter(title__icontains=q)

    page_number = max(1, _qp_int(request, "page", 1))
    per_page = max(1, min(100, _qp_int(request, "per_page", 12)))
    total = qs.count()
    products = list(qs.order_by("-is_featured", "title")[(page_number - 1) * per_page : page_number * per_page])

    return JsonResponse({
        "data": [product.as_dict() for product in products],
        "pagination": {
            "page": page_number,
            "per_page": per_page,
            "total": total,
            "total_pages": max(1, (total + per_page - 1) // per_page),
        },
    })
