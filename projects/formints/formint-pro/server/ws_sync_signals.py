"""
POS Full — WebSocket sync signal handlers.

Sends local entity CRUD events to the connected Cloud CRM in real time.
Receivers are registered when this module is imported.
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from handlers import _ser
from ws_client import cloud_ws_client

logger = logging.getLogger("pos.ws_sync_signals")

# The app label shared by all POS server models.
POS_APP_LABEL = "pos_full"

SYNCED_ENTITIES = cloud_ws_client.SYNCED_ENTITIES


def _is_synced_model(sender) -> bool:
    """Return True if the sender model belongs to this server and is synced."""
    if sender._meta.app_label != POS_APP_LABEL:
        return False
    return sender._meta.model_name in SYNCED_ENTITIES


@receiver(post_save)
def entity_saved(sender, instance, created, **kwargs):
    """Broadcast a create/update event to the cloud when a synced model changes."""
    if kwargs.get("raw"):
        return

    if not _is_synced_model(sender):
        return

    model_name = sender._meta.model_name
    action = "create" if created else "update"
    try:
        data = _ser(instance)
    except Exception as exc:
        logger.warning("Failed to serialize %s#%s for WS sync: %s", model_name, instance.pk, exc)
        data = {"id": instance.pk}

    cloud_ws_client.publish_entity_event(SYNCED_ENTITIES[model_name], action, data)


@receiver(post_delete)
def entity_deleted(sender, instance, **kwargs):
    """Broadcast a delete event to the cloud when a synced model is removed."""
    if not _is_synced_model(sender):
        return

    model_name = sender._meta.model_name
    cloud_ws_client.publish_entity_event(SYNCED_ENTITIES[model_name], "delete", {"id": instance.pk})
