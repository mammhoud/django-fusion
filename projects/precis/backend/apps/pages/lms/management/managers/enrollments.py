from __future__ import annotations

import logging
import uuid
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django_fusion.management.managers.base import CachedManager

if TYPE_CHECKING:
    from apps.pages.lms.models import Enrollment

User = get_user_model()
logger = logging.getLogger(__name__)


class EnrollmentManager(CachedManager):
    """Query and mutation operations for LMS enrollments."""

    CACHE_PREFIX = "enrollment"
    DEFAULT_TIMEOUT = 1800

    def _generation(self, scope: str, identifier: int) -> str:
        key = f"{self.CACHE_PREFIX}:generation:{scope}:{identifier}"
        return cache.get_or_set(key, uuid.uuid4().hex, timeout=self.DEFAULT_TIMEOUT)

    def _bump_generation(self, scope: str, identifier: int) -> None:
        cache.set(
            f"{self.CACHE_PREFIX}:generation:{scope}:{identifier}",
            uuid.uuid4().hex,
            timeout=self.DEFAULT_TIMEOUT,
        )

    @staticmethod
    def _lesson_progress_model():
        from apps.pages.lms.models.courses.progress import LessonProgress

        return LessonProgress

    def _completed_lesson_count(self, enrollment: Enrollment) -> int:
        progress_model = self._lesson_progress_model()
        return progress_model.objects.filter(
            user=enrollment.student,
            lesson__module__course=enrollment.course,
            status=progress_model.StatusChoices.COMPLETED,
        ).count()

    def _learning_minutes(self, user: User, since=None) -> float:
        progress_model = self._lesson_progress_model()
        queryset = progress_model.objects.filter(user=user)
        if since is not None:
            queryset = queryset.filter(last_accessed_at__gte=since)
        return sum(
            item.time_spent.total_seconds() / 60 for item in queryset.only("time_spent")
        )

    def _certificate_info(self, enrollment: Enrollment) -> Dict[str, Any]:
        """Expose enrollment certificate state without duplicating certificate fields."""
        return {
            "available": bool(getattr(enrollment.course, "has_certificate", False)),
            "issued": False,
            "url": None,
        }

    def get_user_enrollments_detailed(
        self,
        user_id: int,
        status: str | None = None,
        progress_filter: str | None = None,
        limit: int | None = None,
        offset: int = 0,
        include_related: bool = True,
    ) -> Dict[str, Any]:
        """Return a user's enrollments with progress and course summaries."""
        generation = self._generation("user", user_id)
        cache_key = (
            f"{self.CACHE_PREFIX}:user:{user_id}:{generation}:"
            f"{status}:{progress_filter}:{limit}:{offset}:{include_related}"
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return {**cached, "from_cache": True}

        user = User.objects.filter(pk=user_id).first()
        if user is None:
            return {"enrollments": [], "total": 0, "has_more": False}

        queryset = self.filter(student=user, is_active=True).select_related(
            "course", "course__instructor"
        )
        if status == "active":
            queryset = queryset.filter(completed_at__isnull=True)
        elif status == "completed":
            queryset = queryset.filter(completed_at__isnull=False)
        elif status == "in_progress":
            queryset = queryset.filter(completed_at__isnull=True, progress__gt=0)

        if progress_filter == "not_started":
            queryset = queryset.filter(progress=0)
        elif progress_filter == "in_progress":
            queryset = queryset.filter(progress__gt=0, progress__lt=100)
        elif progress_filter == "almost_done":
            queryset = queryset.filter(progress__gte=80)

        total = queryset.count()
        enrollments = queryset.order_by("-enrolled_at")[offset : offset + limit if limit else None]
        data = [self._serialize_enrollment(enrollment) for enrollment in enrollments]
        result = {
            "enrollments": data,
            "total": total,
            "has_more": total > offset + len(data),
            "stats": self._user_stats(user),
        }
        cache.set(cache_key, result, timeout=self.DEFAULT_TIMEOUT)
        return {**result, "from_cache": False}

    def _serialize_enrollment(self, enrollment: Enrollment) -> Dict[str, Any]:
        course = enrollment.course
        certificate = self._certificate_info(enrollment)
        return {
            "enrollment_id": enrollment.pk,
            "course_id": course.pk,
            "course_title": course.title,
            "course_slug": course.slug,
            "course_thumbnail": course.image.file.url if course.image else None,
            "course_difficulty": course.difficulty_level,
            "instructor_name": course.instructor.get_full_name() if course.instructor else None,
            "progress": enrollment.progress,
            "status": enrollment.status,
            "enrolled_at": enrollment.enrolled_at,
            "last_accessed": enrollment.last_accessed_at,
            "completed_at": enrollment.completed_at,
            "total_lessons": course.total_lessons,
            "completed_lessons": self._completed_lesson_count(enrollment),
            "certificate_available": certificate["available"],
            "certificate_issued": certificate["issued"],
            "certificate_url": certificate["url"],
        }

    def _user_stats(self, user: User) -> Dict[str, Any]:
        enrollments = self.filter(student=user, is_active=True)
        aggregates = enrollments.aggregate(
            total=Count("id"),
            completed=Count("id", filter=Q(completed_at__isnull=False)),
            average_progress=Avg("progress", filter=Q(completed_at__isnull=True)),
        )
        total = aggregates["total"] or 0
        completed = aggregates["completed"] or 0
        week_ago = timezone.now() - timedelta(days=7)
        return {
            "total_courses": total,
            "completed_courses": completed,
            "active_courses": total - completed,
            "average_progress": round(aggregates["average_progress"] or 0, 1),
            "total_learning_hours": round(self._learning_minutes(user) / 60, 1),
            "weekly_learning_hours": round(self._learning_minutes(user, week_ago) / 60, 1),
            "completion_rate": completed / total * 100 if total else 0,
        }

    def get_course_enrollments_detailed(
        self,
        course_id: int,
        status_filter: str | None = None,
        progress_range: Tuple[int, int] | None = None,
        search_query: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Return paginated course enrollments and aggregate analytics."""
        generation = self._generation("course", course_id)
        cache_key = (
            f"{self.CACHE_PREFIX}:course:{course_id}:{generation}:"
            f"{status_filter}:{progress_range}:{search_query}:{limit}:{offset}"
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return {**cached, "from_cache": True}

        queryset = self.filter(course_id=course_id, is_active=True).select_related("student")
        if status_filter == "active":
            queryset = queryset.filter(completed_at__isnull=True)
        elif status_filter == "completed":
            queryset = queryset.filter(completed_at__isnull=False)
        if progress_range:
            queryset = queryset.filter(progress__range=progress_range)
        if search_query:
            queryset = queryset.filter(
                Q(student__username__icontains=search_query)
                | Q(student__email__icontains=search_query)
                | Q(student__first_name__icontains=search_query)
                | Q(student__last_name__icontains=search_query)
            )

        total = queryset.count()
        enrollments = queryset.order_by("-enrolled_at")[offset : offset + limit]
        data = [
            {
                "id": enrollment.pk,
                "student_id": enrollment.student_id,
                "student_name": enrollment.student.get_full_name(),
                "student_email": enrollment.student.email,
                "enrolled_at": enrollment.enrolled_at,
                "progress": enrollment.progress,
                "status": enrollment.status,
                "completed_at": enrollment.completed_at,
            }
            for enrollment in enrollments
        ]
        analytics = queryset.aggregate(
            total_students=Count("id"),
            completed_students=Count("id", filter=Q(completed_at__isnull=False)),
            average_progress=Avg("progress"),
        )
        result = {
            "enrollments": data,
            "total": total,
            "has_more": total > offset + len(data),
            "analytics": {
                "total_students": analytics["total_students"] or 0,
                "active_students": (analytics["total_students"] or 0)
                - (analytics["completed_students"] or 0),
                "completion_rate": (
                    (analytics["completed_students"] or 0) / total * 100 if total else 0
                ),
                "average_progress": round(analytics["average_progress"] or 0, 1),
                "recent_activity": self._recent_activity(course_id),
            },
        }
        cache.set(cache_key, result, timeout=900)
        return {**result, "from_cache": False}

    def _recent_activity(self, course_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        progress_model = self._lesson_progress_model()
        completions = progress_model.objects.filter(
            lesson__module__course_id=course_id,
            status=progress_model.StatusChoices.COMPLETED,
        ).select_related("user", "lesson").order_by("-completed_at")[:limit]
        return [
            {
                "type": "lesson_completed",
                "student_name": completion.user.get_full_name(),
                "lesson_title": completion.lesson.title,
                "completed_at": completion.completed_at,
                "progress": completion.progress,
            }
            for completion in completions
        ]

    def get_enrollment_summary(self, user_id: int) -> Dict[str, Any]:
        """Return a compact dashboard summary for an authenticated user."""
        user = User.objects.filter(pk=user_id).first()
        if user is None:
            return {}
        active = self.filter(student=user, is_active=True, completed_at__isnull=True).select_related("course")[:5]
        completed = self.filter(student=user, is_active=True, completed_at__isnull=False).select_related("course")[:3]
        return {
            "active_enrollments": [
                {"course_id": item.course_id, "course_title": item.course.title, "progress": item.progress}
                for item in active
            ],
            "recent_completions": [
                {"course_id": item.course_id, "course_title": item.course.title, "completed_at": item.completed_at}
                for item in completed
            ],
            "total_active": self.filter(student=user, is_active=True, completed_at__isnull=True).count(),
            "total_completed": self.filter(student=user, is_active=True, completed_at__isnull=False).count(),
        }

    def get_user_enrollment_for_course(self, user_id: int, course_id: int):
        return self.filter(student_id=user_id, course_id=course_id, is_active=True).first()

    def bulk_enroll_students(
        self,
        course_id: int,
        student_ids: List[int],
        enrollment_date=None,
        created_by: User | None = None,
    ) -> Dict[str, Any]:
        """Enroll multiple users, returning per-user results."""
        results = {"successful": [], "failed": [], "already_enrolled": [], "total_attempted": len(student_ids)}
        with transaction.atomic():
            for student_id in student_ids:
                try:
                    if self.filter(course_id=course_id, student_id=student_id, is_active=True).exists():
                        results["already_enrolled"].append(student_id)
                        continue
                    enrollment = self.create(
                        course_id=course_id,
                        student_id=student_id,
                        payment_status="completed",
                        amount_paid=0,
                        is_active=True,
                    )
                    results["successful"].append({"student_id": student_id, "enrollment_id": enrollment.pk})
                except Exception as exc:
                    results["failed"].append({"student_id": student_id, "error": str(exc)})
        self._invalidate_course_enrollment_cache(course_id)
        return results

    def bulk_update_enrollment_progress(
        self,
        enrollment_ids: List[int],
        progress_increment: float | None = None,
        time_spent_minutes: int | None = None,
    ) -> Dict[str, int]:
        results = {"updated": 0, "failed": 0, "completed": 0}
        for enrollment_id in enrollment_ids:
            try:
                enrollment = self.get(pk=enrollment_id)
                if progress_increment:
                    enrollment.progress = min(100, enrollment.progress + progress_increment)
                if enrollment.progress >= 100 and enrollment.completed_at is None:
                    enrollment.completed_at = timezone.now()
                    results["completed"] += 1
                enrollment.save(update_fields=["progress", "completed_at", "last_accessed_at"])
                self.invalidate_cache_for_enrollment(enrollment_id)
                results["updated"] += 1
            except Exception:
                results["failed"] += 1
        return results

    def invalidate_cache_for_enrollment(self, enrollment_id: int) -> None:
        cache.delete(f"{self.CACHE_PREFIX}:enrollment:{enrollment_id}")
        enrollment = self.filter(pk=enrollment_id).values("student_id", "course_id").first()
        if enrollment:
            self.invalidate_user_enrollment_cache(enrollment["student_id"])
            self._invalidate_course_enrollment_cache(enrollment["course_id"])

    def invalidate_user_enrollment_cache(self, user_id: int) -> None:
        cache.delete(f"{self.CACHE_PREFIX}:summary:{user_id}")
        self._bump_generation("user", user_id)

    def _invalidate_course_enrollment_cache(self, course_id: int) -> None:
        self._bump_generation("course", course_id)
