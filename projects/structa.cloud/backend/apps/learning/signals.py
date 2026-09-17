from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import LessonProgress


def _sync(instance):
    """Recalculate derived learner state after admin or user mutations."""
    if instance.enrollment_id:
        instance.enrollment.recalculate_progress()


@receiver(post_save, sender=LessonProgress)
def sync_enrollment_progress(sender, instance, **kwargs):
    """Recalculate after a lesson is marked complete or incomplete."""
    _sync(instance)


@receiver(post_delete, sender=LessonProgress)
def sync_enrollment_after_delete(sender, instance, **kwargs):
    """Avoid stale progress/certificates after an admin deletes a row."""
    _sync(instance)
