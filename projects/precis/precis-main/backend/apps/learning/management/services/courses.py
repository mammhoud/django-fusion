from __future__ import annotations

from django.db.models import Avg, Count, Prefetch, Q

from apps.learning.models import Course, Lesson, Module


class CourseService:
    """Catalog + detail queries for the learner surface."""

    @staticmethod
    def catalog(query: str = "", difficulty: str = ""):
        """Published courses with counts + rating aggregates, optional filters."""
        return Course.objects.catalog(query=query, difficulty=difficulty).annotate(
            _module_count=Count("modules", distinct=True),
            _lesson_count=Count(
                "modules__lessons",
                filter=Q(modules__lessons__is_active=True),
                distinct=True,
            ),
            _avg_rating=Avg("reviews__rating", filter=Q(reviews__is_published=True)),
            _reviews_count=Count(
                "reviews", filter=Q(reviews__is_published=True), distinct=True
            ),
        )

    @staticmethod
    def course_detail_queryset():
        """Published courses with annotations + a prefetched module tree."""
        return (
            Course.objects.published()
            .select_related("instructor")
            .prefetch_related("specializations", "tags")
            .annotate(
                _module_count=Count("modules", distinct=True),
                _lesson_count=Count(
                    "modules__lessons",
                    filter=Q(modules__lessons__is_active=True),
                    distinct=True,
                ),
                _avg_rating=Avg("reviews__rating", filter=Q(reviews__is_published=True)),
                _reviews_count=Count(
                    "reviews", filter=Q(reviews__is_published=True), distinct=True
                ),
                _enrolled_count=Count(
                    "enrollments",
                    filter=~Q(enrollments__status="cancelled"),
                    distinct=True,
                ),
            )
            .prefetch_related(
                Prefetch(
                    "modules",
                    queryset=Module.objects.prefetch_related(
                        Prefetch(
                            "lessons",
                            queryset=Lesson.objects.prefetch_related("resources"),
                        )
                    ),
                )
            )
        )

    @staticmethod
    def search(query: str):
        """Free-text search across course content fields."""
        return Course.objects.search(query)
