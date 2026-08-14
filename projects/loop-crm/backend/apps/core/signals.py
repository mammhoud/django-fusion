"""Account/profile synchronization for the standard Django user model."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=get_user_model())
def ensure_user_profile(sender, instance, created, **kwargs):
    """Ensure allauth-created and admin-created accounts have a role record."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
