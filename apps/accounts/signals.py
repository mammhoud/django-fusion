"""
Accounts signals for structa.cloud.

Handles email template file uploads.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_osoul.models import EmailTemplate

logger = logging.getLogger(__name__)


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
