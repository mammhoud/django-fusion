"""Course Enrollment Lead Model - Track enrollment prospects."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .info import Course


class CourseEnrollmentLead(models.Model):
    """Track course enrollment leads for sales/marketing."""

    class Status(models.TextChoices):
        """Enrollment lead status."""

        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        ENROLLED = "enrolled", _("Enrolled")
        CANCELLED = "cancelled", _("Cancelled")

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollment_leads",
        help_text=_("Course being enrolled"),
    )
    email = models.EmailField(db_index=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Phone number for contact"),
    )

    # Enrollment Details
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Internal notes about this lead"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    enrolled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the user actually enrolled"),
    )

    class Meta:
        app_label = "lms"
        verbose_name = _("Course Enrollment Lead")
        verbose_name_plural = _("Course Enrollment Leads")
        ordering = ["-created_at"]
        unique_together = [["course", "email"]]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["course", "status"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.course.title}"
