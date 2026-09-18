from __future__ import annotations

from apps.learning.models import Enrollment, Lesson


class EnrollmentService:
    """Learner entitlement queries shared by the views."""

    @staticmethod
    def verified_for(user):
        """All of a user's entitlements that are valid for the course's price."""
        return Enrollment.objects.filter(user=user).verified()

    @staticmethod
    def verified_enrollment(user, course):
        """The user's verified entitlement for a course (active/completed only)."""
        return (
            Enrollment.objects.filter(user=user)
            .verified()
            .active_or_completed()
            .for_course(course)
            .first()
        )

    @staticmethod
    def active_enrollments(user):
        return EnrollmentService.verified_for(user).active_or_completed().select_related("course")

    @staticmethod
    def first_incomplete_lesson(enrollment, course):
        """First incomplete lesson in module/lesson order (None when done)."""
        completed_ids = enrollment.lesson_progress.completed_lesson_ids(enrollment)
        return (
            Lesson.objects.filter(
                module__course=course,
                is_active=True,
            )
            .order_by("module__order", "order")
            .exclude(pk__in=completed_ids)
            .select_related("module")
            .first()
        )

    @staticmethod
    def lesson_neighbors(lesson):
        """Ordered (prev, next) lessons around a lesson in its module tree."""
        siblings = list(
            Lesson.objects.filter(
                module__course=lesson.module.course,
                is_active=True,
            )
            .order_by("module__order", "order")
            .values_list("id", flat=True)
        )
        try:
            index = siblings.index(lesson.pk)
        except ValueError:
            return None, None
        prev_id = siblings[index - 1] if index > 0 else None
        next_id = siblings[index + 1] if index < len(siblings) - 1 else None
        return prev_id, next_id
