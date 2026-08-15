"""
Formint — Django Unfold Admin Registration (Merged Master Manager Panel).

Registers every managed model with the Unfold modern admin theme.
Special focus on the loyalty/settings models requested for the merged
package: ClientCategory (people as a client category), LoyaltyTransaction
(points ledger), and UserSettings (per-user POS settings mirroring the
front Settings page).

Access:
    python manage.py runserver 127.0.0.1:8000
    → http://localhost:8000/admin/

Superuser (auto):
    python manage.py --ensure-superuser
    (or set FORMINT_ADMIN_EMAIL / FORMINT_ADMIN_PASSWORD / FORMINT_ADMIN_NAME)

Unfold docs: https://unfoldadmin.com/
"""

from django.contrib import admin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin, TabularInline

from formint.middleware import seed_user_settings_session
from formint.models import (
    # POS core
    Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee,
    # Menu
    MenuItem, Menu, MenuItemAssignment,
    # Nodes & config
    Node, Heartbeat, NodeEvent, DeviceConfig, MasterDevice, CloudLink, SyncLog,
    # Inventory & operations
    Supplier, PurchaseOrder, PurchaseOrderItem,
    KitchenTicket, SupportTicket,
    # HR & finance
    Payroll, EmployeeSchedule, TaxReport,
    # Extras
    Note, Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
    Currency, TaxProfile,
    # Loyalty & settings (primary focus)
    ClientCategory, LoyaltyTransaction, UserSettings,
    # Sync / token / audit
    SyncApproval, DeviceToken, SignalEvent,
    # CRM
    Company, Pipeline, Stage, Contact, Deal, Activity, CRMNote,
    # Gaming (POS-KO)
    GamingStation, GamingToken, GamingSession, GamingQueueEntry,
    # Gift cards
    GiftCard, GiftCardTransaction,
    # Table management
    RestaurantTable, TableReservation,
    # Delivery integration
    DeliveryProvider, DeliveryOrder,
    # Employee scheduling / time clock
    TimeClockEntry,
    # Self-checkout kiosk
    KioskSession, KioskCartItem,
)

__all__ = [
    "ClientCategoryAdmin", "LoyaltyTransactionAdmin", "UserSettingsAdmin",
]


# ── Inline registrations (Unfold TabularInline) ────────────────────────────

class SaleItemInline(TabularInline):
    model = SaleItem
    extra = 0
    tab = True  # Unfold: show as tab


class PurchaseOrderItemInline(TabularInline):
    model = PurchaseOrderItem
    extra = 0


# ═══════════════════════════════════════════════════════════════════════════
#  Loyalty & Client Settings (primary focus)
# ═══════════════════════════════════════════════════════════════════════════

@admin.register(ClientCategory)
class ClientCategoryAdmin(ModelAdmin):
    """Loyalty tier — people grouped as a client category (points-driven)."""

    list_display = [
        "id", "name", "min_points", "points_per_currency",
        "points_to_currency", "discount_rate", "customer_count", "is_active",
    ]
    list_filter = ["is_active"]
    list_filter_submit = True
    search_fields = ["name", "description"]
    ordering = ["min_points", "name"]
    compressed_fields = True
    list_fullwidth = True
    readonly_fields = ["created_at", "updated_at"]


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(ModelAdmin):
    """Points ledger — earn / redeem / adjust / expire per customer."""

    list_display = [
        "id", "customer", "transaction_type", "points_change",
        "balance_after", "sale", "reason", "created_at",
    ]
    list_filter = ["transaction_type", "created_at"]
    list_filter_submit = True
    search_fields = ["customer__first_name", "customer__last_name", "customer__email", "reason"]
    ordering = ["-created_at"]
    list_fullwidth = True
    readonly_fields = ["created_at"]


