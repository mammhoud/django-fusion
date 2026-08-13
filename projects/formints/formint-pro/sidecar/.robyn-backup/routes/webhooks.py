"""
Webhook receiver route handlers - receive, list, stats.
"""

import json
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify

from routes import state as S

# In-memory store for received webhooks (for testing/debugging)
_received_webhooks: list[dict] = []
_MAX_WEBHOOKS = 100


def register_webhook_routes(app):
    """Register webhook-related routes (Full edition only)."""

    @app.post("/webhooks/receive/:signal_name")
    async def receive_signal_webhook(request, signal_name: str):
        body = request.json() or {}
        entry = {
            "signal": signal_name,
            "id": len(_received_webhooks) + 1,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "payload": body.get("payload", {}),
            "timestamp": body.get("timestamp", ""),
            "headers": {
                k: v for k, v in request.headers.items()
                if k.lower().startswith("x-") or k.lower() in ("content-type", "user-agent")
            },
        }
        _received_webhooks.append(entry)
        while len(_received_webhooks) > _MAX_WEBHOOKS:
            _received_webhooks.pop(0)
        return jsonify({"status": "received", "signal": signal_name, "id": entry["id"]})

    @app.get("/webhooks/receive")
    async def list_received_webhooks(request):
        signal_filter = request.query_params.get("signal", "")
        limit = min(int(str(request.query_params.get("limit", "50"))), _MAX_WEBHOOKS)
        entries = _received_webhooks
        if signal_filter:
            entries = [e for e in entries if e["signal"] == signal_filter]
        return jsonify({
            "total": len(entries),
            "entries": entries[-limit:],
            "by_signal": {
                s: sum(1 for e in _received_webhooks if e["signal"] == s)
                for s in set(e["signal"] for e in _received_webhooks)
            },
        })

    @app.get("/webhooks/receive/stats")
    async def webhook_receive_stats(request):
        total = len(_received_webhooks)
        by_signal = {}
        for e in _received_webhooks:
            sig = e["signal"]
            by_signal[sig] = by_signal.get(sig, 0) + 1

        @sync_to_async
        def _audit_stats():
            return {
                "total_audit_events": S.SignalEvent.objects.count(),
                "webhooks_sent": S.SignalEvent.objects.filter(webhook_status="sent").count(),
                "webhooks_failed": S.SignalEvent.objects.filter(webhook_status="failed").count(),
                "webhooks_skipped": S.SignalEvent.objects.filter(webhook_status="skipped").count(),
            }

        audit = await _audit_stats()
        return jsonify({
            "received": {"total": total, "by_signal": by_signal},
            "audit_trail": audit,
        })
