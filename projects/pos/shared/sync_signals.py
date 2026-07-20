"""
Shared sync signal handlers — track model changes for cloud sync.

Registers @receiver(post_save) handlers for managed models that have
sync tracking fields (is_synced, synced_at, sync_status).

When a tracked model instance is created or updated, it is flagged
for pending sync. The webhook delivery system (shared/handlers/signal.py)
picks up the sync_signal and delivers changes to the configured cloud endpoint.

Safety: uses hasattr() checks before accessing sync fields to avoid
AttributeError on models that don't have them.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger("shared.sync_signals")

# ── Models that sync signals will track ──
# Each sidecar imports this module after its model classes are defined.
# The @receiver decorators use the sender=None pattern to listen to all models,
# then filter by checking for sync fields at runtime.


@receiver(post_save)
def flag_for_sync(sender, instance, created, **kwargs):
    """Flag a model instance for cloud sync after save."""
    if not hasattr(instance, "is_synced"):
        return

    # Don't flag if it's a raw fixture load or migration
    if kwargs.get("raw", False):
        return

    try:
        # Always re-flag on any save — updates to synced records need re-sync
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
    """Track deletions for sync.

    TODO: Create a SyncLog entry or fire a deletion signal so the cloud
    master can remove the corresponding record. Currently this only logs
    the event — deleted records are silently lost during sync cycles.
    """
    if not hasattr(instance, "is_synced"):
        return

    logger.debug("Sync delete tracked: %s#%s", sender.__name__, instance.pk)
