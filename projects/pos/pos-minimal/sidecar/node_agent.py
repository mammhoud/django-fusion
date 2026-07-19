"""
POS Minimal — Node Agent.

Lightweight sync agent that connects a Minimal POS instance to the Master
(Cloud CRM) with a unique identifier. Runs as a background process.

Architecture:
  Minimal (node)  ──HTTP──>  Solo (server/aggregator)  ──HTTP──>  Full/Cloud (master)

Flow:
  1. Agent starts with a unique node_id (from config or auto-generated)
  2. Reports status, last transactions, and product catalog to Solo aggregator
  3. Solo forwards to Cloud Master via webhooks

Usage:
  python3 node_agent.py --master http://solo-host:8765 --node-id POS-NODE-001

Related Names: node, agent, minimal, sync, master, solo, cloud
Tags: #node #agent #minimal #sync #network
"""

from __future__ import annotations

import os
import sys
import json
import uuid
import time
import argparse
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("pos_node_agent")


class NodeAgent:
    """Minimal POS node agent that connects to the Solo aggregator/master.

    Attributes:
        node_id: Unique identifier for this POS instance.
        master_url: URL of the Solo aggregator server.
        db_path: Path to the local SQLite database.
        api_key: Optional API key for authentication.
    """

    def __init__(
        self,
        node_id: str,
        master_url: str = "http://localhost:8765",
        db_path: str = "./restaurant.db",
        api_key: str | None = None,
        interval: int = 60,
    ):
        self.node_id = node_id
        self.master_url = master_url.rstrip("/")
        self.db_path = db_path
        self.api_key = api_key
        self.interval = interval
        self._client = httpx.Client(
            base_url=self.master_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "X-Node-ID": self.node_id,
                "User-Agent": f"POS-MinimalNode/{node_id}",
            },
        )
        if self.api_key:
            self._client.headers["X-API-Key"] = self.api_key

    # ── Database helpers ─────────────────────────────────────────────

    def _db_conn(self) -> sqlite3.Connection | None:
        if not Path(self.db_path).exists():
            return None
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_last_transactions(self, limit: int = 10) -> list[dict]:
        """Fetch last N transactions from local SQLite."""
        conn = self._db_conn()
        if not conn:
            return []
        try:
            rows = conn.execute(
                "SELECT id, total_amount, currency, date, time, "
                "order_type, status, customer_id, created_at "
                "FROM sales ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _get_product_count(self) -> int:
        """Count total products in local database."""
        conn = self._db_conn()
        if not conn:
            return 0
        try:
            row = conn.execute("SELECT COUNT(*) as cnt FROM products").fetchone()
            return row["cnt"] if row else 0
        except Exception:
            return 0
        finally:
            conn.close()

    def _get_recent_products(self, limit: int = 20) -> list[dict]:
        """Fetch recent products from local SQLite."""
        conn = self._db_conn()
        if not conn:
            return []
        try:
            rows = conn.execute(
                "SELECT id, name, price, unit, category_id, created_at "
                "FROM products ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    # ── Heartbeat / status report ────────────────────────────────────

    def get_status_payload(self) -> dict[str, Any]:
        """Build a status report payload for this node."""
        last_tx = self._get_last_transactions(5)
        products = self._get_recent_products(10)
        return {
            "node_id": self.node_id,
            "node_type": "pos-minimal",
            "version": "0.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "online",
            "product_count": self._get_product_count(),
            "recent_products": products,
            "last_transactions": last_tx,
            "db_available": Path(self.db_path).exists(),
        }

    def send_heartbeat(self) -> dict[str, Any]:
        """Send a heartbeat/status report to the master/aggregator.

        POSTs to /api/nodes/<node_id>/heartbeat on the Solo server.
        """
        payload = self.get_status_payload()
        try:
            resp = self._client.post(
                f"/api/nodes/{self.node_id}/heartbeat",
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            logger.info("Heartbeat sent: node=%s status=ok", self.node_id)
            return result
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Heartbeat failed: %s %s", exc.response.status_code, exc.response.text,
            )
            return {"status": "error", "detail": str(exc)}
        except httpx.RequestError as exc:
            logger.warning("Heartbeat failed: master unreachable: %s", exc)
            return {"status": "error", "detail": str(exc)}

    def send_transaction(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Send a single transaction to the master/aggregator."""
        transaction["node_id"] = self.node_id
        try:
            resp = self._client.post(
                f"/api/nodes/{self.node_id}/transactions",
                json=transaction,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("Transaction push failed: %s", exc)
            return {"status": "error", "detail": str(exc)}

    # ── Lifecycle ────────────────────────────────────────────────────

    def sync_all(self) -> dict[str, Any]:
        """Full sync: heartbeat + forward recent transactions."""
        result = self.send_heartbeat()
        transactions = self._get_last_transactions(5)
        for tx in transactions:
            self.send_transaction(tx)
        logger.info(
            "Full sync: node=%s heartbeat=%s transactions=%d",
            self.node_id, result.get("status"), len(transactions),
        )
        return result

    def run_forever(self) -> None:
        """Main loop: sync all data every `interval` seconds."""
        logger.info(
            "Node agent started: node=%s master=%s interval=%ds",
            self.node_id, self.master_url, self.interval,
        )
        self.sync_all()

        while True:
            time.sleep(self.interval)
            self.sync_all()

    def run_once(self) -> dict[str, Any]:
        """Send a single full sync and return result."""
        return self.sync_all()

    def close(self) -> None:
        self._client.close()


def _generate_node_id() -> str:
    """Generate a unique node identifier based on hostname + UUID."""
    hostname = os.uname().nodename if hasattr(os, "uname") else "pos-node"
    short_id = uuid.uuid4().hex[:8]
    return f"{hostname}-{short_id}"


def main() -> None:
    parser = argparse.ArgumentParser(description="POS Minimal Node Agent")
    parser.add_argument("--master", default="http://localhost:8765",
                        help="Solo aggregator/master URL")
    parser.add_argument("--node-id", default=_generate_node_id(),
                        help="Unique node identifier")
    parser.add_argument("--db", default="./restaurant.db",
                        help="Path to local SQLite database")
    parser.add_argument("--interval", type=int, default=60,
                        help="Heartbeat interval in seconds")
    parser.add_argument("--once", action="store_true",
                        help="Send one heartbeat and exit")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    agent = NodeAgent(
        node_id=args.node_id,
        master_url=args.master,
        db_path=args.db,
        interval=args.interval,
    )

    try:
        if args.once:
            result = agent.run_once()
            print(json.dumps(result, indent=2))
        else:
            agent.run_forever()
    except KeyboardInterrupt:
        logger.info("Node agent stopped")
    finally:
        agent.close()


if __name__ == "__main__":
    main()

# @tested pos-minimal - POSKO-MinimalNode → POS-MinimalNode rename verified
