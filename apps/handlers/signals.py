from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps import logger
from apps.LMS.models import Instructor, Student
from django_rseal.pipelines.models.settings.templates import EmailTemplate

User = get_user_model()


# ------------------------------------------------------------------
# SIGNAL HANDLERS
# ------------------------------------------------------------------
@receiver(post_save, sender=EmailTemplate)
def handle_file_uploads(sender, instance, created, **kwargs):
    """
    Automatically update inline content fields when files are uploaded.
    """
    updated = False

    # Update HTML content from uploaded file
    if instance.html_file and instance.html_file.name:
        if instance.update_html_from_file():
            updated = True

    # Update CSS content from uploaded file
    if instance.css_file and instance.css_file.name:
        if instance.update_css_from_file():
            updated = True

    # Save if content was updated from files
    if updated:
        instance.save(update_fields=["html_content", "css_content"])
        logger.info(f"Auto-updated content fields for template: {instance.name}")

    # Ensure only one default per type/language
    if instance.is_default and not instance.is_system:
        EmailTemplate.objects.filter(
            template_type=instance.template_type,
            language=instance.language,
            is_default=True,
        ).exclude(pk=instance.pk).update(is_default=False)


# ---------------------------------------------------------------------
# Signals: auto-create instructor/student profile from Django User
# ---------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """
    Automatically creates a Student or Instructor record when a user is created.
    """
    if not created:
        return

    # If user is staff → Instructor
    if instance.is_staff or instance.is_superuser:
        Instructor.objects.get_or_create(
            user=instance,
            defaults={
                "first_name": instance.first_name or "",
                "last_name": instance.last_name or "",
                "email": instance.email or "",
            },
        )
    else:
        Student.objects.get_or_create(
            user=instance,
            defaults={
                "first_name": instance.first_name or "",
                "last_name": instance.last_name or "",
                "email": instance.email or "",
                "enrollment_id": f"STU-{instance.id:05d}",
            },
        )
