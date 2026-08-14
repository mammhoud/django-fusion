from django.db import models
from django.db.models import Q


class CourseQuerySet(models.QuerySet):
    """QuerySet helpers for the public course catalog."""

    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.published().filter(is_featured=True)

    def catalog(self, query: str = "", difficulty: str = ""):
        """Published courses, optionally filtered by free-text + difficulty."""
        qs = self.published().select_related("instructor").prefetch_related(
            "specializations", "tags"
        )
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(short_description__icontains=query)
                | Q(objectives__icontains=query)
                | Q(tags__name__icontains=query)
                | Q(specializations__title__icontains=query)
            )
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs

    def search(self, query: str):
        """Search across the fields surfaced by the course search API."""
        qs = self.published().select_related("instructor").prefetch_related(
            "specializations", "tags"
        )
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(short_description__icontains=query)
                | Q(objectives__icontains=query)
                | Q(target_audience__icontains=query)
                | Q(tags__name__icontains=query)
                | Q(specializations__title__icontains=query)
            )
        return qs.distinct()
