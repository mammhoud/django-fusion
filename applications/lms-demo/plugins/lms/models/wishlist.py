"""
Wishlist Model for LMS.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Wishlist(models.Model):
    """
    User's course wishlist.

    Attributes:
        user: The user who added the course
        course: The course added to wishlist
        created_at: When the course was added
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name=_("User"),
    )

    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
        verbose_name=_("Course"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Added At"),
    )

    # Optional: Add notes
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Personal notes about this course"),
    )

    class Meta:
        verbose_name = _("Wishlist Item")
        verbose_name_plural = _("Wishlist Items")
        ordering = ["-created_at"]
        unique_together = [["user", "course"]]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.course.title}"

    @classmethod
    def add_to_wishlist(cls, user, course):
        """Add a course to user's wishlist."""
        item, created = cls.objects.get_or_create(
            user=user,
            course=course,
        )
        return item, created

    @classmethod
    def remove_from_wishlist(cls, user, course):
        """Remove a course from user's wishlist."""
        return cls.objects.filter(user=user, course=course).delete()

    @classmethod
    def is_in_wishlist(cls, user, course):
        """Check if a course is in user's wishlist."""
        return cls.objects.filter(user=user, course=course).exists()

    @classmethod
    def get_user_wishlist(cls, user):
        """Get all courses in user's wishlist."""
        return cls.objects.filter(user=user).select_related("course")
