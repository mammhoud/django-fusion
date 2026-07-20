"""
POS Full — Django Admin Registration (Master Manager Panel).

Registers all managed models with the Django admin interface.
Access via: python manage.py runserver 0.0.0.0:8000
             → http://localhost:8000/admin/

Create superuser: python manage.py createsuperuser
"""

from django.contrib import admin
from django.contrib.auth.models import User, Group

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


# ── Inline registrations ──
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


class HeartbeatInline(admin.TabularInline):
    model = Heartbeat
    extra = 0
    readonly_fields = ["received_at"]
    can_delete = False
    max_num = 0


class NodeEventInline(admin.TabularInline):
    model = NodeEvent
    extra = 0
    readonly_fields = ["created_at"]
    can_delete = False
    max_num = 0


# ── Model registrations ──
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "display_order", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    ordering = ["display_order", "name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "price", "unit", "category", "is_active", "created_at"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "sku"]
    ordering = ["name"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email", "phone", "loyalty_points", "total_spent"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering = ["-created_at"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "total", "payment_method", "status", "sale_date"]
    list_filter = ["status", "payment_method", "sale_date"]
    search_fields = ["id"]
    ordering = ["-sale_date"]
    inlines = [SaleItemInline]


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "transaction_type", "quantity", "created_at"]
    list_filter = ["transaction_type"]
    ordering = ["-created_at"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["first_name", "last_name"]
    ordering = ["last_name", "first_name"]


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["node_id", "hostname", "node_type", "status", "last_seen"]
    list_filter = ["status", "node_type", "is_active"]
    search_fields = ["node_id", "hostname"]
    ordering = ["-last_seen"]
    inlines = [HeartbeatInline, NodeEventInline]


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ["id", "node_id", "entity_type", "entity_id", "status", "created_at"]
    list_filter = ["status", "entity_type", "direction"]
    ordering = ["-created_at"]


@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = ["node_id", "config_key", "category", "is_active", "updated_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["node_id", "config_key"]


@admin.register(MasterDevice)
class MasterDeviceAdmin(admin.ModelAdmin):
    list_display = ["id", "device_name", "is_master", "is_active"]


@admin.register(CloudLink)
class CloudLinkAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "url", "is_active"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "contact_name", "email", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "email"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "supplier", "status", "total_amount", "expected_date", "created_at"]
    list_filter = ["status"]
    ordering = ["-created_at"]
    inlines = [PurchaseOrderItemInline]


@admin.register(KitchenTicket)
class KitchenTicketAdmin(admin.ModelAdmin):
    list_display = ["id", "sale", "status", "priority", "created_at"]
    list_filter = ["status"]
    ordering = ["-priority", "created_at"]


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ["id", "subject", "name", "email", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["subject", "name", "email"]
    ordering = ["-created_at"]


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active"]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "price", "is_active"]
    search_fields = ["name"]


# ── Django built-in admin ──
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "is_staff", "is_active", "date_joined"]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["username", "email"]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]
