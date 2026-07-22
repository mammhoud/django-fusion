"""POS Full — Django signals for device configuration and management."""

from __future__ import annotations

import logging
from typing import Any

from django.dispatch import Signal

logger = logging.getLogger("pos.signals")

config_changed: Signal = Signal()
master_device_changed: Signal = Signal()
cloud_link_changed: Signal = Signal()
config_synced: Signal = Signal()
device_status_changed: Signal = Signal()


def fire_config_changed(node_id, config_key, action="updated", old_value=None, new_value=None, category=""):
    config_changed.send(sender=None, node_id=node_id, config_key=config_key, action=action,
                        old_value=old_value, new_value=new_value, category=category)


def fire_master_device_changed(device_id, action="updated", status="", metadata=None):
    master_device_changed.send(sender=None, device_id=device_id, action=action,
                               status=status, metadata=metadata or {})


def fire_cloud_link_changed(link_id, action="updated", status="", cloud_url=""):
    cloud_link_changed.send(sender=None, link_id=link_id, action=action,
                            status=status, cloud_url=cloud_url)


def fire_config_synced(source_device_id, target_device_ids, config_keys, status="success"):
    config_synced.send(sender=None, source_device_id=source_device_id,
                       target_device_ids=target_device_ids, config_keys=config_keys, status=status)


def fire_device_status_changed(node_id, old_status, new_status, reason=""):
    device_status_changed.send(sender=None, node_id=node_id, old_status=old_status,
                               new_status=new_status, reason=reason)
