"""
POS Solo — Cloud CRM Sync Client.

Provides a typed HTTP client that the solo sidecar uses to push
local POS data (products, sales, customers) to the pos-full cloud CRM server.

Architecture:
  pos-solo (sidecar, port 8765)  →  pos-full/cloud/ (port 8766)

Sync flow:
  1. Solo sidecar reads local SQLite data via existing /api/* endpoints
  2. SyncClient serializes and pushes to cloud CRM
  3. Cloud server stores data and returns cloud_id
  4. Solo sidecar records cloud_id locally (sync log)

Related Names: sync, client, cloud, crm, solo, pos-solo
Tags: #sync #client #cloud #crm #solo
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("solo_sync")


class SoloCloudSyncClient:
    """HTTP client for pushing POS data to the pos-full cloud CRM server.

    Usage::

        client = SoloCloudSyncClient(base_url="http://localhost:8766")
        result = client.push_product({"name": "Pizza", "price": 12.99})
        client.push_sale({"total_amount": 45.50, "items": [...]})
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8766",
        api_key: str | None = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "POS-SoloSync/1.0",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            logger.error(
                "HTTP %s %s failed: %s — %s",
                method, path, exc.response.status_code, exc.response.text,
            )
            raise
        except httpx.RequestError as exc:
            logger.error("Request %s %s failed: %s", method, path, exc)
            raise

    # ── Push POS data to cloud CRM ─────────────────────────────────────

    def push_product(self, data: dict[str, Any]) -> dict[str, Any]:
        """Push a product record to the cloud CRM."""
        return self._push("products", data)

    def push_sale(self, data: dict[str, Any]) -> dict[str, Any]:
        """Push a sale with line items to the cloud CRM."""
        return self._push("sales", data)

    def push_customer(self, data: dict[str, Any]) -> dict[str, Any]:
        """Push a customer record to the cloud CRM."""
        return self._push("customers", data)

    def push_inventory(self, data: dict[str, Any]) -> dict[str, Any]:
        """Push an inventory transaction to the cloud CRM."""
        return self._push("inventory", data)

    def push_employee(self, data: dict[str, Any]) -> dict[str, Any]:
        """Push an employee record to the cloud CRM."""
        return self._push("employees", data)

    def push_settings(self, data: dict[str, Any]) -> dict[str, Any]:
        """Push restaurant settings to the cloud CRM."""
        return self._push("settings", data)

    def _push(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Push any entity to the cloud CRM."""
        response = self._request(
            "POST",
            f"/api/sync/push/{entity_type}",
            json=data,
        )
        return response.json()

    # ── Batch operations ───────────────────────────────────────────────

    def bulk_push(self, entity_type: str, entities: list[dict[str, Any]]) -> dict[str, Any]:
        """Bulk-push multiple entities of the same type."""
        response = self._request(
            "POST",
            f"/api/sync/bulk-push/{entity_type}",
            json=entities,
        )
        return response.json()

    # ── Sync management ────────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Check cloud server health."""
        response = self._request("GET", "/health")
        return response.json()

    def sync_status(self) -> dict[str, Any]:
        """Get sync status from cloud server."""
        response = self._request("GET", "/api/sync/status")
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SoloCloudSyncClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

# @tested pos-solo - POSKO-SoloSync → POS-SoloSync rename verified
