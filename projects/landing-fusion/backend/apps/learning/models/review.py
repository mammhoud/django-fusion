from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.learning.managers.reviews import ReviewQuerySet

from .courses.info import Course


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    body = models.TextField(blank=True)
    is_published = models.BooleanField(default=False, verbose_name=_("Published"))
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ReviewQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "user"], name="learning_course_user_review"
            )
        ]

    def __str__(self):
        return f"⭐ {self.user} — {self.course.title} ({self.rating}/5)"

    @property
    def stars(self):
        """Star emoji representation of the rating."""
        return "★" * self.rating + "☆" * (5 - self.rating)

    @property
    def short_body(self):
        """Truncated comment preview for admin lists."""
        if not self.body:
            return _("No comment provided.")
        return f"{self.body[:75]}..." if len(self.body) > 75 else self.body
