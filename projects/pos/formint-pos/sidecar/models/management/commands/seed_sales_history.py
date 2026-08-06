"""
Seed a rich 30-day sales history so the /data/ dashboard charts have real data.

Generates one month of realistic POS transactions (weekday/weekend volume
patterns, morning + lunch rushes, weighted product popularity, a payment-method
mix, and a small share of refunded/cancelled sales) wired to the existing demo
products and customers.

For every **completed** sale the command also creates a matching inventory
``out`` transaction and resets the sold products' ``Product.stock_quantity``
to a deterministic healthy baseline (``STOCK_BASELINE - sold_qty``), so the
inventory page reflects the 30-day sales volume without ever going negative.

NOTE: this overwrites the stock of every sold product (it does not simply
decrement) — run it only against demo data you're happy to replace.

Idempotent: every row created here is tagged ``notes="sales-history-seed"``
(sales) / ``notes="[sales-history-seed] ..."`` (inventory transactions), so
re-running the command removes the previous batch — including the stock
decrements (restored before delete) — before generating a fresh one.
Pre-existing sales are left untouched.

Usage::

    python manage.py seed_sales_history             # last 30 days
    python manage.py seed_sales_history --days 60   # longer window
    python manage.py seed_sales_history --dry-run   # preview only
"""

from __future__ import annotations

import random
from datetime import datetime, time as dtime, timedelta, timezone as dt_timezone
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import F, Sum
from django.utils import timezone

from models.pos import Customer, InventoryTransaction, Product, Sale, SaleItem

SEED_TAG = "sales-history-seed"
INV_SEED_PREFIX = f"[{SEED_TAG}]"

# Stock baseline: each sold product is reset to ``STOCK_BASELINE - sold_qty`` so
# demo stock always looks healthy (and never negative) regardless of the
# products' original seed_demo stock levels. Idempotent: cleanup restores the
# decrement, then the seed re-applies the same deterministic baseline.
STOCK_BASELINE = 250

# ── popularity weights (higher = sold more often) ────────────────────────────
PRODUCT_WEIGHTS = {
    "Cappuccino": 16, "Espresso": 10, "Latte": 14, "Mocha": 9, "Americano": 8,
    "Iced Latte": 9, "Iced Mocha": 6, "Lemonade": 7, "Smoothie": 6,
    "Chocolate Muffin": 10, "Croissant": 12, "Blueberry Scone": 6,
    "Chicken Sandwich": 8, "Club Sandwich": 7, "Veggie Wrap": 5,
    "Cheesecake": 6, "Tiramisu": 4, "Brownie": 7,
}
# products that sell in bigger multiples (cheap add-ons)
BULK_ITEMS = {"Espresso", "Americano", "Croissant", "Lemonade", "Brownie"}

# weighted business hours — morning rush (8–9) + lunch (12–13)
HOURS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
HOUR_WEIGHTS = [5, 16, 18, 12, 10, 14, 13, 7, 5, 3, 2, 1]

PAYMENTS = [("cash", 30), ("card", 45), ("mobile", 20), ("mixed", 5)]
STATUSES = [("completed", 92), ("refunded", 4), ("cancelled", 4)]
TAX_RATE = Decimal("0.08")


