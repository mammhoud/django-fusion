import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .courses.info import Course


class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_certificates"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    certificate_id = models.CharField(
        max_length=32, unique=True, editable=False, default=""
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="learning_user_course_certificate"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
