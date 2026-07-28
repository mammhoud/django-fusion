"""Transaction Components — Sale creation and list fragment."""
from __future__ import annotations

import json
import logging

from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse

from django_fusion.comp.routes import FragmentComponent, RoutableComponent
from django_fusion.site.interface._context_mixins import is_htmx_request

logger = logging.getLogger(__name__)


class SaleCreateComponent(RoutableComponent):
    """
    POS-style sale creation page with Alpine.js cart + HTMX submission.

    URL: /crm/transactions/transactions/new-sale/
    Template: crm/transactions/sale_create.html
    POST: accepts JSON body with cart data → creates Sale + SaleDetails atomically.
    """

    route_name = "sale-create"
    route_path = "new-sale/"
    title = "New Sale"
    page_title = "Create Sale"
    icon = "add_shopping_cart"
    template_name = "crm/transactions/sale_create.html"

    def has_permission(self, user):
        return user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from plugins.accounts_app.models import Customer
        context["customers"] = [c.to_select2() for c in Customer.objects.all()]
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON."}, status=400)

        try:
            return self._create_sale(data)
        except Exception as exc:
            logger.error("Sale creation failed: %s", exc)
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    def _create_sale(self, data: dict) -> JsonResponse:
        from plugins.accounts_app.models import Customer
        from plugins.inventory.models import Item
        from plugins.transactions_app.models import Sale, SaleDetail

        required = ["customer", "sub_total", "grand_total", "amount_paid", "amount_change", "items"]
        for field in required:
            if field not in data:
                return JsonResponse({"status": "error", "message": f"Missing field: {field}"}, status=400)

        with transaction.atomic():
            sale = Sale.objects.create(
                customer=Customer.objects.get(id=data["customer"]),
                sub_total=float(data["sub_total"]),
                grand_total=float(data["grand_total"]),
                tax_amount=float(data.get("tax_amount", 0)),
                tax_percentage=float(data.get("tax_percentage", 0)),
                amount_paid=float(data["amount_paid"]),
                amount_change=float(data["amount_change"]),
            )
            for line in data["items"]:
                item = Item.objects.select_for_update().get(id=line["id"])
                qty = int(line["quantity"])
                if item.quantity < qty:
                    raise ValueError(f"Insufficient stock for '{item.name}'")
                SaleDetail.objects.create(
                    sale=sale,
                    item=item,
                    price=float(line["price"]),
                    quantity=qty,
                    total_detail=float(line["total_item"]),
                )
                item.quantity -= qty
                item.save(update_fields=["quantity", "updated_at"])

        return JsonResponse({
            "status": "success",
            "message": "Sale created successfully.",
            "redirect": "/crm/",
        })


class SaleListFragment(FragmentComponent):
    """
    HTMX-only sales list fragment.

    URL: /crm/transactions/transactions/sales/list-fragment/
    Template: crm/fragments/sale_list.html
    """

    route_name = "sale-list-fragment"
    route_path = "sales/list-fragment/"
    fragment_name = "crm.fragments.sale_list"
    htmx_only = True
    paginate_by = 20
    show_in_menu = False

    def has_permission(self, user):
        return user.is_authenticated

    def get_queryset(self):
        from plugins.transactions_app.models import Sale
        return Sale.objects.select_related("customer").order_by("-date_added")

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context
