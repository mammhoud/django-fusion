"""
Unit tests for pos-cloud sync receiver views.

Tests all four sync receiver endpoints:
- sync_receive_products
- sync_receive_sales
- sync_receive_inventory
- sync_receive_heartbeat

Covers success paths, deduplication, updates, and error handling.
"""
import json
from datetime import datetime, timezone

import pytest
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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def org(db):
    return Organization.objects.create(
        name="Test Org", slug="test-org", is_active=True, subscription_plan="pro",
    )


@pytest.fixture
def branch(db, org):
    return Branch.objects.create(
        organization=org, name="Main Branch", code="MAIN01",
        is_active=True, pos_type="pos-full", node_id="node-test-001",
        sync_enabled=True,
    )


@pytest.fixture
def inactive_branch(db, org):
    return Branch.objects.create(
        organization=org, name="Inactive Branch", code="INACTIVE01",
        is_active=False, pos_type="pos-full", node_id="node-inactive-001",
    )


@pytest.fixture
def factory():
    return RequestFactory()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post(factory, url, payload):
    """Build a POST request with JSON body."""
    return factory.post(url, json.dumps(payload), content_type="application/json")


def _parse(response):
    """Parse JSON response body."""
    return json.loads(response.content)


# ---------------------------------------------------------------------------
# sync_receive_products
# ---------------------------------------------------------------------------

