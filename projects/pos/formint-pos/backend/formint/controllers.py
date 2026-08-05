"""
Formint — ninja-extra model controllers (CRUD API layer).

Every controller extends ``ModelControllerBase`` (ninja-extra) with a
``ModelConfig`` bound to a merged formint model.  This generates the full
REST surface for free:

    GET    /api/v1/<resource>/           list   (pagination + search + ordering)
    POST   /api/v1/<resource>/           create
    GET    /api/v1/<resource>/{id}       find one
    PUT    /api/v1/<resource>/{id}       update
    PATCH  /api/v1/<resource>/{id}       partial update
    DELETE /api/v1/<resource>/{id}       delete

Output uses the django-fusion ModelSchema decoders from ``schemas.py``;
create/update/patch payloads use fusion writable schemas (read-only fields
such as ``created_at`` / ``updated_at`` excluded).  Responses are rendered
with the django-fusion encoder (``JSONRenderer``) via ``api.py`` and every
controller is registered there with ``api.register_controllers()``.
"""

from __future__ import annotations

from ninja_extra import api_controller
from ninja_extra.controllers import ModelConfig, ModelControllerBase

from formint import schemas as s
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
    "CategoryController", "ProductController", "CustomerController",
    "SaleController", "SaleItemController", "InventoryTransactionController",
    "EmployeeController", "MenuItemController", "MenuController",
    "MenuItemAssignmentController", "NodeController", "HeartbeatController",
    "NodeEventController", "DeviceConfigController", "MasterDeviceController",
    "CloudLinkController", "SyncLogController", "SupplierController",
    "PurchaseOrderController", "PurchaseOrderItemController",
    "KitchenTicketController", "SupportTicketController",
    "PayrollController", "EmployeeScheduleController", "TaxReportController",
    "NoteController", "IngredientController", "RecipeController",
    "ReceiptTemplateController", "RoleController", "InventoryAdjustmentController",
    "ClientCategoryController", "LoyaltyTransactionController",
    "UserSettingsController", "SyncApprovalController", "DeviceTokenController",
    "SignalEventController", "CompanyController", "PipelineController",
    "StageController", "ContactController", "DealController",
    "ActivityController", "CRMNoteController",
    "ALL_CONTROLLERS",
]


def _config(model: type, out_schema) -> ModelConfig:
    """Build a ModelConfig with fusion writable schemas for create/update/patch."""
    return ModelConfig(
        model=model,
        retrieve_schema=out_schema,
        create_schema=s.writable_schema_for(model),
        update_schema=s.writable_schema_for(model),
        patch_schema=s.patch_schema_for(model),
        allowed_routes=["create", "find_one", "list", "update", "patch", "delete"],
    )


# ── POS Core ───────────────────────────────────────────────────────────────

@api_controller("/categories", tags=["categories"])
class CategoryController(ModelControllerBase):
    model_config = _config(Category, s.CategoryOut)


@api_controller("/products", tags=["products"])
class ProductController(ModelControllerBase):
    model_config = _config(Product, s.ProductOut)


@api_controller("/customers", tags=["customers"])
class CustomerController(ModelControllerBase):
    model_config = _config(Customer, s.CustomerOut)


@api_controller("/sales", tags=["sales"])
class SaleController(ModelControllerBase):
    model_config = _config(Sale, s.SaleOut)


@api_controller("/sale-items", tags=["sales"])
class SaleItemController(ModelControllerBase):
    model_config = _config(SaleItem, s.SaleItemOut)


@api_controller("/inventory-transactions", tags=["inventory"])
class InventoryTransactionController(ModelControllerBase):
    model_config = _config(InventoryTransaction, s.InventoryTransactionOut)


@api_controller("/employees", tags=["employees"])
class EmployeeController(ModelControllerBase):
    model_config = _config(Employee, s.EmployeeOut)


# ── Menu ───────────────────────────────────────────────────────────────────

@api_controller("/menu-items", tags=["menu"])
class MenuItemController(ModelControllerBase):
    model_config = _config(MenuItem, s.MenuItemOut)


@api_controller("/menus", tags=["menu"])
class MenuController(ModelControllerBase):
    model_config = _config(Menu, s.MenuOut)


@api_controller("/menu-assignments", tags=["menu"])
class MenuItemAssignmentController(ModelControllerBase):
    model_config = _config(MenuItemAssignment, s.MenuItemAssignmentOut)


# ── Nodes & Sync ───────────────────────────────────────────────────────────

@api_controller("/nodes", tags=["nodes"])
class NodeController(ModelControllerBase):
    model_config = _config(Node, s.NodeOut)


@api_controller("/heartbeats", tags=["nodes"])
class HeartbeatController(ModelControllerBase):
    model_config = _config(Heartbeat, s.HeartbeatOut)


@api_controller("/node-events", tags=["nodes"])
class NodeEventController(ModelControllerBase):
    model_config = _config(NodeEvent, s.NodeEventOut)


@api_controller("/device-configs", tags=["config"])
class DeviceConfigController(ModelControllerBase):
    model_config = _config(DeviceConfig, s.DeviceConfigOut)


@api_controller("/master-devices", tags=["config"])
class MasterDeviceController(ModelControllerBase):
    model_config = _config(MasterDevice, s.MasterDeviceOut)


@api_controller("/cloud-links", tags=["config"])
class CloudLinkController(ModelControllerBase):
    model_config = _config(CloudLink, s.CloudLinkOut)


@api_controller("/sync-logs", tags=["sync"])
class SyncLogController(ModelControllerBase):
    model_config = _config(SyncLog, s.SyncLogOut)


# ── Inventory & Operations ─────────────────────────────────────────────────

@api_controller("/suppliers", tags=["inventory"])
class SupplierController(ModelControllerBase):
    model_config = _config(Supplier, s.SupplierOut)


