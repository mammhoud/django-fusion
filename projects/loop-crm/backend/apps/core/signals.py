"""Account/profile synchronization for the standard Django user model."""
from __future__ import annotations

import logging

from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def ensure_user_profile(sender, instance, created, **kwargs):
    """Ensure allauth-created and admin-created accounts have a role record."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(user_signed_up)
def provision_start_free_workspace(sender, request, user, **kwargs):
    """Give every fresh signup (the landing's Start free flow) a demo workspace.

    The account signal fires for email signup right after the user is created;
    social signup routes through the same account flow. A user who already has
    a workspace (admin-created, re-invited, or reseeded) is left untouched.
    """
    profile = getattr(user, "profile", None)
    if profile is None or profile.workspace_id is not None:
        return
    from .demo import ensure_user_workspace

    try:
        ensure_user_workspace(user)
        logger.info("Provisioned demo workspace for new signup %s", user)
    except Exception:  # noqa: BLE001 - never break signup over demo seeding
        logger.exception("Demo workspace provisioning failed for %s", user)

