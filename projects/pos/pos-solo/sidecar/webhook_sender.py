"""
POS Solo — Webhook Sender.

Forwards aggregated POS data (transactions, nodes, products) from the Solo
aggregator to the Cloud Master (pos-full/cloud/) via HTTP webhooks.

Architecture:
  pos-solo (aggregator)  ──webhook──>  pos-full/cloud (master)

Webhook endpoints on master:
  POST /api/webhooks/node-aggregate    — aggregated node data from scanner
  POST /api/webhooks/transaction-batch — batched transactions
  POST /api/webhooks/product-update    — product catalog updates

Related Names: webhook, sender, solo, master, cloud, forward
Tags: #webhook #sender #solo #master #cloud
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger("pos_webhook_sender")


class WebhookSender:
    """Sends webhooks from Solo aggregator to Cloud Master.

    Usage::
        sender = WebhookSender(master_url="http://localhost:8766")
        sender.send_node_aggregate(nodes=[...])
        sender.send_transaction_batch(transactions=[...])
    """

    def __init__(
        self,
        master_url: str = "http://localhost:8766",
        api_key: str | None = None,
        source_id: str = "pos-solo-01",
    ):
        self.master_url = master_url.rstrip("/")
        self.api_key = api_key
        self.source_id = source_id
        self._client = httpx.Client(
            base_url=self.master_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Webhook-Source": self.source_id,
                "User-Agent": f"POS-Webhook/{source_id}",
            },
        )
        if self.api_key:
            self._client.headers["X-API-Key"] = self.api_key

    def _build_payload(self, event_type: str, data: Any) -> dict[str, Any]:
        return {
            "webhook_version": "1.0",
            "source_id": self.source_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

    def _send(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = self._client.post(path, json=payload)
            resp.raise_for_status()
            result = resp.json()
            logger.debug("Webhook sent to %s: %s", path, result)
            return result
        except httpx.HTTPStatusError as exc:
            logger.error("Webhook %s failed: %s %s",
                         path, exc.response.status_code, exc.response.text)
            return {"status": "error", "detail": str(exc)}
        except httpx.RequestError as exc:
            logger.error("Webhook %s failed: master unreachable: %s", path, exc)
            return {"status": "error", "detail": str(exc)}

    # ── Webhook types ────────────────────────────────────────────────

    def send_node_aggregate(
        self,
        nodes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send aggregated node data to master.

        Called by NodeScanner.forward_to_master().
        """
        payload = self._build_payload("node_aggregate", {
            "node_count": len(nodes),
            "nodes": nodes,
        })
        return self._send("/api/webhooks/node-aggregate", payload)

    def send_transaction_batch(
        self,
        transactions: list[dict[str, Any]],
        source_node_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a batch of transactions to master."""
        payload = self._build_payload("transaction_batch", {
            "source_node_id": source_node_id,
            "count": len(transactions),
            "transactions": transactions,
        })
        return self._send("/api/webhooks/transaction-batch", payload)

    def send_product_update(
        self,
        products: list[dict[str, Any]],
        source_node_id: str | None = None,
    ) -> dict[str, Any]:
        """Send product catalog updates to master."""
        payload = self._build_payload("product_update", {
            "source_node_id": source_node_id,
            "count": len(products),
            "products": products,
        })
        return self._send("/api/webhooks/product-update", payload)

    def send_settings_sync(
        self,
        settings: dict[str, Any],
    ) -> dict[str, Any]:
        """Send restaurant settings sync to master."""
        payload = self._build_payload("settings_sync", settings)
        return self._send("/api/webhooks/settings-sync", payload)

    def send_heartbeat(self, status: dict[str, Any]) -> dict[str, Any]:
        """Send a heartbeat to the master (solo self-report)."""
        payload = self._build_payload("heartbeat", status)
        return self._send("/api/webhooks/heartbeat", payload)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> WebhookSender:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

# @tested pos-solo - POSKO-Webhook → POS-Webhook rename verified
