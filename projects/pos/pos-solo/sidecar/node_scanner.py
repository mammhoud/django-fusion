"""
POS Solo — Node Scanner.

Discovers Minimal POS nodes on the local network, fetches their status/
transactions/products, and forwards aggregated data to the Cloud Master
(pos-full/cloud/).

Architecture:
  pos-minimal (nodes)  ──HTTP──>  pos-solo (scanner/aggregator)  ──HTTP──>  pos-full/cloud (master)

Scanner features:
  - Receives heartbeats from minimal nodes via /api/nodes/<id>/heartbeat
  - Maintains a registry of known nodes and their last reported status
  - Fetches pending transactions from known nodes
  - Forwards aggregated data to cloud master via webhook

Related Names: scanner, node, discovery, network, solo, aggregator
Tags: #scanner #node #network #solo #aggregator
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("pos_node_scanner")

# ── Node registry (file-based persistence) ─────────────────────────────

REGISTRY_FILE = Path("./data/node_registry.json")


def _load_registry() -> dict[str, Any]:
    if not REGISTRY_FILE.exists():
        return {"nodes": {}, "last_scan": None, "total_nodes": 0}
    try:
        with open(REGISTRY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"nodes": {}, "last_scan": None, "total_nodes": 0}


def _save_registry(registry: dict[str, Any]) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)


class NodeScanner:
    """Discovers and tracks Minimal POS nodes on the network.

    The Solo sidecar runs this scanner to:
    1. Accept heartbeats from Minimal nodes (POST /api/nodes/<id>/heartbeat)
    2. Maintain a registry of active nodes
    3. Forward aggregated data to the Cloud Master

    Usage:
        scanner = NodeScanner(master_url="http://localhost:8766")
        scanner.register_node("POS-NODE-001", {"status": "online", ...})
        scanner.forward_to_master()
    """

    def __init__(
        self,
        master_url: str = "http://localhost:8766",
        api_key: str | None = None,
    ):
        self.master_url = master_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.master_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "POS-NodeScanner/1.0",
            },
        )
        if self.api_key:
            self._client.headers["X-API-Key"] = self.api_key

    # ── Node registration ────────────────────────────────────────────

    def register_node(self, node_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Register or update a node heartbeat in the local registry.

        Called by the /api/nodes/<id>/heartbeat endpoint.
        Returns the current registry summary.
        """
        registry = _load_registry()
        registry["nodes"][node_id] = {
            "node_id": node_id,
            "last_seen": datetime.utcnow().isoformat(),
            "status": payload.get("status", "online"),
            "product_count": payload.get("product_count", 0),
            "recent_products": payload.get("recent_products", []),
            "last_transactions": payload.get("last_transactions", []),
            "node_type": payload.get("node_type", "pos-minimal"),
            "version": payload.get("version", "unknown"),
            "db_available": payload.get("db_available", False),
        }
        registry["last_scan"] = datetime.utcnow().isoformat()
        registry["total_nodes"] = len(registry["nodes"])
        _save_registry(registry)

        logger.info(
            "Node registered: %s (total: %d)", node_id, len(registry["nodes"]),
        )
        return {
            "status": "registered",
            "node_id": node_id,
            "total_nodes": len(registry["nodes"]),
        }

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Get a specific node's info from the registry."""
        registry = _load_registry()
        return registry["nodes"].get(node_id)

    def list_nodes(self) -> list[dict[str, Any]]:
        """List all registered nodes from the registry."""
        registry = _load_registry()
        return list(registry["nodes"].values())

    def get_online_nodes(self, max_age_seconds: int = 300) -> list[dict[str, Any]]:
        """Get nodes that have reported in within `max_age_seconds`."""
        registry = _load_registry()
        now = datetime.utcnow()
        online = []
        for node_id, info in registry["nodes"].items():
            try:
                last_seen = datetime.fromisoformat(info["last_seen"])
                if (now - last_seen).total_seconds() < max_age_seconds:
                    online.append(info)
            except (ValueError, KeyError):
                pass
        return online

    def remove_stale_nodes(self, max_age_seconds: int = 86400) -> int:
        """Remove nodes that haven't reported in within `max_age_seconds`."""
        registry = _load_registry()
        now = datetime.utcnow()
        stale_ids = []
        for node_id, info in registry["nodes"].items():
            try:
                last_seen = datetime.fromisoformat(info["last_seen"])
                if (now - last_seen).total_seconds() > max_age_seconds:
                    stale_ids.append(node_id)
            except (ValueError, KeyError):
                stale_ids.append(node_id)

        for nid in stale_ids:
            del registry["nodes"][nid]
        registry["total_nodes"] = len(registry["nodes"])
        _save_registry(registry)

        if stale_ids:
            logger.info("Removed %d stale nodes", len(stale_ids))
        return len(stale_ids)

    # ── Forwarding to Master ────────────────────────────────────────

    def forward_to_master(self, max_age: int = 300) -> dict[str, Any]:
        """Forward aggregated node data to the Cloud Master.

        Gathers data from online nodes and sends via webhook POST.
        """
        online_nodes = self.get_online_nodes(max_age_seconds=max_age)
        if not online_nodes:
            return {"forwarded": False, "reason": "no online nodes"}

        payload = {
            "source": "pos-solo-scanner",
            "timestamp": datetime.utcnow().isoformat(),
            "node_count": len(online_nodes),
            "nodes": online_nodes,
        }

        try:
            resp = self._client.post("/api/webhooks/node-aggregate", json=payload)
            resp.raise_for_status()
            result = resp.json()
            logger.info(
                "Forwarded %d nodes to master: %s",
                len(online_nodes), result,
            )
            return result
        except httpx.HTTPStatusError as exc:
            logger.error("Forward to master failed: %s %s",
                         exc.response.status_code, exc.response.text)
            return {"forwarded": False, "error": str(exc)}
        except httpx.RequestError as exc:
            logger.error("Master unreachable: %s", exc)
            return {"forwarded": False, "error": str(exc)}

    # ── Lifecycle ────────────────────────────────────────────────────

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> NodeScanner:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

# @tested pos-solo - POSKO-NodeScanner → POS-NodeScanner rename verified
