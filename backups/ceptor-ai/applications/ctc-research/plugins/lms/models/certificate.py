"""
Certificate Model for LMS course completion certificates.
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Certificate(models.Model):
    """
    Course completion certificate.

    Attributes:
        user: The user who earned the certificate
        course: The course that was completed
        certificate_id: Unique certificate identifier
        issued_at: When the certificate was issued
        pdf_file: Generated PDF certificate file
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("User"),
    )

    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("Course"),
    )

    certificate_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Certificate ID"),
        help_text=_("Unique certificate identifier"),
        editable=False,
    )

    issued_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Issued At"),
    )

    pdf_file = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True,
        verbose_name=_("PDF File"),
    )

    # Additional metadata
    course_title = models.CharField(
        max_length=255,
        verbose_name=_("Course Title"),
        help_text=_("Stored for historical reference"),
    )

    user_name = models.CharField(
        max_length=255,
        verbose_name=_("User Name"),
        help_text=_("Name as it appears on certificate"),
    )

    completion_date = models.DateField(
        verbose_name=_("Completion Date"),
    )

    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        ordering = ["-issued_at"]
        unique_together = [["user", "course"]]
        indexes = [
            models.Index(fields=["certificate_id"]),
            models.Index(fields=["user", "issued_at"]),
        ]

    def __str__(self):
        return f"{self.certificate_id} - {self.user_name}"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = self.generate_certificate_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_certificate_id():
        """Generate a unique certificate ID."""
        return f"CERT-{uuid.uuid4().hex[:12].upper()}"



    def get_verification_url(self):
        """Get URL for certificate verification."""
        from django.urls import reverse
        return reverse("certificate-verify", kwargs={"certificate_id": self.certificate_id})
