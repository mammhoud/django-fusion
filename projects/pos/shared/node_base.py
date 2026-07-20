"""
Base node agent for POS Portal editions.
Provides heartbeat, sync, and registration functionality
that each edition's node app extends.

@tested pos-portal/shared - Base node agent for minimal/solo editions
"""

from __future__ import annotations

import json
import logging
import socket
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from django.core.management.base import BaseCommand

logger = logging.getLogger("pos_portal.node")


class BaseNodeAgent:
    """
    Base node agent that communicates with a server/cloud master.

    Provides:
    - Heartbeat registration
    - Transaction sync
    - Product push
    - Health reporting
    """

    def __init__(
        self,
        node_id: str | None = None,
        master_url: str = "http://localhost:8000",
        api_key: str | None = None,
        interval: int = 60,
        data_dir: str = "./node_data",
    ):
        self.node_id = node_id or f"POS-NODE-{uuid.uuid4().hex[:8].upper()}"
        self.master_url = master_url.rstrip("/")
        self.api_key = api_key
        self.interval = interval
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._client = httpx.Client(
            base_url=self.master_url,
            timeout=30.0,
            headers=self._build_headers(),
        )
        logger.info(
            "NodeAgent initialized: %s → %s (interval: %ds)",
            self.node_id, self.master_url, self.interval,
        )

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"POS-Portal-Node/{self.node_id}",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    # ── Heartbeat ─────────────────────────────────────────────────

    def send_heartbeat(self, **extra_status: Any) -> dict[str, Any]:
        """Send a heartbeat to the master server."""
        payload = {
            "node_id": self.node_id,
            "hostname": socket.gethostname(),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "online",
            **extra_status,
        }
        try:
            resp = self._client.post("/api/nodes/heartbeat", json=payload)
            resp.raise_for_status()
            result = resp.json()
            logger.debug("Heartbeat sent: %s", result)
            return result
        except httpx.HTTPStatusError as exc:
            logger.error("Heartbeat failed: %s %s", exc.response.status_code, exc.response.text)
            return {"status": "error", "detail": str(exc)}
        except httpx.RequestError as exc:
            logger.warning("Master unreachable: %s", exc)
            return {"status": "error", "detail": str(exc)}

    # ── Transaction push ──────────────────────────────────────────

    def push_transaction(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Push a single transaction to the master."""
        payload = {
            "node_id": self.node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "transaction": transaction,
        }
        try:
            resp = self._client.post("/api/nodes/transactions", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Transaction push failed: %s", exc.response.status_code)
            return {"status": "error", "detail": str(exc)}
        except httpx.RequestError as exc:
            logger.warning("Master unreachable for transaction: %s", exc)
            return {"status": "error", "detail": str(exc)}

    # ── Product sync ──────────────────────────────────────────────

    def push_products(self, products: list[dict[str, Any]]) -> dict[str, Any]:
        """Push product catalog to the master."""
        payload = {
            "node_id": self.node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "products": products,
        }
        try:
            resp = self._client.post("/api/nodes/products", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as exc:
            logger.warning("Product push failed: %s", exc)
            return {"status": "error", "detail": str(exc)}

    # ── State persistence ─────────────────────────────────────────

    def save_state(self, state: dict[str, Any]) -> None:
        """Persist node state to disk."""
        state_file = self.data_dir / "node_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self) -> dict[str, Any]:
        """Load persisted node state."""
        state_file = self.data_dir / "node_state.json"
        if not state_file.exists():
            return {"node_id": self.node_id, "transactions_synced": 0}
        try:
            with open(state_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"node_id": self.node_id, "transactions_synced": 0}

    # ── Lifecycle ─────────────────────────────────────────────────

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> BaseNodeAgent:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class BaseNodeCommand(BaseCommand):
    """Base management command for running a node agent."""

    help = "Run the POS Portal node agent"

    def add_arguments(self, parser):
        parser.add_argument("--master", default="http://localhost:8000")
        parser.add_argument("--node-id", default=None)
        parser.add_argument("--interval", type=int, default=60)
        parser.add_argument("--once", action="store_true", help="Single heartbeat, then exit")
        parser.add_argument("--verbose", action="store_true")

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.DEBUG if options["verbose"] else logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        agent = self.get_agent(options)
        self.stdout.write(
            self.style.SUCCESS(f"Node agent started: {agent.node_id}")
        )

        try:
            result = agent.send_heartbeat()
            self.stdout.write(f"Heartbeat: {result}")

            if options["once"]:
                return

            # Continuous mode - run in a loop
            import time
            while True:
                time.sleep(options["interval"])
                result = agent.send_heartbeat()
                self.stdout.write(f"Heartbeat at {datetime.utcnow().isoformat()}: {result.get('status')}")
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Node agent stopped by user"))
        finally:
            agent.close()

    def get_agent(self, options) -> BaseNodeAgent:
        """Override to provide edition-specific agent."""
        raise NotImplementedError("Subclasses must implement get_agent()")