@admin.register(UserSettings)
class UserSettingsAdmin(ModelAdmin):
    """Per-user POS settings — mirrors the front Settings page + preferences.

    Includes the operator-facing ``fusion_render_mode`` preference that
    seeds the session via ``FormintSessionModeMiddleware`` (see
    ``formint/middleware.py``) so non-technical operators can switch the
    POS between server-rendered HTML and JSON API delivery from the admin.
    """

    list_display = [
        "id", "user", "user_email", "restaurant_name", "currency",
        "tax_rate", "fusion_render_mode", "theme", "language",
        "notifications_enabled",
    ]
    list_filter = ["theme", "language", "notifications_enabled", "fusion_render_mode"]
    list_filter_submit = True
    search_fields = ["user__username", "user__email", "restaurant_name", "email"]
    list_fullwidth = True
    compressed_fields = True
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Account", {"fields": ("user",)}),
        ("Business Settings", {"fields": (
            "restaurant_name", "address", "phone", "email", "tax_rate",
            "currency", "opening_time", "closing_time", "receipt_footer",
            "logo", "dine_in_tables", "delivery_fee", "delivery_fee_per_km",
        )}),
        ("Fusion Render Mode", {
            "fields": ("fusion_render_mode",),
            "description": (
                "How the POS serves content: <b>Fusion render-first</b> = finished "
                "server HTML; <b>Data APIs</b> = JSON for the client; "
                "<b>Default (settings)</b> = follow the configured default. "
                "Applies to the logged-in operator on their next page load."
            ),
        }),
        ("User Preferences", {"fields": (
            "theme", "language", "notifications_enabled",
            "inactivity_timeout", "two_factor_enabled",
        )}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        """Persist the row, then immediately re-seed the operator's session
        so the saved ``fusion_render_mode`` takes effect on their next
        request (no need to wait for a new session).

        Only re-seeds when the operator edits their *own* settings row
        (``obj.user_id == request.user.id``) — the middleware seeds every
        other user's session from their own row on their next session, so
        cross-user edits never mutate the operator's session.
        """
        super().save_model(request, obj, form, change)
        if obj.user_id == request.user.id:
            seed_user_settings_session(request, mode=obj.fusion_render_mode)


# ═══════════════════════════════════════════════════════════════════════════
#  POS Core
# ═══════════════════════════════════════════════════════════════════════════

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["id", "name", "slug", "display_order", "is_active", "created_at"]
    list_filter = ["is_active"]
    list_filter_submit = True
    search_fields = ["name"]
    ordering = ["display_order", "name"]
    compressed_fields = True


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["id", "name", "sku", "price", "category", "stock_quantity", "is_active"]
    list_filter = ["is_active", "category", "tax_rate"]
    list_filter_submit = True
    search_fields = ["name", "sku", "barcode"]
    ordering = ["name"]
    list_fullwidth = True
    compressed_fields = True
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = [
        "id", "first_name", "last_name", "email", "phone",
        "loyalty_points", "client_category", "total_spent", "is_active",
    ]
    list_filter = ["is_active", "client_category"]
    list_filter_submit = True
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering = ["-created_at"]
    list_fullwidth = True
    compressed_fields = True


@admin.register(Sale)
class SaleAdmin(ModelAdmin):
    list_display = ["id", "customer", "total", "payment_method", "status", "sale_date"]
    list_filter = ["status", "payment_method", "sale_date"]
    list_filter_submit = True
    search_fields = ["id", "customer__first_name", "customer__last_name"]
    ordering = ["-sale_date"]
    inlines = [SaleItemInline]
    list_fullwidth = True


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(ModelAdmin):
    list_display = ["id", "product", "transaction_type", "quantity", "inventory_id", "created_at"]
    list_filter = ["transaction_type", "inventory_id"]
    list_filter_submit = True
    ordering = ["-created_at"]


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ["id", "first_name", "last_name", "role", "hourly_rate", "is_active"]
    list_filter = ["role", "is_active"]
    list_filter_submit = True
    search_fields = ["first_name", "last_name", "email"]
    ordering = ["last_name", "first_name"]
    compressed_fields = True


# ── Menu ───────────────────────────────────────────────────────────────────

@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    list_display = ["id", "name", "price", "is_available"]
    list_filter = ["is_available"]
    search_fields = ["name"]


@admin.register(Menu)
class MenuAdmin(ModelAdmin):
    list_display = ["id", "name", "is_active"]


@admin.register(MenuItemAssignment)
class MenuItemAssignmentAdmin(ModelAdmin):
    list_display = ["id", "menu", "item", "display_order"]


# ── Nodes & Sync ───────────────────────────────────────────────────────────

@admin.register(Node)
class NodeAdmin(ModelAdmin):
    list_display = ["node_id", "hostname", "node_type", "status", "last_seen"]
    list_filter = ["status", "node_type", "is_active"]
    list_filter_submit = True
    search_fields = ["node_id", "hostname"]
    ordering = ["-last_seen"]
    list_fullwidth = True


@admin.register(Heartbeat)
class HeartbeatAdmin(ModelAdmin):
    list_display = ["id", "node_id", "status", "latency_ms", "received_at"]
    list_filter = ["status"]
    ordering = ["-received_at"]


@admin.register(NodeEvent)
class NodeEventAdmin(ModelAdmin):
    list_display = ["id", "node_id", "event_type", "created_at"]
    list_filter = ["event_type"]
    ordering = ["-created_at"]


@admin.register(DeviceConfig)
class DeviceConfigAdmin(ModelAdmin):
    list_display = ["node_id", "config_key", "category", "is_active", "updated_at"]
    list_filter = ["category", "is_active"]
    list_filter_submit = True
    search_fields = ["node_id", "config_key"]


@admin.register(MasterDevice)
class MasterDeviceAdmin(ModelAdmin):
    list_display = ["id", "name", "device_id", "device_type", "status", "is_active"]
    list_filter = ["device_type", "status", "is_active"]


@admin.register(CloudLink)
class CloudLinkAdmin(ModelAdmin):
    list_display = ["id", "name", "cloud_url", "status", "is_primary", "is_active"]
    list_filter = ["status", "is_active"]


@admin.register(SyncLog)
class SyncLogAdmin(ModelAdmin):
    list_display = ["id", "node_id", "entity_type", "entity_id", "status", "direction", "created_at"]
    list_filter = ["status", "entity_type", "direction"]
    list_filter_submit = True
    ordering = ["-created_at"]
    list_fullwidth = True


# ── Inventory & Operations ─────────────────────────────────────────────────

@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ["id", "name", "contact_name", "email", "phone", "is_active"]
    list_filter = ["is_active"]
    list_filter_submit = True
    search_fields = ["name", "email"]
    compressed_fields = True


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ModelAdmin):
    list_display = ["id", "supplier", "status", "total_amount", "expected_date", "created_at"]
    list_filter = ["status"]
    list_filter_submit = True
    ordering = ["-created_at"]
    inlines = [PurchaseOrderItemInline]
    compressed_fields = True


