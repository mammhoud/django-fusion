"""Accounts Viewsets for customers, vendors, and staff profiles."""
from __future__ import annotations

from django_fusion.comp.routes import ModelViewset


class CustomerViewset(ModelViewset):
    """Full CRUD for customers."""

    from plugins.accounts_app.models import Customer  # noqa: PLC0415

    model = Customer
    icon = "person"
    list_columns = ("first_name", "last_name", "email", "phone", "loyalty_points")
    list_search_fields = ("first_name", "last_name", "email", "phone")
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


class VendorViewset(ModelViewset):
    """Full CRUD for vendors."""

    from plugins.accounts_app.models import Vendor  # noqa: PLC0415

    model = Vendor
    icon = "storefront"
    list_columns = ("name", "phone_number", "address")
    list_search_fields = ("name",)
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


class StaffProfileViewset(ModelViewset):
    """Staff profile management (admin only for create/delete)."""

    from plugins.accounts_app.models import StaffProfile  # noqa: PLC0415

    model = StaffProfile
    icon = "badge"
    list_columns = ("user", "role", "status", "email")
    list_filter_fields = ("role", "status")
    list_template_name = "crm/generic/list.html"
    create_template_name = "crm/generic/form.html"
    update_template_name = "crm/generic/form.html"
    detail_template_name = "crm/generic/detail.html"

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated

    def has_add_permission(self, user):
        return user.is_staff

    def has_change_permission(self, user, obj=None):
        return user.is_staff

    def has_delete_permission(self, user, obj=None):
        return user.is_superuser
