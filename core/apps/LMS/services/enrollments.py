"""
Enrollment Service with comprehensive operations for views.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models, transaction
from django.db.models import F, Q
from django.db.models.aggregates import Avg, Count
from django.utils import timezone

from apps import logger
from django_grep.pipelines.services import BaseService, TokenService

from ..managers import EnrollmentsManager
from ..models import Course, Enrollment, Lesson, LessonProgress, ModuleProgress

User = get_user_model()


Profile = apps.get_model(settings.PROFILE_MODEL)


class EnrollmentService(BaseService):
    """
    service layer for Enrollment operations with view-specific methods.
    """

    model_class = Enrollment
    default_filter_field = "id"
    enable_cache = True
    cache_timeout = 1800
    cache_key_prefix = "enrollment_service"

    # Define which fields require token protection
    SENSITIVE_FIELDS = [
        "payment_status",
        "amount_paid",
        "payment_id",
        "completed_at",
        "certificate_issued",
    ]

    # -------------------------------------------------------------------------
    # User Dashboard Methods
    # -------------------------------------------------------------------------

    @classmethod
    def get_user_learning_dashboard(
        cls,
        user_id: int,
        time_period: str = "weekly",  # weekly, monthly, yearly
        include_recommendations: bool = True,
    ) -> Dict[str, Any]:
        """
        Get comprehensive learning dashboard data for user.

        Args:
            user_id: User ID
            time_period: Time period for analytics
            include_recommendations: Include course recommendations

        Returns:
            Dictionary with dashboard data
        """
        cache_key = f"{cls.cache_key_prefix}:dashboard:{user_id}:{time_period}"

        dashboard = cache.get(cache_key)
        if dashboard is not None:
            return {**dashboard, "from_cache": True}

        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return {"error": "Profile not found", "success": False}

        # Get enrollment summary
        enrollment_summary = EnrollmentsManager().get_enrollment_summary(user_id)

        # Get learning analytics
        learning_analytics = cls._get_learning_analytics(profile, time_period)

        # Get active courses with progress
        active_courses = cls._get_active_courses_with_progress(profile)

        # Get completion timeline
        completion_timeline = cls._get_completion_timeline(profile, time_period)

        # Get learning habits
        learning_habits = cls._get_learning_habits(profile)

        # Get recommendations if requested
        recommendations = []
        if include_recommendations:
            recommendations = cls._get_course_recommendations(profile)

        dashboard = {
            "success": True,
            "user_id": user_id,
            "time_period": time_period,
            "summary": enrollment_summary,
            "analytics": learning_analytics,
            "active_courses": active_courses,
            "completion_timeline": completion_timeline,
            "learning_habits": learning_habits,
            "recommendations": recommendations,
            "last_updated": timezone.now(),
        }

        cache.set(cache_key, dashboard, timeout=cls.cache_timeout)
        return {**dashboard, "from_cache": False}

    @classmethod
    def _get_learning_analytics(cls, profile: Profile, time_period: str) -> Dict[str, Any]:
        """Get learning analytics for the specified time period."""
        from django.db.models import Avg, Count, Sum
        from django.db.models.functions import TruncDate

        # Calculate time range
        if time_period == "weekly":
            days = 7
        elif time_period == "monthly":
            days = 30
        else:  # yearly
            days = 365

        start_date = timezone.now() - timezone.timedelta(days=days)

        # Get enrollments in time period
        enrollments = Enrollment.objects.filter(
            student=profile, enrolled_at__gte=start_date, is_active=True
        )

        # Calculate metrics
        metrics = enrollments.aggregate(
            total_courses_started=Count("id"),
            total_courses_completed=Count("id", filter=Q(completed_at__isnull=False)),
            total_learning_hours=Sum("total_time_spent_minutes"),
            avg_progress=Avg("progress_percentage", filter=Q(completed_at__isnull=True)),
            avg_completion_time=Avg(
                models.F("completed_at") - models.F("enrolled_at"),
                filter=Q(completed_at__isnull=False),
            ),
        )

        # Daily learning activity
        daily_activity = list(
            enrollments.annotate(date=TruncDate("last_accessed_at"))
            .values("date")
            .annotate(
                learning_minutes=Sum("total_time_spent_minutes"),
                active_courses=Count("id", distinct=True),
            )
            .order_by("-date")[:days]
        )

        # Progress over time
        progress_timeline = list(
            enrollments.annotate(week=TruncDate("last_accessed_at"))
            .values("week")
            .annotate(avg_progress=Avg("progress_percentage"))
            .order_by("week")[-30:]  # Last 30 data points
        )

        return {
            "time_period_days": days,
            "courses_started": metrics["total_courses_started"] or 0,
            "courses_completed": metrics["total_courses_completed"] or 0,
            "total_learning_hours": round((metrics["total_learning_hours"] or 0) / 60, 1),
            "average_progress": round(metrics["avg_progress"] or 0, 1),
            "average_completion_days": (
                metrics["avg_completion_time"].days if metrics["avg_completion_time"] else 0
            ),
            "daily_activity": daily_activity,
            "progress_timeline": progress_timeline,
            "completion_rate": (
                (metrics["total_courses_completed"] / metrics["total_courses_started"] * 100)
                if metrics["total_courses_started"]
                else 0
            ),
        }

    @classmethod
    def _get_active_courses_with_progress(cls, profile: Profile) -> List[Dict[str, Any]]:
        """Get active courses with detailed progress information."""
        enrollments = (
            Enrollment.objects.filter(student=profile, is_active=True, completed_at__isnull=True)
            .select_related("course", "course__instructor")
            .order_by("-last_accessed_at")
        )

        courses = []
        for enrollment in enrollments:
            course = enrollment.course

            # Get next lesson
            next_lesson = cls._get_next_lesson_for_enrollment(enrollment)

            # Get estimated completion date
            estimated_completion = cls._estimate_completion_date(enrollment)

            # Get time spent
            time_spent_hours = round(enrollment.total_time_spent_minutes / 60, 1)

            courses.append(
                {
                    "enrollment_id": enrollment.id,
                    "course_id": course.id,
                    "title": course.title,
                    "slug": course.slug,
                    "instructor_name": course.instructor.get_full_name()
                    if course.instructor
                    else "Unknown",
                    "difficulty": course.difficulty_level,
                    "thumbnail": course.thumbnail.url if course.thumbnail else None,
                    "progress_percentage": enrollment.progress_percentage,
                    "last_accessed": enrollment.last_accessed_at,
                    "enrolled_at": enrollment.enrolled_at,
                    "next_lesson": next_lesson,
                    "estimated_completion": estimated_completion,
                    "time_spent_hours": time_spent_hours,
                    "total_modules": course.modules.count(),
                    "total_lessons": getattr(course, "total_lessons", 0),
                    "completed_lessons": enrollment.completed_lessons_count or 0,
                    "is_behind_schedule": cls._is_behind_schedule(enrollment),
                    "priority_score": cls._calculate_course_priority(enrollment),
                }
            )

        return courses

    @classmethod
    def _get_next_lesson_for_enrollment(cls, enrollment: Enrollment) -> Optional[Dict[str, Any]]:
        """Get next lesson for enrollment."""
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
                    "duration_minutes": getattr(next_lesson, "duration_minutes", 0),
                    "lesson_type": getattr(next_lesson, "lesson_type", "video"),
                }
        except Exception as e:
            logger.error(f"Error getting next lesson: {e}")

        return None

    @classmethod
    def _estimate_completion_date(cls, enrollment: Enrollment) -> Optional[timezone.datetime]:
        """Estimate completion date based on learning pace."""
        if enrollment.progress_percentage >= 100:
            return enrollment.completed_at

        # Calculate average daily progress
        days_enrolled = (timezone.now() - enrollment.enrolled_at).days
        if days_enrolled <= 0:
            return None

        daily_progress = enrollment.progress_percentage / days_enrolled
        if daily_progress <= 0:
            return None

        # Estimate days remaining
        remaining_progress = 100 - enrollment.progress_percentage
        days_remaining = remaining_progress / daily_progress

        return timezone.now() + timezone.timedelta(days=days_remaining)

    @classmethod
    def _is_behind_schedule(cls, enrollment: Enrollment) -> bool:
        """Check if user is behind schedule in course."""
        if enrollment.course.end_date:
            days_remaining = (enrollment.course.end_date - timezone.now().date()).days
            if days_remaining < 0:
                return True

            # Calculate required daily progress
            required_daily_progress = (100 - enrollment.progress_percentage) / days_remaining
            current_daily_progress = enrollment.progress_percentage / (
                (timezone.now() - enrollment.enrolled_at).days or 1
            )

            return current_daily_progress < required_daily_progress * 0.7  # 30% buffer

        return False

    @classmethod
    def _calculate_course_priority(cls, enrollment: Enrollment) -> float:
        """Calculate priority score for course (0-100)."""
        score = 0

        # Progress-based priority (lower progress = higher priority)
        progress_priority = 100 - enrollment.progress_percentage
        score += progress_priority * 0.4

        # Deadline-based priority
        if enrollment.course.end_date:
            days_remaining = (enrollment.course.end_date - timezone.now().date()).days
            if days_remaining <= 7:
                score += 30
            elif days_remaining <= 14:
                score += 20
            elif days_remaining <= 30:
                score += 10

        # Recency-based priority (recently accessed = lower priority)
        days_since_access = (timezone.now() - enrollment.last_accessed_at).days
        if days_since_access <= 1:
            score -= 20
        elif days_since_access >= 7:
            score += 20

        # Course difficulty adjustment
        difficulty_weights = {
            "beginner": 0,
            "intermediate": 10,
            "advanced": 20,
            "expert": 30,
        }
        score += difficulty_weights.get(enrollment.course.difficulty_level, 0)

        return min(100, max(0, score))

    @classmethod
    def _get_completion_timeline(cls, profile: Profile, time_period: str) -> List[Dict[str, Any]]:
        """Get course completion timeline."""
        from django.db.models.functions import TruncMonth, TruncWeek

        if time_period == "weekly":
            trunc_func = TruncWeek
        else:  # monthly
            trunc_func = TruncMonth

        completions = Enrollment.objects.filter(
            student=profile, is_active=True, completed_at__isnull=False
        ).annotate(period=trunc_func("completed_at"))

        timeline = list(
            completions.values("period")
            .annotate(
                count=Count("id"),
                avg_completion_days=Avg(models.F("completed_at") - models.F("enrolled_at")),
            )
            .order_by("period")[-12:]  # Last 12 periods
        )

        return timeline

    @classmethod
    def _get_learning_habits(cls, profile: Profile) -> Dict[str, Any]:
        """Analyze user's learning habits."""
        from django.db.models import Count
        from django.db.models.functions import ExtractHour, ExtractWeekDay

        # Get all learning sessions (simplified - using enrollment last_accessed)
        sessions = Enrollment.objects.filter(student=profile, last_accessed_at__isnull=False)

        # Preferred learning time
        preferred_hours = list(
            sessions.annotate(hour=ExtractHour("last_accessed_at"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )

        # Preferred learning days
        preferred_days = list(
            sessions.annotate(day=ExtractWeekDay("last_accessed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Average session length
        avg_session_minutes = (
            sessions.aggregate(avg=Avg("total_time_spent_minutes") / Count("id"))["avg"] or 0
        )

        # Consistency score (days with learning / total days enrolled)
        total_days = (timezone.now().date() - profile.created_at.date()).days
        active_days = sessions.dates("last_accessed_at", "day").distinct().count()
        consistency_score = (active_days / total_days * 100) if total_days > 0 else 0

        return {
            "preferred_hours": preferred_hours,
            "preferred_days": preferred_days,
            "average_session_minutes": round(avg_session_minutes, 1),
            "consistency_score": round(consistency_score, 1),
            "active_days": active_days,
            "total_days_tracked": total_days,
        }

    @classmethod
    def _get_course_recommendations(cls, profile: Profile) -> List[Dict[str, Any]]:
        """Get personalized course recommendations for user."""
        from ..managers.course_manager import CourseCacheManager

        # Get user's completed courses
        completed_courses = Enrollment.objects.filter( 
            student=profile, is_active=True, completed_at__isnull=False
        ).values_list("course_id", flat=True)

        # Get user's enrolled courses (to avoid recommending already enrolled)
        enrolled_courses = Enrollment.objects.filter(student=profile, is_active=True).values_list(
            "course_id", flat=True
        )

        # Get popular courses in user's completed categories
        # This is a simplified recommendation algorithm
        recommendations = CourseCacheManager.get_featured_courses_cached(
            limit=5, include_related=True
        )

        # Filter out already enrolled/completed courses
        filtered_recs = []
        for course in recommendations:
            if course.id not in enrolled_courses:
                filtered_recs.append(
                    {
                        "id": course.id,
                        "title": course.title,
                        "slug": course.slug,
                        "description": course.short_description,
                        "instructor": course.instructor.get_full_name()
                        if course.instructor
                        else None,
                        "difficulty": course.difficulty_level,
                        "rating": course.average_rating,
                        "enrollment_count": course.enrolled_count,
                        "thumbnail": course.thumbnail.url if course.thumbnail else None,
                        "relevance_score": cls._calculate_relevance_score(course, profile),
                    }
                )

        # Sort by relevance score
        filtered_recs.sort(key=lambda x: x["relevance_score"], reverse=True)

        return filtered_recs[:3]  # Return top 3 recommendations

    @classmethod
    def _calculate_relevance_score(cls, course, profile: Profile) -> float:
        """Calculate relevance score for course recommendation."""
        score = 0

        # Based on user's completed courses
        completed_courses = Enrollment.objects.filter(
            student=profile, completed_at__isnull=False
        ).select_related("course")

        # Check if user has completed similar courses
        for completed in completed_courses:
            if completed.course.difficulty_level == course.difficulty_level:
                score += 20
            if completed.course.category == course.category:
                score += 30

        # Popularity boost
        if course.enrolled_count > 1000:
            score += 15
        elif course.enrolled_count > 100:
            score += 10

        # Rating boost
        if course.average_rating >= 4.5:
            score += 20
        elif course.average_rating >= 4.0:
            score += 10

        return score

    # -------------------------------------------------------------------------
    # Course Progress Management
    # -------------------------------------------------------------------------

    @classmethod
    def update_course_progress(
        cls,
        enrollment_id: int,
        lesson_id: int,
        progress_data: Dict[str, Any],
        token: str = None, 
        user_id: int = None,
    ) -> Dict[str, Any]:
        """
        Update course progress after completing a lesson.

        Args:
            enrollment_id: Enrollment ID
            lesson_id: Lesson ID
            progress_data: Progress data including time_spent, score, etc.
            token: Verification token
            user_id: User ID performing the update

        Returns:
            Dictionary with update results
        """
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)

            # Verify user owns the enrollment
            if user_id and enrollment.student.user_id != user_id:
                return {
                    "success": False,
                    "error": "You don't have permission to update this enrollment",
                    "code": "PERMISSION_DENIED",
                }

            # Get or create lesson progress
            lesson_progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson_id=lesson_id,
                defaults={
                    "is_completed": True,
                    "completed_at": timezone.now(),
                    "time_spent_minutes": progress_data.get("time_spent_minutes", 0),
                    "score": progress_data.get("score"),
                    "attempts": 1,
                },
            )

            if not created:
                # Update existing progress
                lesson_progress.is_completed = True
                lesson_progress.completed_at = timezone.now()
                lesson_progress.time_spent_minutes += progress_data.get("time_spent_minutes", 0)
                if "score" in progress_data:
                    lesson_progress.score = max(lesson_progress.score or 0, progress_data["score"])
                    lesson_progress.attempts += 1
                lesson_progress.save()

            # Update module progress
            module_id = Lesson.objects.get(id=lesson_id).module_id
            cls._update_module_progress(enrollment, module_id)

            # Update course progress
            cls._update_course_overall_progress(enrollment)

            # Check if course is completed
            if enrollment.progress_percentage >= 100 and not enrollment.completed_at:
                enrollment.completed_at = timezone.now()
                enrollment.certificate_issued = True
                enrollment.save()

                # Generate certificate
                cls._generate_certificate(enrollment)

            # Update last accessed time
            enrollment.last_accessed_at = timezone.now()
            enrollment.total_time_spent_minutes += progress_data.get("time_spent_minutes", 0)
            enrollment.save()

            # Get next lesson information
            next_lesson = cls._get_next_lesson_for_enrollment(enrollment)

            # Invalidate caches
            cls._invalidate_enrollment_caches(
                enrollment.id, enrollment.student.user_id, enrollment.course_id
            )

            return {
                "success": True,
                "message": "Progress updated successfully",
                "enrollment_id": enrollment.id,
                "progress_percentage": enrollment.progress_percentage,
                "is_course_completed": enrollment.completed_at is not None,
                "next_lesson": next_lesson,
                "certificate_issued": enrollment.certificate_issued,
            }

        except Enrollment.DoesNotExist:
            return {
                "success": False,
                "error": "Enrollment not found",
                "code": "ENROLLMENT_NOT_FOUND",
            }
        except Exception as e:
            logger.error(f"Error updating course progress: {e}")
            return {
                "success": False,
                "error": f"Error updating progress: {str(e)}",
                "code": "PROGRESS_UPDATE_FAILED",
            }

    @classmethod
    def _update_module_progress(cls, enrollment: Enrollment, module_id: int):
        """Update progress for a specific module."""
        # Get all lessons in module
        lessons = Lesson.objects.filter(module_id=module_id)
        total_lessons = lessons.count()

        # Get completed lessons in module
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment, lesson__module_id=module_id, is_completed=True
        ).count()

        # Calculate module progress percentage
        module_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        # Update or create module progress record
        ModuleProgress.objects.update_or_create(
            enrollment=enrollment,
            module_id=module_id,
            defaults={
                "progress_percentage": module_progress,
                "is_completed": module_progress >= 100,
                "completed_at": timezone.now() if module_progress >= 100 else None,
                "last_accessed_at": timezone.now(),
            },
        )

    @classmethod
    def _update_course_overall_progress(cls, enrollment: Enrollment):
        """Update overall course progress."""
        # Get total lessons in course
        total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()

        # Get completed lessons in course
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment, is_completed=True
        ).count()

        # Calculate overall progress
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        # Update enrollment
        enrollment.progress_percentage = progress_percentage
        enrollment.completed_lessons_count = completed_lessons
        enrollment.save(update_fields=["progress_percentage", "completed_lessons_count"])

    @classmethod
    def _generate_certificate(cls, enrollment: Enrollment):
        """Generate certificate for course completion."""
        # This would integrate with your certificate generation service
        # For now, just update the enrollment
        enrollment.certificate_issued = True
        enrollment.certificate_url = f"/certificates/{enrollment.id}/download/"
        enrollment.save(update_fields=["certificate_issued", "certificate_url"])

    # -------------------------------------------------------------------------
    # Bulk Operations
    # -------------------------------------------------------------------------

    @classmethod
    def enroll_user_in_multiple_courses(
        cls,
        user_id: int,
        course_ids: List[int],
        payment_status: str = "pending",
        created_by: User = None,
    ) -> Dict[str, Any]:
        """
        Enroll user in multiple courses at once.

        Args:
            user_id: User ID
            course_ids: List of course IDs
            payment_status: Initial payment status
            created_by: User who created the enrollments

        Returns:
            Dictionary with results
        """
        results = {
            "successful": [],
            "failed": [],
            "already_enrolled": [],
            "total_attempted": len(course_ids),
        }

        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return {
                "success": False,
                "error": "User profile not found",
                "code": "PROFILE_NOT_FOUND",
            }

        with transaction.atomic():
            for course_id in course_ids:
                try:
                    # Check if already enrolled
                    existing = Enrollment.objects.filter(
                        student=profile, course_id=course_id, is_active=True
                    ).exists()

                    if existing:
                        results["already_enrolled"].append(course_id)
                        continue

                    # Create enrollment
                    enrollment = Enrollment.objects.create(
                        student=profile,
                        course_id=course_id,
                        payment_status=payment_status,
                        amount_paid=0.00,
                        is_active=True,
                        enrolled_at=timezone.now(),
                        created_by=created_by,
                    )

                    # Update course enrollment count
                    Course.objects.filter(id=course_id).update(
                        enrolled_count=F("enrolled_count") + 1
                    )

                    results["successful"].append(
                        {
                            "course_id": course_id,
                            "enrollment_id": enrollment.id,
                        }
                    )

                except Exception as e:
                    results["failed"].append({"course_id": course_id, "error": str(e)})

        # Invalidate caches
        for course_id in course_ids:
            EnrollmentsManager()._invalidate_course_enrollment_cache(course_id)
        EnrollmentsManager().invalidate_user_enrollment_cache(user_id)

        return {
            "success": True,
            "results": results,
            "total_successful": len(results["successful"]),
            "total_failed": len(results["failed"]),
            "total_already_enrolled": len(results["already_enrolled"]),
        }

    @classmethod
    def sync_enrollment_progress_from_external(
        cls, user_id: int, course_id: int, external_progress_data: Dict[str, Any], token: str
    ) -> Dict[str, Any]:
        """
        Sync enrollment progress from external learning platform.

        Args:
            user_id: User ID
            course_id: Course ID
            external_progress_data: Progress data from external platform
            token: Verification token

        Returns:
            Sync results
        """
        # Validate token
        validation_result = TokenService.validate_action_token(
            token, expected_action="sync_external_progress"
        )

        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result.get("error", "Token validation failed"),
                "code": validation_result.get("code", "TOKEN_INVALID"),
            }

        try:
            enrollment = Enrollment.objects.get(
                student__user_id=user_id, course_id=course_id, is_active=True
            )
        except Enrollment.DoesNotExist:
            return {
                "success": False,
                "error": "Enrollment not found",
                "code": "ENROLLMENT_NOT_FOUND",
            }

        with transaction.atomic():
            # Update overall progress
            external_progress = external_progress_data.get("progress_percentage", 0)
            if external_progress > enrollment.progress_percentage:
                enrollment.progress_percentage = external_progress
                enrollment.last_accessed_at = timezone.now()

                # Check if completed externally
                if external_progress >= 100 and not enrollment.completed_at:
                    enrollment.completed_at = timezone.now()
                    enrollment.certificate_issued = True

                enrollment.save()

            # Sync individual lessons if provided
            if "completed_lessons" in external_progress_data:
                for lesson_data in external_progress_data["completed_lessons"]:
                    LessonProgress.objects.update_or_create(
                        enrollment=enrollment,
                        lesson_id=lesson_data["lesson_id"],
                        defaults={
                            "is_completed": True,
                            "completed_at": lesson_data.get("completed_at") or timezone.now(),
                            "time_spent_minutes": lesson_data.get("time_spent_minutes", 0),
                            "score": lesson_data.get("score"),
                        },
                    )

        # Invalidate caches
        cls._invalidate_enrollment_caches(enrollment.id, user_id, course_id)

        return {
            "success": True,
            "message": "Progress synced successfully",
            "enrollment_id": enrollment.id,
            "progress_percentage": enrollment.progress_percentage,
            "synced_lessons": len(external_progress_data.get("completed_lessons", [])),
        }

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    @classmethod
    def get_enrollment_certificate_info(
        cls, enrollment_id: int, user_id: int = None
    ) -> Dict[str, Any]:
        """
        Get certificate information for an enrollment.

        Args:
            enrollment_id: Enrollment ID
            user_id: Optional user ID for verification

        Returns:
            Certificate information
        """
        try:
            enrollment = Enrollment.objects.select_related(
                "student", "student__user", "course", "course__instructor"
            ).get(id=enrollment_id)

            # Verify ownership if user_id provided
            if user_id and enrollment.student.user_id != user_id:
                return {
                    "success": False,
                    "error": "You don't have permission to view this certificate",
                    "code": "PERMISSION_DENIED",
                }

            if not enrollment.certificate_issued:
                return {
                    "success": False,
                    "error": "Certificate not issued for this enrollment",
                    "code": "CERTIFICATE_NOT_ISSUED",
                }

            # Get completion details
            completion_days = (enrollment.completed_at - enrollment.enrolled_at).days

            # Get course details
            course = enrollment.course

            return {
                "success": True,
                "certificate_info": {
                    "enrollment_id": enrollment.id,
                    "certificate_url": enrollment.certificate_url,
                    "issued_at": enrollment.completed_at,
                    "valid_until": enrollment.completed_at
                    + timezone.timedelta(days=365),  # 1 year validity
                    "student_name": enrollment.student.user.get_full_name(),
                    "student_email": enrollment.student.user.email,
                    "course_title": course.title,
                    "course_difficulty": course.difficulty_level,
                    "course_duration": getattr(course, "total_duration_hours", 0),
                    "instructor_name": course.instructor.get_full_name()
                    if course.instructor
                    else None,
                    "completion_days": completion_days,
                    "final_score": enrollment.final_score or "N/A",
                    "certificate_id": f"CERT-{enrollment.id.hex[:8].upper()}",
                },
            }

        except Enrollment.DoesNotExist:
            return {
                "success": False,
                "error": "Enrollment not found",
                "code": "ENROLLMENT_NOT_FOUND",
            }

    @classmethod
    def validate_enrollment_for_access(
        cls, user_id: int, course_id: int, lesson_id: int = None
    ) -> Dict[str, Any]:
        """
        Validate if user has access to course/lesson.

        Args:
            user_id: User ID
            course_id: Course ID
            lesson_id: Optional lesson ID

        Returns:
            Validation result
        """
        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return {
                "has_access": False,
                "reason": "User profile not found",
                "code": "PROFILE_NOT_FOUND",
            }

        # Check enrollment
        enrollment = Enrollment.objects.filter(
            student=profile, course_id=course_id, is_active=True
        ).first()

        if not enrollment:
            return {
                "has_access": False,
                "reason": "Not enrolled in this course",
                "code": "NOT_ENROLLED",
            }

        # Check if course is active
        course = enrollment.course
        if not course.is_published or not course.is_active:
            return {
                "has_access": False,
                "reason": "Course is not available",
                "code": "COURSE_INACTIVE",
            }

        result = {
            "has_access": True,
            "enrollment_id": enrollment.id,
            "progress_percentage": enrollment.progress_percentage,
            "is_completed": enrollment.completed_at is not None,
        }

        # If lesson_id provided, check lesson access
        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id, module__course_id=course_id)

                # Check if lesson is available (not locked)
                is_lesson_available = cls._check_lesson_availability(enrollment, lesson)

                result.update(
                    {
                        "lesson_available": is_lesson_available,
                        "lesson_title": lesson.title,
                        "lesson_type": getattr(lesson, "lesson_type", "video"),
                    }
                )

                if not is_lesson_available:
                    result["has_access"] = False
                    result["reason"] = "Lesson is locked"
                    result["code"] = "LESSON_LOCKED"

            except Lesson.DoesNotExist:
                result.update(
                    {
                        "has_access": False,
                        "reason": "Lesson not found",
                        "code": "LESSON_NOT_FOUND",
                    }
                )

        return result

    @classmethod
    def _check_lesson_availability(cls, enrollment: Enrollment, lesson: Lesson) -> bool:
        """Check if a lesson is available for the user."""
        # Check if lesson is active
        if not getattr(lesson, "is_active", True):
            return False

        # If course is completed, all lessons are available
        if enrollment.completed_at:
            return True

        # Check lesson prerequisites
        if hasattr(lesson, "prerequisites"):
            for prereq in lesson.prerequisites.all():
                try:
                    prereq_progress = LessonProgress.objects.get(
                        enrollment=enrollment, lesson=prereq
                    )
                    if not prereq_progress.is_completed:
                        return False
                except LessonProgress.DoesNotExist:
                    return False

        return True

    @classmethod
    def _invalidate_enrollment_caches(cls, enrollment_id: int, user_id: int, course_id: int):
        """Invalidate all relevant caches for an enrollment."""
        # Invalidate manager caches
        EnrollmentsManager().invalidate_cache_for_enrollment(enrollment_id)
        EnrollmentsManager().invalidate_user_enrollment_cache(user_id)
        EnrollmentsManager()._invalidate_course_enrollment_cache(course_id)

        # Invalidate service caches
        cache_keys = [
            f"{cls.cache_key_prefix}:dashboard:{user_id}:*",
            f"{cls.cache_key_prefix}:summary:{user_id}",
            f"{cls.cache_key_prefix}:progress:{enrollment_id}",
        ]

        for key in cache_keys:
            cache.delete(key)
