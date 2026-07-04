"""
Progress Manager for handling progress updates on lessons and modules.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models, transaction
from django.utils import timezone
from django_osoul.core.managers import BaseManager

logger = logging.getLogger(__name__)
User = get_user_model()


class ProgressManager(BaseManager):
    """
    Unified manager for handling all progress-related operations.
    """

    def __init__(self):
        """Initialize with references to all progress models."""
        from ..models import Enrollment, LessonProgress, ModuleProgress

        self.lesson_progress_model = LessonProgress
        self.module_progress_model = ModuleProgress
        self.enrollment_model = Enrollment

    def update_lesson_progress(
        self, user: User, lesson_id: int, progress_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update progress for a specific lesson.

        Args:
            user: User object
            lesson_id: Lesson ID
            progress_data: Dictionary with progress information

        Returns:
            Tuple of (success, result_data)
        """
        try:
            from plugins.lms.models import Lesson

            lesson = Lesson.objects.select_related("module", "module__course").get(id=lesson_id)

            # Get or create enrollment
            enrollment = self._get_enrollment_for_course(user, lesson.module.course)
            if not enrollment:
                return False, {"error": "Enrollment not found"}

            with transaction.atomic():
                # Update lesson progress
                lesson_progress = self._update_or_create_lesson_progress(
                    user, lesson, enrollment, progress_data
                )

                # Update module progress
                module_progress = self._update_module_progress_from_lesson(
                    enrollment, lesson.module, progress_data
                )

                # Update course progress
                course_progress = self._update_course_progress_from_lesson(enrollment)

                # Check if module is completed
                module_completed = self._check_module_completion(enrollment, lesson.module)

                # Check if course is completed
                course_completed = self._check_course_completion(enrollment)

                # Invalidate caches
                self._invalidate_progress_caches(user.id, enrollment.id, lesson.module.course_id)

                result = {
                    "success": True,
                    "lesson_progress": {
                        "id": lesson_progress.id,
                        "progress": lesson_progress.progress,
                        "status": lesson_progress.status,
                        "time_spent": lesson_progress.time_spent.total_seconds() / 60,
                        "score": lesson_progress.score,
                    },
                    "module_progress": {
                        "module_id": lesson.module_id,
                        "progress_percentage": module_progress.progress_percentage,
                        "status": module_progress.status,
                        "is_completed": module_completed,
                    },
                    "course_progress": {
                        "enrollment_id": enrollment.id,
                        "progress_percentage": enrollment.progress_percentage,
                        "is_completed": course_completed,
                    },
                    "next_lesson": self._get_next_lesson(lesson, enrollment),
                }

                return True, result

        except Exception as e:
            logger.error(f"Error updating lesson progress: {e}")
            return False, {"error": str(e)}

    def update_module_progress(
        self, user: User, module_id: int, progress_percentage: float, time_spent_minutes: float = 0
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update progress for a specific module directly.

        Args:
            user: User object
            module_id: Module ID
            progress_percentage: Progress percentage (0-100)
            time_spent_minutes: Time spent in minutes

        Returns:
            Tuple of (success, result_data)
        """
        try:
            from ..models import Module

            module = Module.objects.select_related("course").get(id=module_id)

            # Get or create enrollment
            enrollment = self._get_enrollment_for_course(user, module.course)
            if not enrollment:
                return False, {"error": "Enrollment not found"}

            with transaction.atomic():
                # Update module progress
                module_progress = self._update_or_create_module_progress(
                    enrollment, module, progress_percentage, time_spent_minutes
                )

                # Update all lesson progress in module if marked as completed
                if progress_percentage >= 100:
                    self._mark_lessons_completed(enrollment, module)

                # Update course progress
                course_progress = self._update_course_progress_from_module(enrollment)

                # Check if course is completed
                course_completed = self._check_course_completion(enrollment)

                # Invalidate caches
                self._invalidate_progress_caches(user.id, enrollment.id, module.course_id)

                result = {
                    "success": True,
                    "module_progress": {
                        "module_id": module.id,
                        "progress_percentage": module_progress.progress_percentage,
                        "status": module_progress.status,
                        "time_spent_minutes": module_progress.time_spent_minutes,
                    },
                    "course_progress": {
                        "enrollment_id": enrollment.id,
                        "progress_percentage": enrollment.progress_percentage,
                        "is_completed": course_completed,
                    },
                }

                return True, result

        except Exception as e:
            logger.error(f"Error updating module progress: {e}")
            return False, {"error": str(e)}

    def _get_enrollment_for_course(self, user: User, course) -> Optional[models.Model]:
        """Get or create enrollment for user in course."""
        enrollment, created = self.enrollment_model.objects.get_or_create(
            student=user,
            course=course,
            defaults={
                "is_active": True,
                "enrolled_at": timezone.now(),
                "last_accessed_at": timezone.now(),
            },
        )
        return enrollment

    def _update_or_create_lesson_progress(
        self, user: User, lesson, enrollment, progress_data: Dict[str, Any]
    ) -> models.Model:
        """Update or create lesson progress record."""
        lesson_progress, created = self.lesson_progress_model.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={
                "status": self.lesson_progress_model.StatusChoices.IN_PROGRESS,
                "progress": progress_data.get("progress_percentage", 0),
                "time_spent": timedelta(minutes=progress_data.get("time_spent_minutes", 0)),
                "score": progress_data.get("score"),
                "attempts": 1 if "score" in progress_data else 0,
                "best_score": progress_data.get("score"),
                "started_at": timezone.now(),
                "notes": progress_data.get("notes", ""),
            },
        )

        if not created:
            # Update existing progress
            if progress_data.get("progress_percentage") is not None:
                lesson_progress.progress = max(
                    lesson_progress.progress, progress_data["progress_percentage"]
                )

            if progress_data.get("time_spent_minutes"):
                lesson_progress.time_spent += timedelta(minutes=progress_data["time_spent_minutes"])

            if "score" in progress_data:
                lesson_progress.attempts += 1
                if (
                    lesson_progress.best_score is None
                    or progress_data["score"] > lesson_progress.best_score
                ):
                    lesson_progress.best_score = progress_data["score"]
                lesson_progress.score = progress_data["score"]

            if progress_data.get("notes"):
                lesson_progress.notes = progress_data["notes"]

        # Update status based on progress
        if (
            lesson_progress.progress >= 100
            and lesson_progress.status != self.lesson_progress_model.StatusChoices.COMPLETED
        ):
            lesson_progress.status = self.lesson_progress_model.StatusChoices.COMPLETED
            lesson_progress.completed_at = timezone.now()
        elif (
            lesson_progress.progress > 0
            and lesson_progress.status == self.lesson_progress_model.StatusChoices.NOT_STARTED
        ):
            lesson_progress.status = self.lesson_progress_model.StatusChoices.IN_PROGRESS
            if not lesson_progress.started_at:
                lesson_progress.started_at = timezone.now()

        lesson_progress.last_accessed_at = timezone.now()
        lesson_progress.save()

        return lesson_progress

    def _update_or_create_module_progress(
        self, enrollment, module, progress_percentage: float, time_spent_minutes: float = 0
    ) -> models.Model:
        """Update or create module progress record."""
        module_progress, created = self.module_progress_model.objects.get_or_create(
            enrollment=enrollment,
            module=module,
            defaults={
                "progress_percentage": progress_percentage,
                "time_spent_minutes": time_spent_minutes,
                "status": self.module_progress_model.StatusChoices.IN_PROGRESS,
                "started_at": timezone.now(),
            },
        )

        if not created:
            module_progress.update_progress(progress_percentage, time_spent_minutes)
        else:
            if progress_percentage >= 100:
                module_progress.complete()

        return module_progress

    def _update_module_progress_from_lesson(
        self, enrollment, module, progress_data: Dict[str, Any]
    ) -> models.Model:
        """Update module progress based on lesson completion."""
        # Calculate module progress from all lessons
        from plugins.lms.models import Lesson

        lessons = Lesson.objects.filter(module=module, is_active=True)
        total_lessons = lessons.count()

        if total_lessons == 0:
            return self._update_or_create_module_progress(enrollment, module, 0)

        completed_lessons = self.lesson_progress_model.objects.filter(
            user=enrollment.student,
            lesson__in=lessons,
            status=self.lesson_progress_model.StatusChoices.COMPLETED,
        ).count()

        module_progress_percentage = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        )

        return self._update_or_create_module_progress(
            enrollment, module, module_progress_percentage
        )

    def _mark_lessons_completed(self, enrollment, module):
        """Mark all lessons in module as completed."""
        from plugins.lms.models import Lesson

        lessons = Lesson.objects.filter(module=module, is_active=True)

        for lesson in lessons:
            lesson_progress, created = self.lesson_progress_model.objects.get_or_create(
                user=enrollment.student,
                lesson=lesson,
                defaults={
                    "status": self.lesson_progress_model.StatusChoices.COMPLETED,
                    "progress": 100.0,
                    "completed_at": timezone.now(),
                    "started_at": timezone.now(),
                },
            )

            if (
                not created
                and lesson_progress.status != self.lesson_progress_model.StatusChoices.COMPLETED
            ):
                lesson_progress.status = self.lesson_progress_model.StatusChoices.COMPLETED
                lesson_progress.progress = 100.0
                lesson_progress.completed_at = timezone.now()
                lesson_progress.save()

    def _update_course_progress_from_lesson(self, enrollment) -> float:
        """Update course progress based on lesson completion."""
        from plugins.lms.models import Lesson

        course = enrollment.course

        # Get all active lessons in course
        total_lessons = Lesson.objects.filter(module__course=course, is_active=True).count()

        if total_lessons == 0:
            enrollment.progress_percentage = 0
            enrollment.save()
            return 0

        # Get completed lessons in course
        completed_lessons = self.lesson_progress_model.objects.filter(
            user=enrollment.student,
            lesson__module__course=course,
            status=self.lesson_progress_model.StatusChoices.COMPLETED,
        ).count()

        course_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        enrollment.progress_percentage = course_progress
        enrollment.completed_lessons_count = completed_lessons
        enrollment.save(update_fields=["progress_percentage", "completed_lessons_count"])

        return course_progress

    def _update_course_progress_from_module(self, enrollment) -> float:
        """Update course progress based on module completion."""
        from ..models import Module

        course = enrollment.course

        # Get all modules in course
        total_modules = Module.objects.filter(course=course).count()

        if total_modules == 0:
            enrollment.progress_percentage = 0
            enrollment.save()
            return 0

        # Get completed modules in course
        completed_modules = self.module_progress_model.objects.filter(
            enrollment=enrollment, status=self.module_progress_model.StatusChoices.COMPLETED
        ).count()

        # Calculate weighted progress based on modules
        module_progress = (
            self.module_progress_model.objects.filter(enrollment=enrollment).aggregate(
                avg_progress=models.Avg("progress_percentage")
            )["avg_progress"]
            or 0
        )

        # Use weighted average (70% modules, 30% lessons for better accuracy)
        course_progress = (module_progress * 0.7) + (enrollment.progress_percentage * 0.3)

        enrollment.progress_percentage = course_progress
        enrollment.save(update_fields=["progress_percentage"])

        return course_progress

    def _check_module_completion(self, enrollment, module) -> bool:
        """Check if module is completed."""
        try:
            module_progress = self.module_progress_model.objects.get(
                enrollment=enrollment, module=module
            )
            return module_progress.status == self.module_progress_model.StatusChoices.COMPLETED
        except self.module_progress_model.DoesNotExist:
            return False

    def _check_course_completion(self, enrollment) -> bool:
        """Check if course is completed."""
        if enrollment.progress_percentage >= 100 and not enrollment.completed_at:
            enrollment.completed_at = timezone.now()
            enrollment.certificate_issued = True
            enrollment.save()

            # Generate certificate URL
            certificate_id = f"CERT-{enrollment.id.hex[:8].upper()}"
            enrollment.certificate_url = f"/certificates/{certificate_id}/download/"
            enrollment.save(update_fields=["certificate_url"])

            return True

        return enrollment.completed_at is not None

    def _get_next_lesson(self, current_lesson, enrollment) -> Optional[Dict[str, Any]]:
        """Get next lesson after the current one."""
        try:
            from plugins.lms.models import Lesson

            # Get next lesson in same module
            next_lesson = (
                Lesson.objects.filter(
                    module=current_lesson.module, order__gt=current_lesson.order, is_active=True
                )
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
                }

            # Get first lesson of next module
            next_module = (
                self.module_progress_model.objects.filter(
                    enrollment=enrollment, module__order__gt=current_lesson.module.order
                )
                .order_by("module__order")
                .first()
            )

            if next_module:
                first_lesson = (
                    Lesson.objects.filter(module=next_module.module, is_active=True)
                    .order_by("order")
                    .first()
                )

                if first_lesson:
                    return {
                        "id": first_lesson.id,
                        "title": first_lesson.title,
                        "module_id": first_lesson.module_id,
                        "module_title": first_lesson.module.title,
                        "order": first_lesson.order,
                    }

            return None

        except Exception as e:
            logger.error(f"Error getting next lesson: {e}")
            return None

    def _invalidate_progress_caches(self, user_id: int, enrollment_id: int, course_id: int):
        """Invalidate all relevant progress caches."""
        cache_keys = [
            f"progress_service:overview:{user_id}:*",
            f"progress_service:course_details:{user_id}:{course_id}",
            f"enrollment_service:dashboard:{user_id}:*",
            f"enrollment_service:progress:{enrollment_id}",
        ]

        for key in cache_keys:
            cache.delete(key)

    def get_progress_overview(self, user: User, course_id: int = None) -> Dict[str, Any]:
        """
        Get comprehensive progress overview for user.

        Args:
            user: User object
            course_id: Optional course ID filter

        Returns:
            Dictionary with progress overview
        """
        cache_key = f"progress_manager:overview:{user.id}:{course_id}"
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return {**cached_result, "from_cache": True}

        # Get enrollments
        enrollments = self.enrollment_model.objects.filter(student=user, is_active=True)

        if course_id:
            enrollments = enrollments.filter(course_id=course_id)

        # Calculate metrics
        total_enrollments = enrollments.count()
        total_completed = enrollments.filter(completed_at__isnull=False).count()
        total_active = total_enrollments - total_completed

        # Get average progress
        avg_progress = enrollments.aggregate(avg=models.Avg("progress_percentage"))["avg"] or 0

        # Get recent progress activity
        recent_activity = self._get_recent_progress_activity(user, course_id)

        # Get progress by course
        progress_by_course = []
        for enrollment in enrollments:
            progress_by_course.append(
                {
                    "course_id": enrollment.course_id,
                    "course_title": enrollment.course.title,
                    "progress": enrollment.progress_percentage,
                    "is_completed": enrollment.completed_at is not None,
                    "time_spent_hours": round(enrollment.total_time_spent_minutes / 60, 1),
                }
            )

        result = {
            "user_id": user.id,
            "total_enrollments": total_enrollments,
            "total_completed": total_completed,
            "total_active": total_active,
            "average_progress": round(avg_progress, 1),
            "recent_activity": recent_activity,
            "progress_by_course": progress_by_course,
        }

        cache.set(cache_key, result, timeout=1800)
        return {**result, "from_cache": False}

    def _get_recent_progress_activity(
        self, user: User, course_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get recent progress activity for user."""
        lesson_progress_qs = self.lesson_progress_model.objects.filter(user=user).select_related(
            "lesson", "lesson__module", "lesson__module__course"
        )

        if course_id:
            lesson_progress_qs = lesson_progress_qs.filter(lesson__module__course_id=course_id)

        recent_progress = list(
            lesson_progress_qs.order_by("-last_accessed_at")[:10].values(
                "lesson__title",
                "lesson__module__title",
                "lesson__module__course__title",
                "progress",
                "status",
                "last_accessed_at",
                "time_spent",
            )
        )

        return recent_progress

    def bulk_update_progress(self, user: User, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk update progress for multiple items.

        Args:
            user: User object
            updates: List of update dictionaries

        Returns:
            Dictionary with results
        """
        results = {
            "successful": [],
            "failed": [],
            "total": len(updates),
        }

        with transaction.atomic():
            for update in updates:
                try:
                    update_type = update.get("type")  # 'lesson' or 'module'

                    if update_type == "lesson":
                        lesson_id = update.get("lesson_id")
                        progress_data = update.get("progress_data", {})

                        success, result = self.update_lesson_progress(
                            user, lesson_id, progress_data
                        )

                        if success:
                            results["successful"].append(
                                {"type": "lesson", "lesson_id": lesson_id, "result": result}
                            )
                        else:
                            results["failed"].append(
                                {
                                    "type": "lesson",
                                    "lesson_id": lesson_id,
                                    "error": result.get("error"),
                                    "update": update,
                                }
                            )

                    elif update_type == "module":
                        module_id = update.get("module_id")
                        progress_percentage = update.get("progress_percentage", 0)
                        time_spent = update.get("time_spent_minutes", 0)

                        success, result = self.update_module_progress(
                            user, module_id, progress_percentage, time_spent
                        )

                        if success:
                            results["successful"].append(
                                {"type": "module", "module_id": module_id, "result": result}
                            )
                        else:
                            results["failed"].append(
                                {
                                    "type": "module",
                                    "module_id": module_id,
                                    "error": result.get("error"),
                                    "update": update,
                                }
                            )

                    else:
                        results["failed"].append(
                            {
                                "type": "unknown",
                                "error": f"Unknown update type: {update_type}",
                                "update": update,
                            }
                        )

                except Exception as e:
                    results["failed"].append({"type": "error", "error": str(e), "update": update})

        # Invalidate all user caches
        self._invalidate_progress_caches(user.id, 0, 0)

        return {
            "success": len(results["failed"]) == 0,
            "results": results,
            "successful_count": len(results["successful"]),
            "failed_count": len(results["failed"]),
        }