class TestSyncReceiveProducts:

    def test_syncs_multiple_products(self, factory, branch):
        """Successful sync of 2 products creates DB records + sync log."""
        payload = {
            "node_id": "node-test-001",
            "products": [
                {"id": "p1", "name": "Espresso", "price": 3.50, "sku": "ESP-001",
                 "category_name": "Drinks", "stock_quantity": 100},
                {"id": "p2", "name": "Latte", "price": 4.50, "sku": "LAT-001",
                 "category_name": "Drinks", "stock_quantity": 80},
            ],
        }
        resp = sync_receive_products(_post(factory, "/sync/push/products", payload))
        data = _parse(resp)
        assert resp.status_code == 200
        assert data["synced"] == 2
        assert data["branch"] == "Main Branch"
        assert BranchProduct.objects.filter(branch=branch).count() == 2    # Verify log
            log = BranchSyncLog.objects.filter(branch=branch, entity_type="products").first()
            assert log is not None
            assert log.entity_count == 2
            assert log.status == "processed"

    def test_creates_sync_log(self, factory, branch):
        """SyncLog is created with correct fields."""
        payload = {
            "node_id": "node-test-001",
            "products": [{"id": "p1", "name": "Test", "price": 1.00}],
        }
        sync_receive_products(_post(factory, "/sync/push/products", payload))
        log = BranchSyncLog.objects.filter(branch=branch, entity_type="products").first()
        assert log is not None
        assert log.node_id == "node-test-001"
        assert log.entity_count == 1
        assert log.status == "processed"
        assert log.payload == {"source_node_id": "node-test-001", "count": 1}

    def test_update_or_create_dedup(self, factory, branch):
        """Re-pushing same source_id updates the row, no duplicates."""
        payload = {
            "node_id": "node-test-001",
            "products": [{"id": "p-dup", "name": "Original", "price": 10.00}],
        }
        sync_receive_products(_post(factory, "/sync/push/products", payload))
        assert BranchProduct.objects.filter(branch=branch).count() == 1

        # Re-push with updated price
        payload["products"][0]["price"] = 12.00
        sync_receive_products(_post(factory, "/sync/push/products", payload))
        assert BranchProduct.objects.filter(branch=branch).count() == 1  # still 1
        p = BranchProduct.objects.get(branch=branch, source_id="p-dup")
        assert float(p.price) == 12.00

    def test_update_existing_product_fields(self, factory, branch):
        """Re-pushing updates stock_quantity and name."""
        payload = {
            "node_id": "node-test-001",
            "products": [{"id": "p-up", "name": "V1", "price": 5.00, "stock_quantity": 50}],
        }
        sync_receive_products(_post(factory, "/sync/push/products", payload))

        payload["products"][0].update(name="V2", stock_quantity=25)
        sync_receive_products(_post(factory, "/sync/push/products", payload))
        p = BranchProduct.objects.get(branch=branch, source_id="p-up")
        assert p.name == "V2"
        assert p.stock_quantity == 25

    def test_missing_optional_fields_get_defaults(self, factory, branch):
        """Fields not in payload get model defaults."""
        payload = {
            "node_id": "node-test-001",
            "products": [{"id": "p-min", "name": "Minimal"}],
        }
        sync_receive_products(_post(factory, "/sync/push/products", payload))
        p = BranchProduct.objects.get(branch=branch, source_id="p-min")
        assert float(p.price) == 0.00
        assert p.sku == ""
        assert p.category_name == ""
        assert p.stock_quantity == 0
        assert p.is_active is True

    def test_invalid_json_returns_400(self, factory):
        """Malformed JSON body returns 400."""
        req = factory.post("/sync/push/products", b"not-json", content_type="application/json")
        resp = sync_receive_products(req)
        assert resp.status_code == 400
        assert "Invalid JSON" in _parse(resp)["error"]

    def test_unknown_node_returns_404(self, factory):
        """Node ID that doesn't match any active branch returns 404."""
        payload = {"node_id": "nonexistent", "products": []}
        resp = sync_receive_products(_post(factory, "/sync/push/products", payload))
        assert resp.status_code == 404

    def test_inactive_branch_returns_404(self, factory, inactive_branch):
        """Inactive branch is filtered out (is_active=True check)."""
        payload = {"node_id": "node-inactive-001", "products": [{"id": "x", "name": "Nope"}]}
        resp = sync_receive_products(_post(factory, "/sync/push/products", payload))
        assert resp.status_code == 404
        assert BranchProduct.objects.count() == 0

    def test_empty_products_list_returns_200(self, factory, branch):
        """Empty products array is valid, synced=0."""
        payload = {"node_id": "node-test-001", "products": []}
        resp = sync_receive_products(_post(factory, "/sync/push/products", payload))
        assert resp.status_code == 200
        assert _parse(resp)["synced"] == 0
        assert BranchProduct.objects.count() == 0

    def test_get_method_rejected_405(self, factory):
        """@require_POST rejects GET requests with 405."""
        resp = sync_receive_products(factory.get("/sync/push/products"))
        assert resp.status_code == 405

    def test_missing_product_id_uses_empty_string(self, factory, branch):
        """Missing 'id' field defaults to '' as source_id."""
        payload = {
            "node_id": "node-test-001",
            "products": [{"name": "No ID Product", "price": 1.00}],
        }
        resp = sync_receive_products(_post(factory, "/sync/push/products", payload))
        assert resp.status_code == 200
        assert BranchProduct.objects.filter(source_id="").exists()

    def test_product_with_description(self, factory, branch):
        """Products with description field are stored correctly."""
        payload = {
            "node_id": "node-test-001",
            "products": [{"id": "p-desc", "name": "Fancy", "price": 9.99,
                          "description": "A fancy product"}],
        }
        sync_receive_products(_post(factory, "/sync/push/products", payload))
        p = BranchProduct.objects.get(source_id="p-desc")
        assert p.description == "A fancy product"

    def test_is_active_false(self, factory, branch):
        """Product with is_active=False is stored correctly."""
        payload = {
            "node_id": "node-test-001",
            "products": [{"id": "p-off", "name": "Disabled", "is_active": False}],
        }
        sync_receive_products(_post(factory, "/sync/push/products", payload))
        p = BranchProduct.objects.get(source_id="p-off")
        assert p.is_active is False


# ---------------------------------------------------------------------------
# sync_receive_sales
# ---------------------------------------------------------------------------

