#!/usr/bin/env python3
"""
Standalone test runner for pos-cloud sync receiver unit tests.

Bypasses the global DJANGO_SETTINGS_MODULE (tests.settings) from pyproject.toml
which references `plugins` and other apps not needed for sync receiver tests.

Configures a minimal in-memory SQLite Django environment and runs all tests.
"""
import json
import os
import sys
from pathlib import Path

# ── Path setup ──
_project_root = Path(__file__).resolve().parents[3]  # structa.cloud/
_pos_cloud = _project_root / "projects" / "pos" / "pos-cloud"
sys.path.insert(0, str(_pos_cloud))

# ── Minimal Django settings ──
os.environ["DJANGO_SETTINGS_MODULE"] = ""  # prevent tests.settings from loading

from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key",
        ALLOWED_HOSTS=["*"],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "core",
        ],
        MIDDLEWARE=["django.middleware.common.CommonMiddleware"],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        STATIC_URL="/static/",
        MEDIA_URL="/media/",
        COMPONENTS_INCLUDE_PATH_ROOTS=[],
        FUSION_SITE_NAME="pos_cloud",
        FUSION_SITE_TITLE="POS Cloud Test",
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": []},
        }],
    )

import django
django.setup()

# Apply migrations to create tables in the in-memory database
from django.core.management import call_command
call_command("migrate", "core", interactive=False, verbosity=0)
call_command("migrate", "contenttypes", interactive=False, verbosity=0)
call_command("migrate", "auth", interactive=False, verbosity=0)

# ── Test framework ──
from django.test import RequestFactory
from core.models import (
    Organization, Branch,
    BranchSyncLog, BranchProduct, BranchSale, BranchInventory,
)
from core.sync_api import (
    sync_receive_products,
    sync_receive_sales,
    sync_receive_inventory,
    sync_receive_heartbeat,
)

PASS = 0
FAIL = 0
ERRORS = []


def check(condition, label):
    global PASS, FAIL, ERRORS
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")


def _post(factory, url, payload):
    return factory.post(url, json.dumps(payload), content_type="application/json")


def _parse(response):
    return json.loads(response.content)


# ════════════════════════════════════════════════════════════════
# Fixtures
# ════════════════════════════════════════════════════════════════

factory = RequestFactory()
org = Organization.objects.create(name="Test Org", slug="test-org", is_active=True, subscription_plan="pro")
branch = Branch.objects.create(
    organization=org, name="Main Branch", code="MAIN01",
    is_active=True, pos_type="pos-full", node_id="node-test-001", sync_enabled=True,
)
inactive_branch = Branch.objects.create(
    organization=org, name="Inactive Branch", code="INACTIVE01",
    is_active=False, pos_type="pos-full", node_id="node-inactive-001",
)

print(f"Setup: org={org.slug}, branch={branch.name} (node={branch.node_id})")

# ════════════════════════════════════════════════════════════════
# sync_receive_products
# ════════════════════════════════════════════════════════════════

print("\n── sync_receive_products ──")

# Multi-sync
payload = {
    "node_id": "node-test-001",
    "products": [
        {"id": "p1", "name": "Espresso", "price": 3.50, "sku": "ESP-001", "category_name": "Drinks", "stock_quantity": 100},
        {"id": "p2", "name": "Latte", "price": 4.50, "sku": "LAT-001", "category_name": "Drinks", "stock_quantity": 80},
    ],
}
resp = sync_receive_products(_post(factory, "/sync/push/products", payload))
data = _parse(resp)
check(resp.status_code == 200, f"Status 200: synced={data.get('synced')}")
check(data["synced"] == 2, f"Synced 2 products")
check(data["branch"] == "Main Branch", f"Correct branch name")
check(BranchProduct.objects.filter(branch=branch).count() == 2, "DB has 2 products")

# SyncLog created
log = BranchSyncLog.objects.filter(branch=branch, entity_type="products").first()
check(log is not None and log.entity_count == 2 and log.status == "processed", "SyncLog created correctly")

# update_or_create dedup
sync_receive_products(_post(factory, "/sync/push/products", payload))
check(BranchProduct.objects.filter(branch=branch).count() == 2, "Re-push: no duplicate rows")

# Update existing
payload["products"][0]["price"] = 5.00
sync_receive_products(_post(factory, "/sync/push/products", payload))
p = BranchProduct.objects.get(branch=branch, source_id="p1")
check(float(p.price) == 5.00, f"Price updated: {p.price}")

