"""
POS Full Package — all Django ORM models.

Managed models (app_label="pos_full"):
  pos.py       — Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee
  menu.py      — MenuItem, Menu, MenuItemAssignment
  node.py      — Node, Heartbeat, NodeEvent
  config.py    — DeviceConfig, MasterDevice, CloudLink
  sync.py      — SyncLog
  inventory.py — Supplier, PurchaseOrder, PurchaseOrderItem
  ops.py       — KitchenTicket, SupportTicket

NOTE: This __init__.py is minimal — only imports AppConfig to avoid
premature model loading during Django app registry initialization
(makemigrations / migrate). Server code and tests import directly
from sub-modules:
    from models.pos import Category, Product, Customer, ...
    from models.inventory import Supplier, PurchaseOrder, ...
    from models.ops import KitchenTicket, SupportTicket
"""

from .apps import PosFullConfig  # noqa: F401 - register AppConfig
