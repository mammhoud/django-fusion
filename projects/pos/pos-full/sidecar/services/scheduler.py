"""POS Full — Scheduled branch-data sync to POS Cloud.

Runs as a background asyncio task that periodically queries local
products, sales, and inventory data and pushes them to the POS Cloud
sync receiver API.

Configuration (priority: env > CLI flag > default):
    POS_FULL_SYNC_INTERVAL=60     # Seconds between sync cycles
    POS_FULL_SYNC_ENABLED=true    # Enable/disable scheduled sync

The scheduler respects the sync_state.json "enabled" flag so it can
be toggled at runtime via PATCH /sync/config.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async

logger = logging.getLogger("pos.scheduler")

# Map pos-full local transaction types to pos-cloud expected values.
# pos-full models use 'in'/'out'/'adjustment'/'return'
# pos-cloud models expect 'addition'/'removal'/'adjustment'/'transfer'
_TRANSACTION_TYPE_MAP: dict[str, str] = {
    "in": "addition",
    "out": "removal",
    "adjustment": "adjustment",
    "return": "addition",  # Returning items adds stock back
}


class BranchSyncScheduler:
    """Background scheduler that pushes branch data to POS Cloud periodically.

    Queries local Django ORM models and serializes them for the cloud
    sync receivers. Runs in its own asyncio task so it never blocks the
    main Robyn event loop.
    """

    def __init__(
        self,
        interval: int = 60,
        enabled: bool = True,
        node_id: str = "pos-full-auto",
    ):
        self.interval = interval
        self._enabled = enabled
        self.node_id = node_id
        self._task: asyncio.Task | None = None
        self._running = False
        self._last_sync_at: datetime | None = None
        self._sync_count = 0
        self._error_count = 0

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def stats(self) -> dict:
        return {
            "running": self._running,
            "interval_s": self.interval,
            "enabled": self._enabled,
            "node_id": self.node_id,
            "last_sync_at": self._last_sync_at.isoformat() if self._last_sync_at else None,
            "sync_count": self._sync_count,
            "error_count": self._error_count,
        }

    async def update_interval(self, seconds: int) -> dict:
        """Change the sync interval at runtime.

        The new interval takes effect on the next sleep cycle — no
        restart or task recreation needed. Persists to sync_state.json
        so the setting survives server restarts.
        """
        if seconds < 5:
            return {"status": "error", "message": "Interval must be at least 5 seconds", "interval": self.interval}

        old = self.interval
        self.interval = seconds

        # Persist to sync_state.json
        try:
            from routes.state import _load_sync_state, _save_sync_state
            state = _load_sync_state()
            state["sync_interval"] = seconds
            _save_sync_state(state)
        except Exception as exc:
            logger.warning("Could not persist interval to sync_state.json: %s", exc)

        logger.info("Sync interval changed: %ds → %ds", old, seconds)
        return {"status": "ok", "previous_interval": old, **self.stats}

    async def toggle(self, enabled: bool) -> dict:
        """Enable or disable the scheduler at runtime.

        Only flips the _enabled flag — the existing _loop() already
        checks _is_sync_enabled() on every cycle, so it will stop or
        resume syncing on the next iteration. Persists to sync_state.json
        so the setting survives server restarts.
        """
        if enabled and not self._running:
            return {
                "status": "not_running",
                "message": "Scheduler was not started at boot. Restart with --sync-interval flag.",
                "enabled": False,
            }

        self._enabled = enabled

        # Persist to sync_state.json
        try:
            from routes.state import _load_sync_state, _save_sync_state
            state = _load_sync_state()
            state["enabled"] = enabled
            _save_sync_state(state)
        except Exception as exc:
            logger.warning("Could not persist toggle to sync_state.json: %s", exc)

        if enabled:
            logger.info("Scheduler re-enabled — will resume on next cycle")
        else:
            logger.info("Scheduler disabled — skipping future cycles")

        return {"status": "ok", **self.stats}

    async def start(self) -> None:
        """Start the background sync loop if not already running."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        if not self._enabled:
            logger.info("Scheduler disabled — not starting")
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(
            "Branch sync scheduler started (interval=%ds, node_id=%s)",
            self.interval, self.node_id,
        )

    async def stop(self) -> None:
        """Stop the background sync loop gracefully.

        NOTE: When the scheduler runs in a daemon thread (the default
        in server.py), the thread is killed on process exit and this
        method will never be called. It exists for non-daemon usage
        (e.g., testing or embedded scenarios).
        """
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Branch sync scheduler stopped (synced=%d, errors=%d)",
                     self._sync_count, self._error_count)

    async def _loop(self) -> None:
        """Main loop — sleep for interval, then sync, repeat."""
        while self._running:
            try:
                # Re-read interval from sync_state.json at each cycle so
                # runtime changes (via PATCH /sync/scheduler/interval) survive
                # server restarts (consistent with _is_sync_enabled pattern).
                self._refresh_interval()

                # Re-check enabled flag from sync_state.json at each cycle
                if not self._is_sync_enabled():
                    logger.debug("Sync disabled via config — skipping cycle")
                    await asyncio.sleep(self.interval)
                    continue

                await self._sync_cycle()
                self._sync_count += 1
            except Exception as exc:
                self._error_count += 1
                logger.error("Sync cycle failed: %s", exc)

            await asyncio.sleep(self.interval)

    def _refresh_interval(self) -> None:
        """Re-read the sync interval from sync_state.json.

        Allows runtime interval changes to survive server restarts.
        Uses the existing self.interval as fallback if the state file
        is unreadable or the stored value is invalid.
        """
        try:
            from routes.state import _load_sync_state
            state = _load_sync_state()
            stored = state.get("sync_interval")
            if isinstance(stored, (int, float)) and stored >= 5:
                self.interval = int(stored)
        except Exception:
            pass  # Keep existing self.interval on any error

    def _is_sync_enabled(self) -> bool:
        """Check if sync is enabled in sync_state.json AND locally."""
        if not self._enabled:
            return False
        try:
            from routes.state import _load_sync_state
            state = _load_sync_state()
            return state.get("enabled", True)
        except Exception:
            return True  # Default to enabled if state file unreadable

    # ------------------------------------------------------------------
    # Sync cycle
    # ------------------------------------------------------------------

    async def _sync_cycle(self) -> dict:
        """Run one full sync cycle: products, sales, inventory, heartbeat.

        Each data query is individually wrapped so a single failing query
        (e.g., locked SQLite table) doesn't prevent other entity types
        from syncing.
        """
        from routes.state import SyncClient, _log_sync

        cloud = SyncClient()
        results: dict[str, Any] = {"products": 0, "sales": 0, "inventory": 0}

        # ── Query local data (each isolated so one failure doesn't block others) ──
        products: list[dict] = []
        sales: list[dict] = []
        inventory: list[dict] = []

        try:
            products = await self._get_products()
        except Exception as exc:
            logger.warning("Failed to query local products: %s", exc)

        try:
            sales = await self._get_sales()
        except Exception as exc:
            logger.warning("Failed to query local sales: %s", exc)

        try:
            inventory = await self._get_inventory()
        except Exception as exc:
            logger.warning("Failed to query local inventory: %s", exc)

        # ── Push products ──
        if products:
            try:
                r = await cloud._push("products", {
                    "node_id": self.node_id,
                    "products": products,
                })
                results["products"] = len(products)
                await _log_sync(
                    self.node_id, "products_branch", "auto-scheduled",
                    r.get("status", "unknown"), r.get("error", ""),
                )
            except Exception as exc:
                logger.warning("Failed to push products to cloud: %s", exc)

        # ── Push sales ──
        if sales:
            try:
                r = await cloud._push("sales", {
                    "node_id": self.node_id,
                    "sales": sales,
                })
                results["sales"] = len(sales)
                await _log_sync(
                    self.node_id, "sales_branch", "auto-scheduled",
                    r.get("status", "unknown"), r.get("error", ""),
                )
            except Exception as exc:
                logger.warning("Failed to push sales to cloud: %s", exc)

        # ── Push inventory ──
        if inventory:
            try:
                r = await cloud._push("inventory", {
                    "node_id": self.node_id,
                    "transactions": inventory,
                })
                results["inventory"] = len(inventory)
                await _log_sync(
                    self.node_id, "inventory_branch", "auto-scheduled",
                    r.get("status", "unknown"), r.get("error", ""),
                )
            except Exception as exc:
                logger.warning("Failed to push inventory to cloud: %s", exc)

        # ── Heartbeat (always send one per cycle) ──
        try:
            await cloud._push("heartbeat", {
                "node_id": self.node_id,
                "status": "online",
                "product_count": len(products),
                "sales_count": len(sales),
            })
        except Exception as exc:
            logger.warning("Failed to send heartbeat: %s", exc)

        self._last_sync_at = datetime.now(timezone.utc)
        logger.info(
            "Sync cycle #%d: products=%d, sales=%d, inventory=%d",
            self._sync_count + 1,
            len(products), len(sales), len(inventory),
        )
        return results

    # ------------------------------------------------------------------
    # Django ORM queries (sync_to_async wrappers)
    # ------------------------------------------------------------------

    async def _get_products(self) -> list[dict]:
        """Query all active products from the local Django ORM."""
        @sync_to_async
        def _q():
            from models.pos import Product
            return [
                {
                    "id": p.id,
                    "name": str(p.name or ""),
                    "price": float(p.price) if isinstance(p.price, Decimal) else (p.price or 0),
                    "sku": str(p.sku or "") if p.sku else "",
                    "category_name": str(p.category.name) if p.category else "",
                    "stock_quantity": int(p.stock_quantity or 0),
                    "description": str(p.description or ""),
                    "is_active": bool(p.is_active),
                }
                for p in Product.objects.select_related("category").all().order_by("id")[:500]
            ]
        return await _q()

    async def _get_sales(self) -> list[dict]:
        """Query recent sales from the local Django ORM (last 24h)."""
        @sync_to_async
        def _q():
            from models.pos import Sale
            from datetime import timedelta
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            return [
                {
                    "id": s.id,
                    "customer_name": str(s.customer) if s.customer else "",
                    "total_amount": float(s.total) if isinstance(s.total, Decimal) else (s.total or 0),
                    "payment_method": str(s.payment_method or "cash"),
                    "sale_date": s.sale_date.isoformat() if s.sale_date else (s.created_at.isoformat() if s.created_at else datetime.now(timezone.utc).isoformat()),
                    "item_count": s.items.count(),
                    "items": [{"name": si.product_name, "qty": si.quantity, "price": float(si.unit_price)} for si in s.items.all()],
                }
                for s in Sale.objects.prefetch_related("items").select_related("customer").filter(created_at__gte=cutoff).order_by("-id")[:200]
            ]
        return await _q()

    async def _get_inventory(self) -> list[dict]:
        """Query recent inventory transactions from the local Django ORM (last 24h)."""
        @sync_to_async
        def _q():
            from models.pos import InventoryTransaction
            from datetime import timedelta
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            return [
                {
                    "id": t.id,
                    "product_name": str(t.product.name) if t.product else "",
                    "transaction_type": _TRANSACTION_TYPE_MAP.get(
                        str(t.transaction_type), "addition"
                    ),
                    "quantity": int(t.quantity or 0),
                    "notes": str(t.notes or ""),
                    "transaction_date": t.created_at.isoformat() if t.created_at else datetime.now(timezone.utc).isoformat(),
                }
                for t in InventoryTransaction.objects.select_related("product").filter(created_at__gte=cutoff).order_by("-id")[:200]
            ]
        return await _q()


# ------------------------------------------------------------------
# Factory helper for server.py
# ------------------------------------------------------------------

def create_scheduler(
    interval: int | None = None,
    enabled: bool | None = None,
    node_id: str | None = None,
) -> BranchSyncScheduler:
    """Create a BranchSyncScheduler from env vars, sync_state, and defaults.

    Priority: explicit args > env vars > sync_state.json > defaults.
    """
    # Interval
    if interval is None:
        interval = int(os.environ.get("POS_FULL_SYNC_INTERVAL", "60"))

    # Enabled
    if enabled is None:
        env_enabled = os.environ.get("POS_FULL_SYNC_ENABLED", "").lower()
        if env_enabled in ("false", "0", "no"):
            enabled = False
        elif env_enabled in ("true", "1", "yes"):
            enabled = True
        else:
            # Default to enabled; sync_state.json can still disable at runtime
            enabled = True

    # Node ID
    if node_id is None:
        node_id = os.environ.get("POS_FULL_NODE_ID", "pos-full-auto")

    return BranchSyncScheduler(interval=interval, enabled=enabled, node_id=node_id)