# Missing fields use defaults
payload2 = {"node_id": "node-test-001", "products": [{"id": "p-min", "name": "Minimal"}]}
sync_receive_products(_post(factory, "/sync/push/products", payload2))
p = BranchProduct.objects.get(branch=branch, source_id="p-min")
check(float(p.price) == 0.00 and p.sku == "", "Missing fields get defaults")

# Invalid JSON
resp = sync_receive_products(factory.post("/sync/push/products", b"bad", content_type="application/json"))
check(resp.status_code == 400, "Invalid JSON → 400")

# Unknown node
resp = sync_receive_products(_post(factory, "/sync/push/products", {"node_id": "ghost", "products": []}))
check(resp.status_code == 404, "Unknown node → 404")

# Inactive branch
resp = sync_receive_products(_post(factory, "/sync/push/products", {"node_id": "node-inactive-001", "products": [{"id": "x", "name": "Nope"}]}))
check(resp.status_code == 404, "Inactive branch → 404")

# Empty products
resp = sync_receive_products(_post(factory, "/sync/push/products", {"node_id": "node-test-001", "products": []}))
check(resp.status_code == 200 and _parse(resp)["synced"] == 0, "Empty list: synced=0")

# GET rejected
resp = sync_receive_products(factory.get("/sync/push/products"))
check(resp.status_code == 405, "GET → 405")

# ════════════════════════════════════════════════════════════════
# sync_receive_sales
# ════════════════════════════════════════════════════════════════

print("\n── sync_receive_sales ──")

payload = {
    "node_id": "node-test-001",
    "sales": [
        {"id": "s1", "customer_name": "Alice", "total_amount": 15.00, "payment_method": "card",
         "sale_date": "2026-07-22T10:00:00Z", "item_count": 2, "items": [{"name": "Latte", "qty": 2}]},
        {"id": "s2", "customer_name": "Bob", "total_amount": 5.00, "payment_method": "cash",
         "sale_date": "2026-07-22T11:00:00Z", "item_count": 1, "items": [{"name": "Espresso", "qty": 1}]},
    ],
}
resp = sync_receive_sales(_post(factory, "/sync/push/sales", payload))
data = _parse(resp)
check(resp.status_code == 200 and data["synced"] == 2, "Synced 2 sales")
check(BranchSale.objects.filter(branch=branch).count() == 2, "DB has 2 sales")

# Items stored as JSON
s = BranchSale.objects.get(source_id="s1")
check(len(s.items) == 1 and s.items[0]["name"] == "Latte", "Line items stored")

# Default payment_method
payload2 = {"node_id": "node-test-001", "sales": [{"id": "s-def", "customer_name": "T", "total_amount": 1.00, "sale_date": "2026-07-22T12:00:00Z"}]}
sync_receive_sales(_post(factory, "/sync/push/sales", payload2))
s = BranchSale.objects.get(source_id="s-def")
check(s.payment_method == "cash", "Default payment_method = cash")

# Dedup
sync_receive_sales(_post(factory, "/sync/push/sales", payload))
check(BranchSale.objects.filter(branch=branch).count() == 3, "Re-push: no duplicates (3 total)")

# SyncLog
log = BranchSyncLog.objects.filter(branch=branch, entity_type="sales").first()
check(log is not None and log.status == "processed", "SyncLog created")

# Error cases
check(sync_receive_sales(factory.post("/sync/push/sales", b"bad", content_type="application/json")).status_code == 400, "Invalid JSON → 400")
check(sync_receive_sales(_post(factory, "/sync/push/sales", {"node_id": "ghost", "sales": []})).status_code == 404, "Unknown node → 404")
check(sync_receive_sales(factory.get("/sync/push/sales")).status_code == 405, "GET → 405")

# ════════════════════════════════════════════════════════════════
# sync_receive_inventory
# ════════════════════════════════════════════════════════════════

print("\n── sync_receive_inventory ──")

payload = {
    "node_id": "node-test-001",
    "transactions": [
        {"id": "inv-1", "product_name": "Espresso", "transaction_type": "addition", "quantity": 50, "transaction_date": "2026-07-22T08:00:00Z"},
        {"id": "inv-2", "product_name": "Croissant", "transaction_type": "removal", "quantity": 5, "transaction_date": "2026-07-22T09:00:00Z"},
        {"id": "inv-3", "product_name": "Latte", "transaction_type": "adjustment", "quantity": -2, "transaction_date": "2026-07-22T10:00:00Z"},
    ],
}
resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
data = _parse(resp)
check(resp.status_code == 200 and data["synced"] == 3, "Synced 3 inventory txs")
check(BranchInventory.objects.filter(branch=branch).count() == 3, "DB has 3 txs")

