from django.contrib import admin

from apps.billing.models import BillingAccount, Plan, Seat


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "period", "price_cents", "seat_limit", "is_active")
    list_filter = ("period", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BillingAccount)
class BillingAccountAdmin(admin.ModelAdmin):
    list_display = ("workspace", "plan", "status", "stripe_subscription_id", "trial_ends_at")
    list_filter = ("status", "plan")
    search_fields = ("workspace__name", "stripe_customer_id", "stripe_subscription_id")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("workspace", "user", "created_at")
    list_filter = ("workspace",)
    search_fields = ("workspace__name", "user__email")
