"""POS Full — sync signal handlers: track model changes for cloud sync."""

from __future__ import annotations

import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger("pos.sync_signals")


@receiver(post_save)
def flag_for_sync(sender, instance, created, **kwargs):
    if not hasattr(instance, "is_synced"):
        return
    if kwargs.get("raw", False):
        return
    action = "created" if created else "updated"
    try:
        instance.__class__.objects.filter(pk=instance.pk).update(
            is_synced=False, sync_status="pending",
        )
        logger.debug("Sync flagged (%s): %s#%s", action, sender.__name__, instance.pk)
    except Exception as exc:
        logger.warning("Sync flag failed for %s#%s: %s", sender.__name__, instance.pk, exc)

    # Real-time multi-terminal broadcast — notify connected peers so they can
    # pull the change via GET /sync/changes/ without polling.
    try:
        from consumers import broadcast_entities

        broadcast_entities({
            "type": "entity_change",
            "entity": sender.__name__.lower(),
            "id": instance.pk,
            "action": action,
        })
    except Exception as exc:  # pragma: no cover — channel layer may not be ready
        logger.debug("Sync broadcast skipped for %s#%s: %s", sender.__name__, instance.pk, exc)


@receiver(post_delete)
def flag_delete_for_sync(sender, instance, **kwargs):
    if not hasattr(instance, "is_synced"):
        return
    logger.debug("Sync delete tracked: %s#%s", sender.__name__, instance.pk)
