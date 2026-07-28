"""Invoice Viewset."""
from __future__ import annotations

from django_fusion.comp.routes import ModelViewset


class InvoiceViewset(ModelViewset):
    """Full CRUD for invoices."""

    from plugins.invoice_app.models import Invoice  # noqa: PLC0415

    model = Invoice
    icon = "receipt"
    list_columns = ("customer_name", "item", "grand_total", "date")
    list_search_fields = ("customer_name", "slug")
    list_template_name = "crm/generic/list.html"
    create_template_name = "crm/generic/form.html"
    update_template_name = "crm/generic/form.html"
    detail_template_name = "crm/generic/detail.html"

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated

    def has_add_permission(self, user):
        return user.is_authenticated

    def has_change_permission(self, user, obj=None):
        return user.is_staff

    def has_delete_permission(self, user, obj=None):
        return user.is_superuser
