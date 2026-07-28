"""
CRM — Routable Components Site Configuration
=============================================

Defines the Application and Site hierarchy for the django-fusion
routable-components routing system.

Mount in www/urls.py::

    from www.core.routes import site
    urlpatterns += [path("crm/", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))]

Generated URL prefix: /crm/
  /crm/dashboard/
  /crm/inventory/items/
  /crm/inventory/categories/
  /crm/inventory/deliveries/
  /crm/transactions/sales/
  /crm/transactions/purchases/
  /crm/transactions/new-sale/
  /crm/invoices/
  /crm/bills/
  /crm/accounts/customers/
  /crm/accounts/vendors/
  /crm/accounts/staff/
"""

from __future__ import annotations

from django_fusion.comp.routes import Application, Site, viewprop


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardApp(Application):
    """CRM main dashboard."""

    title = "Dashboard"
    icon = "dashboard"
    app_name = "dashboard"

    @viewprop
    def viewsets(self):
        from plugins.inventory.components import CRMDashboardComponent
        return [CRMDashboardComponent()]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated


# ---------------------------------------------------------------------------
# Inventory Application
# ---------------------------------------------------------------------------

class InventoryApp(Application):
    """Inventory — items, categories, deliveries."""

    title = "Inventory"
    icon = "inventory_2"
    app_name = "inventory"

    @viewprop
    def viewsets(self):
        from plugins.inventory.viewsets import (
            ItemViewset,
            CategoryViewset,
            DeliveryViewset,
        )
        from plugins.inventory.components import ItemListFragment
        return [
            ItemViewset(),
            CategoryViewset(),
            DeliveryViewset(),
            ItemListFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated


# ---------------------------------------------------------------------------
# Transactions Application
# ---------------------------------------------------------------------------

class TransactionsApp(Application):
    """Sales and purchases."""

    title = "Transactions"
    icon = "receipt_long"
    app_name = "transactions"

    @viewprop
    def viewsets(self):
        from plugins.transactions_app.viewsets import (
            SaleViewset,
            PurchaseViewset,
        )
        from plugins.transactions_app.components import (
            SaleCreateComponent,
            SaleListFragment,
        )
        return [
            SaleViewset(),
            PurchaseViewset(),
            SaleCreateComponent(),
            SaleListFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated


# ---------------------------------------------------------------------------
# Invoices Application
# ---------------------------------------------------------------------------

class InvoicesApp(Application):
    """Invoices management."""

    title = "Invoices"
    icon = "receipt"
    app_name = "invoices"

    @viewprop
    def viewsets(self):
        from plugins.invoice_app.viewsets import InvoiceViewset
        return [InvoiceViewset()]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated


# ---------------------------------------------------------------------------
# Bills Application
# ---------------------------------------------------------------------------

class BillsApp(Application):
    """Bills management."""

    title = "Bills"
    icon = "payments"
    app_name = "bills"

    @viewprop
    def viewsets(self):
        from plugins.bills_app.viewsets import BillViewset
        return [BillViewset()]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated


# ---------------------------------------------------------------------------
# Accounts Application
# ---------------------------------------------------------------------------

class AccountsApp(Application):
    """Customers, vendors, and staff profiles."""

    title = "Accounts"
    icon = "people"
    app_name = "accounts_app"

    @viewprop
    def viewsets(self):
        from plugins.accounts_app.viewsets import (
            CustomerViewset,
            VendorViewset,
            StaffProfileViewset,
        )
        from plugins.accounts_app.components import CustomerListFragment
        return [
            CustomerViewset(),
            VendorViewset(),
            StaffProfileViewset(),
            CustomerListFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated


# ---------------------------------------------------------------------------
# Site
# ---------------------------------------------------------------------------

site = Site(
    title="CRM",
    viewsets=[
        DashboardApp(),
        InventoryApp(),
        TransactionsApp(),
        InvoicesApp(),
        BillsApp(),
        AccountsApp(),
    ],
)