@api_controller("/purchase-orders", tags=["inventory"])
class PurchaseOrderController(ModelControllerBase):
    model_config = _config(PurchaseOrder, s.PurchaseOrderOut)


@api_controller("/purchase-order-items", tags=["inventory"])
class PurchaseOrderItemController(ModelControllerBase):
    model_config = _config(PurchaseOrderItem, s.PurchaseOrderItemOut)


@api_controller("/kitchen-tickets", tags=["operations"])
class KitchenTicketController(ModelControllerBase):
    model_config = _config(KitchenTicket, s.KitchenTicketOut)


@api_controller("/support-tickets", tags=["operations"])
class SupportTicketController(ModelControllerBase):
    model_config = _config(SupportTicket, s.SupportTicketOut)


# ── HR & Finance ───────────────────────────────────────────────────────────

@api_controller("/payroll", tags=["hr"])
class PayrollController(ModelControllerBase):
    model_config = _config(Payroll, s.PayrollOut)


@api_controller("/employee-schedules", tags=["hr"])
class EmployeeScheduleController(ModelControllerBase):
    model_config = _config(EmployeeSchedule, s.EmployeeScheduleOut)


@api_controller("/tax-reports", tags=["hr"])
class TaxReportController(ModelControllerBase):
    model_config = _config(TaxReport, s.TaxReportOut)


# ── Notes & Extras ─────────────────────────────────────────────────────────

@api_controller("/notes", tags=["notes"])
class NoteController(ModelControllerBase):
    model_config = _config(Note, s.NoteOut)


@api_controller("/ingredients", tags=["recipes"])
class IngredientController(ModelControllerBase):
    model_config = _config(Ingredient, s.IngredientOut)


@api_controller("/recipes", tags=["recipes"])
class RecipeController(ModelControllerBase):
    model_config = _config(Recipe, s.RecipeOut)


@api_controller("/receipt-templates", tags=["settings"])
class ReceiptTemplateController(ModelControllerBase):
    model_config = _config(ReceiptTemplate, s.ReceiptTemplateOut)


@api_controller("/roles", tags=["settings"])
class RoleController(ModelControllerBase):
    model_config = _config(Role, s.RoleOut)


@api_controller("/inventory-adjustments", tags=["inventory"])
class InventoryAdjustmentController(ModelControllerBase):
    model_config = _config(InventoryAdjustment, s.InventoryAdjustmentOut)


# ── Loyalty & Client Settings ──────────────────────────────────────────────

@api_controller("/client-categories", tags=["loyalty"])
class ClientCategoryController(ModelControllerBase):
    model_config = _config(ClientCategory, s.ClientCategoryOut)


@api_controller("/loyalty-transactions", tags=["loyalty"])
class LoyaltyTransactionController(ModelControllerBase):
    model_config = _config(LoyaltyTransaction, s.LoyaltyTransactionOut)


@api_controller("/user-settings", tags=["settings"])
class UserSettingsController(ModelControllerBase):
    model_config = _config(UserSettings, s.UserSettingsOut)


# ── Approval, Token, Audit ─────────────────────────────────────────────────

@api_controller("/sync-approvals", tags=["sync"])
class SyncApprovalController(ModelControllerBase):
    model_config = _config(SyncApproval, s.SyncApprovalOut)


@api_controller("/device-tokens", tags=["sync"])
class DeviceTokenController(ModelControllerBase):
    model_config = _config(DeviceToken, s.DeviceTokenOut)


@api_controller("/signal-events", tags=["audit"])
class SignalEventController(ModelControllerBase):
    model_config = _config(SignalEvent, s.SignalEventOut)


# ── CRM ────────────────────────────────────────────────────────────────────

@api_controller("/crm/companies", tags=["crm"])
class CompanyController(ModelControllerBase):
    model_config = _config(Company, s.CompanyOut)


@api_controller("/crm/pipelines", tags=["crm"])
class PipelineController(ModelControllerBase):
    model_config = _config(Pipeline, s.PipelineOut)


@api_controller("/crm/stages", tags=["crm"])
class StageController(ModelControllerBase):
    model_config = _config(Stage, s.StageOut)


@api_controller("/crm/contacts", tags=["crm"])
class ContactController(ModelControllerBase):
    model_config = _config(Contact, s.ContactOut)


@api_controller("/crm/deals", tags=["crm"])
class DealController(ModelControllerBase):
    model_config = _config(Deal, s.DealOut)


@api_controller("/crm/activities", tags=["crm"])
class ActivityController(ModelControllerBase):
    model_config = _config(Activity, s.ActivityOut)


@api_controller("/crm/notes", tags=["crm"])
class CRMNoteController(ModelControllerBase):
    model_config = _config(CRMNote, s.CRMNoteOut)


ALL_CONTROLLERS = [
    CategoryController, ProductController, CustomerController,
    SaleController, SaleItemController, InventoryTransactionController,
    EmployeeController, MenuItemController, MenuController,
    MenuItemAssignmentController, NodeController, HeartbeatController,
    NodeEventController, DeviceConfigController, MasterDeviceController,
    CloudLinkController, SyncLogController, SupplierController,
    PurchaseOrderController, PurchaseOrderItemController,
    KitchenTicketController, SupportTicketController,
    PayrollController, EmployeeScheduleController, TaxReportController,
    NoteController, IngredientController, RecipeController,
    ReceiptTemplateController, RoleController, InventoryAdjustmentController,
    ClientCategoryController, LoyaltyTransactionController,
    UserSettingsController, SyncApprovalController, DeviceTokenController,
    SignalEventController, CompanyController, PipelineController,
    StageController, ContactController, DealController,
    ActivityController, CRMNoteController,
]
