"""
Django models module for the pos_full app.

Loaded by Django during import_models() which is called at the correct time
in django.setup() — after the app registry is initialized. This avoids the
AppRegistryNotReady error that occurs when models are imported in __init__.py.

NOTE: This module is separate from __init__.py to prevent circular imports
during Django's app initialization.
"""

from models.pos import (  # noqa: F401 — discovered by Django
    Category, Product, Customer, Sale, SaleItem,
    InventoryTransaction, Employee,
)
from models.menu import MenuItem, Menu, MenuItemAssignment  # noqa: F401
from models.node import Node, Heartbeat, NodeEvent  # noqa: F401
from models.config import DeviceConfig, MasterDevice, CloudLink  # noqa: F401
from models.sync import SyncLog  # noqa: F401
from models.inventory import Supplier, PurchaseOrder, PurchaseOrderItem  # noqa: F401
from models.ops import KitchenTicket, SupportTicket  # noqa: F401
from models.hr import Payroll, EmployeeSchedule, TaxReport  # noqa: F401
from models.notes import Note  # noqa: F401
from models.extra import (  # noqa: F401
    Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
    Currency, TaxProfile,
)
from models.loyalty import ClientCategory, LoyaltyTransaction, UserSettings  # noqa: F401
from models.approval import SyncApproval  # noqa: F401
from models.token import DeviceToken  # noqa: F401
from models.audit import SignalEvent  # noqa: F401
from models.crm import (  # noqa: F401
    Company, Pipeline, Stage, Contact, Deal, Activity, CRMNote,
)
