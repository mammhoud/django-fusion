"""
FormintModule — module-organized POS navigation backed by django-fusion Module/Application.

Provides hierarchical navigation context consumed by:
- ``formint.fusion.navigation_api`` → GET /api/v1/navigation/ (JSON)
- Astro Layout.astro → client-side sidenav renderer

The site is organized into 7 business modules, each represented by an
``Application`` subclass.  Each Application declares its own ``menu_title``,
``menu_icon``, color accent, and ordered list of child routes.

Frontend integration
---------------------
The ``get_navigation_context()`` method returns a nested dict::

    {
        "brand": { "label": "Formint POS", "href": "/" },
        "modules": [
            {
                "id": "pos", "label": "Point of Sale", "icon": "shopping_cart",
                "color": "#6366f1",  "routes": [ ... ]
            },
            ...
        ]
    }

The Astro Layout fetches this from ``/api/v1/navigation/`` at mount time and
renders a collapsible sidenav with module groups.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django_fusion.routes.core.sites import Application, Module


# ── Route descriptor ────────────────────────────────────────────────────────


@dataclass
class NavRoute:
    """A single navigation route within a module."""

    label: str
    href: str
    icon: str = ""
    badge: str = ""          # e.g. "NEW", "BETA"
    show_in_nav: bool = True


# ── Module Applications ──────────────────────────────────────────────────────


class POSApplication(Application):
    """Point of Sale — sales, products, customers, inventory, suppliers."""

    title = "Point of Sale"
    icon = "shopping_cart"
    app_name = "pos"
    primary_color = "#6366f1"  # indigo
    menu_order = 10

    def get_module_routes(self) -> list[NavRoute]:
        return [
            NavRoute("Sale Register", "/pos/sale/", "cart", show_in_nav=True),
            NavRoute("Products", "/pos/products/", "inventory", show_in_nav=True),
            NavRoute("Customers", "/pos/customers/", "people", show_in_nav=True),
            NavRoute("Inventory", "/pos/inventory/", "warehouse", show_in_nav=True),
            NavRoute("Suppliers", "/pos/suppliers/", "local_shipping", show_in_nav=True),
        ]


class KitchenApplication(Application):
    """Kitchen Display System — KDS tickets, recipes."""

    title = "Kitchen & KDS"
    icon = "restaurant"
    app_name = "kitchen"
    primary_color = "#f59e0b"  # amber
    menu_order = 20

    def get_module_routes(self) -> list[NavRoute]:
        return [
            NavRoute("Kitchen Display", "/kitchen/", "room_service", show_in_nav=True),
            NavRoute("Recipes", "/kitchen/recipes/", "menu_book", show_in_nav=True),
        ]


class HRApplication(Application):
    """Human Resources — employees, schedules, payroll, roles."""

    title = "HR & Staff"
    icon = "people"
    app_name = "hr"
    primary_color = "#10b981"  # emerald
    menu_order = 30

    def get_module_routes(self) -> list[NavRoute]:
        return [
            NavRoute("Employees", "/hr/employees/", "badge", show_in_nav=True),
            NavRoute("Schedules", "/hr/schedules/", "calendar_month", show_in_nav=True),
            NavRoute("Payroll", "/hr/payroll/", "payments", show_in_nav=True),
            NavRoute("Roles", "/hr/roles/", "shield", show_in_nav=True),
        ]


class CRMApplication(Application):
    """Customer Relationship Management — contacts, companies, deals."""

    title = "CRM"
    icon = "contact_page"
    app_name = "crm"
    primary_color = "#3b82f6"  # blue
    menu_order = 40

    def get_module_routes(self) -> list[NavRoute]:
        return [
            NavRoute("Dashboard", "/crm/dashboard", "dashboard", show_in_nav=True),
            NavRoute("Contacts", "/crm/contacts", "contacts", show_in_nav=True),
            NavRoute("Companies", "/crm/companies", "business", show_in_nav=True),
            NavRoute("Deals", "/crm/deals", "handshake", show_in_nav=True),
            NavRoute("Pipeline", "/crm/pipelines", "view_kanban", show_in_nav=True),
            NavRoute("Activities", "/crm/activities", "task", show_in_nav=True),
            NavRoute("Notes", "/crm/notes", "sticky_note_2", show_in_nav=True),
        ]


class DataApplication(Application):
    """Analytics & Data — transactions, reports, fusion debug."""

    title = "Data & Analytics"
    icon = "analytics"
    app_name = "data"
    primary_color = "#8b5cf6"  # violet
    menu_order = 50

    def get_module_routes(self) -> list[NavRoute]:
        return [
            NavRoute("Dashboard", "/data/", "insights", show_in_nav=True),
            NavRoute("Transactions", "/pos/transactions/", "receipt_long", show_in_nav=True),
            NavRoute("Reports", "/admin/reports/", "assessment", show_in_nav=True),
            NavRoute("Fusion", "/fusion/", "science", show_in_nav=True),
        ]


class OperationsApplication(Application):
    """Operations — coupons, delivery, shifts, sync, nodes, webhooks, approvals."""

    title = "Operations"
    icon = "settings_applications"
    app_name = "ops"
    primary_color = "#ef4444"  # red
    menu_order = 60

    def get_module_routes(self) -> list[NavRoute]:
        return [
            NavRoute("Coupons", "/ops/coupons/", "confirmation_number", show_in_nav=True),
            NavRoute("Delivery Types", "/ops/delivery-types/", "delivery_dining", show_in_nav=True),
            NavRoute("Delivery Zones", "/ops/delivery-zones/", "map", show_in_nav=True),
            NavRoute("Shifts", "/ops/shifts/", "schedule", show_in_nav=True),
            NavRoute("Sync Center", "/ops/sync/", "sync", show_in_nav=True, badge="NEW"),
            NavRoute("Nodes", "/ops/nodes/", "hub", show_in_nav=False),
        ]


class AdminApplication(Application):
    """Administration — settings, notes, support, API keys, about."""

    title = "Administration"
    icon = "admin_panel_settings"
    app_name = "admin"
    primary_color = "#64748b"  # slate
    menu_order = 90

    def get_module_routes(self) -> list[NavRoute]:
        return [
            NavRoute("Settings", "/admin/settings/", "settings", show_in_nav=True),
            NavRoute("Notes", "/admin/notes/", "note", show_in_nav=True),
            NavRoute("Support", "/admin/support/", "support", show_in_nav=True),
            NavRoute("API Keys", "/admin/api-keys/", "key", show_in_nav=False),
            NavRoute("About", "/admin/about/", "info", show_in_nav=False),
        ]


# ── Module ──────────────────────────────────────────────────────────────────


class FormintModule(Module):
    """Top-level module — aggregates module Applications into the full nav tree.

    Each Application registered here contributes its module definition to the
    ``/api/v1/navigation/`` response consumed by the Astro Layout sidenav.
    """

    title = "Formint POS"
    app_name = "formint_module"
    primary_color = "#6366f1"

    # Ordered list of modules that appear in the sidenav.
    MODULES: list[type[Application]] = [
        POSApplication,
        KitchenApplication,
        HRApplication,
        CRMApplication,
        DataApplication,
        OperationsApplication,
        AdminApplication,
    ]

    # ── Navigation context (consumed by /api/v1/navigation/) ─────────────

    def get_navigation_context(self, request: Any = None) -> dict[str, Any]:
        """Return the full hierarchical nav tree for the frontend sidenav.

        Returns::

            {
                "brand": { "label": "Formint POS", "href": "/", "tag": "Pro·P2" },
                "modules": [
                    {
                        "id": "pos", "label": "Point of Sale",
                        "icon": "shopping_cart", "color": "#6366f1",
                        "routes": [
                            { "label": "Sale Register", "href": "/pos/sale/",
                              "icon": "cart", "active": false, "badge": "" },
                            ...
                        ]
                    },
                    ...
                ]
            }
        """
        current_path = getattr(request, "path", "") if request else ""
        current_clean = current_path.rstrip("/")

        modules: list[dict[str, Any]] = []

        for mod_cls in self.MODULES:
            inst = mod_cls()
            routes: list[dict[str, Any]] = []
            for r in inst.get_module_routes():
                if not r.show_in_nav:
                    continue
                routes.append(
                    {
                        "label": r.label,
                        "href": r.href,
                        "icon": r.icon,
                        "active": current_clean == r.href.rstrip("/"),
                        "badge": r.badge,
                    }
                )

            modules.append(
                {
                    "id": mod_cls.app_name,
                    "label": mod_cls.title,
                    "icon": mod_cls.icon,
                    "color": getattr(mod_cls, "primary_color", "#6366f1"),
                    "order": getattr(mod_cls, "menu_order", 99),
                    "routes": routes,
                    # A module is "active" if any of its routes match the current path
                    "active": any(r["active"] for r in routes),
                }
            )

        # Sort by menu_order for stable rendering
        modules.sort(key=lambda m: m["order"])

        return {
            "brand": {
                "label": "Formint POS",
                "href": "/",
                "tag": "Pro · P2",
            },
            "modules": modules,
        }


# Singleton instance — used by the API and view handlers.
formint_module = FormintModule()
