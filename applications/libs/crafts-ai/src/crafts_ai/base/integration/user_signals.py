"""
Signals for django-grep pipelines.

Auto-creates a Person profile when a new User registers.
Also syncs basic user data (email, first_name, last_name) to Person on update.
"""
import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


def _get_person_model():
    """Lazy import to avoid circular imports at module load time."""
    from crafts_ai.content.models.users.users import Person
    return Person


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_create_person_on_registration(sender, instance, created, **kwargs):
    """
    Signal: Create a Person profile whenever a new User is saved for the first time.

    - On CREATE: builds a new Person linked to the user, pre-filling
      first_name, last_name, email, display_name, slug from user data.
      Sets is_registered=True (user already exists) and registration_date.
    - On UPDATE: syncs first_name, last_name, email from user → person
      if person exists and those fields are still blank.
    """
    Person = _get_person_model()

    if created:
        try:
            # Guard: only create if not already existing (e.g. fixtures)
            if not Person.objects.filter(user=instance).exists():
                # Build slug from username or email
                import uuid

                from django.utils.text import slugify
                base_slug = slugify(instance.username or instance.email.split("@")[0] or str(uuid.uuid4())[:8])
                slug = base_slug
                counter = 1
                while Person.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                full_name = f"{instance.first_name} {instance.last_name}".strip() or instance.username

                Person.objects.create(
                    user=instance,
                    first_name=instance.first_name or "",
                    last_name=instance.last_name or "",
                    full_name=full_name,
                    display_name=full_name or instance.username,
                    email=instance.email,
                    slug=slug,
                    is_registered=True,
                    registration_date=timezone.now(),
                    status="ACTIVE" if instance.is_active else "PENDING",
                    profile_type="STU",  # Default — admin can change
                )
                logger.info(f"[Person Signal] Created Person profile for user: {instance.username}")
        except Exception as e:
            logger.error(f"[Person Signal] Failed to create Person for user {instance.pk}: {e}")

    else:
        # Sync user data → Person on updates (non-destructive: only fills blanks)
        try:
            person = Person.objects.filter(user=instance).first()
            if not person:
                return

            updated_fields = []

            if instance.email and not person.email:
                person.email = instance.email
                updated_fields.append("email")

            if instance.first_name and not person.first_name:
                person.first_name = instance.first_name
                updated_fields.append("first_name")

            if instance.last_name and not person.last_name:
                person.last_name = instance.last_name
                updated_fields.append("last_name")

            if not person.full_name and (person.first_name or person.last_name):
                person.full_name = f"{person.first_name} {person.last_name}".strip()
                updated_fields.append("full_name")

            # Sync active status
            if instance.is_active and person.status == "PENDING":
                person.status = "ACTIVE"
                updated_fields.append("status")

            if updated_fields:
                person.save(update_fields=updated_fields)
                logger.debug(f"[Person Signal] Synced fields {updated_fields} for user: {instance.username}")

        except Exception as e:
            logger.error(f"[Person Signal] Failed to sync Person for user {instance.pk}: {e}")