class TestSyncReceiveSales:

    def test_syncs_multiple_sales_with_items(self, factory, branch):
        """Successful sync of 2 sales with line items."""
        payload = {
            "node_id": "node-test-001",
            "sales": [
                {"id": "s1", "customer_name": "Alice", "total_amount": 15.00,
                 "payment_method": "card", "sale_date": "2026-07-22T10:00:00Z",
                 "item_count": 2, "items": [{"name": "Latte", "qty": 2}]},
                {"id": "s2", "customer_name": "Bob", "total_amount": 5.00,
                 "payment_method": "cash", "sale_date": "2026-07-22T11:00:00Z",
                 "item_count": 1, "items": [{"name": "Espresso", "qty": 1}]},
            ],
        }
        resp = sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        data = _parse(resp)
        assert resp.status_code == 200
        assert data["synced"] == 2
        assert data["branch"] == "Main Branch"
        assert BranchSale.objects.filter(branch=branch).count() == 2

    def test_sale_items_stored_as_json(self, factory, branch):
        """Line items array is stored in the JSONField."""
        items = [{"name": "Mocha", "qty": 1}, {"name": "Cookie", "qty": 2}]
        payload = {
            "node_id": "node-test-001",
            "sales": [{"id": "s-items", "customer_name": "Test", "total_amount": 7.00,
                       "sale_date": "2026-07-22T12:00:00Z", "items": items}],
        }
        sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        s = BranchSale.objects.get(source_id="s-items")
        assert s.items == items

    def test_default_payment_method_cash(self, factory, branch):
        """Missing payment_method defaults to 'cash'."""
        payload = {
            "node_id": "node-test-001",
            "sales": [{"id": "s-cash", "customer_name": "Test", "total_amount": 10.00,
                       "sale_date": "2026-07-22T12:00:00Z"}],
        }
        sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        s = BranchSale.objects.get(source_id="s-cash")
        assert s.payment_method == "cash"

    def test_update_or_create_dedup(self, factory, branch):
        """Re-push updates existing sale."""
        payload = {
            "node_id": "node-test-001",
            "sales": [{"id": "s-dup", "customer_name": "V1", "total_amount": 10.00,
                       "sale_date": "2026-07-22T12:00:00Z"}],
        }
        sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        assert BranchSale.objects.count() == 1

        payload["sales"][0]["total_amount"] = 20.00
        sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        assert BranchSale.objects.count() == 1
        s = BranchSale.objects.get(source_id="s-dup")
        assert float(s.total_amount) == 20.00

    def test_creates_sync_log(self, factory, branch):
        """SyncLog created with correct fields."""
        payload = {
            "node_id": "node-test-001",
            "sales": [{"id": "s-log", "customer_name": "T", "total_amount": 1.00,
                       "sale_date": "2026-07-22T12:00:00Z"}],
        }
        sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        log = BranchSyncLog.objects.filter(branch=branch, entity_type="sales").first()
        assert log is not None
        assert log.entity_count == 1
        assert log.status == "processed"

    def test_invalid_json_returns_400(self, factory):
        resp = sync_receive_sales(
            factory.post("/sync/push/sales", b"bad", content_type="application/json"))
        assert resp.status_code == 400

    def test_unknown_node_returns_404(self, factory):
        payload = {"node_id": "ghost", "sales": []}
        resp = sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        assert resp.status_code == 404

    def test_inactive_branch_returns_404(self, factory, inactive_branch):
        payload = {"node_id": "node-inactive-001",
                   "sales": [{"id": "x", "customer_name": "N", "total_amount": 1.00,
                              "sale_date": "2026-07-22T12:00:00Z"}]}
        resp = sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        assert resp.status_code == 404

    def test_empty_sales_list_returns_200(self, factory, branch):
        payload = {"node_id": "node-test-001", "sales": []}
        resp = sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        assert resp.status_code == 200
        assert _parse(resp)["synced"] == 0

    def test_get_method_rejected_405(self, factory):
        """@require_POST rejects GET requests with 405."""
        resp = sync_receive_sales(factory.get("/sync/push/sales"))
        assert resp.status_code == 405

    def test_missing_sale_id_uses_empty_string(self, factory, branch):
        """Missing 'id' field defaults to '' as source_id."""
        payload = {
            "node_id": "node-test-001",
            "sales": [{"customer_name": "No ID", "total_amount": 1.00,
                       "sale_date": "2026-07-22T12:00:00Z"}],
        }
        resp = sync_receive_sales(_post(factory, "/sync/push/sales", payload))
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# sync_receive_inventory
# ---------------------------------------------------------------------------

