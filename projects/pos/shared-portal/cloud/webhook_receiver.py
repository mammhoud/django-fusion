"""
Cloud Master — Webhook Receiver.

Accepts webhooks from Solo aggregator and Minimal nodes across the POS network.

Endpoints:
  POST /api/webhooks/node-aggregate     — aggregated node data from Solo scanner
  POST /api/webhooks/transaction-batch  — batched transactions
  POST /api/webhooks/product-update     — product catalog updates
  POST /api/webhooks/settings-sync      — restaurant settings sync
  POST /api/webhooks/heartbeat          — node/service heartbeats

Architecture:
  pos-minimal  ──>  pos-solo (aggregator)  ──webhook──>  shared-portal/cloud (master)
                                                              │
                                                        stores in sync_proxy
                                                        + returns ack + webhook_id

Related Names: webhook, receiver, master, cloud, sync
Tags: #webhook #receiver #master #cloud #sync
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from sanic import Blueprint, Request
from sanic.response import json as sanic_json

logger = logging.getLogger("cloud_webhook_receiver")

webhook_bp = Blueprint("webhooks", url_prefix="/api/webhooks")

# ── Storage ───────────────────────────────────────────────────────────

DATA_DIR: Path = Path("./cloud_data") / "webhooks"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _store_webhook(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Store a received webhook payload and return a receipt."""
    _ensure_dir()
    webhook_id = str(uuid.uuid4())
    record = {
        "webhook_id": webhook_id,
        "event_type": event_type,
        "received_at": datetime.utcnow().isoformat(),
        **payload,
    }
    # Append to event-specific log
    log_file = DATA_DIR / f"{event_type}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(record) + "\n")

    return {
        "status": "received",
        "webhook_id": webhook_id,
        "event_type": event_type,
        "timestamp": record["received_at"],
    }


def _load_webhook_log(event_type: str, limit: int = 50) -> list[dict]:
    """Load recent webhook records for an event type."""
    log_file = DATA_DIR / f"{event_type}.jsonl"
    if not log_file.exists():
        return []
    records = []
    with open(log_file, "r") as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                pass
    return records[-limit:]


# ── Endpoints ─────────────────────────────────────────────────────────

@webhook_bp.post("/node-aggregate")
async def receive_node_aggregate(request: Request):
    """Receive aggregated node data from Solo scanner."""
    payload = request.json or {}
    result = _store_webhook("node_aggregate", payload)
    node_count = payload.get("data", {}).get("node_count", 0)
    logger.info("Received node aggregate: %d nodes", node_count)
    return sanic_json(result, status=202)


@webhook_bp.post("/transaction-batch")
async def receive_transaction_batch(request: Request):
    """Receive a batch of transactions from Solo/Minimal nodes."""
    payload = request.json or {}
    data = payload.get("data", {})
    count = data.get("count", 0)
    result = _store_webhook("transaction_batch", payload)
    logger.info("Received transaction batch: %d transactions", count)
    return sanic_json(result, status=202)


@webhook_bp.post("/product-update")
async def receive_product_update(request: Request):
    """Receive product catalog updates from any POS node."""
    payload = request.json or {}
    data = payload.get("data", {})
    count = data.get("count", 0)
    result = _store_webhook("product_update", payload)
    logger.info("Received product update: %d products", count)
    return sanic_json(result, status=202)


@webhook_bp.post("/settings-sync")
async def receive_settings_sync(request: Request):
    """Receive restaurant settings sync."""
    payload = request.json or {}
    result = _store_webhook("settings_sync", payload)
    logger.info("Received settings sync")
    return sanic_json(result, status=202)


@webhook_bp.post("/heartbeat")
async def receive_heartbeat(request: Request):
    """Receive a heartbeat from any service (Solo, Minimal)."""
    payload = request.json or {}
    source = request.headers.get("X-Webhook-Source", "unknown")
    result = _store_webhook("heartbeat", {
        "source": source,
        **payload,
    })
    return sanic_json(result, status=202)


@webhook_bp.get("/log")
async def get_webhook_log(request: Request):
    """Get webhook history, optionally filtered by event_type.

    Query params:
        event_type  Filter by event type (node_aggregate, transaction_batch, etc.)
        limit       Max records to return (default: 50)

    Returns a dict with 'event_type', 'total', and 'records' list.
    """
    event_type = request.args.get("event_type", "")
    limit = int(request.args.get("limit", 50))

    if event_type:
        records = _load_webhook_log(event_type, limit)
        return sanic_json({
            "event_type": event_type,
            "total": len(records),
            "records": records,
        })

    # Return summary of all event types
    summary: dict[str, int] = {}
    for etype in ("node_aggregate", "transaction_batch", "product_update",
                  "settings_sync", "heartbeat"):
        records = _load_webhook_log(etype, 1)
        summary[etype] = len(records)
    return sanic_json({
        "event_type": "summary",
        "total": sum(summary.values()),
        "records": summary,
    })


@webhook_bp.get("/stats")
async def get_webhook_stats(request: Request):
    """Get webhook statistics summary."""
    _ensure_dir()
    stats: dict[str, Any] = {"total_webhooks": 0}
    for etype in ("node_aggregate", "transaction_batch", "product_update",
                  "settings_sync", "heartbeat"):
        log = _load_webhook_log(etype, 10000)
        stats[etype] = len(log)
        stats["total_webhooks"] += len(log)
    stats["status"] = "ok"
    return sanic_json(stats)
@tested shared-portal/cloud - POS-KO → POS, POSKO-* → POS-* rename verified
