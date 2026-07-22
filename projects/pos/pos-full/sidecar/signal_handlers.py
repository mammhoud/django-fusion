"""
POS Full — shared signal handlers (logging, webhooks, audit persistence).

To activate, import this module at server startup:
    import signal_handlers  # noqa: F401
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from django.dispatch import receiver

from models.audit import SignalEvent
from signals import (
    config_changed, master_device_changed, cloud_link_changed,
    config_synced, device_status_changed,
)

logger = logging.getLogger("pos.signal_handlers")

WEBHOOK_TIMEOUT = int(os.environ.get("WEBHOOK_TIMEOUT_SECONDS", "10"))

_WEBHOOK_ENV_MAP = {
    "config_changed": "WEBHOOK_URL_CONFIG_CHANGED",
    "master_device_changed": "WEBHOOK_URL_MASTER_DEVICE_CHANGED",
    "cloud_link_changed": "WEBHOOK_URL_CLOUD_LINK_CHANGED",
    "config_synced": "WEBHOOK_URL_CONFIG_SYNCED",
    "device_status_changed": "WEBHOOK_URL_DEVICE_STATUS_CHANGED",
}


class _WebhookUrls(dict):
    def __init__(self):
        super().__init__({k: None for k in _WEBHOOK_ENV_MAP})

    def __getitem__(self, key):
        env_var = _WEBHOOK_ENV_MAP.get(key)
        return os.environ.get(env_var) if env_var else None

    def get(self, key, default=None):
        env_var = _WEBHOOK_ENV_MAP.get(key)
        return os.environ.get(env_var) if env_var else default

    def __setitem__(self, key, value):
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


WEBHOOK_URLS = _WebhookUrls()


def _send_webhook(signal_name, payload):
    url = WEBHOOK_URLS.get(signal_name)
    if not url:
        return "skipped", "no_webhook_url_configured"
    try:
        import httpx
        with httpx.Client(timeout=WEBHOOK_TIMEOUT) as client:
            resp = client.post(url, json={
                "signal": signal_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": payload,
            }, headers={
                "Content-Type": "application/json",
                "User-Agent": "POS-SignalWebhook/1.0",
                "X-Signal-Name": signal_name,
            })
            resp.raise_for_status()
            return "sent", ""
    except Exception as exc:
        logger.warning("Webhook %s delivery failed: %s", signal_name, exc)
        return "failed", str(exc)


def _persist_audit(signal_name, action, node_id="", resource_id="",
                   payload=None, webhook_status="", webhook_error=""):
    try:
        SignalEvent.objects.create(
            signal_name=signal_name, action=action, node_id=node_id,
            resource_id=resource_id, payload=payload or {},
            webhook_status=webhook_status, webhook_error=webhook_error,
        )
    except Exception as exc:
        logger.error("Failed to persist SignalEvent audit record: %s", exc)


def _log_signal(signal_name, action, node_id="", details=""):
    logger.info("SIGNAL [%s] action=%s node=%s %s", signal_name, action, node_id or "(global)", details)


@receiver(config_changed)
def handle_config_changed(sender, **kwargs):
    node_id = kwargs.get("node_id", "")
    config_key = kwargs.get("config_key", "")
    action = kwargs.get("action", "updated")
    category = kwargs.get("category", "")
    _log_signal("config_changed", action, node_id, f"key={config_key} category={category}")
    payload = {"node_id": node_id, "config_key": config_key, "action": action,
               "category": category, "old_value": kwargs.get("old_value"), "new_value": kwargs.get("new_value")}
    wh_status, wh_error = _send_webhook("config_changed", payload)
    _persist_audit("config_changed", action, node_id, config_key, payload, wh_status, wh_error)


@receiver(master_device_changed)
def handle_master_device_changed(sender, **kwargs):
    device_id = kwargs.get("device_id", "")
    action = kwargs.get("action", "updated")
    _log_signal("master_device_changed", action, device_id, f"status={kwargs.get('status', '')}")
    payload = {"device_id": device_id, "action": action, "status": kwargs.get("status", ""),
               "metadata": kwargs.get("metadata", {})}
    wh_status, wh_error = _send_webhook("master_device_changed", payload)
    _persist_audit("master_device_changed", action, device_id, device_id, payload, wh_status, wh_error)


@receiver(cloud_link_changed)
def handle_cloud_link_changed(sender, **kwargs):
    link_id = str(kwargs.get("link_id", ""))
    action = kwargs.get("action", "updated")
    _log_signal("cloud_link_changed", action, link_id,
                f"status={kwargs.get('status', '')} url={kwargs.get('cloud_url', '')}")
    payload = {"link_id": link_id, "action": action, "status": kwargs.get("status", ""),
               "cloud_url": kwargs.get("cloud_url", "")}
    wh_status, wh_error = _send_webhook("cloud_link_changed", payload)
    _persist_audit("cloud_link_changed", action, resource_id=link_id, payload=payload,
                   webhook_status=wh_status, webhook_error=wh_error)


@receiver(config_synced)
def handle_config_synced(sender, **kwargs):
    source = kwargs.get("source_device_id", "")
    targets = kwargs.get("target_device_ids", [])
    config_keys = kwargs.get("config_keys", [])
    status = kwargs.get("status", "success")
    _log_signal("config_synced", status, source, f"targets={len(targets)} keys={len(config_keys)}")
    payload = {"source_device_id": source, "target_device_ids": targets,
               "config_keys": config_keys, "status": status}
    wh_status, wh_error = _send_webhook("config_synced", payload)
    _persist_audit("config_synced", status, source, f"synced_{len(config_keys)}_keys",
                   payload, wh_status, wh_error)


@receiver(device_status_changed)
def handle_device_status_changed(sender, **kwargs):
    node_id = kwargs.get("node_id", "")
    old_status = kwargs.get("old_status", "")
    new_status = kwargs.get("new_status", "")
    reason = kwargs.get("reason", "")
    _log_signal("device_status_changed", new_status, node_id, f"old={old_status} reason={reason}")
    payload = {"node_id": node_id, "old_status": old_status, "new_status": new_status, "reason": reason}
    wh_status, wh_error = _send_webhook("device_status_changed", payload)
    _persist_audit("device_status_changed", new_status, node_id,
                   f"{old_status}->{new_status}", payload, wh_status, wh_error)
