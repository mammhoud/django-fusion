"""Small, read-only export endpoints shared by the Pro reporting surface."""

from __future__ import annotations

import csv
import json
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse

from formint.models import Customer, InventoryTransaction, Product, Sale


_EXPORTS: dict[str, tuple[type, tuple[str, ...]]] = {
    "products": (Product, ("id", "name", "sku", "price", "tax_rate", "is_active")),
    "sales": (Sale, ("id", "sale_date", "subtotal", "tax_amount", "total", "payment_method", "status")),
    "customers": (Customer, ("id", "first_name", "last_name", "email", "phone", "loyalty_points")),
    "inventory": (InventoryTransaction, ("id", "product_id", "transaction_type", "quantity", "inventory_id", "created_at")),
}


def export_resource(request: HttpRequest, resource: str, file_format: str = "csv") -> HttpResponse:
    """Export a supported Pro resource as CSV or JSON.

    The endpoint is intentionally read-only. Authentication for the legacy
    Robyn API-key surface remains enforced by its middleware; the Django
    reporting surface uses the same session/API gateway as the rest of the
    server-rendered Pro application.
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Exports are read-only."}, status=405)

    # Keep the stable ``/export/<resource>.csv?format=json`` client contract.
    file_format = request.GET.get("format", file_format).lower()
    definition = _EXPORTS.get(resource)
    if definition is None or file_format not in {"csv", "json"}:
        return JsonResponse({"detail": "Unknown export resource or format."}, status=404)

    model, fields = definition
    rows: list[dict[str, Any]] = list(model.objects.values(*fields))
    serialized = [
        {key: value.isoformat() if hasattr(value, "isoformat") else value for key, value in row.items()}
        for row in rows
    ]

    if file_format == "json":
        response = JsonResponse({"resource": resource, "count": len(serialized), "items": serialized})
        response["Content-Disposition"] = f'attachment; filename="{resource}.json"'
        return response

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{resource}.csv"'
    writer = csv.DictWriter(response, fieldnames=fields)
    writer.writeheader()
    writer.writerows(serialized)
    return response
