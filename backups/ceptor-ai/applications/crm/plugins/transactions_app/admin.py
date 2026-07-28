from django.contrib import admin
from .models import Purchase, Sale, SaleDetail


class SaleDetailInline(admin.TabularInline):
    model = SaleDetail
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "grand_total", "date_added")
    inlines = [SaleDetailInline]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("item", "vendor", "quantity", "price", "total_value", "delivery_status")
    list_filter = ("delivery_status",)
