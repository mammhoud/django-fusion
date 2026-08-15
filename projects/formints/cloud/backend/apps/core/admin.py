"""POS Cloud — Unfold Admin configuration."""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    BackupRun,
    Branch,
    BranchInventory,
    BranchProduct,
    BranchReport,
    BranchSale,
    BranchSettings,
    BranchSyncLog,
    Contact,
    Deal,
    DeviceToken,
    Domain,
    InventoryReport,
    Lead,
    Organization,
    SyncConflict,
    SyncQueueItem,
    Tenant,
)

# TenantAdminMixin adds the domain inline management used by django-tenants;
# falls back to the plain Unfold ModelAdmin when unavailable.
try:
    from django_tenants.admin import TenantAdminMixin
    _TenantAdminBase = (TenantAdminMixin, ModelAdmin)
except ImportError:  # pragma: no cover — django-tenants is a declared dep
    _TenantAdminBase = (ModelAdmin,)


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


class BranchSettingsInline(admin.StackedInline):
    """Complete per-branch configuration inline on BranchAdmin."""

    model = BranchSettings
    extra = 0
    can_delete = False
    fieldsets = (
        ("Financial", {"fields": ("currency_code", "tax_profile_id", "tax_rate", "price_decimal_places", "round_after_tax")}),
        ("Time / Locale", {"fields": ("timezone", "locale", "week_starts_on")}),
        ("Receipt", {"fields": ("receipt_footer", "receipt_logo_url", "receipt_paper_width_mm", "auto_print_receipt")}),
        ("Sync / Ops", {"fields": ("sync_interval_seconds", "offline_grace_minutes", "low_stock_threshold")}),
        ("Flags", {"fields": ("features", "settings")}),
    )


@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ["name", "code", "organization", "pos_type", "is_active", "created_at"]
    list_filter = ["organization", "pos_type", "is_active"]
    search_fields = ["name", "code", "city"]
    list_select_related = ["organization"]
    inlines = [BranchSettingsInline]


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


@admin.register(SyncConflict)
class SyncConflictAdmin(ModelAdmin):
    list_display = ["entity_type", "entity_id", "branch", "status", "resolver_used", "created_at"]
    list_filter = ["status", "entity_type", "branch"]
    search_fields = ["entity_id", "node_id"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Conflict", {"fields": ("branch", "node_id", "entity_type", "entity_id")}),
        ("Data", {"fields": ("local_data", "remote_data", "conflict_fields")}),
        ("Resolution", {"fields": ("status", "resolver_used", "reason", "resolved_by", "resolved_at", "resolution_notes")}),
    )


@admin.register(SyncQueueItem)
class SyncQueueItemAdmin(ModelAdmin):
    list_display = ["entity_type", "operation", "branch", "status", "attempt_count", "created_at"]
    list_filter = ["status", "entity_type", "operation", "branch"]
    search_fields = ["node_id", "idempotency_key"]
    readonly_fields = ["created_at", "delivered_at"]
    fieldsets = (
        ("Queue Item", {"fields": ("branch", "node_id", "entity_type", "operation")}),
        ("Payload", {"fields": ("payload", "idempotency_key")}),
        ("Delivery", {"fields": ("status", "attempt_count", "max_attempts", "last_error", "next_retry_at", "delivered_at")}),
    )


@admin.register(BackupRun)
class BackupRunAdmin(ModelAdmin):
    """Admin for database backup attempts (Cloud capability)."""

    list_display = ["filename", "status", "size_bytes", "started_at", "finished_at"]
    list_filter = ["status"]
    search_fields = ["filename", "error_message"]
    readonly_fields = ["started_at", "finished_at"]
    fieldsets = (
        ("Backup", {"fields": ("filename", "status", "size_bytes", "error_message")}),
        ("Timing", {"fields": ("started_at", "finished_at")}),
    )


@admin.register(BranchSettings)
class BranchSettingsAdmin(ModelAdmin):
    list_display = ["branch", "currency_code", "tax_rate", "timezone", "updated_at"]
    list_filter = ["currency_code", "timezone"]
    search_fields = ["branch__name", "branch__code"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Tenant)
class TenantAdmin(*_TenantAdminBase):
    """Tenant registry — one PostgreSQL schema per Organization (public schema)."""

    list_display = ["schema_name", "organization", "auto_create_schema"]
    search_fields = ["schema_name", "organization__name"]
    list_select_related = ["organization"]
    fieldsets = (
        ("Tenant", {"fields": ("schema_name", "organization", "auto_create_schema")}),
    )


@admin.register(Domain)
class DomainAdmin(ModelAdmin):
    list_display = ["domain", "tenant", "is_primary"]
    list_filter = ["is_primary"]
    search_fields = ["domain", "tenant__schema_name"]


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