# All TX_TYPES
for tx_type in ["addition", "removal", "adjustment", "transfer"]:
    p = {"node_id": "node-test-001", "transactions": [{"id": f"inv-{tx_type}", "product_name": "T", "transaction_type": tx_type, "quantity": 1, "transaction_date": "2026-07-22T12:00:00Z"}]}
    check(sync_receive_inventory(_post(factory, "/sync/push/inventory", p)).status_code == 200, f"TX type '{tx_type}' accepted")
check(BranchInventory.objects.count() == 7, "All 4 TX types + original 3 = 7")

# Default transaction_type
p = {"node_id": "node-test-001", "transactions": [{"id": "inv-def", "product_name": "T", "quantity": 1, "transaction_date": "2026-07-22T12:00:00Z"}]}
sync_receive_inventory(_post(factory, "/sync/push/inventory", p))
check(BranchInventory.objects.get(source_id="inv-def").transaction_type == "addition", "Default = addition")

# Notes
p = {"node_id": "node-test-001", "transactions": [{"id": "inv-note", "product_name": "T", "quantity": 1, "notes": "Spoilage #42", "transaction_date": "2026-07-22T12:00:00Z"}]}
sync_receive_inventory(_post(factory, "/sync/push/inventory", p))
check(BranchInventory.objects.get(source_id="inv-note").notes == "Spoilage #42", "Notes stored")

# Dedup
sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
check(BranchInventory.objects.filter(branch=branch).count() == 9, "Re-push: no duplicates (3 original + 4 types + 1 def + 1 note = 9)")

# SyncLog
log = BranchSyncLog.objects.filter(branch=branch, entity_type="inventory").first()
check(log is not None and log.status == "processed", "SyncLog created")

# Error cases
check(sync_receive_inventory(factory.post("/sync/push/inventory", b"bad", content_type="application/json")).status_code == 400, "Invalid JSON → 400")
check(sync_receive_inventory(_post(factory, "/sync/push/inventory", {"node_id": "ghost", "transactions": []})).status_code == 404, "Unknown node → 404")
check(sync_receive_inventory(factory.get("/sync/push/inventory")).status_code == 405, "GET → 405")

# ════════════════════════════════════════════════════════════════
# sync_receive_heartbeat
# ════════════════════════════════════════════════════════════════

print("\n── sync_receive_heartbeat ──")

payload = {"node_id": "node-test-001", "status": "online", "product_count": 42, "sales_count": 150}
resp = sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", payload))
data = _parse(resp)
check(resp.status_code == 200 and data["status"] == "received", "Heartbeat received")
check(data["branch"] == "Main Branch", "Correct branch")

# SyncLog
log = BranchSyncLog.objects.filter(branch=branch, entity_type="heartbeat").first()
check(log is not None and log.status == "received" and log.entity_count == 1, "Heartbeat SyncLog created")

# Payload stored
check(log.payload["product_count"] == 42 and log.payload["sales_count"] == 150, "Payload stored in log")

