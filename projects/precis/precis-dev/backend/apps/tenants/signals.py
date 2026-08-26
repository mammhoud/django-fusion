"""Course Center signals — provision center on registration approval."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CenterRegistration


@receiver(post_save, sender=CenterRegistration)
def provision_on_approval(sender, instance: CenterRegistration, **kwargs):
    """When a registration is approved, enqueue CourseCenter provisioning."""

    if instance.status != CenterRegistration.Status.APPROVED:
        return

    # Avoid double-provisioning
    from .models import CourseCenter

    if CourseCenter.objects.filter(slug=instance.subdomain).exists():
        return

    try:
        from django_fusion.tasks import enqueue

        enqueue("system", "centers.provision", registration_id=instance.id)
    except Exception:
        pass