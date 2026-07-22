"""
POS Solo — sync signal handlers: track model changes for cloud sync.

Registers @receiver(post_save) handlers for managed models that have
sync tracking fields (is_synced, synced_at, sync_status).
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger("pos.sync_signals")


@receiver(post_save)
def flag_for_sync(sender, instance, created, **kwargs):
    """Flag a model instance for cloud sync after save."""
    if not hasattr(instance, "is_synced"):
        return

    if kwargs.get("raw", False):
        return

    try:
        instance.__class__.objects.filter(pk=instance.pk).update(
            is_synced=False,
            sync_status="pending",
        )
        if created:
            logger.debug("Sync flagged (created): %s#%s", sender.__name__, instance.pk)
        else:
            logger.debug("Sync flagged (updated): %s#%s", sender.__name__, instance.pk)
    except Exception as exc:
        logger.warning("Sync flag failed for %s#%s: %s", sender.__name__, instance.pk, exc)


@receiver(post_delete)
def flag_delete_for_sync(sender, instance, **kwargs):
    """Track deletions for sync."""
    if not hasattr(instance, "is_synced"):
        return

    logger.debug("Sync delete tracked: %s#%s", sender.__name__, instance.pk)
