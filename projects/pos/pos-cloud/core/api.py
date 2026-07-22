"""POS Cloud — Analytics API for branch sync data.

Provides REST endpoints consumed by the analytics dashboard at /apis/.
Auto-discovered by django_bolt's autodiscover_apis() on startup.
"""

import msgspec
from django_bolt import BoltAPI

from .models import (
    BranchProduct, BranchSale, BranchInventory, BranchSyncLog,
    Organization, Branch,
)

api = BoltAPI(prefix="/apis/data")


# ── Serializers ──

class ProductSummary(msgspec.Struct):
    id: int
    name: str
    branch_name: str
    sku: str
    price: str  # Decimal → str for JSON
    stock_quantity: int
    last_synced_at: str | None = None


class SaleSummary(msgspec.Struct):
    id: int
    branch_name: str
    customer_name: str
    total_amount: str
    payment_method: str
    sale_date: str | None = None


class InventorySummary(msgspec.Struct):
    id: int
    branch_name: str
    product_name: str
    transaction_type: str
    quantity: int
    transaction_date: str | None = None


class SyncStats(msgspec.Struct):
    total_products: int
    total_sales: int
    total_inventory: int
    total_sync_logs: int
    branches: int
    organizations: int


class BranchStats(msgspec.Struct):
    name: str
    node_id: str
    products: int
    sales: int
    inventory_txs: int
    # Sync metrics from BranchSyncLog
    sync_count: int = 0
    sync_errors: int = 0
    last_sync_at: str | None = None


class SyncLogEntry(msgspec.Struct):
    id: int
    branch_name: str
    node_id: str
    entity_type: str
    entity_count: int
    status: str
    received_at: str | None = None


# ── Analytics Endpoints ──

@api.get("/stats")
async def sync_stats() -> SyncStats:
    """Overall sync statistics for the dashboard."""
    return SyncStats(
        total_products=await BranchProduct.objects.acount(),
        total_sales=await BranchSale.objects.acount(),
        total_inventory=await BranchInventory.objects.acount(),
        total_sync_logs=await BranchSyncLog.objects.acount(),
        branches=await Branch.objects.filter(is_active=True).acount(),
        organizations=await Organization.objects.acount(),
    )


@api.get("/products")
async def list_products(limit: int = 50) -> list[ProductSummary]:
    """Latest synced products from all branches."""
    products = []
    async for p in BranchProduct.objects.select_related("branch").order_by("-last_synced_at")[:limit]:
        products.append(ProductSummary(
            id=p.id, name=p.name, branch_name=p.branch.name,
            sku=p.sku, price=str(p.price), stock_quantity=p.stock_quantity,
            last_synced_at=p.last_synced_at.isoformat() if p.last_synced_at else None,
        ))
    return products


@api.get("/sales")
async def list_sales(limit: int = 50) -> list[SaleSummary]:
    """Latest sales from all branches."""
    sales = []
    async for s in BranchSale.objects.select_related("branch").order_by("-sale_date")[:limit]:
        sales.append(SaleSummary(
            id=s.id, branch_name=s.branch.name, customer_name=s.customer_name,
            total_amount=str(s.total_amount), payment_method=s.payment_method,
            sale_date=s.sale_date.isoformat() if s.sale_date else None,
        ))
    return sales


@api.get("/inventory")
async def list_inventory(limit: int = 50) -> list[InventorySummary]:
    """Latest inventory transactions from all branches."""
    txs = []
    async for tx in BranchInventory.objects.select_related("branch").order_by("-transaction_date")[:limit]:
        txs.append(InventorySummary(
            id=tx.id, branch_name=tx.branch.name, product_name=tx.product_name,
            transaction_type=tx.transaction_type, quantity=tx.quantity,
            transaction_date=tx.transaction_date.isoformat() if tx.transaction_date else None,
        ))
    return txs


@api.get("/branches")
async def branch_stats() -> list[BranchStats]:
    """Per-branch statistics with sync metrics."""
    stats = []
    async for b in Branch.objects.filter(is_active=True):
        # Aggregate sync metrics from BranchSyncLog
        sync_count = await b.sync_logs.acount()
        sync_errors = await b.sync_logs.filter(status="failed").acount()
        last_sync = await b.sync_logs.order_by("-received_at").afirst()
        stats.append(BranchStats(
            name=b.name, node_id=b.node_id,
            products=await b.synced_products.acount(),
            sales=await b.synced_sales.acount(),
            inventory_txs=await b.synced_inventory.acount(),
            sync_count=sync_count,
            sync_errors=sync_errors,
            last_sync_at=last_sync.received_at.isoformat() if last_sync else None,
        ))
    return stats


@api.get("/sync-logs")
async def recent_sync_logs(limit: int = 30) -> list[SyncLogEntry]:
    """Recent sync activity across all branches."""
    entries = []
    async for sl in BranchSyncLog.objects.select_related("branch").order_by("-received_at")[:limit]:
        entries.append(SyncLogEntry(
            id=sl.id,
            branch_name=sl.branch.name if sl.branch else "unknown",
            node_id=sl.node_id,
            entity_type=sl.entity_type,
            entity_count=sl.entity_count,
            status=sl.status,
            received_at=sl.received_at.isoformat() if sl.received_at else None,
        ))
    return entries
