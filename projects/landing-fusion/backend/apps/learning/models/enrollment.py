from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .courses.info import Course
from .certificate import Certificate
from apps.learning.managers.enrollments import EnrollmentQuerySet


class Enrollment(models.Model):
    """User entitlement for a course; payments can attach later without changing access logic."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    progress = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    provider = models.CharField(
        max_length=40, blank=True, help_text=_("Payment provider reference, when configured.")
    )
    provider_reference = models.CharField(max_length=160, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="learning_user_course")
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["course", "status"]),
        ]

    objects = EnrollmentQuerySet.as_manager()

    def __str__(self):
        return f"{self.user} · {self.course}"

    @property
    def has_verified_payment(self) -> bool:
        """Whether this row carries enough evidence to unlock a paid course."""
        return self.course.is_free or (
            bool(self.provider_reference) and self.amount_paid >= self.course.price
        )

    def mark_progress(self, value: int):
        self.progress = max(0, min(100, int(value)))
        self.last_accessed_at = timezone.now()
        if self.progress >= 100:
            self.progress = 100
            self.status = self.Status.COMPLETED
            self.completed_at = self.completed_at or timezone.now()
        elif self.status == self.Status.COMPLETED:
            self.status = self.Status.ACTIVE
            self.completed_at = None
        self.save(update_fields=["progress", "status", "completed_at", "last_accessed_at"])

    def recalculate_progress(self) -> int:
        """Persist lesson-derived progress and keep certificates consistent.

        Views call this explicitly; the signal remains a compatibility safety
        net for admin edits and imports. A certificate is revoked when a
        learner toggles below completion and issued again when they finish.
        """
        total = self.course.lesson_count
        completed = self.lesson_progress.filter(completed=True).count()
        value = round(completed / total * 100) if total else 0
        self.mark_progress(value)
        if self.course.has_certificate:
            if value >= 100:
                Certificate.objects.get_or_create(user=self.user, course=self.course)
            else:
                Certificate.objects.filter(user=self.user, course=self.course).delete()
        return value
