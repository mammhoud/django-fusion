"""
Formint — merged Django ORM models (from POS Full + POS Solo).

Managed models (app_label="formint"):
  pos.py       — Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee
  menu.py      — MenuItem, Menu, MenuItemAssignment
  node.py      — Node, Heartbeat, NodeEvent
  config.py    — DeviceConfig, MasterDevice, CloudLink
  sync.py      — SyncLog
  inventory.py — Supplier, PurchaseOrder, PurchaseOrderItem
  ops.py       — KitchenTicket, SupportTicket
  hr.py        — Payroll, EmployeeSchedule, TaxReport
  notes.py     — Note
  extra.py     — Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment
  loyalty.py   — ClientCategory, LoyaltyTransaction, UserSettings
  approval.py  — SyncApproval
  token.py     — DeviceToken (django_fusion BaseDeviceToken subclass)
  audit.py     — SignalEvent
  crm.py       — Company, Pipeline, Stage, Contact, Deal, Activity, CRMNote

Table names are preserved from the legacy editions (full_*, pos_crm_*, ...)
so existing POS databases remain readable during the migration window.
"""

from formint.models.pos import (  # noqa: F401
    Category, Product, Customer, Sale, SaleItem,
    InventoryTransaction, Employee,
)
from formint.models.menu import MenuItem, Menu, MenuItemAssignment  # noqa: F401
from formint.models.node import Node, Heartbeat, NodeEvent  # noqa: F401
from formint.models.config import DeviceConfig, MasterDevice, CloudLink  # noqa: F401
from formint.models.sync import SyncLog  # noqa: F401
from formint.models.inventory import Supplier, PurchaseOrder, PurchaseOrderItem  # noqa: F401
from formint.models.ops import KitchenTicket, SupportTicket  # noqa: F401
from formint.models.hr import Payroll, EmployeeSchedule, TaxReport  # noqa: F401
from formint.models.notes import Note  # noqa: F401
from formint.models.extra import (  # noqa: F401
    Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
)
from formint.models.loyalty import ClientCategory, LoyaltyTransaction, UserSettings  # noqa: F401
from formint.models.approval import SyncApproval  # noqa: F401
from formint.models.token import DeviceToken  # noqa: F401
from formint.models.audit import SignalEvent  # noqa: F401
from formint.models.crm import (  # noqa: F401
    Company, Pipeline, Stage, Contact, Deal, Activity, CRMNote,
)

__all__ = [
    "Category", "Product", "Customer", "Sale", "SaleItem",
    "InventoryTransaction", "Employee",
    "MenuItem", "Menu", "MenuItemAssignment",
    "Node", "Heartbeat", "NodeEvent",
    "DeviceConfig", "MasterDevice", "CloudLink",
    "SyncLog",
    "Supplier", "PurchaseOrder", "PurchaseOrderItem",
    "KitchenTicket", "SupportTicket",
    "Payroll", "EmployeeSchedule", "TaxReport",
    "Note",
    "Ingredient", "Recipe", "ReceiptTemplate", "Role", "InventoryAdjustment",
    "ClientCategory", "LoyaltyTransaction", "UserSettings",
    "SyncApproval",
    "DeviceToken",
    "SignalEvent",
    "Company", "Pipeline", "Stage", "Contact", "Deal", "Activity", "CRMNote",
]
