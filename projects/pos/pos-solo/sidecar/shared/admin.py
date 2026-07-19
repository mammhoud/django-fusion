"""
Shared admin registration for POS Portal models.
Registered in each edition's admin.py.

@tested pos-portal/shared - Admin registration for all editions
"""

from __future__ import annotations

from django.contrib import admin

from .models import Category, Menu, MenuItem, MenuItemAssignment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "display_order", "is_active", "item_count"]
    list_editable = ["display_order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            item_count=models.Count("items")
        )

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "price", "currency", "is_available",
        "is_featured", "preparation_time",
    ]
    list_filter = ["category", "is_available", "is_featured", "currency"]
    list_editable = ["price", "is_available", "is_featured"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description", "ingredients"]
    fieldsets = [
        ("Basic", {"fields": ["category", "name", "slug", "description", "image"]}),
        ("Pricing", {"fields": ["price", "currency"]}),
        ("Availability", {"fields": ["is_available", "is_featured", "display_order"]}),
        ("Kitchen", {"fields": ["preparation_time", "ingredients", "allergens", "calories"]}),
        ("POS Sync", {"fields": ["pos_product_id", "pos_synced_at"], "classes": ["collapse"]}),
    ]


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "valid_from", "valid_until", "item_count"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["items"]
    search_fields = ["name", "description"]

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()


admin.site.register(MenuItemAssignment)
