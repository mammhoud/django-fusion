"""Auto-create StaffProfile when a User is saved."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def handle_crm_staff_profile(sender, instance, created, **kwargs):
    from plugins.accounts_app.models import StaffProfile

    if created:
        StaffProfile.objects.get_or_create(user=instance)
    else:
        # Only save if profile already exists — don't force creation for every user
        StaffProfile.objects.filter(user=instance).update()
