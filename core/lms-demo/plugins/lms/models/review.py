from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_fusion.core.models import BaseModel as DefaultBase

from .courses import Course


class Review(DefaultBase):
    """
    Represents a students review for a specific course.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Course"),
        blank=True,
        null=True,
        help_text=_("The course this review is associated with."),
    )
    profile = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Student Profile"),
        help_text=_("The student who submitted this review."),
    )
    rating = models.IntegerField(
        _("Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        help_text=_("Rating between 1 (lowest) and 5 (highest)."),
    )
    comment = models.TextField(
        _("Comment"),
        blank=True,
        null=True,
        help_text=_("Optional written feedback from the student."),
    )
    is_displayed = models.BooleanField(
        default=True,
        verbose_name=_("Display Publicly"),
        help_text=_("Determines whether the review is visible to the public."),
    )

    class Meta:
        app_label = "lms"
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        db_table = "reviews"
        ordering = ["-created_at"]
        unique_together = ("course", "profile")
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["is_displayed"]),
        ]

    def __str__(self):
        student_name = getattr(self.profile.user, "get_full_name", lambda: self.profile.user.username)()
        course_title = getattr(self.course, "title", _("(No Course)"))
        return f"⭐ {student_name} — {course_title} ({self.rating}/5)"

    def get_absolute_url(self):
        return reverse("review-detail", kwargs={"pk": self.pk})

    @property
    def short_comment(self):
        """Return a truncated comment preview."""
        if self.comment:
            return f"{self.comment[:75]}..." if len(self.comment) > 75 else self.comment
        return _("No comment provided.")

    @property
    def stars(self):
        """Return star emoji representation of rating."""
        return "⭐" * self.rating + "☆" * (5 - self.rating)
