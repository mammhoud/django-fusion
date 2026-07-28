"""Bills Viewset."""
from __future__ import annotations

from django_fusion.comp.routes import ModelViewset


class BillViewset(ModelViewset):
    """Full CRUD for bills."""

    from plugins.bills_app.models import Bill  # noqa: PLC0415

    model = Bill
    icon = "payments"
    list_columns = ("institution_name", "amount", "status", "date")
    list_filter_fields = ("status",)
    list_search_fields = ("institution_name", "description")
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
        return user.is_superuser