# Error cases
check(sync_receive_heartbeat(factory.post("/sync/push/heartbeat", b"bad", content_type="application/json")).status_code == 400, "Invalid JSON → 400")
check(sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", {"node_id": "ghost"})).status_code == 404, "Unknown node → 404")
check(sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", {"status": "online"})).status_code == 404, "Missing node_id → 404")
check(sync_receive_heartbeat(factory.get("/sync/push/heartbeat")).status_code == 405, "GET → 405")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Cross-branch isolation
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Cross-branch isolation ──")

branch2 = Branch.objects.create(
    organization=org, name="Branch Two", code="BR02",
    is_active=True, pos_type="pos-full", node_id="node-branch-002", sync_enabled=True,
)

# Same source_id on different branches = separate records
p1 = {"node_id": "node-test-001", "products": [{"id": "shared-id", "name": "Branch1 Shared", "price": 10.00}]}
p2 = {"node_id": "node-branch-002", "products": [{"id": "shared-id", "name": "Branch2 Shared", "price": 20.00}]}
sync_receive_products(_post(factory, "/sync/push/products", p1))
sync_receive_products(_post(factory, "/sync/push/products", p2))
check(BranchProduct.objects.filter(source_id="shared-id").count() == 2, "Same source_id, diff branches = 2 records")
bp1 = BranchProduct.objects.get(branch=branch, source_id="shared-id")
bp2 = BranchProduct.objects.get(branch=branch2, source_id="shared-id")
check(float(bp1.price) == 10.00, f"Branch1 price correct: {bp1.price}")
check(float(bp2.price) == 20.00, f"Branch2 price correct: {bp2.price}")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Bulk payload
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Bulk payload ──")

bulk_products = []
for i in range(25):
    bulk_products.append({"id": f"bulk-{i}", "name": f"Bulk Item {i}", "price": i + 1.0, "sku": f"BLK-{i:03d}"})
bulk_payload = {"node_id": "node-test-001", "products": bulk_products}
resp = sync_receive_products(_post(factory, "/sync/push/products", bulk_payload))
data = _parse(resp)
check(resp.status_code == 200, "Bulk 25 products: 200")
check(data["synced"] == 25, f"Bulk 25 products synced (got {data['synced']})")
check(BranchProduct.objects.filter(source_id__startswith="bulk-").count() == 25, "DB has all 25 bulk products")

bulk_sales = []
for i in range(15):
    bulk_sales.append({"id": f"bs-{i}", "customer_name": f"Cust {i}", "total_amount": 10.0 + i,
                       "sale_date": "2026-07-22T12:00:00Z", "item_count": 1})
resp = sync_receive_sales(_post(factory, "/sync/push/sales", {"node_id": "node-test-001", "sales": bulk_sales}))
check(resp.status_code == 200 and _parse(resp)["synced"] == 15, "Bulk 15 sales synced")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Decimal precision
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Decimal precision ──")

precise_payload = {"node_id": "node-test-001", "products": [
    {"id": "prec-1", "name": "Precise", "price": 0.01},
    {"id": "prec-2", "name": "Big", "price": 999999.99},
    {"id": "prec-3", "name": "Tiny", "price": 0.001},
]}
resp = sync_receive_products(_post(factory, "/sync/push/products", precise_payload))
check(resp.status_code == 200, "Decimal-precision products accepted")
# Precisely check stored values
p_small = BranchProduct.objects.get(source_id="prec-1")
p_big = BranchProduct.objects.get(source_id="prec-2")
p_tiny = BranchProduct.objects.get(source_id="prec-3")
check(float(p_small.price) == 0.01, f"Price 0.01 stored exactly: {p_small.price}")
check(float(p_big.price) == 999999.99, f"Price 999999.99 stored: {p_big.price}")
check(float(p_tiny.price) == 0.00, f"Price 0.001 rounded to 0.00 (decimal_places=2): {p_tiny.price}")

# Precise sale amounts
resp = sync_receive_sales(_post(factory, "/sync/push/sales", {
    "node_id": "node-test-001",
    "sales": [{"id": "prec-sale", "customer_name": "Precise", "total_amount": 0.05,
               "sale_date": "2026-07-22T12:00:00Z"}]
}))
check(resp.status_code == 200, "Fractional-cent sale accepted")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Unicode & special characters
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Unicode & special characters ──")

unicode_payload = {"node_id": "node-test-001", "products": [
    {"id": "uni-1", "name": "Café au Lait ☕", "description": "French café with croissant 🥐"},
    {"id": "uni-2", "name": "こんにちは", "sku": "JPN-あいう"},
    {"id": "uni-3", "name": "Über Coffee", "description": "Straße 42 — München"},
]}
resp = sync_receive_products(_post(factory, "/sync/push/products", unicode_payload))
check(resp.status_code == 200, "Unicode products accepted")
p = BranchProduct.objects.get(source_id="uni-1")
check("☕" in p.name, f"Emoji preserved: {p.name}")
p = BranchProduct.objects.get(source_id="uni-2")
check("こんにちは" == p.name, f"Japanese preserved: {p.name}")
p = BranchProduct.objects.get(source_id="uni-3")
check("Ü" in p.name, f"Umlaut preserved: {p.name}")

# Unicode in sales
resp = sync_receive_sales(_post(factory, "/sync/push/sales", {
    "node_id": "node-test-001",
    "sales": [{"id": "uni-sale", "customer_name": "José García", "total_amount": 12.50,
               "sale_date": "2026-07-22T12:00:00Z",
               "items": [{"name": "Café", "qty": 1}, {"name": "パン", "qty": 2}]}]
}))
check(resp.status_code == 200, "Unicode sale accepted")

# ════════════════════════════════════════════════════════════════
# Edge Cases — is_active toggle
# ════════════════════════════════════════════════════════════════

print("\n── Edge: is_active toggle ──")

sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [{"id": "toggle-1", "name": "Toggle", "is_active": True}]
}))
check(BranchProduct.objects.get(source_id="toggle-1").is_active, "Product created active")

sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [{"id": "toggle-1", "name": "Toggle", "is_active": False}]
}))
check(not BranchProduct.objects.get(source_id="toggle-1").is_active, "Product toggled inactive via re-push")

sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [{"id": "toggle-1", "name": "Toggle", "is_active": True}]
}))
check(BranchProduct.objects.get(source_id="toggle-1").is_active, "Product toggled back active")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Zero values, empty strings, nulls
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Zero values & nulls ──")

# Zero-quantity inventory
resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", {
    "node_id": "node-test-001",
    "transactions": [{"id": "inv-zero", "product_name": "Zero Qty", "quantity": 0,
                      "transaction_date": "2026-07-22T12:00:00Z"}]
}))
check(resp.status_code == 200, "Zero-quantity inventory accepted")
check(BranchInventory.objects.get(source_id="inv-zero").quantity == 0, "Quantity stored as 0")

# Zero-amount sale
resp = sync_receive_sales(_post(factory, "/sync/push/sales", {
    "node_id": "node-test-001",
    "sales": [{"id": "sale-zero", "customer_name": "Free", "total_amount": 0,
               "sale_date": "2026-07-22T12:00:00Z"}]
}))
check(resp.status_code == 200, "Zero-amount sale accepted")
check(float(BranchSale.objects.get(source_id="sale-zero").total_amount) == 0, "Amount is 0")

# Zero-price product
resp = sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [{"id": "prod-free", "name": "Freebie", "price": 0}]
}))
check(resp.status_code == 200, "Zero-price product accepted")

# Null-like fields — both omitted keys and explicit None values
resp = sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [{"id": "null-1", "name": "Omitted Keys"}]
}))
check(resp.status_code == 200, "Omitted optional fields: accepted")
p = BranchProduct.objects.get(source_id="null-1")
check(p.description == "" and p.sku == "", "Omitted fields default to empty strings")

# Explicit None values in JSON (converted to empty by receiver)
resp = sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [{"id": "null-2", "name": "Explicit None", "description": None, "sku": None}]
}))
check(resp.status_code == 200, "Explicit null fields: accepted")
p = BranchProduct.objects.get(source_id="null-2")
check(p.description == "" and p.sku == "", "Explicit None values converted to empty strings")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Multiple SyncLog entries
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Multiple SyncLog entries ──")

logs_before = BranchSyncLog.objects.filter(entity_type="heartbeat").count()
for i in range(5):
    sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat",
        {"node_id": "node-test-001", "status": "online", "seq": i}))
logs_after = BranchSyncLog.objects.filter(entity_type="heartbeat").count()
check(logs_after == logs_before + 5, f"5 heartbeats = 5 new logs (had {logs_before}, now {logs_after})")

# Verify payloads differ
seqs = [log.payload.get("seq") for log in BranchSyncLog.objects.filter(
    entity_type="heartbeat").order_by("-received_at")[:5]]
check(seqs == [4, 3, 2, 1, 0], f"Heartbeat seqs preserved: {seqs}")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Same source_id within single batch (dedup-merge)
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Duplicate IDs within batch ──")

# Duplicate IDs within batch — last-write-wins
resp = sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [
        {"id": "dup-batch", "name": "First", "price": 1.00},
        {"id": "dup-batch", "name": "Second", "price": 2.00},
    ]
}))
check(resp.status_code == 200, "Duplicate IDs in batch accepted")
check(_parse(resp)["synced"] == 2, "synced=2 (counts iterations, not unique DB rows)")
check(BranchProduct.objects.filter(source_id="dup-batch").count() == 1, "Only 1 DB record despite 2 entries")
p = BranchProduct.objects.get(source_id="dup-batch")
check(p.name == "Second" and float(p.price) == 2.00, f"Last-write-wins: name={p.name}, price={p.price}")

