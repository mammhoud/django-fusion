"""
user_signals.py
---------------
Handles automatic setup when a new User is created:
- Creates Person and Profile
- Assigns Role
- Links Django Group and updates Role.group reference
- Sends welcome notification
"""

import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Person

logger = logging.getLogger(__name__)

User = get_user_model()
Profile = apps.get_model(settings.PROFILE_MODEL)

@receiver(post_save, sender=User)
def create_user_related_records(sender, instance, created, **kwargs):
    """
    Automatically creates related Person and Profile records
    when a new user is created, and links them to a default Role and Group.
    """
    if not created:
        return

    # Skip if profile already exists
    if hasattr(instance, "profile"):
        logger.info(f"👤 Profile already exists for user [{instance.username}]")
        return

    try:
        with transaction.atomic():
            # 1. Create linked Person
            person = Person.objects.create(
                first_name=instance.first_name or instance.username.title(),
                last_name=instance.last_name or "User",
                email=instance.email,
                is_active=True,
            )
            logger.info(f"🧍 Created Person for [{instance.username}]")

            # # 2. Get or create default Role
            # role, role_created = Role.objects.get_or_create(
            #     is_default=True,
            #     defaults={
            #         "name": "Default Role",
            #         "description": "Fallback default role created automatically",
            #     },
            # )
            # if role_created:
            #     logger.info(f"🛠️ Created default Role [{role.name}]")

            # 3. Create or get Django Group for this Role
            # group, group_created = Group.objects.get_or_create(name)
            # if group_created:
            #     logger.info(f"👥 Created Django Group [{group.name}]")

            # 4. Ensure Role.group is correctly referenced
            # if getattr(role, "group_id", None) != group.id:
            #     role.group = group
            #     role.save(update_fields=["group"])
            #     logger.info(f"🔗 Linked Role [{role.name}] to Group [{group.name}]")

            # 5. Create or get Profile linking all parts
            profile, created = Profile.objects.get_or_create(
                user=instance,
                defaults={
                    "person": person,
                    # "role": role,
                    "is_active": True,
                    "status": Profile.ProfileStatus.ACTIVE,
                },
            )

            if created:
                logger.info(f"✅ Created Profile for [{instance.username}]")
            else:
                logger.info(
                    f"⚠️ Profile already exists for [{instance.username}], using existing record."
                )
            # 6. Add user to the group
            # instance.groups.add(group)
            # logger.info(
            #     f"🔒 Added [{instance.username}] to Django Group [{group.name}]"
            # )

            # # 7. Optionally sync permissions from Role → Group
            # if hasattr(role, "permissions"):
            #     group.permissions.set(role.permissions.all())
            #     logger.info(f"🧩 Synced Role permissions to Group [{group.name}]")

            # 8. Optionally send welcome message
            try:
                from apps.pages.tasks import send_user_welcome_notification

                send_user_welcome_notification(instance, profile)
                logger.info(f"📨 Sent welcome notification to [{instance.username}]")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send welcome notification: {e}")

    except Exception as e:
        logger.error(f"❌ Failed to set up user [{instance.username}]: {e}")