class Command(BaseCommand):
    help = "Seed 30 days of realistic demo sales history for the /data/ analytics."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=30,
            help="How many days of history to seed (default 30).",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print what would be seeded without writing anything.",
        )

    def handle(self, *args, **options):
        self.days = max(1, min(options["days"], 120))
        self.dry_run = options["dry_run"]

        random.seed(20260806)
        products = list(Product.objects.filter(is_active=True))
        if not products:
            self.stderr.write("No active products found — run `seed_demo` first.")
            return

        if self.dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — nothing will be written.\n"))
            self._preview(len(products))
            return

        self._cleanup_previous_seed()

        end = timezone.now().date() - timedelta(days=1)   # yesterday
        start = end - timedelta(days=self.days - 1)       # inclusive window
        custs = list(Customer.objects.all()[:200])

        weights = {p.id: PRODUCT_WEIGHTS.get(p.name, 5) for p in products}
        by_id = {p.id: p for p in products}
        sand_ids = {p.id for p in products
                    if p.category and p.category.name == "Sandwiches"}
        payment_pool = [p for p, _w in PAYMENTS for _ in range(_w)]
        status_pool = [s for s, _w in STATUSES for _ in range(_w)]

        sales: list[Sale] = []
        items: list[SaleItem] = []
        inv_lines: list[tuple[Sale, Product, int]] = []  # (sale, product, qty)
        stock_delta: dict[int, int] = {}

        for offset in range(self.days):
            day = start + timedelta(days=offset)
            growth = 0.85 + 0.30 * (offset / max(1, self.days - 1))  # slow growth
            wd = day.weekday()
            base = random.randint(10, 16) if wd >= 4 else random.randint(7, 12)
            if wd == 1:  # Tuesday is the slow day
                base = max(5, base - 3)
            n_sales = max(3, int(round(base * growth)))

            for _ in range(n_sales):
                hour = random.choices(HOURS, weights=HOUR_WEIGHTS)[0]
                sale_dt = timezone.make_aware(
                    datetime.combine(
                        day,
                        dtime(hour, random.randint(0, 59), random.randint(0, 59)),
                    ),
                    dt_timezone.utc,
                )

                # pick 1–4 distinct products (lunch hours lean toward sandwiches)
                wlist = [weights[p.id] for p in products]
                if hour in (11, 12, 13, 14):
                    wlist = [w * 3 if p.id in sand_ids else w
                             for p, w in zip(products, wlist)]
                n_lines = random.choices([1, 2, 3, 4], weights=[30, 35, 22, 13])[0]
                pool = list(zip([p.id for p in products], wlist))
                chosen: list[int] = []
                for _ in range(min(n_lines, len(pool))):
                    total = sum(w for _pid, w in pool)
                    pick = random.uniform(0, total)
                    cum = 0.0
                    for i, (pid, w) in enumerate(pool):
                        cum += w
                        if pick <= cum:
                            chosen.append(pid)
                            pool.pop(i)
                            break

                lines = []
                subtotal = Decimal("0.00")
                for pid in chosen:
                    prod = by_id[pid]
                    if prod.name in BULK_ITEMS:
                        qty = random.choices([1, 2, 3, 4], weights=[55, 30, 10, 5])[0]
                    elif prod.price >= Decimal("6.00"):
                        qty = random.choices([1, 2], weights=[85, 15])[0]
                    else:
                        qty = random.choices([1, 2, 3], weights=[70, 22, 8])[0]
                    line_total = (prod.price * qty).quantize(Decimal("0.01"))
                    subtotal += line_total
                    lines.append((prod, qty, line_total))

                tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
                total = (subtotal + tax).quantize(Decimal("0.01"))
                status = random.choice(status_pool)
                payment = "card" if status == "refunded" else random.choice(payment_pool)
                customer = random.choice(custs) if (custs and random.random() >= 0.3) \
                    else None
                created = sale_dt + timedelta(minutes=random.randint(1, 4),
                                              seconds=random.randint(0, 59))

                sale = Sale(
                    customer=customer,
                    sale_date=sale_dt,
                    subtotal=subtotal,
                    tax_amount=tax,
                    discount_amount=Decimal("0.00"),
                    cashback_amount=Decimal("0.00"),
                    total=total,
                    payment_method=payment,
                    status=status,
                    notes=SEED_TAG,
                    created_at=created,
                    updated_at=created,
                    is_synced=False,
                    sync_status="pending",
                )
                sales.append(sale)
                # Only completed sales consume stock (refunded/cancelled never
                # moved goods — their transactions exist but were reversed).
                stock_consumed = status == "completed"
                for prod, qty, line_total in lines:
                    items.append(SaleItem(
                        sale=sale,
                        product=prod,
                        product_name=prod.name,
                        quantity=qty,
                        unit_price=prod.price,
                        line_total=line_total,
                        notes="",
                        is_synced=False,
                        sync_status="pending",
                    ))
                    if stock_consumed:
                        inv_lines.append((sale, prod, qty))
                        stock_delta[prod.id] = stock_delta.get(prod.id, 0) + qty

        Sale.objects.bulk_create(sales)
        SaleItem.objects.bulk_create(items)

        # ── Inventory: matching 'out' transactions + stock decrements ──
        if inv_lines:
            inv_txs = []
            for sale, prod, qty in inv_lines:
                inv_txs.append(InventoryTransaction(
                    product=prod,
                    transaction_type="out",
                    quantity=qty,
                    reference=f"sale_{sale.id}",
                    notes=f"{INV_SEED_PREFIX} Sold {qty}x {prod.name} (sale #{sale.id})",
                    inventory_id="main",
                    is_synced=False,
                    sync_status="pending",
                ))
            InventoryTransaction.objects.bulk_create(inv_txs)
            # Reset each sold product's stock to a deterministic baseline so
            # inventory stays healthy even when the original stock was tiny.
            for pid, qty in stock_delta.items():
                Product.objects.filter(id=pid).update(
                    stock_quantity=STOCK_BASELINE - qty,
                )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(sales)} sales / {len(items)} items over "
            f"{start} → {end}."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Created {len(inv_lines)} inventory 'out' transactions and reset "
            f"stock (baseline {STOCK_BASELINE} − sold) across "
            f"{len(stock_delta)} products."
        ))
        self._summary()

    # ── helpers ─────────────────────────────────────────────────────────────

    def _cleanup_previous_seed(self) -> None:
        """Remove the previous batch generated by this command (idempotent).

        Restores the stock decrements and deletes the seed inventory
        transactions, then removes the previous seed sales + items.
        """
        # 1) Restore stock decremented by the previous seed run
        prior_txs = list(
            InventoryTransaction.objects.filter(
                notes__startswith=INV_SEED_PREFIX,
            ).values_list("product_id", "quantity")
        )
        if prior_txs:
            for pid, qty in prior_txs:
                Product.objects.filter(id=pid).update(
                    stock_quantity=F("stock_quantity") + qty,
                )
            InventoryTransaction.objects.filter(
                notes__startswith=INV_SEED_PREFIX,
                transaction_type="out",
            ).delete()

        # 2) Remove the previous sales batch
        prior = list(
            Sale.objects.filter(notes=SEED_TAG).values_list("id", flat=True)
        )
        if not prior:
            return
        SaleItem.objects.filter(sale_id__in=prior).delete()
        Sale.objects.filter(id__in=prior).delete()
        self.stdout.write(f"Removed previous seed batch ({len(prior)} sales).")

    def _preview(self, n_products: int) -> None:
        total_sales = total_items = 0
        for offset in range(self.days):
            wd = (timezone.now().date() - timedelta(days=self.days - 1 - offset)).weekday()
            base = random.randint(10, 16) if wd >= 4 else random.randint(7, 12)
            total_sales += max(3, base)
            total_items += base * 2
        self.stdout.write(
            f"Would seed ~{total_sales} sales / ~{total_items} items over "
            f"{self.days} days using {n_products} products."
        )

    def _summary(self) -> None:
        completed = Sale.objects.filter(status="completed")
        revenue = completed.aggregate(s=Sum("total"))["s"] or 0
        inv_out = InventoryTransaction.objects.filter(
            transaction_type="out", notes__startswith=INV_SEED_PREFIX,
        ).count()
        self.stdout.write(f"Completed sales:     {completed.count()}")
        self.stdout.write(f"Last-30-days revenue: ${float(revenue):,.2f}")
        self.stdout.write(f"Total sale items:    {SaleItem.objects.count()}")
        self.stdout.write(f"Seed inventory out-txns: {inv_out}")