class TestSyncReceiveInventory:

    def test_syncs_multiple_transactions(self, factory, branch):
        """Successful sync of 3 inventory transactions."""
        payload = {
            "node_id": "node-test-001",
            "transactions": [
                {"id": "inv-1", "product_name": "Espresso", "transaction_type": "addition",
                 "quantity": 50, "transaction_date": "2026-07-22T08:00:00Z"},
                {"id": "inv-2", "product_name": "Croissant", "transaction_type": "removal",
                 "quantity": 5, "transaction_date": "2026-07-22T09:00:00Z"},
                {"id": "inv-3", "product_name": "Latte", "transaction_type": "adjustment",
                 "quantity": -2, "transaction_date": "2026-07-22T10:00:00Z"},
            ],
        }
        resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        data = _parse(resp)
        assert resp.status_code == 200
        assert data["synced"] == 3
        assert data["branch"] == "Main Branch"
        assert BranchInventory.objects.filter(branch=branch).count() == 3

    def test_all_transaction_types(self, factory, branch):
        """All four TX_TYPES can be synced."""
        for tx_type in ["addition", "removal", "adjustment", "transfer"]:
            payload = {
                "node_id": "node-test-001",
                "transactions": [
                    {"id": f"inv-{tx_type}", "product_name": "Test",
                     "transaction_type": tx_type, "quantity": 10,
                     "transaction_date": "2026-07-22T12:00:00Z"},
                ],
            }
            resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
            assert resp.status_code == 200
        assert BranchInventory.objects.count() == 4

    def test_default_transaction_type_addition(self, factory, branch):
        """Missing transaction_type defaults to 'addition'."""
        payload = {
            "node_id": "node-test-001",
            "transactions": [{"id": "inv-def", "product_name": "Test", "quantity": 5,
                              "transaction_date": "2026-07-22T12:00:00Z"}],
        }
        sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        tx = BranchInventory.objects.get(source_id="inv-def")
        assert tx.transaction_type == "addition"

    def test_notes_field(self, factory, branch):
        """Notes field is stored correctly."""
        payload = {
            "node_id": "node-test-001",
            "transactions": [{"id": "inv-note", "product_name": "Test", "quantity": 1,
                              "notes": "Spoilage report #42",
                              "transaction_date": "2026-07-22T12:00:00Z"}],
        }
        sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        tx = BranchInventory.objects.get(source_id="inv-note")
        assert tx.notes == "Spoilage report #42"

    def test_update_or_create_dedup(self, factory, branch):
        """Re-push updates existing transaction."""
        payload = {
            "node_id": "node-test-001",
            "transactions": [{"id": "inv-dup", "product_name": "V1", "quantity": 10,
                              "transaction_date": "2026-07-22T12:00:00Z"}],
        }
        sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        assert BranchInventory.objects.count() == 1

        payload["transactions"][0]["quantity"] = 20
        sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        assert BranchInventory.objects.count() == 1
        tx = BranchInventory.objects.get(source_id="inv-dup")
        assert tx.quantity == 20

    def test_creates_sync_log(self, factory, branch):
        """SyncLog created with correct fields."""
        payload = {
            "node_id": "node-test-001",
            "transactions": [{"id": "inv-log", "product_name": "T", "quantity": 1,
                              "transaction_date": "2026-07-22T12:00:00Z"}],
        }
        sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        log = BranchSyncLog.objects.filter(branch=branch, entity_type="inventory").first()
        assert log is not None
        assert log.entity_count == 1
        assert log.status == "processed"

    def test_invalid_json_returns_400(self, factory):
        resp = sync_receive_inventory(
            factory.post("/sync/push/inventory", b"bad", content_type="application/json"))
        assert resp.status_code == 400

    def test_unknown_node_returns_404(self, factory):
        payload = {"node_id": "ghost", "transactions": []}
        resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        assert resp.status_code == 404

    def test_inactive_branch_returns_404(self, factory, inactive_branch):
        payload = {"node_id": "node-inactive-001",
                   "transactions": [{"id": "x", "product_name": "N", "quantity": 1,
                                     "transaction_date": "2026-07-22T12:00:00Z"}]}
        resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        assert resp.status_code == 404

    def test_empty_transactions_list_returns_200(self, factory, branch):
        payload = {"node_id": "node-test-001", "transactions": []}
        resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        assert resp.status_code == 200
        assert _parse(resp)["synced"] == 0

    def test_get_method_rejected_405(self, factory):
        """@require_POST rejects GET requests with 405."""
        resp = sync_receive_inventory(factory.get("/sync/push/inventory"))
        assert resp.status_code == 405

    def test_missing_tx_id_uses_empty_string(self, factory, branch):
        """Missing 'id' field defaults to '' as source_id."""
        payload = {
            "node_id": "node-test-001",
            "transactions": [{"product_name": "No ID", "quantity": 1,
                              "transaction_date": "2026-07-22T12:00:00Z"}],
        }
        resp = sync_receive_inventory(_post(factory, "/sync/push/inventory", payload))
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# sync_receive_heartbeat
# ---------------------------------------------------------------------------

