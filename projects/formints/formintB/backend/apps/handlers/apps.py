"""POS Cloud — Handlers Django app config (consumers, dashboard, fragments, sync API)."""

import logging

from django.apps import AppConfig


class HandlersConfig(AppConfig):
    name = "apps.handlers"
    label = "handlers"
    verbose_name = "POS Cloud — Request Handlers"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Register sync broker handlers for incoming terminal messages."""
        from apps.domain.sync_broker import broker
        from apps.handlers.sync_api import _broadcast_sync_event

        from datetime import datetime, timezone

        logger = logging.getLogger("pos.sync_events")

        def _on_sync_push(branch_code: str, payload: dict):
            """Handle sync_push messages from branches via WebSocket."""
            entity_type = payload.get("entity_type", "unknown")
            count = payload.get("count", 0)
            logger.info(
                "WebSocket sync_push from %s: %s x%d",
                branch_code, entity_type, count,
            )
            _broadcast_sync_event(entity_type, {
                "entity_type": entity_type,
                "synced": count,
                "branch": branch_code,
                "node_id": payload.get("node_id", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        def _on_heartbeat(branch_code: str, payload: dict):
            """Handle heartbeat messages from branches via WebSocket."""
            status = payload.get("status", "online")
            logger.info(
                "WebSocket heartbeat from %s: %s", branch_code, status,
            )
            _broadcast_sync_event("heartbeat", {
                "entity_type": "heartbeat",
                "branch": branch_code,
                "node_id": payload.get("node_id", ""),
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        def _on_ack(branch_code: str, payload: dict):
            """Handle acknowledgment messages from branches."""
            queue_item_id = payload.get("queue_item_id")
            logger.info(
                "Ack from %s for queue item %s", branch_code, queue_item_id,
            )

        broker.on("sync_push", _on_sync_push)
        broker.on("heartbeat", _on_heartbeat)
        broker.on("ack", _on_ack)
