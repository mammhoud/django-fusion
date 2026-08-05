"""
Formint — API schemas (decoder layer).

Every schema derives from ``django_fusion.routes.schemas.model_schema.ModelSchema``
(the django-fusion enhancement of ninja-schema) so that:

  * input payloads are validated and decoded through the fusion schema base
    (``create`` / ``update`` / ``save`` helpers available),
  * output payloads reuse the same field configuration (single source of truth),
  * all django-fusion enhancements (ModelSchema.create/update/save, sync field
    handling, Pydantic v2 semantics) apply to the whole POS API.

Field lists are deliberately explicit so API surfaces stay stable and readable.
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.schemas.model_schema import ModelSchema as FusionModelSchema

from formint.models import (
    Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee,
    MenuItem, Menu, MenuItemAssignment,
    Node, Heartbeat, NodeEvent,
    DeviceConfig, MasterDevice, CloudLink, SyncLog,
    Supplier, PurchaseOrder, PurchaseOrderItem,
    KitchenTicket, SupportTicket,
    Payroll, EmployeeSchedule, TaxReport,
    Note,
    Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
    ClientCategory, LoyaltyTransaction, UserSettings,
    SyncApproval, DeviceToken, SignalEvent,
    Company, Pipeline, Stage, Contact, Deal, Activity, CRMNote,
)

__all__ = [
    "CategoryOut", "ProductOut", "CustomerOut", "SaleOut", "SaleItemOut",
    "InventoryTransactionOut", "EmployeeOut",
    "MenuItemOut", "MenuOut", "MenuItemAssignmentOut",
    "NodeOut", "HeartbeatOut", "NodeEventOut",
    "DeviceConfigOut", "MasterDeviceOut", "CloudLinkOut", "SyncLogOut",
    "SupplierOut", "PurchaseOrderOut", "PurchaseOrderItemOut",
    "KitchenTicketOut", "SupportTicketOut",
    "PayrollOut", "EmployeeScheduleOut", "TaxReportOut",
    "NoteOut", "IngredientOut", "RecipeOut", "ReceiptTemplateOut",
    "RoleOut", "InventoryAdjustmentOut",
    "ClientCategoryOut", "LoyaltyTransactionOut", "UserSettingsOut",
    "SyncApprovalOut", "DeviceTokenOut", "SignalEventOut",
    "CompanyOut", "PipelineOut", "StageOut", "ContactOut", "DealOut",
    "ActivityOut", "CRMNoteOut",
]


# ── POS Core ───────────────────────────────────────────────────────────────

class CategoryOut(FusionModelSchema):
    class Config:
        model = Category
        include = [
            "id", "name", "slug", "description", "display_order",
            "is_active", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class ProductOut(FusionModelSchema):
    # URLField with default "" fails AnyUrl validation; expose as plain string.
    image_url: str | None = None

    class Config:
        model = Product
        include = [
            "id", "name", "sku", "category", "price", "cost_price",
            "tax_rate", "barcode", "is_active", "stock_quantity",
            "low_stock_threshold", "description", "image_url",
            "border_color", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class CustomerOut(FusionModelSchema):
    class Config:
        model = Customer
        include = [
            "id", "first_name", "last_name", "email", "phone",
            "loyalty_points", "client_category", "total_spent", "notes",
            "is_active", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class SaleOut(FusionModelSchema):
    class Config:
        model = Sale
        include = [
            "id", "customer", "sale_date", "subtotal", "tax_amount",
            "discount_amount", "cashback_amount", "total", "payment_method",
            "status", "notes", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class SaleItemOut(FusionModelSchema):
    class Config:
        model = SaleItem
        include = [
            "id", "sale", "product", "product_name", "quantity",
            "unit_price", "line_total", "notes",
            "is_synced", "synced_at", "sync_status",
        ]


class InventoryTransactionOut(FusionModelSchema):
    class Config:
        model = InventoryTransaction
        include = [
            "id", "product", "transaction_type", "quantity", "reference",
            "notes", "created_by", "shipping_fee", "inventory_id",
            "transfer_to_inventory", "created_at",
            "is_synced", "synced_at", "sync_status",
        ]


class EmployeeOut(FusionModelSchema):
    class Config:
        model = Employee
        include = [
            "id", "first_name", "last_name", "email", "phone", "role",
            "pin_code", "is_active", "hourly_rate", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


# ── Menu ───────────────────────────────────────────────────────────────────

class MenuItemOut(FusionModelSchema):
    class Config:
        model = MenuItem
        include = [
            "id", "category", "name", "slug", "description", "price",
            "currency", "is_available", "is_featured", "display_order",
            "preparation_time", "ingredients", "allergens", "calories",
            "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class MenuOut(FusionModelSchema):
    class Config:
        model = Menu
        include = [
            "id", "name", "slug", "description", "is_active",
            "valid_from", "valid_until", "display_order",
            "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class MenuItemAssignmentOut(FusionModelSchema):
    class Config:
        model = MenuItemAssignment
        include = [
            "id", "menu", "item", "override_price", "display_order",
            "is_synced", "synced_at", "sync_status",
        ]


# ── Nodes & Sync ───────────────────────────────────────────────────────────

class NodeOut(FusionModelSchema):
    class Config:
        model = Node
        include = [
            "id", "node_id", "hostname", "node_type", "version",
            "api_version", "status", "status_message", "is_active",
            "product_count", "transaction_count", "customer_count",
            "ip_address", "port", "capabilities", "metadata",
            "first_seen", "last_seen", "last_synced_at",
            "created_at", "updated_at",
        ]


class HeartbeatOut(FusionModelSchema):
    class Config:
        model = Heartbeat
        include = [
            "id", "node_id", "status", "payload", "latency_ms",
            "received_at", "is_synced", "synced_at", "sync_status",
        ]


class NodeEventOut(FusionModelSchema):
    class Config:
        model = NodeEvent
        include = [
            "id", "node_id", "event_type", "description", "metadata",
            "created_at", "is_synced", "synced_at", "sync_status",
        ]


class DeviceConfigOut(FusionModelSchema):
    class Config:
        model = DeviceConfig
        include = [
            "id", "node_id", "config_key", "config_value", "category",
            "description", "is_active", "version", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class MasterDeviceOut(FusionModelSchema):
    class Config:
        model = MasterDevice
        include = [
            "id", "name", "device_id", "node_id", "device_type", "status",
            "status_message", "ip_address", "port", "api_version",
            "capabilities", "config", "managed_node_ids", "is_active",
            "last_heartbeat_at", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class CloudLinkOut(FusionModelSchema):
    class Config:
        model = CloudLink
        include = [
            "id", "name", "cloud_url", "api_key", "status", "status_message",
            "is_primary", "sync_interval", "last_connected_at", "last_sync_at",
            "metadata", "is_active", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class SyncLogOut(FusionModelSchema):
    class Config:
        model = SyncLog
        include = [
            "id", "node_id", "entity_type", "entity_id", "direction",
            "status", "payload_size", "duration_ms", "error_message",
            "retry_count", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


# ── Inventory & Operations ─────────────────────────────────────────────────

class SupplierOut(FusionModelSchema):
    class Config:
        model = Supplier
        include = [
            "id", "name", "contact_name", "email", "phone", "address",
            "tax_id", "payment_terms", "is_active", "created_at", "updated_at",
        ]


class PurchaseOrderOut(FusionModelSchema):
    class Config:
        model = PurchaseOrder
        include = [
            "id", "supplier", "reference_number", "status", "total_amount",
            "expected_date", "notes", "created_at", "updated_at",
        ]


class PurchaseOrderItemOut(FusionModelSchema):
    class Config:
        model = PurchaseOrderItem
        include = [
            "id", "purchase_order", "product", "product_name", "quantity",
            "cost_per_unit", "received_quantity",
        ]


class KitchenTicketOut(FusionModelSchema):
    class Config:
        model = KitchenTicket
        include = [
            "id", "sale", "status", "priority", "notes",
            "created_at", "completed_at",
        ]


class SupportTicketOut(FusionModelSchema):
    class Config:
        model = SupportTicket
        include = [
            "id", "name", "email", "subject", "message", "status",
            "created_at", "updated_at",
        ]


# ── HR & Finance ───────────────────────────────────────────────────────────

class PayrollOut(FusionModelSchema):
    class Config:
        model = Payroll
        include = [
            "id", "employee", "period_start", "period_end", "regular_hours",
            "overtime_hours", "total_pay", "base_salary", "deductions",
            "bonuses", "net_pay", "status", "notes",
            "created_at", "updated_at",
        ]


class EmployeeScheduleOut(FusionModelSchema):
    class Config:
        model = EmployeeSchedule
        include = [
            "id", "employee", "day_of_week", "start_time", "end_time",
            "status", "notes", "created_at", "updated_at",
        ]


class TaxReportOut(FusionModelSchema):
    class Config:
        model = TaxReport
        include = [
            "id", "report_type", "period_start", "period_end",
            "total_sales", "total_tax", "transaction_count", "status",
            "generated_at",
        ]


# ── Notes & Extras ─────────────────────────────────────────────────────────

class NoteOut(FusionModelSchema):
    class Config:
        model = Note
        include = [
            "id", "title", "content", "status", "reference_type",
            "reference_id", "created_by", "created_at", "updated_at",
        ]


class IngredientOut(FusionModelSchema):
    class Config:
        model = Ingredient
        include = [
            "id", "name", "unit", "current_quantity", "reorder_level",
            "reorder_quantity", "cost_per_unit", "is_active",
            "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class RecipeOut(FusionModelSchema):
    class Config:
        model = Recipe
        include = [
            "id", "product", "name", "instructions", "yield_quantity",
            "is_active", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class ReceiptTemplateOut(FusionModelSchema):
    class Config:
        model = ReceiptTemplate
        include = [
            "id", "name", "description", "template_html", "template_css",
            "is_default", "is_active", "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class RoleOut(FusionModelSchema):
    class Config:
        model = Role
        include = [
            "id", "name", "description", "permissions", "is_active",
            "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class InventoryAdjustmentOut(FusionModelSchema):
    class Config:
        model = InventoryAdjustment
        include = [
            "id", "ingredient", "quantity", "adjustment_type",
            "previous_quantity", "new_quantity", "reason", "notes",
            "created_by", "created_at",
            "is_synced", "synced_at", "sync_status",
        ]


# ── Loyalty & Client Settings ──────────────────────────────────────────────

class ClientCategoryOut(FusionModelSchema):
    class Config:
        model = ClientCategory
        include = [
            "id", "name", "description", "min_points", "points_per_currency",
            "points_to_currency", "discount_rate", "perks", "is_active",
            "created_at", "updated_at",
            "is_synced", "synced_at", "sync_status",
        ]


class LoyaltyTransactionOut(FusionModelSchema):
    class Config:
        model = LoyaltyTransaction
        include = [
            "id", "customer", "sale", "transaction_type", "points_change",
            "balance_after", "reason", "created_at",
            "is_synced", "synced_at", "sync_status",
        ]


class UserSettingsOut(FusionModelSchema):
    class Config:
        model = UserSettings
        include = [
            "id", "user", "restaurant_name", "address", "phone", "email",
            "tax_rate", "currency", "opening_time", "closing_time",
            "receipt_footer", "logo", "dine_in_tables", "delivery_fee",
            "delivery_fee_per_km", "theme", "language",
            "notifications_enabled", "inactivity_timeout",
            "two_factor_enabled", "fusion_render_mode",
            "created_at", "updated_at",
        ]


# ── Approval, Token, Audit ─────────────────────────────────────────────────

class SyncApprovalOut(FusionModelSchema):
    class Config:
        model = SyncApproval
        include = [
            "id", "node_id", "entity_type", "entity_id", "change_data",
            "change_summary", "status", "reviewed_by", "review_notes",
            "reviewed_at", "error_message", "retry_count", "direction",
            "created_at", "updated_at",
        ]


class DeviceTokenOut(FusionModelSchema):
    class Config:
        model = DeviceToken
        include = [
            "id", "device_id", "token_hash", "token_prefix", "node_id_link",
            "role", "node_type", "capabilities", "allowed_entities",
            "app_type", "issued_at", "expires_at", "last_used_at",
            "last_synced_at", "is_active", "sync_status",
            "metadata", "created_at", "updated_at",
        ]


class SignalEventOut(FusionModelSchema):
    class Config:
        model = SignalEvent
        include = [
            "id", "signal_name", "action", "node_id", "resource_id",
            "payload", "webhook_status", "webhook_error", "created_at",
        ]


# ── CRM ────────────────────────────────────────────────────────────────────

class CompanyOut(FusionModelSchema):
    # URLField with default "" fails AnyUrl validation; expose as plain string.
    website: str | None = None

    class Config:
        model = Company
        include = [
            "id", "name", "website", "email", "phone", "address", "city",
            "country", "industry", "description", "is_active",
            "created_at", "updated_at",
        ]


class PipelineOut(FusionModelSchema):
    class Config:
        model = Pipeline
        include = [
            "id", "name", "description", "is_default", "is_active",
            "display_order", "created_at", "updated_at",
        ]


class StageOut(FusionModelSchema):
    class Config:
        model = Stage
        include = [
            "id", "pipeline", "name", "display_order", "probability", "color",
            "is_active", "is_won_stage", "is_lost_stage",
            "created_at", "updated_at",
        ]


class ContactOut(FusionModelSchema):
    class Config:
        model = Contact
        include = [
            "id", "company", "first_name", "last_name", "email", "phone",
            "mobile", "job_title", "source", "notes", "is_active",
            "pos_customer_id", "created_at", "updated_at",
        ]


class DealOut(FusionModelSchema):
    class Config:
        model = Deal
        include = [
            "id", "contact", "company", "pipeline", "stage", "title",
            "description", "value", "currency", "probability",
            "expected_close_date", "is_closed", "is_won", "lost_reason",
            "is_active", "created_at", "updated_at",
        ]


class ActivityOut(FusionModelSchema):
    class Config:
        model = Activity
        include = [
            "id", "contact", "deal", "activity_type", "subject",
            "description", "is_completed", "due_date", "completed_at",
            "created_at", "updated_at",
        ]


class CRMNoteOut(FusionModelSchema):
    class Config:
        model = CRMNote
        include = [
            "id", "contact", "deal", "content", "is_pinned",
            "created_at", "updated_at",
        ]


# ── Writable schema factory (create/update/patch) ──────────────────────────
# ninja-extra auto-generates create/update/patch schemas from the retrieve
# schema, which includes read-only fields (created_at, updated_at, ...).
# These factories build schemas from the model's writable fields only, so
# POST/PUT/PATCH accept exactly the payload the model can write.

from django.db import models as dj_models

_AUTO_FIELD_TYPES = (dj_models.AutoField, dj_models.BigAutoField, dj_models.SmallAutoField)


def _writable_field_names(model: type) -> list[str]:
    """Return the writable, editable field names for a model."""
    names: list[str] = []
    for field in model._meta.fields:
        if isinstance(field, _AUTO_FIELD_TYPES):
            continue
        if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
            continue
        if not field.editable:
            continue
        if isinstance(field, dj_models.URLField):
            # URLField maps to pydantic AnyUrl and rejects the model default
            # ""; the writable payload should not require a valid URL.
            continue
        names.append(field.name)
    return names


def make_writable_schema(model: type, suffix: str) -> type[FusionModelSchema]:
    """Build a fusion ModelSchema subclass containing only writable fields.

    NOTE: ninja-schema (the base of django-fusion's ModelSchema) configures
    field selection with ``include``/``exclude`` (not ``model_fields``, which
    is the django-ninja convention).  ``include`` is set to the writable field
    names so create/update/patch payloads never require read-only fields.
    """
    class_name = f"{model.__name__}{suffix}"
    config = type("Config", (), {
        "model": model,
        "include": _writable_field_names(model),
    })
    # pydantic treats a class in the namespace as a nested type only when its
    # __qualname__ is prefixed by the outer class name; set it explicitly so
    # the dynamically-created Config is not mistaken for a model field.
    config.__module__ = __name__
    config.__qualname__ = f"{class_name}.Config"
    return type(
        class_name,
        (FusionModelSchema,),
        {"Config": config, "__module__": __name__, "__qualname__": class_name},
    )


def writable_schema_for(model: type) -> type[FusionModelSchema]:
    """Return (and cache) the writable schema for a model (used by controllers)."""
    return make_writable_schema(model, "Writable")


def make_patch_schema(model: type) -> type[FusionModelSchema]:
    """Build a writable schema where every field is optional (PATCH body)."""
    class_name = f"{model.__name__}Patch"
    writable = _writable_field_names(model)
    config = type("Config", (), {
        "model": model,
        "include": writable,
        # ninja-schema: the `optional` set makes listed fields non-required,
        # so a PATCH body may send only the fields it wants to change.
        "optional": writable,
    })
    config.__module__ = __name__
    config.__qualname__ = f"{class_name}.Config"
    return type(
        class_name,
        (FusionModelSchema,),
        {"Config": config, "__module__": __name__, "__qualname__": class_name},
    )


def patch_schema_for(model: type) -> type[FusionModelSchema]:
    """Return the patch (all-optional writable) schema for a model."""
    return make_patch_schema(model)


def schema_payload(model: type, data: dict[str, Any]) -> dict[str, Any]:
    """Return a plain dict for a model instance via the matching *Out schema.

    Used by fusion table components and reports so JSON fragments and
    server-rendered tables share the exact same decoded field set.
    """
    for schema in globals().values():
        if (
            isinstance(schema, type)
            and issubclass(schema, FusionModelSchema)
            and getattr(getattr(schema, "Config", None), "model", None) is model
        ):
            return schema.from_orm(data).dict()
    raise ValueError(f"No schema registered for model {model.__name__}")
