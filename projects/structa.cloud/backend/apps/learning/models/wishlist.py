from django.conf import settings
from django.db import models

from .courses.info import Course


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_wishlist"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="learning_user_course_wishlist"
            )
        ]
