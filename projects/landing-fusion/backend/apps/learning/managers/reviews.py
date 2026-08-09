from django.db import models


class ReviewQuerySet(models.QuerySet):
    """QuerySet helpers for reviews (Precis parity: publishing workflow)."""

    def published(self):
        """Only reviews visible to the public."""
        return self.filter(is_published=True)

    def for_course(self, course):
        """Reviews for a course, newest first."""
        return self.filter(course=course).order_by("-created_at")
