from __future__ import annotations

import logging
from typing import Any

from django.core.cache import cache
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)
from crafts_ai.rseal.services.infrastructure.base import BaseService
from crafts_ai.rseal.services.infrastructure.token import TokenService

from plugins.lms.models import Lesson


class LessonsService(BaseService):
    """
    Service layer for Lesson operations.
    """

    model_class = Lesson
    default_filter_field = "id"
    enable_cache = True
    cache_timeout = 1800
    cache_key_prefix = "lesson_service"

  
    def get_course_modules(self, course, include_lessons=True):
        """
        Get modules for a course.
        
        Args:
            course: Course object
            include_lessons: Include lesson details
        
        Returns:
            QuerySet of modules
        """
        queryset = self.filter(course=course, is_active=True)
        
        if include_lessons:
            queryset = queryset.prefetch_related(
                models.Prefetch(
                    'lessons',
                    queryset=Lesson.objects.filter(is_active=True).order_by('order')
                )
            )
        
        return queryset.order_by('order')
    
    @classmethod
    def get_lesson_by_id(cls, lesson_id: int, use_cache: bool = True) -> Lesson | None:
        """Get lesson by ID."""
        return cls.get_instance(
            filter_value=lesson_id,
            use_cache=use_cache
        )

    @classmethod
    def get_lesson_by_slug(cls, slug: str, use_cache: bool = True) -> Lesson | None:
        """Get lesson by slug."""
        return cls.get_instance(
            filter_value=slug,
            filter_field='slug',
            use_cache=use_cache
        )

    @classmethod
    def get_course_lessons(
        cls,
        course_id: int,
        user_id: int | None = None,
        include_preview: bool = True
    ) -> dict[str, Any]:
        """
        Get all lessons for a course with user progress.
        
        Args:
            course_id: Course ID
            user_id: Optional user ID for progress tracking
            include_preview: Include preview lessons
        
        Returns:
            Dictionary with lessons and metadata
        """
        lessons = Lesson.objects.get_course_lessons(course_id)

        if not include_preview:
            lessons = lessons.filter(is_preview=False)

        total_lessons = lessons.count()

        # Get user progress if user_id provided
        user_progress = {}
        if user_id:
            # This would come from LessonProgress model
            pass

        return {
            'lessons': list(lessons),
            'total': total_lessons,
            'user_progress': user_progress,
            'include_preview': include_preview,
        }

    @classmethod
    def get_module_lessons(
        cls,
        module_id: int,
        user_id: int | None = None
    ) -> dict[str, Any]:
        """
        Get lessons for a module.
        
        Args:
            module_id: Module ID
            user_id: Optional user ID for progress tracking
        
        Returns:
            Dictionary with lessons
        """
        lessons = Lesson.objects.get_lessons_by_module(module_id)

        user_progress = {}
        if user_id:
            # Get user progress for these lessons
            pass

        return {
            'lessons': list(lessons),
            'total': lessons.count(),
            'user_progress': user_progress,
        }

    @classmethod
    def get_lesson_with_context(
        cls,
        lesson_id: int,
        user_id: int | None = None
    ) -> dict[str, Any]:
        """
        Get lesson with context (previous/next lessons, progress).
        
        Args:
            lesson_id: Lesson ID
            user_id: Optional user ID
        
        Returns:
            Dictionary with lesson and context
        """
        lesson = cls.get_lesson_by_id(lesson_id)
        if not lesson:
            return {
                'success': False,
                'error': 'Lesson not found',
                'code': 'LESSON_NOT_FOUND'
            }

        # Get previous and next lessons
        previous_lesson = Lesson.objects.get_previous_lesson(lesson_id)
        next_lesson = Lesson.objects.get_next_lesson(lesson_id, user_id)

        # Get user progress
        user_progress = {}
        if user_id:
            user_progress = Lesson.objects.get_lesson_progress(lesson_id, user_id)

        # Check if user has access to this lesson
        has_access = cls._check_lesson_access(lesson, user_id)

        return {
            'success': True,
            'lesson': lesson,
            'previous_lesson': previous_lesson,
            'next_lesson': next_lesson,
            'user_progress': user_progress,
            'has_access': has_access,
            'module': lesson.module,
            'course': lesson.module.course if lesson.module else None,
        }

    @classmethod
    def _check_lesson_access(cls, lesson: Lesson, user_id: int | None) -> bool:
        """
        Check if user has access to a lesson.
        
        Rules:
        1. Preview lessons are accessible to everyone
        2. Non-preview lessons require enrollment
        3. Admins/instructors have access to all lessons
        """
        if lesson.is_preview:
            return True

        if not user_id:
            return False

        # Check if user is enrolled in the course
        from .enrollment_services import EnrollmentService

        course_id = lesson.module.course_id if lesson.module else None
        if not course_id:
            return False

        enrollment = EnrollmentService.check_if_user_enrolled(user_id, course_id)
        return enrollment['is_enrolled']

    @classmethod
    def mark_lesson_as_completed(
        cls,
        lesson_id: int,
        user_id: int,
        token: str | None = None,
        completed_at: timezone.datetime | None = None
    ) -> dict[str, Any]:
        """
        Mark a lesson as completed for a user.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID
            token: Verification token (optional)
            completed_at: Completion timestamp
        
        Returns:
            Completion result
        """
        lesson = cls.get_lesson_by_id(lesson_id)
        if not lesson:
            return {
                'success': False,
                'error': 'Lesson not found',
                'code': 'LESSON_NOT_FOUND'
            }

        # Check access
        if not cls._check_lesson_access(lesson, user_id):
            return {
                'success': False,
                'error': 'Access denied',
                'code': 'ACCESS_DENIED'
            }

        # Mark as completed
        success = Lesson.objects.mark_as_completed(
            lesson_id=lesson_id,
            user_id=user_id,
            completed_at=completed_at or timezone.now()
        )

        if success:
            # Check if all lessons in course are completed
            cls._check_course_completion(user_id, lesson.module.course_id)

            return {
                'success': True,
                'message': 'Lesson marked as completed',
                'lesson_id': lesson_id,
                'completed_at': completed_at or timezone.now(),
            }

        return {
            'success': False,
            'error': 'Failed to mark lesson as completed',
            'code': 'COMPLETION_FAILED'
        }

    @classmethod
    def _check_course_completion(cls, user_id: int, course_id: int) -> None:
        """
        Check if all lessons in a course are completed and mark enrollment as completed.
        """
        from .enrollment_services import EnrollmentService

        # Get total lessons
        lessons = Lesson.objects.get_course_lessons(course_id)
        total_lessons = lessons.count()

        # Get completed lessons (this would come from LessonProgress)
        completed_lessons = 0  # This should be fetched from progress model

        # If all lessons completed, mark enrollment as completed
        if completed_lessons >= total_lessons:
            enrollment = EnrollmentService.get_user_enrollment_for_course(
                user_id=user_id,
                course_id=course_id
            )

            if enrollment and not enrollment.completed_at:
                enrollment.completed_at = timezone.now()
                enrollment.save(update_fields=['completed_at'])

    @classmethod
    def get_lesson_progress(
        cls,
        lesson_id: int,
        user_id: int
    ) -> dict[str, Any]:
        """
        Get user's progress for a specific lesson.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID
        
        Returns:
            Progress dictionary
        """
        lesson = cls.get_lesson_by_id(lesson_id)
        if not lesson:
            return {
                'success': False,
                'error': 'Lesson not found',
                'code': 'LESSON_NOT_FOUND'
            }

        progress = Lesson.objects.get_lesson_progress(lesson_id, user_id)

        return {
            'success': True,
            'lesson_id': lesson_id,
            'user_id': user_id,
            'progress': progress,
            'lesson': lesson,
        }

    @classmethod
    def update_lesson(
        cls,
        lesson_id: int,
        data: dict[str, Any],
        token: str,
        user_id: int,
    ) -> dict[str, Any]:
        """
        Update lesson with token protection.
        
        Args:
            lesson_id: Lesson ID
            data: Data to update
            token: Verification token
            user_id: User ID
        
        Returns:
            Update result
        """
        lesson = cls.get_lesson_by_id(lesson_id)
        if not lesson:
            return {
                'success': False,
                'error': 'Lesson not found',
                'code': 'LESSON_NOT_FOUND'
            }

        # Check if user has permission to update this lesson
        # Only course instructor or admin can update lessons
        course = lesson.module.course if lesson.module else None
        if not course:
            return {
                'success': False,
                'error': 'Lesson has no associated course',
                'code': 'NO_COURSE'
            }

        # Validate token for lesson update
        validation_result = TokenService.validate_action_token(
            token,
            expected_action='update_lesson'
        )

        if not validation_result['valid']:
            return {
                'success': False,
                'error': validation_result.get('error', 'Token validation failed'),
                'code': validation_result.get('code', 'TOKEN_INVALID')
            }

        # Check if user is instructor or admin
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.filter(id=user_id).first()
        if not user:
            return {
                'success': False,
                'error': 'User not found',
                'code': 'USER_NOT_FOUND'
            }

        if course.instructor_id != user_id and not user.is_staff:
            return {
                'success': False,
                'error': 'Permission denied',
                'code': 'PERMISSION_DENIED'
            }

        # Update lesson
        try:
            for field, value in data.items():
                setattr(lesson, field, value)

            lesson.save()

            # Invalidate caches
            cls._invalidate_lesson_caches(lesson_id, lesson.module_id)

            return {
                'success': True,
                'message': 'Lesson updated successfully',
                'lesson': lesson,
            }

        except Exception as e:
            logger.error(f"Failed to update lesson {lesson_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'UPDATE_FAILED'
            }

    @classmethod
    def _invalidate_lesson_caches(cls, lesson_id: int, module_id: int | None) -> None:
        """Invalidate caches related to a lesson."""
        cache_keys = [
            f"lesson_service:detail:{lesson_id}",
            f"lesson_service:lesson_with_context:{lesson_id}",
        ]

        if module_id:
            cache_keys.append(f"lesson_service:module_lessons:{module_id}")

        for key in cache_keys:
            cache.delete(key)
