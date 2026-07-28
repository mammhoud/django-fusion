from django.contrib import admin
from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("institution_name", "amount", "status", "date")
    list_filter = ("status",)
    search_fields = ("institution_name",)