@admin.register(KitchenTicket)
class KitchenTicketAdmin(ModelAdmin):
    list_display = ["id", "sale", "status", "priority", "created_at"]
    list_filter = ["status"]
    list_filter_submit = True
    ordering = ["-priority", "created_at"]


@admin.register(SupportTicket)
class SupportTicketAdmin(ModelAdmin):
    list_display = ["id", "subject", "name", "email", "status", "created_at"]
    list_filter = ["status"]
    list_filter_submit = True
    search_fields = ["subject", "name", "email"]
    ordering = ["-created_at"]
    list_fullwidth = True


# ── HR & Finance ───────────────────────────────────────────────────────────

@admin.register(Payroll)
class PayrollAdmin(ModelAdmin):
    list_display = ["id", "employee", "total_pay", "net_pay", "status"]


@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(ModelAdmin):
    list_display = ["id", "employee", "day_of_week", "start_time", "end_time"]


@admin.register(TimeClockEntry)
class TimeClockEntryAdmin(ModelAdmin):
    list_display = ["id", "employee", "clock_in", "clock_out", "break_minutes", "is_active"]
    list_filter = ["employee"]
    list_filter_submit = True
    search_fields = ["employee__first_name", "employee__last_name"]
    ordering = ["-clock_in"]
    list_fullwidth = True


