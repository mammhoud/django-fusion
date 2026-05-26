import logging

from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)
Profile = apps.get_model(settings.PROFILE_MODEL)


@receiver(post_save, sender=Profile)
def sync_profile_to_user(sender, instance, **kwargs):
    """Sync key fields from Profile back to User."""
    user = instance.user
    if not user:
        return

    try:
        updates = []

        if (
            instance.email_verified
            and instance.person
            and user.email != instance.person.email
        ):
            user.email = instance.person.email
            updates.append("email")

        if user.is_active != instance.is_active:
            user.is_active = instance.is_active
            updates.append("is_active")

        if updates:
            user.save(update_fields=updates)
            logger.info(f"Synced Profile → User for {user.username}: {updates}")

    except Exception as e:
        logger.error(f"Profile sync error for {user.username}: {e!s}")
