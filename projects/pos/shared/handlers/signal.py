"""
Signal handlers for the POS signal system.

Provides three categories of @receiver handlers for every signal:
  1. Logging — structured log output for debugging and monitoring
  2. Webhook — HTTP POST callbacks to configured URLs
  3. Audit — persistent storage in SignalEvent database table

Configuration (environment variables):
  WEBHOOK_URL_CONFIG_CHANGED       — POST URL for config_changed signals
  WEBHOOK_URL_MASTER_DEVICE_CHANGED — POST URL for master_device_changed signals
  WEBHOOK_URL_CLOUD_LINK_CHANGED   — POST URL for cloud_link_changed signals
  WEBHOOK_URL_CONFIG_SYNCED        — POST URL for config_synced signals
  WEBHOOK_URL_DEVICE_STATUS_CHANGED — POST URL for device_status_changed signals
  WEBHOOK_TIMEOUT_SECONDS          — HTTP timeout for webhook delivery (default: 10)

To activate, import this module at server startup:
    import shared.handlers.signal  # noqa: F401 — registers @receiver handlers

Usage from server.py:
    from django.dispatch import receiver
    from shared.signals import config_changed

    @receiver(config_changed)
    def my_custom_handler(sender, **kwargs):
        pass
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from django.dispatch import receiver

from shared.models.audit import SignalEvent
from shared.signals import (
    config_changed,
    master_device_changed,
    cloud_link_changed,
    config_synced,
    device_status_changed,
)

logger = logging.getLogger("pos.signal_handlers")

# ---------------------------------------------------------------------------
# Webhook configuration
# ---------------------------------------------------------------------------

WEBHOOK_TIMEOUT = int(os.environ.get("WEBHOOK_TIMEOUT_SECONDS", "10"))

# Map signal names to environment variable names for lazy URL resolution.
# URLs are read from os.environ on each access (not at import time) so that
# tests can set env vars after module load and still see the correct values.
_WEBHOOK_ENV_MAP: dict[str, str] = {
    "config_changed": "WEBHOOK_URL_CONFIG_CHANGED",
    "master_device_changed": "WEBHOOK_URL_MASTER_DEVICE_CHANGED",
    "cloud_link_changed": "WEBHOOK_URL_CLOUD_LINK_CHANGED",
    "config_synced": "WEBHOOK_URL_CONFIG_SYNCED",
    "device_status_changed": "WEBHOOK_URL_DEVICE_STATUS_CHANGED",
}


class _WebhookUrls(dict):
    """Dict subclass that reads webhook URLs from environment variables on each access.

    This lazy-loading approach ensures that os.environ changes (e.g. from test
    setup) are picked up even after this module has been imported.
    Extends dict so that mock.patch.dict() and iteration work correctly.
    """

    def __init__(self):
        # Initialize with empty values; real values are resolved lazily
        super().__init__({k: None for k in _WEBHOOK_ENV_MAP})

    def __getitem__(self, key: str) -> str | None:
        env_var = _WEBHOOK_ENV_MAP.get(key)
        return os.environ.get(env_var) if env_var else None

    def get(self, key: str, default: str | None = None) -> str | None:
        env_var = _WEBHOOK_ENV_MAP.get(key)
        return os.environ.get(env_var) if env_var else default

    def __setitem__(self, key: str, value: str | None) -> None:
        """Allow test code (mock.patch.dict) to temporarily override values."""
        env_var = _WEBHOOK_ENV_MAP.get(key)
        if env_var:
            if value is None:
                os.environ.pop(env_var, None)
            else:
                os.environ[env_var] = value

    def items(self):
        return [(k, os.environ.get(v)) for k, v in _WEBHOOK_ENV_MAP.items()]

    def keys(self):
        return _WEBHOOK_ENV_MAP.keys()

    def values(self):
        return [os.environ.get(v) for v in _WEBHOOK_ENV_MAP.values()]


WEBHOOK_URLS: _WebhookUrls = _WebhookUrls()


# ---------------------------------------------------------------------------
# Helper: send webhook
# ---------------------------------------------------------------------------


def _send_webhook(signal_name: str, payload: dict) -> tuple[str, str]:
    """Send a synchronous webhook POST to the configured URL for the given signal.

    Returns (status, error_message).
    """
    url = WEBHOOK_URLS.get(signal_name)
    if not url:
        return "skipped", "no_webhook_url_configured"

    try:
        import httpx

        with httpx.Client(timeout=WEBHOOK_TIMEOUT) as client:
            resp = client.post(
                url,
                json={
                    "signal": signal_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "payload": payload,
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "POS-SignalWebhook/1.0",
                    "X-Signal-Name": signal_name,
                },
            )
            resp.raise_for_status()
            return "sent", ""
    except Exception as exc:
        logger.warning("Webhook %s delivery failed: %s", signal_name, exc)
        return "failed", str(exc)


# ---------------------------------------------------------------------------
# Helper: persist audit record
# ---------------------------------------------------------------------------


def _persist_audit(
    signal_name: str,
    action: str,
    node_id: str = "",
    resource_id: str = "",
    payload: dict | None = None,
    webhook_status: str = "",
    webhook_error: str = "",
) -> None:
    """Create a SignalEvent audit record in the database."""
    try:
        SignalEvent.objects.create(
            signal_name=signal_name,
            action=action,
            node_id=node_id,
            resource_id=resource_id,
            payload=payload or {},
            webhook_status=webhook_status,
            webhook_error=webhook_error,
        )
    except Exception as exc:
        logger.error("Failed to persist SignalEvent audit record: %s", exc)


# ---------------------------------------------------------------------------
# Helper: build structured log line
# ---------------------------------------------------------------------------


def _log_signal(signal_name: str, action: str, node_id: str = "", details: str = "") -> None:
    """Log a structured signal event."""
    logger.info(
        "SIGNAL [%s] action=%s node=%s %s",
        signal_name,
        action,
        node_id or "(global)",
        details,
    )


# ---------------------------------------------------------------------------
# 1. config_changed — device config created, updated, or deleted
# ---------------------------------------------------------------------------


@receiver(config_changed)
def handle_config_changed(sender, **kwargs: Any) -> None:
    """Log, webhook, and audit a config_changed signal."""
    node_id = kwargs.get("node_id", "")
    config_key = kwargs.get("config_key", "")
    action = kwargs.get("action", "updated")
    category = kwargs.get("category", "")
    old_value = kwargs.get("old_value")
    new_value = kwargs.get("new_value")

    _log_signal("config_changed", action, node_id, f"key={config_key} category={category}")

    payload = {
        "node_id": node_id,
        "config_key": config_key,
        "action": action,
        "category": category,
        "old_value": old_value,
        "new_value": new_value,
    }

    wh_status, wh_error = _send_webhook("config_changed", payload)

    _persist_audit(
        signal_name="config_changed",
        action=action,
        node_id=node_id,
        resource_id=config_key,
        payload=payload,
        webhook_status=wh_status,
        webhook_error=wh_error,
    )


# ---------------------------------------------------------------------------
# 2. master_device_changed — master device registered, updated, deactivated
# ---------------------------------------------------------------------------


@receiver(master_device_changed)
def handle_master_device_changed(sender, **kwargs: Any) -> None:
    """Log, webhook, and audit a master_device_changed signal."""
    device_id = kwargs.get("device_id", "")
    action = kwargs.get("action", "updated")
    status = kwargs.get("status", "")

    _log_signal("master_device_changed", action, device_id, f"status={status}")

    payload = {
        "device_id": device_id,
        "action": action,
        "status": status,
        "metadata": kwargs.get("metadata", {}),
    }

    wh_status, wh_error = _send_webhook("master_device_changed", payload)

    _persist_audit(
        signal_name="master_device_changed",
        action=action,
        node_id=device_id,
        resource_id=device_id,
        payload=payload,
        webhook_status=wh_status,
        webhook_error=wh_error,
    )


# ---------------------------------------------------------------------------
# 3. cloud_link_changed — cloud link connection status changed
# ---------------------------------------------------------------------------


@receiver(cloud_link_changed)
def handle_cloud_link_changed(sender, **kwargs: Any) -> None:
    """Log, webhook, and audit a cloud_link_changed signal."""
    link_id = kwargs.get("link_id", "")
    action = kwargs.get("action", "updated")
    status = kwargs.get("status", "")
    cloud_url = kwargs.get("cloud_url", "")

    _log_signal("cloud_link_changed", action, str(link_id), f"status={status} url={cloud_url}")

    payload = {
        "link_id": str(link_id),
        "action": action,
        "status": status,
        "cloud_url": cloud_url,
    }

    wh_status, wh_error = _send_webhook("cloud_link_changed", payload)

    _persist_audit(
        signal_name="cloud_link_changed",
        action=action,
        resource_id=str(link_id),
        payload=payload,
        webhook_status=wh_status,
        webhook_error=wh_error,
    )


# ---------------------------------------------------------------------------
# 4. config_synced — configuration pushed from master to child devices
# ---------------------------------------------------------------------------


@receiver(config_synced)
def handle_config_synced(sender, **kwargs: Any) -> None:
    """Log, webhook, and audit a config_synced signal."""
    source = kwargs.get("source_device_id", "")
    targets = kwargs.get("target_device_ids", [])
    config_keys = kwargs.get("config_keys", [])
    status = kwargs.get("status", "success")

    _log_signal("config_synced", status, source, f"targets={len(targets)} keys={len(config_keys)}")

    payload = {
        "source_device_id": source,
        "target_device_ids": targets,
        "config_keys": config_keys,
        "status": status,
    }

    wh_status, wh_error = _send_webhook("config_synced", payload)

    _persist_audit(
        signal_name="config_synced",
        action=status,
        node_id=source,
        resource_id=f"synced_{len(config_keys)}_keys",
        payload=payload,
        webhook_status=wh_status,
        webhook_error=wh_error,
    )


# ---------------------------------------------------------------------------
# 5. device_status_changed — device heartbeat / status change
# ---------------------------------------------------------------------------


@receiver(device_status_changed)
def handle_device_status_changed(sender, **kwargs: Any) -> None:
    """Log, webhook, and audit a device_status_changed signal."""
    node_id = kwargs.get("node_id", "")
    old_status = kwargs.get("old_status", "")
    new_status = kwargs.get("new_status", "")
    reason = kwargs.get("reason", "")

    _log_signal("device_status_changed", new_status, node_id, f"old={old_status} reason={reason}")

    payload = {
        "node_id": node_id,
        "old_status": old_status,
        "new_status": new_status,
        "reason": reason,
    }

    wh_status, wh_error = _send_webhook("device_status_changed", payload)

    _persist_audit(
        signal_name="device_status_changed",
        action=new_status,
        node_id=node_id,
        resource_id=f"{old_status}->{new_status}",
        payload=payload,
        webhook_status=wh_status,
        webhook_error=wh_error,
    )
