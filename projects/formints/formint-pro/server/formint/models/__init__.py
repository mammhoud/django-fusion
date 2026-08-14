"""
Formint — model layer (re-exports the canonical pos_full models).

After the backend/ + server/ merge, both apps share a single Django model
layer: the ``models`` package (app_label="pos_full") is canonical — it is
the layer the Robyn server, the sync signals, and the Unfold admin all use.

The formint app (Ninja API, fusion render-mode, HTMX fragment handlers, and
the merged admin dashboard) operates on those same model classes.  This
module re-exports every model so ``from formint.models import Product``
keeps working for the merged code while avoiding duplicated table
definitions (models.E028 / reverse-accessor clashes).

Why this is safe:
* The pre-merge ``formint/models/*`` files were byte-for-byte copies of
  ``models/*`` except for ``app_label`` (formint vs pos_full) — same
  ``db_table``, same fields, same ``related_name``.
* Re-exporting means one set of tables, one migration chain
  (``models/migrations/``), one admin registration.

Like the canonical package, model discovery happens in the ``models.models``
sub-module during Django's phase-2 ``import_models()``; keep this package
light (no direct ``models.*`` imports at phase 1).
"""

from models.models import (  # noqa: F401 — imported during phase 2
    Activity,
    CRMNote,
    Currency,
    TaxProfile,
    Category,
    ClientCategory,
    CloudLink,
    Company,
    Contact,
    Customer,
    Deal,
    DeviceConfig,
    DeviceToken,
    Employee,
    EmployeeSchedule,
    Heartbeat,
    Ingredient,
    InventoryAdjustment,
    InventoryTransaction,
    KitchenTicket,
    LoyaltyTransaction,
    MasterDevice,
    Menu,
    MenuItem,
    MenuItemAssignment,
    Node,
    NodeEvent,
    Note,
    Payroll,
    Pipeline,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    ReceiptTemplate,
    Recipe,
    Role,
    Sale,
    SaleItem,
    SignalEvent,
    Stage,
    Supplier,
    SupportTicket,
    SyncApproval,
    SyncLog,
    TaxReport,
    UserSettings,
)
