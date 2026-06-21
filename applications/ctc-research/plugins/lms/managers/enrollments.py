from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, Count, F, Max, Min, Q
from django.db.models.aggregates import Sum
from django.utils import timezone
from django_osoul.managers import CachedManager

if TYPE_CHECKING:
    from plugins.lms.models import Course, Enrollment, Lesson, Module

try:
    from crafts_ai.rseal.models import Person as Profile
except ImportError:
    Profile = None  # type: ignore[assignment,misc]

User = get_user_model()
logger = logging.getLogger(__name__)


class EnrollmentManager(CachedManager):
    """
    manager for Enrollment operations with view-specific methods.
    """

    CACHE_PREFIX = "enrollment"
    DEFAULT_TIMEOUT = 1800  # 30 minutes

    # -------------------------------------------------------------------------
    # User Enrollment Methods (For User Dashboard)
    # -------------------------------------------------------------------------

    def get_user_enrollments_detailed(
        self,
        user_id: int,
        status: str = None,
        progress_filter: str = None,
        limit: int = None,
        offset: int = 0,
        include_related: bool = True,
    ) -> Dict[str, Any]:
        """
        Get detailed enrollments for user dashboard with progress information.

        Args:
            user_id: User ID
            status: Filter by enrollment status
            progress_filter: Filter by progress range
            limit: Maximum results
            offset: Pagination offset
            include_related: Include course and module details

        Returns:
            Dictionary with enrollments and metadata
        """
        cache_key = f"{self.CACHE_PREFIX}:user:{user_id}:{status}:{progress_filter}:{limit}:{offset}:{include_related}"

        result = cache.get(cache_key)
        if result is not None:
            logger.debug(f"Cache hit for user enrollments: {user_id}")
            return {**result, "from_cache": True}

        # Base queryset
        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return {"enrollments": [], "total": 0, "has_more": False}

        queryset = self.filter(student=profile, is_active=True)

        # Apply status filter
        if status:
            if status == "active":
                queryset = queryset.filter(completed_at__isnull=True, is_active=True)
            elif status == "completed":
                queryset = queryset.filter(completed_at__isnull=False)
            elif status == "in_progress":
                queryset = queryset.filter(completed_at__isnull=True, is_active=True).exclude(
                    progress_percentage=0
                )

        # Apply progress filter
        if progress_filter:
            if progress_filter == "not_started":
                queryset = queryset.filter(progress_percentage=0)
            elif progress_filter == "in_progress":
                queryset = queryset.filter(progress_percentage__gt=0, progress_percentage__lt=100)
            elif progress_filter == "almost_done":
                queryset = queryset.filter(progress_percentage__gte=80)

        # Include related data
        if include_related:
            queryset = queryset.select_related("course", "course__instructor").prefetch_related(
                "course__modules", "course__modules__lessons"
            )

        # Get total count
        total_count = queryset.count()

        # Apply pagination
        if offset:
            queryset = queryset[offset:]
        if limit:
            queryset = queryset[:limit]

        # Calculate additional statistics
        enrollments_list = []
        for enrollment in queryset:
            enrollment_data = self._get_enrollment_dashboard_data(enrollment)
            enrollments_list.append(enrollment_data)

        result = {
            "enrollments": enrollments_list,
            "total": total_count,
            "has_more": total_count > (offset + len(enrollments_list)),
            "stats": self._get_user_enrollment_stats(profile),
        }

        cache.set(cache_key, result, timeout=self.DEFAULT_TIMEOUT)
        return {**result, "from_cache": False}

    def _get_enrollment_dashboard_data(self, enrollment: Enrollment) -> Dict[str, Any]:
        """Get enrollment data formatted for dashboard."""
        course = enrollment.course

        # Calculate time estimates
        total_duration = getattr(course, "total_duration", 0)
        estimated_time_left = 0
        if total_duration and enrollment.progress_percentage < 100:
            estimated_time_left = total_duration * (100 - enrollment.progress_percentage) / 100

        # Get next lesson
        next_lesson = self._get_next_lesson_for_enrollment(enrollment)

        # Get module progress
        module_progress = self._get_module_progress(enrollment)

        return {
            "enrollment_id": enrollment.id,
            "course_id": course.id,
            "course_title": course.title,
            "course_slug": course.slug,
            "course_thumbnail": course.thumbnail.url if course.thumbnail else None,
            "course_difficulty": course.difficulty_level,
            "instructor_name": course.instructor.get_full_name() if course.instructor else None,
            "instructor_avatar": getattr(course.instructor.profile, "avatar_url", None)
            if course.instructor
            else None,
            "progress_percentage": enrollment.progress_percentage,
            "status": "completed" if enrollment.completed_at else "active",
            "enrolled_at": enrollment.enrolled_at,
            "last_accessed": enrollment.last_accessed_at,
            "completed_at": enrollment.completed_at,
            "total_modules": course.modules.count() if hasattr(course, "modules") else 0,
            "total_lessons": getattr(course, "total_lessons", 0),
            "completed_lessons": enrollment.completed_lessons_count,
            "estimated_time_left_minutes": estimated_time_left,
            "next_lesson": next_lesson,
            "module_progress": module_progress,
            "certificate_available": enrollment.certificate_issued,
            "certificate_url": enrollment.certificate_url,
        }

    def _get_next_lesson_for_enrollment(self, enrollment: Enrollment) -> Optional[Dict[str, Any]]:
        """Get next lesson for an enrollment."""
        from ..models.courses.detail import LessonProgress

        try:
            # Get the last completed lesson
            last_completed = (
                LessonProgress.objects.filter(enrollment=enrollment, is_completed=True)
                .order_by("-completed_at")
                .first()
            )

            if last_completed:
                # Get next lesson after the last completed one
                next_lesson = (
                    Lesson.objects.filter(
                        module__course=enrollment.course, order__gt=last_completed.lesson.order
                    )
                    .order_by("order")
                    .first()
                )
            else:
                # Get first lesson in course
                next_lesson = (
                    Lesson.objects.filter(module__course=enrollment.course)
                    .order_by("order")
                    .first()
                )

            if next_lesson:
                return {
                    "id": next_lesson.id,
                    "title": next_lesson.title,
                    "module_id": next_lesson.module_id,
                    "module_title": next_lesson.module.title,
                    "order": next_lesson.order,
                    "duration": getattr(next_lesson, "duration_minutes", 0),
                    "lesson_type": getattr(next_lesson, "lesson_type", "video"),
                }
        except Exception as e:
            logger.error(f"Error getting next lesson: {e}")

        return None

    def _get_module_progress(self, enrollment: Enrollment) -> List[Dict[str, Any]]:
        """Get progress for each module in course."""
        from ..models.courses.detail import ModuleProgress

        module_progress = []

        try:
            modules = Module.objects.filter(course=enrollment.course).order_by("order")

            for module in modules:
                # Get module progress record
                try:
                    mod_progress = ModuleProgress.objects.get(enrollment=enrollment, module=module)
                    completed = mod_progress.is_completed
                    progress = mod_progress.progress_percentage
                except ModuleProgress.DoesNotExist:
                    completed = False
                    progress = 0

                module_progress.append(
                    {
                        "module_id": module.id,
                        "module_title": module.title,
                        "module_order": module.order,
                        "total_lessons": module.lessons.count(),
                        "completed_lessons": module.lessons.filter(
                            lessonprogress__enrollment=enrollment, lessonprogress__is_completed=True
                        ).count(),
                        "is_completed": completed,
                        "progress_percentage": progress,
                        "last_accessed": getattr(mod_progress, "last_accessed_at", None)
                        if "mod_progress" in locals()
                        else None,
                    }
                )
        except Exception as e:
            logger.error(f"Error getting module progress: {e}")

        return module_progress

    def _get_user_enrollment_stats(self, profile: Profile) -> Dict[str, Any]:
        """Get statistics for user enrollments."""
        enrollments = self.filter(student=profile, is_active=True)

        stats = enrollments.aggregate(
            total_enrollments=Count("id"),
            completed_courses=Count("id", filter=Q(completed_at__isnull=False)),
            active_courses=Count("id", filter=Q(completed_at__isnull=True)),
            avg_progress=Avg("progress_percentage", filter=Q(completed_at__isnull=True)),
            total_learning_hours=Sum("total_time_spent_minutes"),
            last_enrollment_date=Max("enrolled_at"),
        )

        # Calculate streak
        streak = self._calculate_learning_streak(profile)

        # Calculate weekly learning time
        weekly_time = self._get_weekly_learning_time(profile)

        return {
            "total_courses": stats["total_enrollments"] or 0,
            "completed_courses": stats["completed_courses"] or 0,
            "active_courses": stats["active_courses"] or 0,
            "average_progress": round(stats["avg_progress"] or 0, 1),
            "total_learning_hours": round((stats["total_learning_hours"] or 0) / 60, 1),
            "learning_streak_days": streak,
            "weekly_learning_hours": weekly_time,
            "completion_rate": (
                (stats["completed_courses"] / stats["total_enrollments"] * 100)
                if stats["total_enrollments"]
                else 0
            ),
        }

    def _calculate_learning_streak(self, profile: Profile) -> int:
        """Calculate consecutive days of learning."""
        from datetime import timedelta

        today = timezone.now().date()
        streak = 0

        # Check last 30 days
        for i in range(30):
            check_date = today - timedelta(days=i)

            # Check if user had learning activity on this date
            had_activity = self.filter(student=profile, last_accessed_at__date=check_date).exists()

            if had_activity:
                streak += 1
            else:
                break

        return streak

    def _get_weekly_learning_time(self, profile: Profile) -> float:
        """Get total learning time for the past week."""
        week_ago = timezone.now() - timedelta(days=7)

        weekly_time = (
            self.filter(student=profile, last_accessed_at__gte=week_ago).aggregate(
                total_minutes=Sum("total_time_spent_minutes")
            )["total_minutes"]
            or 0
        )

        return round(weekly_time / 60, 1)  # Convert to hours

    # -------------------------------------------------------------------------
    # Course Enrollment Methods (For Course Dashboard)
    # -------------------------------------------------------------------------

    def get_course_enrollments_detailed(
        self,
        course_id: int,
        status_filter: str = None,
        progress_range: Tuple[int, int] = None,
        search_query: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get detailed enrollments for a course with student information.

        Args:
            course_id: Course ID
            status_filter: Filter by enrollment status
            progress_range: Tuple of (min_progress, max_progress)
            search_query: Search in student names/emails
            limit: Results per page
            offset: Pagination offset

        Returns:
            Dictionary with enrollments and analytics
        """
        cache_key = f"{self.CACHE_PREFIX}:course:{course_id}:{status_filter}:{progress_range}:{search_query}:{limit}:{offset}"

        result = cache.get(cache_key)
        if result is not None:
            logger.debug(f"Cache hit for course enrollments: {course_id}")
            return {**result, "from_cache": True}

        queryset = self.filter(course_id=course_id, is_active=True).select_related(
            "student", "student__user"
        )

        # Apply filters
        if status_filter:
            if status_filter == "active":
                queryset = queryset.filter(completed_at__isnull=True)
            elif status_filter == "completed":
                queryset = queryset.filter(completed_at__isnull=False)

        if progress_range:
            min_progress, max_progress = progress_range
            queryset = queryset.filter(
                progress_percentage__gte=min_progress, progress_percentage__lte=max_progress
            )

        if search_query:
            queryset = queryset.filter(
                Q(student__user__username__icontains=search_query)
                | Q(student__user__email__icontains=search_query)
                | Q(student__user__first_name__icontains=search_query)
                | Q(student__user__last_name__icontains=search_query)
            )

        # Get total count
        total_count = queryset.count()

        # Get course analytics
        analytics = self._get_course_enrollment_analytics(course_id)

        # Apply pagination
        enrollments = queryset.order_by("-enrolled_at")[offset : offset + limit]

        enrollment_list = []
        for enrollment in enrollments:
            enrollment_list.append(
                {
                    "id": enrollment.id,
                    "student_id": enrollment.student.user_id,
                    "student_name": enrollment.student.user.get_full_name(),
                    "student_email": enrollment.student.user.email,
                    "student_avatar": getattr(enrollment.student, "avatar_url", None),
                    "enrolled_at": enrollment.enrolled_at,
                    "progress_percentage": enrollment.progress_percentage,
                    "status": "completed" if enrollment.completed_at else "active",
                    "completed_at": enrollment.completed_at,
                    "last_accessed_at": enrollment.last_accessed_at,
                    "total_time_spent_hours": round(enrollment.total_time_spent_minutes / 60, 1),
                    "certificate_issued": enrollment.certificate_issued,
                }
            )

        result = {
            "enrollments": enrollment_list,
            "total": total_count,
            "has_more": total_count > (offset + len(enrollment_list)),
            "analytics": analytics,
        }

        cache.set(cache_key, result, timeout=900)  # 15 minutes for course dashboards
        return {**result, "from_cache": False}

    def _get_course_enrollment_analytics(self, course_id: int) -> Dict[str, Any]:
        """Get analytics for course enrollments."""
        enrollments = self.filter(course_id=course_id, is_active=True)

        # Basic statistics
        stats = enrollments.aggregate(
            total_students=Count("id"),
            active_students=Count("id", filter=Q(completed_at__isnull=True)),
            completed_students=Count("id", filter=Q(completed_at__isnull=False)),
            avg_progress=Avg("progress_percentage"),
            avg_completion_time=Avg(
                "total_time_spent_minutes", filter=Q(completed_at__isnull=False)
            ),
            max_progress=Max("progress_percentage"),
            min_progress=Min("progress_percentage"),
        )

        # Progress distribution
        progress_distribution = list(
            enrollments.values("progress_range")
            .annotate(count=Count("id"))
            .order_by("progress_range")
        )

        # Weekly enrollment trend
        from django.db.models.functions import TruncWeek

        weekly_enrollments = list(
            enrollments.annotate(week=TruncWeek("enrolled_at"))
            .values("week")
            .annotate(count=Count("id"))
            .order_by("-week")[:8]  # Last 8 weeks
        )

        # Average progress by day of week
        from django.db.models.functions import ExtractWeekDay

        daily_progress = list(
            enrollments.annotate(day=ExtractWeekDay("last_accessed_at"))
            .values("day")
            .annotate(avg_progress=Avg("progress_percentage"))
            .order_by("day")
        )

        return {
            "total_students": stats["total_students"] or 0,
            "active_students": stats["active_students"] or 0,
            "completion_rate": (
                (stats["completed_students"] / stats["total_students"] * 100)
                if stats["total_students"]
                else 0
            ),
            "average_progress": round(stats["avg_progress"] or 0, 1),
            "average_completion_time_hours": round((stats["avg_completion_time"] or 0) / 60, 1),
            "progress_distribution": progress_distribution,
            "weekly_trend": weekly_enrollments,
            "daily_pattern": daily_progress,
            "top_performers": self._get_top_performers(course_id, limit=5),
            "recent_activity": self._get_recent_activity(course_id, limit=10),
        }

    def _get_top_performers(self, course_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing students in a course."""
        return list(
            self.filter(course_id=course_id, is_active=True, progress_percentage__gte=80)
            .select_related("student", "student__user")
            .order_by("-progress_percentage", "completed_at")[:limit]
            .values(
                "student__user__first_name",
                "student__user__last_name",
                "progress_percentage",
                "completed_at",
                "total_time_spent_minutes",
            )
        )

    def _get_recent_activity(self, course_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent enrollment activity."""
        from ..models.courses.detail import LessonProgress

        recent_completions = (
            LessonProgress.objects.filter(enrollment__course_id=course_id, is_completed=True)
            .select_related(
                "enrollment", "enrollment__student", "enrollment__student__user", "lesson"
            )
            .order_by("-completed_at")[:limit]
        )

        activity = []
        for completion in recent_completions:
            activity.append(
                {
                    "type": "lesson_completed",
                    "student_name": completion.enrollment.student.user.get_full_name(),
                    "lesson_title": completion.lesson.title,
                    "completed_at": completion.completed_at,
                    "progress": completion.enrollment.progress_percentage,
                }
            )

        return activity

    # -------------------------------------------------------------------------
    # Batch Operations
    # -------------------------------------------------------------------------

    def bulk_enroll_students(
        self,
        course_id: int,
        student_ids: List[int],
        enrollment_date: timezone.datetime = None,
        created_by: User = None,
    ) -> Dict[str, Any]:
        """
        Enroll multiple students in a course at once.

        Args:
            course_id: Course ID
            student_ids: List of student profile IDs
            enrollment_date: Date of enrollment
            created_by: User who created the enrollments

        Returns:
            Dictionary with results
        """
        from django.db import IntegrityError

        if not enrollment_date:
            enrollment_date = timezone.now()

        results = {
            "successful": [],
            "failed": [],
            "already_enrolled": [],
            "total_attempted": len(student_ids),
        }

        with transaction.atomic():
            for student_id in student_ids:
                try:
                    # Check if already enrolled
                    existing = self.filter(
                        course_id=course_id, student_id=student_id, is_active=True
                    ).exists()

                    if existing:
                        results["already_enrolled"].append(student_id)
                        continue

                    # Create enrollment
                    enrollment = self.create(
                        course_id=course_id,
                        student_id=student_id,
                        enrolled_at=enrollment_date,
                        is_active=True,
                        payment_status="completed",  # Assuming batch enrollments are free/completed
                        amount_paid=0.00,
                        created_by=created_by,
                    )

                    results["successful"].append(
                        {
                            "student_id": student_id,
                            "enrollment_id": enrollment.id,
                        }
                    )

                except IntegrityError as e:
                    results["failed"].append({"student_id": student_id, "error": str(e)})
                except Exception as e:
                    results["failed"].append({"student_id": student_id, "error": str(e)})

        # Update course enrollment count
        try:
            course = Course.objects.get(id=course_id)
            course.enrolled_count = F("enrolled_count") + len(results["successful"])
            course.save(update_fields=["enrolled_count"])
        except Course.DoesNotExist:
            pass

        # Invalidate caches
        self._invalidate_course_enrollment_cache(course_id)

        return results

    def bulk_update_enrollment_progress(
        self,
        enrollment_ids: List[int],
        progress_increment: float = None,
        time_spent_minutes: int = None,
    ) -> Dict[str, Any]:
        """
        Bulk update progress for multiple enrollments.

        Args:
            enrollment_ids: List of enrollment IDs
            progress_increment: Progress to add (percentage)
            time_spent_minutes: Time to add (minutes)

        Returns:
            Dictionary with results
        """
        results = {
            "updated": 0,
            "failed": 0,
            "completed": 0,
        }

        with transaction.atomic():
            for enrollment_id in enrollment_ids:
                try:
                    enrollment = self.get(id=enrollment_id)

                    # Update progress
                    if progress_increment:
                        new_progress = min(100, enrollment.progress_percentage + progress_increment)
                        enrollment.progress_percentage = new_progress

                        # Check for completion
                        if new_progress >= 100 and not enrollment.completed_at:
                            enrollment.completed_at = timezone.now()
                            enrollment.certificate_issued = True
                            results["completed"] += 1

                    # Update time spent
                    if time_spent_minutes:
                        enrollment.total_time_spent_minutes = (
                            enrollment.total_time_spent_minutes + time_spent_minutes
                        )
                        enrollment.last_accessed_at = timezone.now()

                    enrollment.save()
                    results["updated"] += 1

                    # Invalidate cache for this enrollment
                    self.invalidate_cache_for_enrollment(enrollment_id)

                except Exception as e:
                    logger.error(f"Failed to update enrollment {enrollment_id}: {e}")
                    results["failed"] += 1

        return results

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def get_enrollment_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get enrollment summary for user dashboard.

        Args:
            user_id: User ID

        Returns:
            Summary dictionary
        """
        cache_key = f"{self.CACHE_PREFIX}:summary:{user_id}"

        summary = cache.get(cache_key)
        if summary is not None:
            return summary

        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return {}

        # Get active enrollments
        active_enrollments = (
            self.filter(student=profile, is_active=True, completed_at__isnull=True)
            .select_related("course")
            .order_by("-last_accessed_at")[:5]
        )

        # Get recent completions
        recent_completions = (
            self.filter(student=profile, is_active=True, completed_at__isnull=False)
            .select_related("course")
            .order_by("-completed_at")[:3]
        )

        # Get upcoming deadlines
        upcoming_deadlines = self._get_upcoming_deadlines(profile)

        # Get learning streak
        streak = self._calculate_learning_streak(profile)

        summary = {
            "active_enrollments": [
                {
                    "course_id": e.course_id,
                    "course_title": e.course.title,
                    "progress": e.progress_percentage,
                    "last_accessed": e.last_accessed_at,
                }
                for e in active_enrollments
            ],
            "recent_completions": [
                {
                    "course_id": e.course_id,
                    "course_title": e.course.title,
                    "completed_at": e.completed_at,
                    "certificate_issued": e.certificate_issued,
                }
                for e in recent_completions
            ],
            "upcoming_deadlines": upcoming_deadlines,
            "learning_streak": streak,
            "total_active": self.filter(
                student=profile, is_active=True, completed_at__isnull=True
            ).count(),
            "total_completed": self.filter(
                student=profile, is_active=True, completed_at__isnull=False
            ).count(),
        }

        cache.set(cache_key, summary, timeout=1800)  # 30 minutes
        return summary

    def _get_upcoming_deadlines(self, profile: Profile) -> List[Dict[str, Any]]:
        """Get upcoming deadlines for user's enrollments."""
        deadlines = []
        today = timezone.now().date()

        # Get enrollments with deadlines in next 7 days
        upcoming = (
            self.filter(
                student=profile,
                is_active=True,
                completed_at__isnull=True,
                course__end_date__gte=today,
                course__end_date__lte=today + timedelta(days=7),
            )
            .select_related("course")
            .order_by("course__end_date")
        )

        for enrollment in upcoming:
            days_left = (enrollment.course.end_date - today).days
            deadlines.append(
                {
                    "course_id": enrollment.course_id,
                    "course_title": enrollment.course.title,
                    "deadline": enrollment.course.end_date,
                    "days_left": days_left,
                    "progress": enrollment.progress_percentage,
                }
            )

        return deadlines

    def invalidate_user_enrollment_cache(self, user_id: int) -> None:
        """Invalidate all enrollment caches for a user."""
        cache_keys = [
            f"{self.CACHE_PREFIX}:user:{user_id}:*",
            f"{self.CACHE_PREFIX}:summary:{user_id}",
        ]

        # This is a simplified approach - in production, you'd use Redis pattern deletion
        for key in cache_keys:
            cache.delete(key)

    def _invalidate_course_enrollment_cache(self, course_id: int) -> None:
        """Invalidate enrollment caches for a course."""
        cache_keys = [
            f"{self.CACHE_PREFIX}:course:{course_id}:*",
        ]

        for key in cache_keys:
            cache.delete(key)
