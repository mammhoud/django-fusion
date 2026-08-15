"""
Seed realistic demo data for the Formint POS server.

Covers every resource the HTMX tables and the branch summary render:

  * ``/htmx/tables/products/``        → Product (+ Category)
  * ``/htmx/tables/categories/``      → Category
  * ``/htmx/tables/customers/``       → Customer (+ ClientCategory)
  * ``/htmx/tables/client-categories/`` → ClientCategory (loyalty tiers)
  * ``/htmx/tables/sales/``           → Sale + SaleItem
  * ``/htmx/tables/suppliers/``       → Supplier (+ PurchaseOrder)

  * ``/htmx/branches/summary/``       → Node (branches), Sale (orders today),
                                        SyncLog (sync status)

Also seeds the supporting managed models (Menu, Employee, Ingredient, Recipe,
ReceiptTemplate, Role, InventoryAdjustment, LoyaltyTransaction, UserSettings)
so the admin panel and Ninja API have realistic rows.

Usage::

    python manage.py seed_demo               # seed only what is missing
    python manage.py seed_demo --force       # wipe + re-seed everything
    python manage.py seed_demo --models products,customers   # partial
    python manage.py seed_demo --dry-run     # print what would happen
"""

from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from models.crm import Company, Contact, Deal
from models.extra import (
    Ingredient, InventoryAdjustment, ReceiptTemplate, Recipe, Role,
)
from models.hr import Payroll, TaxReport
from models.inventory import PurchaseOrder, PurchaseOrderItem, Supplier
from models.loyalty import (
    ClientCategory, LoyaltyTransaction, UserSettings,
)
from models.menu import Menu, MenuItem, MenuItemAssignment
from models.node import Node, NodeEvent
from models.ops import KitchenTicket, SupportTicket
from models.pos import Category, Customer, Employee, Product, Sale, SaleItem
from models.sync import SyncLog