class TestSyncReceiveHeartbeat:

    def test_records_heartbeat(self, factory, branch):
        """Heartbeat creates a SyncLog with status 'received'."""
        payload = {"node_id": "node-test-001", "status": "online",
                   "product_count": 42, "sales_count": 150}
        resp = sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", payload))
        data = _parse(resp)
        assert resp.status_code == 200
        assert data["status"] == "received"
        assert data["branch"] == "Main Branch"

    def test_creates_sync_log(self, factory, branch):
        """SyncLog for heartbeat has entity_type='heartbeat', status='received'."""
        payload = {"node_id": "node-test-001", "status": "online"}
        sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", payload))
        log = BranchSyncLog.objects.filter(branch=branch, entity_type="heartbeat").first()
        assert log is not None
        assert log.node_id == "node-test-001"
        assert log.status == "received"
        assert log.entity_count == 1

    def test_payload_stored_in_log(self, factory, branch):
        """Full payload is stored in the SyncLog."""
        payload = {"node_id": "node-test-001", "status": "online",
                   "product_count": 10, "sales_count": 5,
                   "extra": "metadata"}
        sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", payload))
        log = BranchSyncLog.objects.filter(branch=branch, entity_type="heartbeat").first()
        assert log is not None
        assert log.payload["status"] == "online"
        assert log.payload["extra"] == "metadata"

    def test_invalid_json_returns_400(self, factory):
        resp = sync_receive_heartbeat(
            factory.post("/sync/push/heartbeat", b"bad", content_type="application/json"))
        assert resp.status_code == 400

    def test_unknown_node_returns_404(self, factory):
        payload = {"node_id": "ghost", "status": "online"}
        resp = sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", payload))
        assert resp.status_code == 404

    def test_inactive_branch_returns_404(self, factory, inactive_branch):
        payload = {"node_id": "node-inactive-001", "status": "online"}
        resp = sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", payload))
        assert resp.status_code == 404

    def test_missing_node_id_returns_404(self, factory):
        """Missing node_id defaults to 'unknown' which won't match any branch → 404."""
        payload = {"status": "online"}
        resp = sync_receive_heartbeat(_post(factory, "/sync/push/heartbeat", payload))
        assert resp.status_code == 404

    def test_get_method_rejected_405(self, factory):
        """@require_POST rejects GET requests with 405."""
        resp = sync_receive_heartbeat(factory.get("/sync/push/heartbeat"))
        assert resp.status_code == 405
