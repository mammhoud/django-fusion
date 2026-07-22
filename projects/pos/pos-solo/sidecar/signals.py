"""
POS Solo — Django signals for device configuration and management.

These signals are fired by model save/delete operations and can be
consumed by Robyn WebSocket streams or sync infrastructure.
"""

from __future__ import annotations

import logging
from typing import Any

from django.dispatch import Signal

logger = logging.getLogger("pos.signals")

# ===========================================================================
# Signal definitions
# ===========================================================================

config_changed: Signal = Signal()
master_device_changed: Signal = Signal()
cloud_link_changed: Signal = Signal()
config_synced: Signal = Signal()
device_status_changed: Signal = Signal()


# ===========================================================================
# Signal helpers
# ===========================================================================


def fire_config_changed(
    node_id: str,
    config_key: str,
    action: str = "updated",
    old_value: Any = None,
    new_value: Any = None,
    category: str = "",
) -> None:
    """Fire a config_changed signal with structured payload."""
    config_changed.send(
        sender=None,
        node_id=node_id,
        config_key=config_key,
        action=action,
        old_value=old_value,
        new_value=new_value,
        category=category,
    )


def fire_master_device_changed(
    device_id: str,
    action: str = "updated",
    status: str = "",
    metadata: dict | None = None,
) -> None:
    """Fire a master_device_changed signal."""
    master_device_changed.send(
        sender=None,
        device_id=device_id,
        action=action,
        status=status,
        metadata=metadata or {},
    )


def fire_cloud_link_changed(
    link_id: int | str,
    action: str = "updated",
    status: str = "",
    cloud_url: str = "",
) -> None:
    """Fire a cloud_link_changed signal."""
    cloud_link_changed.send(
        sender=None,
        link_id=link_id,
        action=action,
        status=status,
        cloud_url=cloud_url,
    )


def fire_config_synced(
    source_device_id: str,
    target_device_ids: list[str],
    config_keys: list[str],
    status: str = "success",
) -> None:
    """Fire a config_synced signal after pushing config to devices."""
    config_synced.send(
        sender=None,
        source_device_id=source_device_id,
        target_device_ids=target_device_ids,
        config_keys=config_keys,
        status=status,
    )


def fire_device_status_changed(
    node_id: str,
    old_status: str,
    new_status: str,
    reason: str = "",
) -> None:
    """Fire a device_status_changed signal."""
    device_status_changed.send(
        sender=None,
        node_id=node_id,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
    )
