from django.contrib import admin
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("slug", "customer_name", "item", "grand_total", "date")
    search_fields = ("customer_name", "slug")
