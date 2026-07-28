from django.contrib import admin
from .models import Category, Delivery, Item


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity", "price", "vendor", "created_at")
    list_filter = ("category", "vendor")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("item", "customer_name", "location", "date", "is_delivered")
    list_filter = ("is_delivered",)
