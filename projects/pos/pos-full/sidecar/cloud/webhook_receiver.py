"""
Cloud Master Webhook Receiver.
Accepts webhooks from Solo/Minimal nodes across the POS network.
Replaces the old Sanic webhook receiver with Django views.

@tested pos-portal/full - Webhook receiver for cloud master
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger("cloud.webhook")

DATA_DIR = Path(__file__).parent.parent / "cloud_data" / "webhooks"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _store_webhook(event_type: str, payload: dict) -> dict:
    _ensure_dir()
    webhook_id = str(uuid.uuid4())
    record = {
        "webhook_id": webhook_id,
        "event_type": event_type,
        "received_at": datetime.utcnow().isoformat(),
        **payload,
    }
    log_file = DATA_DIR / f"{event_type}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(record) + "\n")

    return {
        "status": "received",
        "webhook_id": webhook_id,
        "event_type": event_type,
        "timestamp": record["received_at"],
    }


@csrf_exempt
@require_POST
def receive_node_aggregate(request):
    """Receive aggregated node data from Solo scanner."""
    payload = json.loads(request.body)
    result = _store_webhook("node_aggregate", payload)
    node_count = payload.get("data", {}).get("node_count", 0)
    logger.info("Received node aggregate: %d nodes", node_count)
    return JsonResponse(result, status=202)


@csrf_exempt
@require_POST
def receive_transaction_batch(request):
    """Receive a batch of transactions from Solo/Minimal nodes."""
    payload = json.loads(request.body)
    count = payload.get("data", {}).get("count", 0)
    result = _store_webhook("transaction_batch", payload)
    logger.info("Received transaction batch: %d transactions", count)
    return JsonResponse(result, status=202)


@csrf_exempt
@require_POST
def receive_product_update(request):
    """Receive product catalog updates from any POS node."""
    payload = json.loads(request.body)
    result = _store_webhook("product_update", payload)
    logger.info("Received product update")
    return JsonResponse(result, status=202)


@csrf_exempt
@require_POST
def receive_heartbeat(request):
    """Receive a heartbeat from any service (Solo, Minimal)."""
    payload = json.loads(request.body)
    result = _store_webhook("heartbeat", payload)
    return JsonResponse(result, status=202)


@require_GET
def webhook_stats(request):
    """Get webhook statistics summary."""
    _ensure_dir()
    stats = {"total_webhooks": 0}
    for etype in ("node_aggregate", "transaction_batch", "product_update", "heartbeat"):
        log_file = DATA_DIR / f"{etype}.jsonl"
        count = sum(1 for _ in open(log_file)) if log_file.exists() else 0
        stats[etype] = count
        stats["total_webhooks"] += count
    stats["status"] = "ok"
    return JsonResponse(stats)
