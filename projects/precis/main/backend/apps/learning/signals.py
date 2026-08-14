"""
LMS signals for lms-fusion.com.

Handles automatic setup when a new User is created:
- Creates Instructor or Student profile based on user role
"""

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

User = get_user_model()


# ------------------------------------------------------------------
# SIGNAL HANDLERS
# ------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_lms_profiles(sender, instance, created, **kwargs):
    """
    Automatically creates a Student or Instructor record when a user is created.

    Uses lazy imports via apps.get_model() to avoid circular imports.

    - If user is staff or superuser → creates Instructor
    - Otherwise → creates Student
    """
    if not created:
        return

    # If user is staff → Instructor
    if instance.is_staff or instance.is_superuser:
        try:
            Instructor = apps.get_model("alliance", "Instructor")
            Instructor.objects.get_or_create(
                user=instance,
                defaults={
                    "first_name": instance.first_name or "",
                    "last_name": instance.last_name or "",
                    "email": instance.email or "",
                },
            )
        except (LookupError, Exception) as e:
            logger.debug(f"Could not create Instructor profile for {instance.email}: {e}")
    else:
        try:
            Student = apps.get_model("alliance", "Student")
            Student.objects.get_or_create(
                user=instance,
                defaults={
                    "first_name": instance.first_name or "",
                    "last_name": instance.last_name or "",
                    "email": instance.email or "",
                    "enrollment_id": f"STU-{instance.id:05d}",
                },
            )
        except (LookupError, Exception) as e:
            logger.debug(f"Could not create Student profile for {instance.email}: {e}")