@admin.register(TaxReport)
class TaxReportAdmin(ModelAdmin):
    list_display = ["id", "report_type", "total_sales", "total_tax", "status"]


@admin.register(KioskSession)
class KioskSessionAdmin(ModelAdmin):
    list_display = ["id", "session_key", "name", "status", "sale", "payment_method", "created_at"]
    list_filter = ["status"]
    list_filter_submit = True
    search_fields = ["session_key", "name"]
    ordering = ["-created_at"]
    list_fullwidth = True


@admin.register(KioskCartItem)
class KioskCartItemAdmin(ModelAdmin):
    list_display = ["id", "session", "product_name", "quantity", "unit_price"]
    list_filter = ["session"]
    list_filter_submit = True
    search_fields = ["product_name", "session__session_key"]
    ordering = ["-id"]


# ── Extras ─────────────────────────────────────────────────────────────────

@admin.register(Note)
class NoteAdmin(ModelAdmin):
    list_display = ["id", "title", "created_at"]


@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ["id", "name", "unit", "current_quantity", "reorder_level"]


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ["id", "name", "product", "yield_quantity", "is_active"]


@admin.register(ReceiptTemplate)
class ReceiptTemplateAdmin(ModelAdmin):
    list_display = ["id", "name", "is_default", "is_active"]


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ["id", "name", "permissions"]


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(ModelAdmin):
    list_display = ["id", "ingredient", "quantity", "adjustment_type", "reason", "created_at"]


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ["code", "name", "symbol", "exchange_rate", "is_default", "is_active"]
    list_filter = ["is_default", "is_active"]
    search_fields = ["code", "name"]


@admin.register(TaxProfile)
class TaxProfileAdmin(ModelAdmin):
    list_display = ["name", "code", "rate", "is_default", "is_active"]
    list_filter = ["is_default", "is_active"]
    search_fields = ["name", "code"]


# ── Sync / Token / Audit ───────────────────────────────────────────────────

@admin.register(SyncApproval)
class SyncApprovalAdmin(ModelAdmin):
    list_display = ["id", "entity_type", "entity_id", "status", "direction", "created_at"]
    list_filter = ["status", "entity_type", "direction"]


@admin.register(DeviceToken)
class DeviceTokenAdmin(ModelAdmin):
    list_display = ["id", "device_id", "token_prefix", "app_type", "is_active", "issued_at"]


@admin.register(SignalEvent)
class SignalEventAdmin(ModelAdmin):
    list_display = ["id", "signal_name", "created_at"]
    list_filter = ["signal_name"]


# ── Gaming (POS-KO) ───────────────────────────────────────────────────────

@admin.register(GamingStation)
class GamingStationAdmin(ModelAdmin):
    list_display = ["id", "name", "slug", "station_type", "status", "hourly_rate", "is_active"]
    list_filter = ["status", "station_type", "is_active"]
    list_filter_submit = True
    search_fields = ["name", "slug"]
    ordering = ["name"]
    compressed_fields = True


@admin.register(GamingToken)
class GamingTokenAdmin(ModelAdmin):
    list_display = ["id", "name", "minutes", "remaining_minutes", "price", "status", "sold_at"]
    list_filter = ["status"]
    list_filter_submit = True
    search_fields = ["name"]
    ordering = ["-sold_at"]


@admin.register(GamingSession)
class GamingSessionAdmin(ModelAdmin):
    list_display = ["id", "station", "customer", "status", "active_seconds", "cost", "started_at"]
    list_filter = ["status"]
    list_filter_submit = True
    search_fields = ["station__name", "customer__first_name", "customer__last_name"]
    ordering = ["-started_at"]
    list_fullwidth = True


