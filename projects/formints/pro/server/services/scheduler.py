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
    # Offline outbox handoff — persist a failed push for retry
    # ------------------------------------------------------------------

    def _enqueue_failed_push_sync(self, entity_type: str, payload: dict) -> bool:
        """Sync: persist a failed cloud push into the durable ``OutboxQueue``.

        ``OfflineQueueService`` retries the entry (with exponential backoff and
        dead-lettering) once the cloud master is reachable again, so a transient
        sync failure is never lost.

        Dedup guard: a periodic scheduler would otherwise pile up one entry per
        cycle while the cloud is down, so at most one pending/failed entry is
        kept per (node, entity_type). Returns True when a new entry was queued.
        """
        from models.outbox import OutboxQueue
        from services.outbox import OfflineQueueService

        try:
            if OutboxQueue.objects.filter(
                node_id=self.node_id,
                entity_type=entity_type,
                status__in=["pending", "failed"],
            ).exists():
                return False
            OfflineQueueService().enqueue(
                entity_type=entity_type,
                entity_id="",
                action="push",
                payload=payload,
                node_id=self.node_id,
            )
            return True
        except Exception as exc:
            logger.warning(
                "Could not enqueue failed %s push into offline outbox: %s",
                entity_type, exc,
            )
            return False

    async def _enqueue_failed_push(self, entity_type: str, payload: dict) -> bool:
        """Async wrapper for ``_enqueue_failed_push_sync`` (offloads DB I/O)."""
        return await sync_to_async(self._enqueue_failed_push_sync)(entity_type, payload)

    # ------------------------------------------------------------------
    # Sync cycle
    # ------------------------------------------------------------------

    async def _sync_cycle(self) -> dict:
        """Run one full sync cycle: products, sales, inventory, heartbeat.

        Uses DataToken sync_batch() for indexed queries when django-fusion
        is available, falling back to table scans otherwise. After each
        successful push, tagged tokens are auto-marked as synced.

        After each cycle, runs cleanup tasks to purge old synced DataTokens
        and stale sync logs.
        """
        from routes.state import SyncClient, _log_sync

        cloud = SyncClient()
        results: dict[str, Any] = {"products": 0, "sales": 0, "inventory": 0}

        # ── Try DataToken-based indexed sync first ──
        try:
            from django_fusion.core.models import DataToken
            results = await self._sync_via_datatoken(cloud, _log_sync)
            self._last_sync_at = datetime.now(timezone.utc)
            # ── Run cleanup after successful sync — purge old synced tokens and stale logs
            await self._run_cleanup()
            # ── Best-effort Loop-CRM POS ingest push (Formint ↔ Loop-CRM) ──
            await self._push_loop_ingest()
            return results
        except ImportError:
            logger.debug("django-fusion not available — falling back to table scans")
        except Exception as exc:
            logger.debug("DataToken sync unavailable: %s — falling back to table scans", exc)

        # ── Fallback: table-scan queries ──
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
            payload = {"node_id": self.node_id, "products": products}
            try:
                r = await cloud._push("products", payload)
                results["products"] = len(products)
                await _log_sync(
                    self.node_id, "products_branch", "auto-scheduled",
                    r.get("status", "unknown"), r.get("error", ""),
                )
            except Exception as exc:
                logger.warning("Failed to push products to cloud: %s", exc)
                r = {"status": "failed", "error": str(exc)}
            if r.get("status") == "failed":
                await self._enqueue_failed_push("products", payload)

        # ── Push sales ──
        if sales:
            payload = {"node_id": self.node_id, "sales": sales}
            try:
                r = await cloud._push("sales", payload)
                results["sales"] = len(sales)
                await _log_sync(
                    self.node_id, "sales_branch", "auto-scheduled",
                    r.get("status", "unknown"), r.get("error", ""),
                )
            except Exception as exc:
                logger.warning("Failed to push sales to cloud: %s", exc)
                r = {"status": "failed", "error": str(exc)}
            if r.get("status") == "failed":
                await self._enqueue_failed_push("sales", payload)

        # ── Push inventory ──
        if inventory:
            payload = {"node_id": self.node_id, "transactions": inventory}
            try:
                r = await cloud._push("inventory", payload)
                results["inventory"] = len(inventory)
                await _log_sync(
                    self.node_id, "inventory_branch", "auto-scheduled",
                    r.get("status", "unknown"), r.get("error", ""),
                )
            except Exception as exc:
                logger.warning("Failed to push inventory to cloud: %s", exc)
                r = {"status": "failed", "error": str(exc)}
            if r.get("status") == "failed":
                await self._enqueue_failed_push("inventory", payload)

        # ── Heartbeat ──
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
        # ── Run cleanup after fallback sync too — purge old tokens and stale logs
        await self._run_cleanup()
        # ── Best-effort Loop-CRM POS ingest push (Formint ↔ Loop-CRM) ──
        await self._push_loop_ingest()
        return results

    async def _push_loop_ingest(self) -> None:
        """Push completed/refunded sales to Loop-CRM (best-effort).

        Runs alongside the existing POS Cloud sync; an unconfigured Loop-CRM
        link (no ``LOOP_CRM_URL``/``LOOP_CRM_INGEST_API_KEY``) is a no-op so a
        terminal without the CRM integration never fails its sync cycle.
        """
        try:
            from services.pos_ingest import push_pending_sales

            result = await sync_to_async(push_pending_sales)(limit=500)
            if result.get("status") != "skipped":
                logger.info(
                    "Loop-CRM ingest: status=%s count=%s",
                    result.get("status"), result.get("count"),
                )
        except Exception as exc:  # noqa: BLE001 - never break the sync cycle
            logger.debug("Loop-CRM ingest push skipped: %s", exc)

    async def _sync_via_datatoken(self, cloud, _log_sync) -> dict:
        """Sync using DataToken indexed batches (fast path).

        Groups tokens by content_type (exact match) and pushes each
        group as a single batch HTTP request — not one per token.
        """
        from django_fusion.core.models import DataToken

        results: dict[str, Any] = {"products": 0, "sales": 0, "inventory": 0}
        synced_token_ids: list[int] = []

        batch = DataToken.objects.sync_batch(node_id=self.node_id, limit=100)

        @sync_to_async
        def _get_batch():
            return list(batch)

        tokens = await _get_batch()

        # ── Group tokens by content_type for batched push ──
        grouped: dict[str, tuple[list[dict], list[int]]] = {
            "product": ([], []),
            "sale": ([], []),
            "inventorytransaction": ([], []),
        }

        for token in tokens:
            ct_model = token.content_type.model if token.content_type_id else ""
            obj = token.content_object
            if obj is None or ct_model not in grouped:
                continue

            payloads, tids = grouped[ct_model]
            tids.append(token.pk)

            if ct_model == "product":
                payloads.append({
                    "id": obj.pk,
                    "name": str(getattr(obj, "name", "")),
                    "price": float(getattr(obj, "price", 0) or 0),
                    "sku": str(getattr(obj, "sku", "") or ""),
                    "stock_quantity": int(getattr(obj, "stock_quantity", 0) or 0),
                })
            elif ct_model == "sale":
                payloads.append({
                    "id": obj.pk,
                    "customer_name": str(getattr(obj, "customer_name", "")),
                    "total_amount": float(getattr(obj, "total_amount", 0) or 0),
                    "payment_method": str(getattr(obj, "payment_method", "cash")),
                })
            elif ct_model == "inventorytransaction":
                payloads.append({
                    "id": obj.pk,
                    "product_name": str(getattr(obj, "product_name", "")),
                    "transaction_type": _TRANSACTION_TYPE_MAP.get(
                        str(getattr(obj, "transaction_type", "in")), "addition"),
                    "quantity": int(getattr(obj, "quantity", 0) or 0),
                })

        # ── Push each group as a single batch request ──
        entity_map = {
            "product": ("products", "products"),
            "sale": ("sales", "sales"),
            "inventorytransaction": ("inventory", "transactions"),
        }

        for ct_model, (push_endpoint, payload_key) in entity_map.items():
            payloads, tids = grouped[ct_model]
            if not payloads:
                continue
            payload = {"node_id": self.node_id, payload_key: payloads}
            try:
                r = await cloud._push(push_endpoint, payload)
                results_key = {
                    "products": "products",
                    "sales": "sales",
                    "inventory": "inventory",
                }.get(push_endpoint, push_endpoint)
                results[results_key] = len(payloads)
                await _log_sync(
                    self.node_id, f"{ct_model}_branch", "auto-scheduled",
                    r.get("status", "unknown"), r.get("error", ""),
                )
                if r.get("status") == "received":
                    synced_token_ids.extend(tids)
            except Exception as exc:
                logger.warning("Failed to push %s batch via DataToken: %s", ct_model, exc)
                r = {"status": "failed", "error": str(exc)}
            if r.get("status") == "failed":
                await self._enqueue_failed_push(push_endpoint, payload)

        # ── Bulk-mark synced tokens ──
        if synced_token_ids:
            @sync_to_async
            def _mark():
                DataToken.objects.mark_batch_synced(synced_token_ids)
            await _mark()

        # ── Heartbeat ──
        try:
            await cloud._push("heartbeat", {
                "node_id": self.node_id,
                "status": "online",
                "product_count": results["products"],
                "sales_count": results["sales"],
            })
        except Exception as exc:
            logger.warning("Failed to send heartbeat: %s", exc)

        logger.info(
            "DataToken sync #%d: products=%d, sales=%d, inventory=%d, tokens_synced=%d",
            self._sync_count + 1,
            results["products"], results["sales"], results["inventory"],
            len(synced_token_ids),
        )
        return results

    # ------------------------------------------------------------------
    # Cleanup tasks — run after each successful sync cycle
    # ------------------------------------------------------------------

    async def _run_cleanup(self) -> None:
        """Post-sync cleanup: purge old synced DataTokens and stale sync logs.

        Runs after each successful sync cycle to keep the DataToken table
        from growing unboundedly. Cleans:
          1. DataToken rows that have been marked as synced and are older
             than 7 days (configurable via POS_FULL_TOKEN_RETENTION_DAYS).
          2. SyncLog entries older than 30 days (configurable via
             POS_FULL_SYNC_LOG_RETENTION_DAYS).
          3. Resets error count in sync_state if there were no recent errors.
        """
        token_retention = int(os.environ.get("POS_FULL_TOKEN_RETENTION_DAYS", "7"))
        log_retention = int(os.environ.get("POS_FULL_SYNC_LOG_RETENTION_DAYS", "30"))

        try:
            from datetime import timedelta

            from django_fusion.core.models import DataToken

            cutoff = datetime.now(timezone.utc) - timedelta(days=token_retention)

            @sync_to_async
            def _purge_tokens():
                deleted, _ = DataToken.objects.filter(
                    is_synced=True,
                    synced_at__lt=cutoff,
                ).delete()
                return deleted

            purged = await _purge_tokens()
            if purged:
                logger.info("Cleanup: purged %d synced DataToken(s) older than %d days",
                            purged, token_retention)
        except ImportError:
            pass  # django-fusion not available — skip DataToken cleanup
        except Exception as exc:
            logger.debug("DataToken cleanup skipped: %s", exc)

        # ── Purge stale sync logs ──
        try:
            from datetime import timedelta

            from routes.state import SyncLog

            log_cutoff = datetime.now(timezone.utc) - timedelta(days=log_retention)

            @sync_to_async
            def _purge_logs():
                deleted, _ = SyncLog.objects.filter(created_at__lt=log_cutoff).delete()
                return deleted

            purged_logs = await _purge_logs()
            if purged_logs:
                logger.info("Cleanup: purged %d SyncLog(s) older than %d days",
                            purged_logs, log_retention)
        except Exception as exc:
            logger.debug("SyncLog cleanup skipped: %s", exc)

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
            from datetime import timedelta

            from models.pos import Sale
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
            from datetime import timedelta

            from models.pos import InventoryTransaction
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
