"""
Cloud Sync Client — HTTP client for sidecar <-> cloud CRM communication.

Provides a typed Python client that the sidecar (or any local process)
uses to push/pull CRM data to/from the cloud server.

Architecture:

  +-------------------+      HTTP REST      +-------------------+
  |  sidecar (local)  |  <--------------->  |  cloud server     |
  |  port 8765        |   sync_client.py    |  port 8766        |
  +-------------------+                     +-------------------+
        |                                            |
  JSON file storage                            JSON file storage
  (sidecar/data/)                            (cloud/cloud_data/)

Sync flow:
  1. Sidecar creates CRM entity → records in local JSON + SyncQueue
  2. SyncClient.push_entity() → sends to cloud server
  3. Cloud server processes → stores in cloud JSON + returns cloud_id
  4. SyncClient records cloud_id in local entity

Related Names: sync, client, cloud, crm, sidecar, httpx
Tags: #sync #client #cloud #crm #sidecar #pos-full
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger("cloud_sync")


class SyncClient:
    """HTTP client for syncing CRM data between sidecar and cloud server.

    Usage::

        client = SyncClient(base_url="http://localhost:8766", api_key="...")
        result = client.push_contact({"first_name": "John", "last_name": "Doe"})
        contacts = client.pull_contacts(page=1, per_page=50)
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
        """Build default HTTP headers including optional auth."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "POS-CloudSync/1.0",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an HTTP request with error handling."""
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
            logger.error(
                "Request %s %s failed: %s", method, path, exc,
            )
            raise

    # -------------------------------------------------------------------
    # Push (local → cloud)
    # -------------------------------------------------------------------

    def push_entity(
        self,
        entity_type: str,
        data: dict[str, Any],
        action: str = "create",
    ) -> dict[str, Any]:
        """Push an entity to the cloud CRM server.

        Args:
            entity_type: One of 'contacts', 'companies', 'deals', 'activities', 'notes'.
            data: Entity data dict.
            action: 'create' for new entities, 'update' for existing.

        Returns:
            Cloud response data (including cloud_id).

        Raises:
            httpx.HTTPStatusError: On 4xx/5xx response.
            httpx.RequestError: On connection failure.
        """
        response = self._request(
            "POST" if action == "create" else "PATCH",
            f"/api/crm/{entity_type}",
            json=data,
        )
        return response.json()

    def push_contact(self, data: dict[str, Any], action: str = "create") -> dict[str, Any]:
        """Push a contact to the cloud."""
        return self.push_entity("contacts", data, action)

    def push_company(self, data: dict[str, Any], action: str = "create") -> dict[str, Any]:
        """Push a company to the cloud."""
        return self.push_entity("companies", data, action)

    def push_deal(self, data: dict[str, Any], action: str = "create") -> dict[str, Any]:
        """Push a deal to the cloud."""
        return self.push_entity("deals", data, action)

    def push_activity(self, data: dict[str, Any], action: str = "create") -> dict[str, Any]:
        """Push an activity to the cloud."""
        return self.push_entity("activities", data, action)

    def push_note(self, data: dict[str, Any], action: str = "create") -> dict[str, Any]:
        """Push a note to the cloud."""
        return self.push_entity("notes", data, action)

    # -------------------------------------------------------------------
    # Pull (cloud → local)
    # -------------------------------------------------------------------

    def pull_contacts(
        self,
        page: int = 1,
        per_page: int = 50,
        q: str | None = None,
        **filters: Any,
    ) -> dict[str, Any]:
        """Pull contacts from the cloud server.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page (max 200).
            q: Optional search query.
            **filters: Additional filter params (company_id, source, etc.).

        Returns:
            Paginated response dict with 'data', 'pagination' keys.
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if q:
            params["q"] = q
        params.update(filters)
        response = self._request("GET", "/api/crm/contacts", params=params)
        return response.json()

    def pull_companies(
        self,
        page: int = 1,
        per_page: int = 50,
        q: str | None = None,
        **filters: Any,
    ) -> dict[str, Any]:
        """Pull companies from the cloud server."""
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if q:
            params["q"] = q
        params.update(filters)
        response = self._request("GET", "/api/crm/companies", params=params)
        return response.json()

    def pull_deals(
        self,
        page: int = 1,
        per_page: int = 50,
        q: str | None = None,
        **filters: Any,
    ) -> dict[str, Any]:
        """Pull deals from the cloud server."""
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if q:
            params["q"] = q
        params.update(filters)
        response = self._request("GET", "/api/crm/deals", params=params)
        return response.json()

    def pull_dashboard(self) -> dict[str, Any]:
        """Pull CRM dashboard statistics from the cloud."""
        response = self._request("GET", "/api/crm/dashboard")
        return response.json()

    # -------------------------------------------------------------------
    # Sync management
    # -------------------------------------------------------------------

    def sync_status(self) -> dict[str, Any]:
        """Get sync status from cloud server."""
        response = self._request("GET", "/api/crm/sync/status")
        return response.json()

    def trigger_sync(self) -> dict[str, Any]:
        """Trigger a manual sync on the cloud server."""
        response = self._request("POST", "/api/crm/sync/trigger")
        return response.json()

    def get_sync_log(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get sync history log."""
        response = self._request("GET", "/api/crm/sync/log", params={"limit": limit})
        return response.json()

    # -------------------------------------------------------------------
    # Bulk operations
    # -------------------------------------------------------------------

    def bulk_import(self, entity_type: str, entities: list[dict[str, Any]]) -> dict[str, Any]:
        """Bulk-import entities to the cloud server.

        Args:
            entity_type: One of 'contacts', 'companies', 'deals', 'activities', 'notes'.
            entities: List of entity dicts.

        Returns:
            Import summary with created/error counts.
        """
        response = self._request(
            "POST",
            f"/api/crm/import/{entity_type}",
            json=entities,
        )
        return response.json()

    # -------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """Check cloud server health."""
        response = self._request("GET", "/health")
        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> SyncClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
@tested shared-portal/cloud - POSKO-CloudSync → POS-CloudSync rename verified
