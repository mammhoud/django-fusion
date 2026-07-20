"""
POS Full — Django Unfold Admin Registration (Master Manager Panel).

Registers all managed models with the Unfold modern admin theme.
Access via: python manage.py runserver 0.0.0.0:8000
             → http://localhost:8000/admin/

Create superuser: python manage.py createsuperuser

Unfold docs: https://unfoldadmin.com/
"""

from django.contrib import admin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin, TabularInline

# ── POS Core Models ──
from models.pos import Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee
from models.menu import MenuItem, Menu, MenuItemAssignment

# ── Node & Config Models ──
from models.node import Node, Heartbeat, NodeEvent
from models.config import DeviceConfig, MasterDevice, CloudLink
from models.sync import SyncLog

# ── Inventory & Operations ──
from models.inventory import Supplier, PurchaseOrder, PurchaseOrderItem
from models.ops import KitchenTicket, SupportTicket


# ── Inline registrations (Unfold TabularInline) ──
class SaleItemInline(TabularInline):
    model = SaleItem
    extra = 0
    tab = True  # Unfold: show as tab


class PurchaseOrderItemInline(TabularInline):
    model = PurchaseOrderItem
    extra = 0


class HeartbeatInline(TabularInline):
    model = Heartbeat
    extra = 0
    readonly_fields = ["received_at"]
    can_delete = False
    max_num = 0


class NodeEventInline(TabularInline):
    model = NodeEvent
    extra = 0
    readonly_fields = ["created_at"]
    can_delete = False
    max_num = 0


# ── POS Core Admin Classes ──
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["id", "name", "display_order", "is_active", "created_at"]
    list_filter = ["is_active"]
    list_filter_submit = True  # Unfold: submit button on filter sidebar
    search_fields = ["name"]
    ordering = ["display_order", "name"]
    compressed_fields = True  # Unfold: compact form layout


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["id", "name", "price", "unit", "category", "is_active", "created_at"]
    list_filter = ["is_active", "category"]
    list_filter_submit = True
    search_fields = ["name", "sku"]
    ordering = ["name"]
    list_fullwidth = True
    compressed_fields = True
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email", "phone", "loyalty_points", "total_spent"]
    list_filter = ["is_active"]
    list_filter_submit = True
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering = ["-created_at"]
    list_fullwidth = True


@admin.register(Sale)
class SaleAdmin(ModelAdmin):
    list_display = ["id", "customer", "total", "payment_method", "status", "sale_date"]
    list_filter = ["status", "payment_method", "sale_date"]
    list_filter_submit = True
    search_fields = ["id"]
    ordering = ["-sale_date"]
    inlines = [SaleItemInline]
    list_fullwidth = True


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(ModelAdmin):
    list_display = ["id", "product", "transaction_type", "quantity", "created_at"]
    list_filter = ["transaction_type"]
    list_filter_submit = True
    ordering = ["-created_at"]


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ["id", "first_name", "last_name", "role", "is_active"]
    list_filter = ["role", "is_active"]
    list_filter_submit = True
    search_fields = ["first_name", "last_name"]
    ordering = ["last_name", "first_name"]
    compressed_fields = True


@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    list_display = ["id", "name", "price", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Menu)
class MenuAdmin(ModelAdmin):
    list_display = ["id", "name", "is_active"]


# ── Nodes & Sync Admin Classes ──
@admin.register(Node)
class NodeAdmin(ModelAdmin):
    list_display = ["node_id", "hostname", "node_type", "status", "last_seen"]
    list_filter = ["status", "node_type", "is_active"]
    list_filter_submit = True
    search_fields = ["node_id", "hostname"]
    ordering = ["-last_seen"]
    inlines = [HeartbeatInline, NodeEventInline]
    list_fullwidth = True


@admin.register(SyncLog)
class SyncLogAdmin(ModelAdmin):
    list_display = ["id", "node_id", "entity_type", "entity_id", "status", "direction", "created_at"]
    list_filter = ["status", "entity_type", "direction"]
    list_filter_submit = True
    ordering = ["-created_at"]
    list_fullwidth = True


@admin.register(DeviceConfig)
class DeviceConfigAdmin(ModelAdmin):
    list_display = ["node_id", "config_key", "category", "is_active", "updated_at"]
    list_filter = ["category", "is_active"]
    list_filter_submit = True
    search_fields = ["node_id", "config_key"]


@admin.register(MasterDevice)
class MasterDeviceAdmin(ModelAdmin):
    list_display = ["id", "device_name", "is_master", "is_active"]


@admin.register(CloudLink)
class CloudLinkAdmin(ModelAdmin):
    list_display = ["id", "name", "url", "is_active"]


# ── Operations Admin Classes ──
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


# ── Django built-in admin (Unfold themed) ──
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
