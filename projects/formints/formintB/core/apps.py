"""POS Cloud — Core Django app config with django-fusion fragment auto-registration."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"
    label = "core"
    verbose_name = "POS Cloud — Branches, Orgs, Leads & Reports"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Register django-fusion fragments and sync broker handlers at startup."""
        from .fragments import tables, modals, reports, layouts, skeletons  # noqa: F401

        # Register broker handlers for incoming messages from POS terminals
        from .sync_broker import broker
        from .sync_api import _broadcast_sync_event

        from datetime import datetime, timezone

        def _on_sync_push(branch_code: str, payload: dict):
            """Handle sync_push messages from branches via WebSocket."""
            logger = logging.getLogger("pos.sync_events")
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
            logger = logging.getLogger("pos.sync_events")
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
            logger = logging.getLogger("pos.sync_events")
            queue_item_id = payload.get("queue_item_id")
            logger.info(
                "Ack from %s for queue item %s", branch_code, queue_item_id,
            )

        broker.on("sync_push", _on_sync_push)
        broker.on("heartbeat", _on_heartbeat)
        broker.on("ack", _on_ack)
