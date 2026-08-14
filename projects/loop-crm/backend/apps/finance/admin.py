from django.contrib import admin

from .models import Invoice, Payment, RevenueEvent


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "company", "total", "status", "due_on", "workspace")
    list_filter = ("workspace", "status", "currency")
    search_fields = ("number", "company__name", "deal__name")
    readonly_fields = ("total", "created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "paid_on", "method", "workspace")
    list_filter = ("workspace", "method", "paid_on")
    search_fields = ("invoice__number", "reference")


@admin.register(RevenueEvent)
class RevenueEventAdmin(admin.ModelAdmin):
    list_display = ("deal", "campaign", "kind", "amount", "recognized_on", "workspace")
    list_filter = ("workspace", "kind", "recognized_on")
    search_fields = ("deal__name", "campaign__name")
    readonly_fields = [field.name for field in RevenueEvent._meta.fields]
