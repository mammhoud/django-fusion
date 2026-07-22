"""POS Cloud — Unfold Admin configuration."""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Organization,
    Branch,
    Lead,
    Contact,
    Deal,
    InventoryReport,
    BranchReport,
    BranchSyncLog,
    BranchProduct,
    BranchSale,
    BranchInventory,
    DeviceToken,
)


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = ["name", "slug", "subscription_plan", "is_active", "created_at"]
    list_filter = ["subscription_plan", "is_active"]
    search_fields = ["name", "slug", "email"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Info", {"fields": ("name", "slug", "description", "website", "email", "phone", "address", "logo")}),
        ("Status", {"fields": ("is_active", "subscription_plan", "settings")}),
    )


@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ["name", "code", "organization", "pos_type", "is_active", "created_at"]
    list_filter = ["organization", "pos_type", "is_active"]
    search_fields = ["name", "code", "city"]
    list_select_related = ["organization"]


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ["full_name", "organization", "status", "source", "assigned_to", "created_at"]
    list_filter = ["status", "source", "organization", "is_active"]
    search_fields = ["first_name", "last_name", "email", "company_name"]
    list_select_related = ["organization", "assigned_to"]

    @admin.display(description="Name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ["first_name", "last_name", "email", "organization", "is_active"]
    search_fields = ["first_name", "last_name", "email"]


@admin.register(Deal)
class DealAdmin(ModelAdmin):
    list_display = ["title", "organization", "stage", "value", "created_at"]
    list_filter = ["stage", "organization"]
    search_fields = ["title"]


@admin.register(InventoryReport)
class InventoryReportAdmin(ModelAdmin):
    list_display = ["title", "report_type", "organization", "created_at"]
    list_filter = ["report_type", "organization"]
    readonly_fields = ["created_at"]


@admin.register(BranchReport)
class BranchReportAdmin(ModelAdmin):
    list_display = ["title", "report_type", "branch", "date_from", "date_to", "created_at"]
    list_filter = ["report_type", "organization", "branch"]
    readonly_fields = ["created_at"]


@admin.register(BranchSyncLog)
class BranchSyncLogAdmin(ModelAdmin):
    list_display = ["node_id", "branch", "entity_type", "entity_count", "status", "received_at"]
    list_filter = ["status", "entity_type", "branch"]
    readonly_fields = ["received_at"]


@admin.register(BranchProduct)
class BranchProductAdmin(ModelAdmin):
    list_display = ["name", "branch", "sku", "price", "stock_quantity", "last_synced_at"]
    list_filter = ["branch", "is_active"]
    search_fields = ["name", "sku"]


@admin.register(BranchSale)
class BranchSaleAdmin(ModelAdmin):
    list_display = ["source_id", "branch", "total_amount", "payment_method", "sale_date"]
    list_filter = ["branch", "payment_method"]
    readonly_fields = ["created_at"]


@admin.register(BranchInventory)
class BranchInventoryAdmin(ModelAdmin):
    list_display = ["source_id", "branch", "product_name", "transaction_type", "quantity", "transaction_date"]
    list_filter = ["branch", "transaction_type"]


@admin.register(DeviceToken)
class DeviceTokenAdmin(ModelAdmin):
    list_display = ["device_id", "role", "app_type", "sync_status", "branch", "is_active"]
    list_filter = ["role", "app_type", "sync_status", "is_active", "branch"]
    search_fields = ["device_id", "token_prefix", "node_id_link"]
    readonly_fields = ["issued_at", "created_at", "updated_at", "token_hash"]
    fieldsets = (
        ("Identity", {"fields": ("device_id", "token_hash", "token_prefix", "node_id_link", "branch")}),
        ("Role & Type", {"fields": ("role", "app_type", "node_type", "capabilities", "allowed_entities")}),
        ("Sync Tracking", {"fields": ("sync_status", "last_synced_at")}),
        ("Lifecycle", {"fields": ("is_active", "issued_at", "expires_at", "last_used_at", "metadata")}),
    )
