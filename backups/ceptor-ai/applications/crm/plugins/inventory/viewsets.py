"""
Inventory Viewsets
==================
ModelViewsets for Item, Category, and Delivery — registered in
www/projects/routes.py → InventoryApp.
"""
from __future__ import annotations

from django_fusion.comp.routes import ModelViewset


class ItemViewset(ModelViewset):
    """Full CRUD for inventory items."""

    from plugins.inventory.models import Item  # noqa: PLC0415

    model = Item
    icon = "inventory_2"
    list_columns = ("name", "category", "quantity", "price", "vendor")
    list_filter_fields = ("category",)
    list_search_fields = ("name", "description")
    # Templates
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


class CategoryViewset(ModelViewset):
    """Full CRUD for item categories."""

    from plugins.inventory.models import Category  # noqa: PLC0415

    model = Category
    icon = "category"
    list_columns = ("name",)
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


class DeliveryViewset(ModelViewset):
    """Full CRUD for deliveries."""

    from plugins.inventory.models import Delivery  # noqa: PLC0415

    model = Delivery
    icon = "local_shipping"
    list_columns = ("item", "customer_name", "location", "date", "is_delivered")
    list_filter_fields = ("is_delivered",)
    list_search_fields = ("customer_name", "location")
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
