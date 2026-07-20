"""
POS Full Package — all Django ORM models.

Managed models (app_label="pos_full"):
  pos.py    — Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee
  menu.py   — MenuItem, Menu, MenuItemAssignment
  node.py   — Node, Heartbeat, NodeEvent
  config.py — DeviceConfig, MasterDevice, CloudLink
  sync.py   — SyncLog

Rust-mirror models (app_label="posapp", managed=False):
  core.py      — AppSettings, Category, Product, DeliveryType, EmployeeType
  sales.py     — Customer, Sale, SaleItem, LoyaltyTransaction
  people.py    — Employee, EmployeeSchedule, Payroll, User, Role, UserRole
  inventory.py — Ingredient, Recipe, Supplier, PurchaseOrder, etc.
  ops.py       — KitchenTicket, SupportTicket, ReceiptTemplate, TaxReport, ReportMetadata
  crm.py       — CRMCompany, CRMContact, CRMPipeline, etc.

NOTE: This __init__.py is minimal — only imports AppConfig to avoid
premature model loading during Django app registry initialization
(makemigrations / migrate). Server code and tests import directly
from sub-modules:
    from models.pos import Category, Product, Customer, ...
    from models.menu import MenuItem, Menu, MenuItemAssignment
    from models.node import Node, Heartbeat, NodeEvent
    from models.posapp import Product as PosProduct, ...
"""

from models.apps import PosFullConfig  # noqa: F401 - register AppConfig
