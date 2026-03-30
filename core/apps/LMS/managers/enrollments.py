from __future__ import annotations

import hashlib
import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Avg, Count, F, Prefetch, Q, QuerySet
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.LMS.models.courses import Course
from django_grep.pipelines.managers import BaseManager

logger = logging.getLogger(__name__)
User = get_user_model()
class EnrollmentsManager(BaseManager):
    """
    Enhanced manager for Enrollment model.
    """

    def get_user_enrollments(self, user, status=None, include_course_details=True):
        """
        Get enrollments for a user.

        Args:
            user: The user (student)
            status: Optional status filter
            include_course_details: Include course details

        Returns:
            QuerySet of enrollments
        """
        queryset = self.filter(student=user)

        if status:
            queryset = queryset.filter(status=status)

        if include_course_details:
            queryset = queryset.select_related(
                'course',
                'course__instructor'
            ).prefetch_related(
                'course__tags',
                'course__modules'
            )

        return queryset.order_by('-enrolled_at')

    def get_enrollment_analytics(self, user):
        """
        Get enrollment analytics for a user.

        Args:
            user: The user

        Returns:
            Dictionary with analytics
        """
        enrollments = self.filter(student=user)

        analytics = enrollments.aggregate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed')),
            average_progress=Avg('progress', filter=Q(status='active')),
            completion_rate=Count(
                'id',
                filter=Q(status='completed')
            ) * 100.0 / Count('id'),
        )

        # Add progress distribution
        progress_distribution = list(
            enrollments.filter(status='active')
            .values('progress')
            .annotate(count=Count('id'))
            .order_by('progress')
        )

        analytics['progress_distribution'] = progress_distribution

        # Add time-based analytics
        recent_completions = list(
            enrollments.filter(
                status='completed',
                completion_date__gte=timezone.now() - timezone.timedelta(days=30)
            ).values('course__title', 'completion_date', 'grade', 'score')
            .order_by('-completion_date')[:5]
        )

        analytics['recent_completions'] = recent_completions

        return analytics

    def get_course_enrollments(self, course, status=None, include_user_details=True):
        """
        Get enrollments for a course.

        Args:
            course: Course object
            status: Optional status filter
            include_user_details: Include user details

        Returns:
            QuerySet of enrollments
        """
        queryset = self.filter(course=course)

        if status:
            queryset = queryset.filter(status=status)

        if include_user_details:
            queryset = queryset.select_related('student').prefetch_related(
                'student__person'
            )

        return queryset.order_by('-enrolled_at')

    def get_learning_path(self, user, max_courses=5):
        """
        Get recommended learning path for a user.

        Args:
            user: The user
            max_courses: Maximum courses in path

        Returns:
            List of recommended courses
        """
        from apps.handlers.models import Course

        # Get user's completed courses
        completed_courses = self.filter(
            student=user,
            status='completed'
        ).values_list('course_id', flat=True)

        # Get active enrollments
        active_enrollments = self.filter(
            student=user,
            status='active'
        ).select_related('course').order_by('-last_accessed_at')

        # If user has active enrollments, suggest related courses
        if active_enrollments.exists():
            # Get tags from active courses
            tags = set()
            for enrollment in active_enrollments:
                tags.update(enrollment.course.tags.values_list('name', flat=True))

            # Find related courses
            related_courses = Course.objects.filter(
                tags__name__in=tags,
                status='published'
            ).exclude(
                id__in=completed_courses
            ).exclude(
                enrollments__student=user
            ).distinct().order_by(
                '-enrollment_count',
                '-average_rating'
            )[:max_courses]

            return list(related_courses)

        # If no active enrollments, suggest popular beginner courses
        beginner_courses = Course.objects.filter(
            difficulty='beginner',
            status='published'
        ).exclude(
            id__in=completed_courses
        ).exclude(
            enrollments__student=user
        ).order_by(
            '-enrollment_count',
            '-average_rating'
        )[:max_courses]

        return list(beginner_courses)

    def bulk_update_progress(self, enrollment_ids, progress_increment):
        """
        Bulk update progress for multiple enrollments.

        Args:
            enrollment_ids: List of enrollment IDs
            progress_increment: Progress increment

        Returns:
            Number of updated enrollments
        """
        from django.db.models import F

        updated = self.filter(
            id__in=enrollment_ids,
            status='active'
        ).update(
            progress=F('progress') + progress_increment,
            last_accessed_at=timezone.now()
        )

        return updated

    def cleanup_inactive_enrollments(self, days_threshold=180):
        """
        Clean up inactive enrollments.

        Args:
            days_threshold: Days of inactivity

        Returns:
            Number of cleaned enrollments
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days_threshold)

        inactive_enrollments = self.filter(
            status='active',
            last_accessed_at__lt=cutoff_date,
            progress__lt=10  # Less than 10% progress
        )

        count = inactive_enrollments.count()

        # Update status to dropped
        inactive_enrollments.update(
            status='dropped',
            notes='Automatically dropped due to inactivity'
        )

        return count

