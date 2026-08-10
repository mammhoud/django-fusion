"""
POS Cloud — WebSocket Broker for Bidirectional Real-Time Sync.

Brokers messages between connected POS terminals and the cloud server.
Each branch gets a dedicated channel group so the cloud can push
targeted updates (catalog refresh, config change, approval resolution)
without broadcasting to all terminals.

Architecture
------------
                ┌───────────────────────────┐
                │  Django Channels Layer     │
                │  (Redis / In-Memory)       │
                └──────┬─────────────────┬──┘
                       │                 │
              ┌────────▼──┐     ┌────────▼──┐
              │ branch_abc │     │ branch_xyz │
              │ group      │     │ group      │
              ├───────────┤     ├───────────┤
              │ WS Client │     │ WS Client │
              │ (pos-full)│     │ (pos-full)│
              └───────────┘     └───────────┘

Cloud services use ``SyncBroker.push_to_branch()`` to send a message
to all connected terminals of a specific branch.  The broker also
supports broadcasting to all connected branches (e.g., for global
config updates) and per-branch health checks.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone as django_timezone

logger = logging.getLogger("pos.sync_broker")


# ══════════════════════════════════════════════════════════════════════
# Data types
# ══════════════════════════════════════════════════════════════════════


@dataclass
class BrokerMessage:
    """A message sent through the sync broker."""

    type: str  # Message type discriminator
    payload: dict[str, Any] = field(default_factory=dict)
    source_node_id: str = ""
    target_branch_code: str = ""
    message_id: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "broker_message",
            "subtype": self.type,
            "payload": self.payload,
            "source_node_id": self.source_node_id,
            "target_branch_code": self.target_branch_code,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
        }


# ══════════════════════════════════════════════════════════════════════
# Channel Group Helpers
# ══════════════════════════════════════════════════════════════════════

# Channel group name format per branch:  "branch_{branch_code}"
# Global broadcast group:                "sync_broadcast"


def _branch_group(branch_code: str) -> str:
    """Get the channel group name for a specific branch."""
    return f"branch_{branch_code}"


# ══════════════════════════════════════════════════════════════════════
# Broker
# ══════════════════════════════════════════════════════════════════════


class SyncBroker:
    """Brokers real-time messages between cloud and connected POS terminals.

    Usage::

        from core.sync_broker import broker

        # Push a catalog update to a specific branch
        broker.push_to_branch(
            branch_code="BR001",
            message=BrokerMessage(
                type="catalog_update",
                payload={"products": [...], "updated_at": "..."},
            ),
        )

        # Push a config update to all branches
        broker.broadcast(
            message=BrokerMessage(
                type="config_update",
                payload={"sync_interval": 60},
            ),
        )

        # Request sync from a specific branch
        broker.push_to_branch(
            branch_code="BR001",
            message=BrokerMessage(
                type="sync_request",
                payload={"entity_types": ["products", "inventory"]},
            ),
        )
    """

    def __init__(self) -> None:
        self._message_handlers: dict[str, list[Callable]] = {}
        self._connected_branches: dict[str, set[str]] = {}
        logger.info("SyncBroker initialized")

    # ── Public API ──────────────────────────────────────────────────

    def push_to_branch(
        self,
        branch_code: str,
        message: BrokerMessage,
    ) -> bool:
        """Send a message to all connected terminals of a specific branch.

        Args:
            branch_code: The branch code (e.g. ``"BR001"``).
            message: The message to deliver.

        Returns:
            ``True`` if the channel layer accepted the message, ``False`` if
            no channel layer is configured.
        """
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.warning("No channel layer configured — cannot push to branch %s", branch_code)
            return False

        message.target_branch_code = branch_code
        event = {
            "type": "broker_message",
            "data": message.to_dict(),
        }

        try:
            async_to_sync(channel_layer.group_send)(
                _branch_group(branch_code),
                event,
            )
            logger.debug(
                "Pushed %s message to branch %s (id=%s)",
                message.type, branch_code, message.message_id,
            )
            return True
        except Exception as exc:
            logger.error("Failed to push to branch %s: %s", branch_code, exc)
            return False

    def broadcast(self, message: BrokerMessage) -> bool:
        """Broadcast a message to ALL connected branches.

        Args:
            message: The message to deliver to all branches.

        Returns:
            ``True`` if the channel layer accepted the broadcast.
        """
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.warning("No channel layer configured — cannot broadcast")
            return False

        event = {
            "type": "broker_message",
            "data": message.to_dict(),
        }

        try:
            async_to_sync(channel_layer.group_send)(
                "sync_broadcast",
                event,
            )
            logger.debug("Broadcast %s message (id=%s)", message.type, message.message_id)
            return True
        except Exception as exc:
            logger.error("Failed to broadcast message: %s", exc)
            return False

    def reset(self, *, keep_handlers: bool = True) -> None:
        """Reset the broker's runtime state (used by the test suite).

        Clears the connection registry so branch health checks start
        clean between tests.  Message handlers registered by
        ``AppConfig.ready()`` are preserved by default; pass
        ``keep_handlers=False`` to also wipe them (test-only escape
        hatch for validating handler registration).
        """
        self._connected_branches.clear()
        if not keep_handlers:
            self._message_handlers.clear()

    def branch_health_check(self, branch_code: str) -> dict[str, Any]:
        """Check if a branch has any connected WebSocket terminals.

        The channel layer doesn't expose connected clients directly, so
        we track them via the ``_connected_branches`` dict updated by the
        consumer's ``connect`` / ``disconnect`` methods.

        Returns:
            A dict with ``{"online": bool, "connected_terminals": int}``.
        """
        terminals = self._connected_branches.get(branch_code, set())
        return {
            "online": len(terminals) > 0,
            "connected_terminals": len(terminals),
            "branch_code": branch_code,
        }

    def all_branch_health(self) -> dict[str, Any]:
        """Return health status for all branches with connected terminals."""
        return {
            code: {
                "online": len(terminals) > 0,
                "connected_terminals": len(terminals),
            }
            for code, terminals in self._connected_branches.items()
        }

    # ── Internal (called by the WebSocket consumer) ──────────────────

    def register_connection(self, branch_code: str, channel_name: str) -> None:
        """Track a connected WebSocket channel for a branch.

        Called by the consumer on ``connect``.
        """
        if branch_code not in self._connected_branches:
            self._connected_branches[branch_code] = set()
        self._connected_branches[branch_code].add(channel_name)
        logger.debug(
            "Registered %s for branch %s (%d terminals connected)",
            channel_name, branch_code, len(self._connected_branches[branch_code]),
        )

    def unregister_connection(self, branch_code: str, channel_name: str) -> None:
        """Remove a disconnected WebSocket channel for a branch.

        Called by the consumer on ``disconnect``.
        """
        terminals = self._connected_branches.get(branch_code)
        if terminals:
            terminals.discard(channel_name)
            if not terminals:
                del self._connected_branches[branch_code]
            logger.debug(
                "Unregistered %s from branch %s (%d terminals remaining)",
                channel_name, branch_code, len(terminals) if terminals else 0,
            )

    # ── Message handler registration ────────────────────────────────

    def on(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a specific message type from branches.

        Args:
            message_type: e.g. ``"sync_push"``, ``"heartbeat"``, ``"ack"``.
            handler: Callable receiving ``(branch_code, payload)``.
        """
        if message_type not in self._message_handlers:
            self._message_handlers[message_type] = []
        self._message_handlers[message_type].append(handler)
        logger.debug("Registered handler for message type %s", message_type)

    def dispatch(self, branch_code: str, message: BrokerMessage) -> None:
        """Dispatch an incoming message from a branch to registered handlers.

        Called by the consumer on receiving a message from a connected
        POS terminal.
        """
        handlers = self._message_handlers.get(message.type, [])
        if not handlers:
            logger.debug("No handlers registered for message type %s", message.type)
            return

        for handler in handlers:
            try:
                handler(branch_code, message.payload)
            except Exception as exc:
                logger.error(
                    "Handler %s failed for %s message from %s: %s",
                    handler.__name__, message.type, branch_code, exc,
                )


# ══════════════════════════════════════════════════════════════════════
# Singleton
# ══════════════════════════════════════════════════════════════════════

broker = SyncBroker()
"""Global sync broker singleton. Import this in views and consumers."""