@admin.register(GamingQueueEntry)
class GamingQueueEntryAdmin(ModelAdmin):
    list_display = ["id", "customer_name", "requested_minutes", "status", "station", "created_at"]
    list_filter = ["status"]
    list_filter_submit = True
    search_fields = ["customer_name"]
    ordering = ["created_at"]


# ── Gift Cards ─────────────────────────────────────────────────────────────

@admin.register(GiftCard)
class GiftCardAdmin(ModelAdmin):
    list_display = ["id", "code", "balance", "initial_balance", "currency", "status", "issued_at"]
    list_filter = ["status", "currency"]
    list_filter_submit = True
    search_fields = ["code", "recipient_name", "recipient_email"]
    ordering = ["-issued_at"]
    compressed_fields = True


@admin.register(GiftCardTransaction)
class GiftCardTransactionAdmin(ModelAdmin):
    list_display = ["id", "gift_card", "transaction_type", "amount", "balance_after", "created_at"]
    list_filter = ["transaction_type"]
    list_filter_submit = True
    ordering = ["-created_at"]
    list_fullwidth = True


# ── Table Management ───────────────────────────────────────────────────────

@admin.register(RestaurantTable)
class RestaurantTableAdmin(ModelAdmin):
    list_display = ["id", "name", "section", "shape", "capacity", "status", "current_sale", "is_active"]
    list_filter = ["status", "section", "shape", "is_active"]
    list_filter_submit = True
    search_fields = ["name", "section"]
    ordering = ["section", "name"]
    compressed_fields = True


@admin.register(TableReservation)
class TableReservationAdmin(ModelAdmin):
    list_display = ["id", "table", "display_name", "party_size", "reservation_time", "status"]
    list_filter = ["status"]
    list_filter_submit = True
    search_fields = ["customer_name", "customer__first_name", "customer__last_name", "table__name"]
    ordering = ["reservation_time"]
    list_fullwidth = True


# ── Delivery Integration ───────────────────────────────────────────────────

@admin.register(DeliveryProvider)
class DeliveryProviderAdmin(ModelAdmin):
    list_display = ["id", "name", "provider_type", "status", "commission_rate", "is_active"]
    list_filter = ["provider_type", "status", "is_active"]
    list_filter_submit = True
    search_fields = ["name"]
    ordering = ["provider_type", "name"]
    compressed_fields = True


@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(ModelAdmin):
    list_display = ["id", "provider", "provider_order_id", "customer_name", "status", "delivery_fee", "total", "created_at"]
    list_filter = ["status", "provider"]
    list_filter_submit = True
    search_fields = ["provider_order_id", "customer_name", "customer_phone", "delivery_address"]
    ordering = ["-created_at"]
    list_fullwidth = True


# ── CRM ────────────────────────────────────────────────────────────────────

@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ["id", "name", "website", "is_active"]


@admin.register(Pipeline)
class PipelineAdmin(ModelAdmin):
    list_display = ["id", "name", "is_active"]


@admin.register(Stage)
class StageAdmin(ModelAdmin):
    list_display = ["id", "name", "pipeline", "probability", "display_order"]


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email", "company"]


@admin.register(Deal)
class DealAdmin(ModelAdmin):
    list_display = ["id", "title", "value", "stage", "is_closed", "is_won"]


@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    list_display = ["id", "activity_type", "subject", "due_date", "is_completed"]


@admin.register(CRMNote)
class CRMNoteAdmin(ModelAdmin):
    list_display = ["id", "contact", "deal", "is_pinned", "created_at"]


# ── Django built-in admin (Unfold themed) ──────────────────────────────────

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ["id", "username", "email", "is_staff", "is_active", "date_joined"]
    list_filter = ["is_staff", "is_active"]
    list_filter_submit = True
    search_fields = ["username", "email"]
    compressed_fields = True


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]