class Command(BaseCommand):
    help = "Seed realistic demo data for the Formint POS server."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing demo data and re-seed from scratch.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be seeded without writing anything.",
        )
        parser.add_argument(
            "--models",
            default="",
            help="Comma-separated subset: products,categories,customers,"
                 "client-categories,sales,suppliers,purchase-orders,nodes,"
                 "sync-logs,menu,employees,inventory,crm,ops,settings",
        )

    # ── helpers ─────────────────────────────────────────────────────────────

    def _should_seed(self, name: str) -> bool:
        if not self.models_filter:
            return True
        return name in self.models_filter

    def _create(self, model, key_fields: dict, **extra) -> object | None:
        """Create-or-skip (or delete+recreate under --force)."""
        if self.dry_run:
            self.stdout.write(f"  [dry-run] would create {model.__name__}: {key_fields}")
            return None
        obj = model.objects.filter(**key_fields).first()
        if obj is not None:
            if self.force:
                obj.delete()
                obj = None
            else:
                return obj
        obj = model.objects.create(**key_fields, **extra)
        self.stdout.write(f"  + {model.__name__}: {obj}")
        return obj

    def _count(self, label: str, model) -> None:
        self.stdout.write(f"  {label}: {model.objects.count()} rows")

    # ── seed groups ─────────────────────────────────────────────────────────

    def seed_categories(self) -> None:
        if not self._should_seed("categories"):
            return
        self.stdout.write("Categories:")
        cats = [
            {"name": "Hot Drinks", "slug": "hot-drinks", "display_order": 1},
            {"name": "Cold Drinks", "slug": "cold-drinks", "display_order": 2},
            {"name": "Pastries", "slug": "pastries", "display_order": 3},
            {"name": "Sandwiches", "slug": "sandwiches", "display_order": 4},
            {"name": "Desserts", "slug": "desserts", "display_order": 5},
        ]
        for c in cats:
            self._create(
                Category,
                {"slug": c["slug"]},
                name=c["name"],
                display_order=c["display_order"],
                description=f"{c['name']} menu category",
            )
        self._count("  total", Category)

    def seed_products(self) -> None:
        if not self._should_seed("products"):
            return
        self.stdout.write("Products:")
        cats = {c.name: c for c in Category.objects.all()}
        prods = [
            {"name": "Cappuccino", "sku": "CAP-001", "price": "4.50",
             "cost_price": "1.80", "category": "Hot Drinks", "stock": 50,
             "desc": "Classic Italian cappuccino with steamed milk foam"},
            {"name": "Espresso", "sku": "ESP-001", "price": "3.00",
             "cost_price": "1.00", "category": "Hot Drinks", "stock": 120,
             "desc": "Single shot of rich, dark espresso"},
            {"name": "Iced Latte", "sku": "ICL-001", "price": "5.50",
             "cost_price": "2.20", "category": "Cold Drinks", "stock": 40,
             "desc": "Cold latte over ice"},
            {"name": "Mocha", "sku": "MOC-001", "price": "5.00",
             "cost_price": "2.00", "category": "Hot Drinks", "stock": 35,
             "desc": "Espresso with chocolate and steamed milk"},
            {"name": "Chocolate Muffin", "sku": "MUF-001", "price": "3.75",
             "cost_price": "1.50", "category": "Pastries", "stock": 25,
             "desc": "Double-chocolate muffin"},
            {"name": "Croissant", "sku": "CRO-001", "price": "2.50",
             "cost_price": "0.90", "category": "Pastries", "stock": 60,
             "desc": "Buttery, flaky French croissant"},
            {"name": "Chicken Sandwich", "sku": "CS-001", "price": "8.50",
             "cost_price": "3.40", "category": "Sandwiches", "stock": 20,
             "desc": "Grilled chicken with lettuce and tomato"},
            {"name": "Club Sandwich", "sku": "CLS-001", "price": "9.00",
             "cost_price": "3.60", "category": "Sandwiches", "stock": 18,
             "desc": "Triple-decker with turkey, bacon and avocado"},
            {"name": "Cheesecake", "sku": "CHK-001", "price": "6.50",
             "cost_price": "2.60", "category": "Desserts", "stock": 15,
             "desc": "New York style cheesecake with berry topping"},
        ]
        for p in prods:
            self._create(
                Product,
                {"sku": p["sku"]},
                name=p["name"],
                category=cats.get(p["category"]),
                price=Decimal(p["price"]),
                cost_price=Decimal(p["cost_price"]),
                stock_quantity=p["stock"],
                low_stock_threshold=10,
                description=p["desc"],
                barcode=f"4{p['sku'].split('-')[1]}{p['sku'].split('-')[0][0]}",
            )
        self._count("  total", Product)

    def seed_client_categories(self) -> None:
        if not self._should_seed("client-categories"):
            return
        self.stdout.write("Client categories (loyalty tiers):")
        tiers = [
            {"name": "Bronze", "min_points": 0, "points_per_currency": 1,
             "points_to_currency": 100, "discount_rate": "0.00",
             "perks": ["Standard accrual"]},
            {"name": "Silver", "min_points": 500, "points_per_currency": 1,
             "points_to_currency": 90, "discount_rate": "5.00",
             "perks": ["5% discount", "Birthday bonus points"]},
            {"name": "Gold", "min_points": 2000, "points_per_currency": 2,
             "points_to_currency": 80, "discount_rate": "10.00",
             "perks": ["10% discount", "Priority support", "Free delivery"]},
        ]
        for t in tiers:
            self._create(
                ClientCategory,
                {"name": t["name"]},
                description=f"{t['name']} loyalty tier",
                min_points=t["min_points"],
                points_per_currency=t["points_per_currency"],
                points_to_currency=t["points_to_currency"],
                discount_rate=Decimal(t["discount_rate"]),
                perks=t["perks"],
            )
        self._count("  total", ClientCategory)

    def seed_customers(self) -> None:
        if not self._should_seed("customers"):
            return
        self.stdout.write("Customers:")
        tiers = {t.name: t for t in ClientCategory.objects.all()}
        custs = [
            {"first": "John", "last": "Doe", "email": "john.doe@example.com",
             "phone": "+1 555 0100", "points": 2400, "spent": "1250.00",
             "tier": "Gold"},
            {"first": "Jane", "last": "Smith", "email": "jane.smith@example.com",
             "phone": "+1 555 0101", "points": 780, "spent": "430.50",
             "tier": "Silver"},
            {"first": "Ahmed", "last": "Hassan", "email": "ahmed@example.com",
             "phone": "+1 555 0102", "points": 120, "spent": "95.75",
             "tier": "Bronze"},
            {"first": "Maria", "last": "Garcia", "email": "maria@example.com",
             "phone": "+1 555 0103", "points": 3150, "spent": "1870.25",
             "tier": "Gold"},
            {"first": "Liam", "last": "Brown", "email": "liam@example.com",
             "phone": "+1 555 0104", "points": 45, "spent": "32.00",
             "tier": "Bronze"},
        ]
        for c in custs:
            self._create(
                Customer,
                {"email": c["email"]},
                first_name=c["first"],
                last_name=c["last"],
                phone=c["phone"],
                loyalty_points=c["points"],
                client_category=tiers.get(c["tier"]),
                total_spent=Decimal(c["spent"]),
                notes=f"Demo customer — {c['tier']} tier",
            )
        self._count("  total", Customer)

    def seed_suppliers(self) -> None:
        if not self._should_seed("suppliers"):
            return
        self.stdout.write("Suppliers:")
        supps = [
            {"name": "Bean Supply Co", "contact": "Bob Vendor",
             "email": "sales@beansupply.com", "phone": "+1 555 0200",
             "terms": "net30"},
            {"name": "Dairy Fresh", "contact": "Sara Milkman",
             "email": "orders@dairyfresh.com", "phone": "+1 555 0201",
             "terms": "net15"},
            {"name": "Bakery Goods Inc", "contact": "Chef Pierre",
             "email": "hello@bakerygoods.com", "phone": "+1 555 0202",
             "terms": "net30"},
            {"name": "Fresh Produce Co", "contact": "Ana Green",
             "email": "orders@freshproduce.com", "phone": "+1 555 0203",
             "terms": "cod"},
        ]
        for s in supps:
            self._create(
                Supplier,
                {"name": s["name"]},
                contact_name=s["contact"],
                email=s["email"],
                phone=s["phone"],
                payment_terms=s["terms"],
                address="123 Market St",
            )
        self._count("  total", Supplier)

    def seed_sales(self) -> None:
        if not self._should_seed("sales"):
            return
        self.stdout.write("Sales + sale items:")
        if Sale.objects.exists() and not self.force:
            self.stdout.write(f"  {Sale.objects.count()} existing, skipping (use --force to re-seed)")
            return
        custs = list(Customer.objects.all())
        prods = list(Product.objects.all())
        now = timezone.now()
        today = now.date()
        # 8 sales today + 4 spread over the last 2 weeks
        dates = [now - timedelta(hours=h) for h in (1, 2, 3, 4, 5, 6, 7, 8)]
        dates += [now - timedelta(days=d) for d in (2, 5, 9, 13)]
        for i, d in enumerate(dates):
            customer = custs[i % len(custs)] if custs else None
            items = random.sample(prods, k=min(3, len(prods)))
            subtotal = sum(Decimal(str(p.price)) for p in items)
            tax = (subtotal * Decimal("0.08")).quantize(Decimal("0.01"))
            total = subtotal + tax
            status = "completed" if d.date() < today or i < 6 else "pending"
            if self.dry_run:
                self.stdout.write(f"  [dry-run] would create Sale for {customer}")
                continue
            sale = Sale.objects.create(
                customer=customer,
                sale_date=d,
                subtotal=subtotal,
                tax_amount=tax,
                total=total,
                payment_method=random.choice(["cash", "card", "mobile"]),
                status=status,
            )
            self.stdout.write(f"  + Sale #{sale.id}: {total} ({sale.payment_method})")
            for p in items:
                SaleItem.objects.create(
                    sale=sale,
                    product=p,
                    product_name=p.name,
                    quantity=1,
                    unit_price=p.price,
                    line_total=p.price,
                )
            # Loyalty points for the customer (10 pts per $1)
            if customer:
                LoyaltyTransaction.objects.create(
                    customer=customer,
                    sale=sale,
                    transaction_type="earn",
                    points_change=int(total),
                    balance_after=customer.loyalty_points + int(total),
                    reason="Purchase",
                )
        self._count("  total", Sale)

    def seed_purchase_orders(self) -> None:
        if not self._should_seed("purchase-orders"):
            return
        self.stdout.write("Purchase orders:")
        if PurchaseOrder.objects.exists() and not self.force:
            self.stdout.write(f"  {PurchaseOrder.objects.count()} existing, skipping (use --force to re-seed)")
            return
        supps = list(Supplier.objects.all())
        prods = list(Product.objects.all())
        for i, s in enumerate(supps):
            po = self._create(
                PurchaseOrder,
                {"reference_number": f"PO-2026-{i + 1:03d}"},
                supplier=s,
                status=random.choice(["draft", "ordered", "received"]),
                total_amount=Decimal("0.00"),
                expected_date=timezone.now().date() + timedelta(days=7),
                notes="Demo purchase order",
            )
            if po is None:
                continue
            line = prods[i % len(prods)] if prods else None
            qty = 10
            cost = line.price if line else Decimal("1.00")
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=line,
                product_name=line.name if line else "Generic item",
                quantity=qty,
                cost_per_unit=cost,
            )
            po.total_amount = cost * qty
            po.save(update_fields=["total_amount"])
        self._count("  total", PurchaseOrder)

    def seed_nodes(self) -> None:
        if not self._should_seed("nodes"):
            return
        self.stdout.write("Nodes (branches):")
        if Node.objects.exists() and not self.force:
            self.stdout.write(f"  {Node.objects.count()} existing, skipping (use --force to re-seed)")
            return
        now = timezone.now()
        nodes = [
            {"node_id": "main-branch", "hostname": "pos-main", "node_type": "pos-full",
             "status": "online", "ip": "10.0.0.10", "port": 8767},
            {"node_id": "kitchen-branch", "hostname": "pos-kitchen", "node_type": "pos-solo",
             "status": "online", "ip": "10.0.0.11", "port": 8768},
            {"node_id": "bar-branch", "hostname": "pos-bar", "node_type": "pos-minimal",
             "status": "degraded", "ip": "10.0.0.12", "port": 8769},
        ]
        for n in nodes:
            node = self._create(
                Node,
                {"node_id": n["node_id"]},
                hostname=n["hostname"],
                node_type=n["node_type"],
                status=n["status"],
                version="2.0.0",
                api_version="1.0",
                ip_address=n["ip"],
                port=n["port"],
                product_count=Product.objects.count(),
                transaction_count=Sale.objects.count(),
                customer_count=Customer.objects.count(),
                last_synced_at=now - timedelta(minutes=5),
            )
            if node is not None:
                NodeEvent.objects.create(
                    node_id=node.node_id,
                    event_type="heartbeat",
                    description=f"{n['hostname']} reported online",
                )
        self._count("  total", Node)

    def seed_sync_logs(self) -> None:
        if not self._should_seed("sync-logs"):
            return
        self.stdout.write("Sync logs:")
        if SyncLog.objects.exists() and not self.force:
            self.stdout.write(f"  {SyncLog.objects.count()} existing, skipping (use --force to re-seed)")
            return
        now = timezone.now()
        entries = [
            {"entity": "products", "dir": "push", "status": "success", "dur": 120},
            {"entity": "sales", "dir": "push", "status": "success", "dur": 95},
            {"entity": "customers", "dir": "push", "status": "success", "dur": 60},
            {"entity": "inventory", "dir": "pull", "status": "success", "dur": 150},
        ]
        for e in entries:
            self._create(
                SyncLog,
                {"node_id": "main-branch", "entity_type": e["entity"],
                 "direction": e["dir"], "status": e["status"],
                 "created_at": now - timedelta(minutes=10)},
                payload_size=2048,
                duration_ms=e["dur"],
            )
        self._count("  total", SyncLog)

    def seed_menu(self) -> None:
        if not self._should_seed("menu"):
            return
        self.stdout.write("Menus + menu items:")
        if Menu.objects.exists() and not self.force:
            self.stdout.write(f"  {MenuItem.objects.count()} items existing, skipping (use --force to re-seed)")
            return
        menu = self._create(Menu, {"name": "Main Menu"}, slug="main-menu")
        if menu is None:
            return
        cats = {c.name: c for c in Category.objects.all()}
        items = [
            {"name": "Cappuccino", "cat": "Hot Drinks", "price": "4.50"},
            {"name": "Iced Latte", "cat": "Cold Drinks", "price": "5.50"},
            {"name": "Chicken Sandwich", "cat": "Sandwiches", "price": "8.50"},
            {"name": "Cheesecake", "cat": "Desserts", "price": "6.50"},
        ]
        for idx, it in enumerate(items):
            item = self._create(
                MenuItem,
                {"name": it["name"]},
                category=cats.get(it["cat"]),
                slug=it["name"].lower().replace(" ", "-"),
                price=Decimal(it["price"]),
                description=f"From the {it['cat']} section",
                is_available=True,
                is_featured=it["name"] == "Cheesecake",
                display_order=idx,
                preparation_time=10,
            )
            if item is not None and not self.dry_run:
                MenuItemAssignment.objects.create(menu=menu, item=item, display_order=idx)
        self._count("  total", MenuItem)

    def seed_employees(self) -> None:
        if not self._should_seed("employees"):
            return
        self.stdout.write("Employees:")
        staff = [
            {"first": "Alice", "last": "Worker", "email": "alice@formint.pos",
             "role": "cashier", "pin": "1234"},
            {"first": "Bob", "last": "Manager", "email": "bob@formint.pos",
             "role": "manager", "pin": "2345"},
            {"first": "Chef", "last": "Cooks", "email": "chef@formint.pos",
             "role": "kitchen", "pin": "3456"},
            {"first": "Sara", "last": "Server", "email": "sara@formint.pos",
             "role": "server", "pin": "4567"},
        ]
        for e in staff:
            self._create(
                Employee,
                {"email": e["email"]},
                first_name=e["first"],
                last_name=e["last"],
                phone="+1 555 0300",
                role=e["role"],
                pin_code=e["pin"],
                hourly_rate=Decimal("15.00"),
            )
        self._count("  total", Employee)

    def seed_inventory(self) -> None:
        if not self._should_seed("inventory"):
            return
        self.stdout.write("Ingredients + adjustments:")
        ingredients = [
            {"name": "Coffee Beans", "unit": "kg", "qty": "50.0", "cost": "15.00"},
            {"name": "Milk", "unit": "liter", "qty": "30.0", "cost": "2.50"},
            {"name": "Sugar", "unit": "kg", "qty": "20.0", "cost": "1.50"},
            {"name": "All-Purpose Flour", "unit": "kg", "qty": "25.0", "cost": "1.20"},
            {"name": "Dark Chocolate", "unit": "kg", "qty": "15.0", "cost": "8.00"},
        ]
        ing_objs = []
        for ing in ingredients:
            obj = self._create(
                Ingredient,
                {"name": ing["name"]},
                unit=ing["unit"],
                current_quantity=Decimal(ing["qty"]),
                reorder_level=Decimal("10.0"),
                reorder_quantity=Decimal("20.0"),
                cost_per_unit=Decimal(ing["cost"]),
            )
            if obj:
                ing_objs.append(obj)
        if ing_objs:
            adj = self._create(
                InventoryAdjustment,
                {"ingredient": ing_objs[0], "reason": "return"},
                quantity=Decimal("20.0"),
                adjustment_type="addition",
                notes="Weekly delivery from Bean Supply Co",
                created_by="system",
            )
        self._count("  total", Ingredient)

    def seed_recipes(self) -> None:
        if not self._should_seed("recipes"):
            return
        self.stdout.write("Recipes:")
        for p in Product.objects.all()[:5]:
            self._create(
                Recipe,
                {"product": p},
                name=f"Recipe: {p.name}",
                instructions=f"1. Prepare {p.name} according to standard recipe.",
                yield_quantity=Decimal("1"),
            )
        self._count("  total", Recipe)

    def seed_roles(self) -> None:
        if not self._should_seed("roles"):
            return
        self.stdout.write("Roles:")
        roles = [
            {"name": "Admin", "perms": ["*"]},
            {"name": "Manager", "perms": ["manage_products", "manage_sales"]},
            {"name": "Cashier", "perms": ["manage_sales"]},
        ]
        for r in roles:
            self._create(
                Role,
                {"name": r["name"]},
                description=f"{r['name']} role",
                permissions={"permissions": r["perms"]},
            )
        self._count("  total", Role)

    def seed_receipt_templates(self) -> None:
        if not self._should_seed("receipt-templates"):
            return
        self.stdout.write("Receipt templates:")
        tpls = [
            {"name": "Standard Receipt", "default": True},
            {"name": "Commercial Invoice", "default": False},
            {"name": "Minimal Receipt", "default": False},
        ]
        for t in tpls:
            self._create(
                ReceiptTemplate,
                {"name": t["name"]},
                description=f"{t['name']} template",
                template_html="<div>{{restaurant_name}}</div>",
                template_css="body { font-family: monospace; }",
                is_default=t["default"],
            )
        self._count("  total", ReceiptTemplate)

    def seed_settings(self) -> None:
        if not self._should_seed("settings"):
            return
        self.stdout.write("UserSettings:")
        User = get_user_model()
        users = User.objects.filter(is_superuser=True)
        for u in users:
            self._create(
                UserSettings,
                {"user": u},
                restaurant_name="Formint POS Downtown",
                address="1 Main Street",
                phone="+1 555 0001",
                email="pos@formint.cloud",
                tax_rate=Decimal("8.00"),
                currency="USD",
                opening_time="09:00",
                closing_time="22:00",
                receipt_footer="Thank you for your business!",
                dine_in_tables=12,
                delivery_fee=Decimal("2.00"),
                delivery_fee_per_km=Decimal("0.50"),
                theme="dark",
                language="en",
                notifications_enabled=True,
            )
        self._count("  total", UserSettings)

    def seed_crm(self) -> None:
        if not self._should_seed("crm"):
            return
        self.stdout.write("CRM:")
        company = self._create(
            Company, {"name": "Acme Corp"},
            website="acme.example.com",
            industry="Retail",
        )
        if company is not None:
            contact = self._create(
                Contact,
                {"email": "jane@acme.example.com"},
                first_name="Jane", last_name="Contact",
                company=company,
                job_title="CEO",
            )
            if contact is not None:
                self._create(
                    Deal, {"title": "Bulk catering deal", "contact": contact},
                    value=Decimal("25000.00"),
                    pipeline=None,
                    stage=None,
                )
        self._count("  total", Company)

    def seed_ops(self) -> None:
        if not self._should_seed("ops"):
            return
        self.stdout.write("Ops (kitchen + support tickets):")
        for s in Sale.objects.all()[:3]:
            self._create(
                KitchenTicket,
                {"sale": s, "status": "completed"},
                priority=1,
                notes="Standard prep",
            )
        self._create(
            SupportTicket,
            {"subject": "Printer not working", "email": "owner@formint.cloud"},
            name="Store Owner",
            message="The receipt printer on the main till is offline.",
            status="open",
        )
        self._count("  total", KitchenTicket)

    # ── entry point ─────────────────────────────────────────────────────────

    def handle(self, *args, **options):
        self.force = options["force"]
        self.dry_run = options["dry_run"]
        self.models_filter = {
            m.strip() for m in options["models"].split(",") if m.strip()
        }

        if self.dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — nothing will be written.\n"))

        if self.force and not self.dry_run:
            self.stdout.write(self.style.WARNING("--force: wiping existing demo data...\n"))
            for model in (
                KitchenTicket, SupportTicket, SyncLog, NodeEvent, Node,
                SaleItem, Sale, LoyaltyTransaction, PurchaseOrderItem,
                PurchaseOrder, Customer, Product, Category, Supplier,
                Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
                Employee, Payroll, TaxReport, MenuItem, Menu,
                MenuItemAssignment, ClientCategory, UserSettings,
                Company, Contact, Deal,
            ):
                model.objects.all().delete()

        # Dependencies first: categories → products → customers; suppliers →
        # purchase orders; sales need products + customers.
        self.seed_categories()
        self.seed_client_categories()
        self.seed_products()
        self.seed_customers()
        self.seed_suppliers()
        self.seed_sales()
        self.seed_purchase_orders()
        self.seed_nodes()
        self.seed_sync_logs()
        self.seed_menu()
        self.seed_employees()
        self.seed_inventory()
        self.seed_recipes()
        self.seed_roles()
        self.seed_receipt_templates()
        self.seed_crm()
        self.seed_ops()
        self.seed_settings()

        if self.dry_run:
            self.stdout.write("\n" + self.style.WARNING("DRY RUN complete — no data written."))
            return

        self.stdout.write("\n" + self.style.SUCCESS("Seed complete — final counts:"))
        for label, model in (
            ("Categories", Category), ("Products", Product),
            ("ClientCategories", ClientCategory), ("Customers", Customer),
            ("Sales", Sale), ("SaleItems", SaleItem),
            ("Suppliers", Supplier), ("PurchaseOrders", PurchaseOrder),
            ("Nodes", Node), ("SyncLogs", SyncLog),
            ("Menus", Menu), ("MenuItems", MenuItem),
            ("Employees", Employee), ("Ingredients", Ingredient),
            ("Recipes", Recipe), ("Roles", Role),
            ("ReceiptTemplates", ReceiptTemplate),
        ):
            self._count(f"  {label}", model)
