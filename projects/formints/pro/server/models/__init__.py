"""
POS Full Package — Django ORM models.

Managed models (app_label="pos_full"):
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
  gaming.py    — GamingStation, GamingToken, GamingSession, GamingQueueEntry
  giftcard.py  — GiftCard, GiftCardTransaction
  tables.py    — RestaurantTable, TableReservation
  delivery.py  — DeliveryProvider, DeliveryOrder
  timeclock.py — TimeClockEntry
  kiosk.py     — KioskSession, KioskCartItem

IMPORTANT: Do NOT import model sub-modules here. Django imports the app
module (this package) during phase 1 of apps.populate() — before the app
registry is ready — and defining models at that point raises
AppRegistryNotReady. Model discovery happens in the `models.models`
sub-module, which Django loads in phase 2 via AppConfig.import_models()
(after apps_ready=True). Keep this package light.
"""

from .apps import PosFullConfig  # noqa: F401 - register AppConfig
