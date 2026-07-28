"""Transaction Viewsets — Sales and Purchases."""
from __future__ import annotations

from django_fusion.comp.routes import ModelViewset, ReadonlyModelViewset


class SaleViewset(ReadonlyModelViewset):
    """Read-only list + detail for sales."""

    from plugins.transactions_app.models import Sale  # noqa: PLC0415

    model = Sale
    icon = "point_of_sale"
    list_columns = ("customer", "grand_total", "amount_paid", "date_added")
    list_filter_fields = ("customer",)
    list_template_name = "crm/generic/list.html"
    detail_template_name = "crm/generic/detail.html"

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated


class PurchaseViewset(ModelViewset):
    """Full CRUD for purchase orders."""

    from plugins.transactions_app.models import Purchase  # noqa: PLC0415

    model = Purchase
    icon = "shopping_cart"
    list_columns = ("item", "vendor", "quantity", "price", "total_value", "delivery_status")
    list_filter_fields = ("delivery_status",)
    list_search_fields = ("item__name", "vendor__name")
    list_template_name = "crm/generic/list.html"
    create_template_name = "crm/generic/form.html"
    update_template_name = "crm/generic/form.html"
    detail_template_name = "crm/generic/detail.html"

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated

    def has_add_permission(self, user):
        return user.is_authenticated

    def has_change_permission(self, user, obj=None):
        return user.is_authenticated

    def has_delete_permission(self, user, obj=None):
        return user.is_staff