# Bulk sales SyncLog
check(BranchSyncLog.objects.filter(entity_type="sales", entity_count=15).exists(),
      "SyncLog created for 15 bulk sales")

# Same for sales — duplicate IDs in single batch, last-write-wins
resp = sync_receive_sales(_post(factory, "/sync/push/sales", {
    "node_id": "node-test-001",
    "sales": [
        {"id": "dup-sale-batch", "customer_name": "A", "total_amount": 1.00, "sale_date": "2026-07-22T12:00:00Z"},
        {"id": "dup-sale-batch", "customer_name": "B", "total_amount": 2.00, "sale_date": "2026-07-22T12:00:00Z"},
    ]
}))
check(resp.status_code == 200, "Duplicate sale IDs in batch accepted")
s = BranchSale.objects.get(source_id="dup-sale-batch")
check(s.customer_name == "B" and float(s.total_amount) == 2.00, "Last-write-wins for sales too")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Date defaults
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Date defaults ──")

# Sale without sale_date → defaults to now
resp = sync_receive_sales(_post(factory, "/sync/push/sales", {
    "node_id": "node-test-001",
    "sales": [{"id": "sale-no-date", "customer_name": "No Date", "total_amount": 5.00}]
}))
check(resp.status_code == 200, "Sale without sale_date: accepted")
s = BranchSale.objects.get(source_id="sale-no-date")
check(s.sale_date is not None, "sale_date defaulted to now (not null)")

# Inventory without transaction_date → defaults to now
resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", {
    "node_id": "node-test-001",
    "transactions": [{"id": "inv-no-date", "product_name": "No Date", "quantity": 1}]
}))
check(resp.status_code == 200, "Inventory without transaction_date: accepted")
tx = BranchInventory.objects.get(source_id="inv-no-date")
check(tx.transaction_date is not None, "transaction_date defaulted to now (not null)")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Unicode inventory
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Unicode inventory ──")

resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", {
    "node_id": "node-test-001",
    "transactions": [
        {"id": "uni-inv-1", "product_name": "Café ☕", "quantity": 5, "transaction_type": "addition",
         "transaction_date": "2026-07-22T12:00:00Z"},
        {"id": "uni-inv-2", "product_name": "パン 🍞", "quantity": 3, "transaction_type": "removal",
         "transaction_date": "2026-07-22T12:00:00Z"},
    ]
}))
check(resp.status_code == 200, "Unicode inventory: accepted")
check(BranchInventory.objects.get(source_id="uni-inv-1").product_name == "Café ☕", "Emoji preserved in product_name")
check(BranchInventory.objects.get(source_id="uni-inv-2").product_name == "パン 🍞", "Japanese + emoji preserved")

# ════════════════════════════════════════════════════════════════
# Edge Cases — Inventory edges
# ════════════════════════════════════════════════════════════════

print("\n── Edge: Inventory edges ──")

# Large negative quantity
resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", {
    "node_id": "node-test-001",
    "transactions": [{"id": "inv-big-neg", "product_name": "Correction", "quantity": -999,
                      "transaction_date": "2026-07-22T12:00:00Z"}]
}))
check(resp.status_code == 200, "Large negative quantity accepted")
check(BranchInventory.objects.get(source_id="inv-big-neg").quantity == -999, "Stored as -999")

# Very long notes
long_note = "x" * 500
resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", {
    "node_id": "node-test-001",
    "transactions": [{"id": "inv-long", "product_name": "Long", "quantity": 1,
                      "notes": long_note, "transaction_date": "2026-07-22T12:00:00Z"}]
}))
check(resp.status_code == 200, "Long notes (500 chars) accepted")
check(len(BranchInventory.objects.get(source_id="inv-long").notes) == 500, "Notes length preserved")

# Very long product name
long_name = "Very Long Product Name " * 15
resp = sync_receive_products(_post(factory, "/sync/push/products", {
    "node_id": "node-test-001",
    "products": [{"id": "long-name", "name": long_name}]
}))
check(resp.status_code == 200, "Long product name accepted")

# ════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════

total = PASS + FAIL
print(f"\n{'='*60}")
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {total} checks")
print(f"{'='*60}")

if FAIL > 0:
    print("❌ SOME TESTS FAILED")
    sys.exit(1)
else:
    print("✅ ALL TESTS PASSED")
    sys.exit(0)
