
from __future__ import annotations

import hashlib
import json
import logging
from datetime import timedelta
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Q, QuerySet
from django.db.models.functions import TruncDate
from django.utils import timezone
from django_fusion.management.managers.base import CachedManager

logger = logging.getLogger(__name__)
User = get_user_model()


class CourseManager(CachedManager):
    """
    Enhanced Course Manager with comprehensive user operations.
    """

    CACHE_PREFIX = "course"
    DEFAULT_TIMEOUT = 3600  # 1 hour
    SEARCH_CACHE_TIMEOUT = 900  # 15 minutes

    # -----------------------------------------------------------------
    # User-Centric Course Operations
    # -----------------------------------------------------------------

    @classmethod
    def get_user_enrolled_courses(
        cls,
        user_id: int,
        include_completed: bool = True,
        include_inactive: bool = False,
        **filters
    ) -> Dict[str, Any]:
        """
        Get courses where user is enrolled.

        Args:
            user_id: User ID
            include_completed: Include completed courses
            include_inactive: Include inactive enrollments
            **filters: Additional filters

        Returns:
            Dictionary with courses and metadata
        """
        cache_key = f"{cls.CACHE_PREFIX}:user_enrolled:{user_id}:{include_completed}:{include_inactive}:{filters}"

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for user enrolled courses: {user_id}")
            return {**cached_result, 'from_cache': True}

        # Get enrollment model
        from apps.pages.lms.models.enrollment import Enrollment

        # Build enrollment filters
        enrollment_filters = {'student__user_id': user_id}

        if not include_inactive:
            enrollment_filters['is_active'] = True

        if not include_completed:
            enrollment_filters['status__in'] = ['active', 'enrolled']

        # Get enrolled courses
        enrollments = Enrollment.objects.filter(**enrollment_filters)

        # Get course IDs
        course_ids = enrollments.values_list('course_id', flat=True)

        # Get courses with details
        courses = cls.get_published_courses_cached(
            filters={'id__in': course_ids, **filters},
            include_related=True
        )

        # Add enrollment info to each course
        enrollment_map = {e.course_id: e for e in enrollments}

        enhanced_courses = []
        for course in courses.get('courses', []):
            enrollment = enrollment_map.get(course.id)
            if enrollment:
                course_data = {
                    'course': course,
                    'enrollment': {
                        'id': enrollment.id,
                        'status': enrollment.status,
                        'progress_percentage': enrollment.progress_percentage,
                        'enrolled_at': enrollment.enrolled_at,
                        'last_accessed_at': enrollment.last_accessed_at,
                        'completed_at': enrollment.completed_at,
                    }
                }
                enhanced_courses.append(course_data)

        result = {
            'courses': enhanced_courses,
            'total_count': len(enhanced_courses),
            'filters': filters,
            'from_cache': False,
        }

        cache.set(cache_key, result, timeout=cls.SEARCH_CACHE_TIMEOUT)
        logger.debug(f"Cached user enrolled courses: {user_id}")

        return result

    @classmethod
    def _get_user_interests(cls, user_id: int) -> Dict[str, List]:
        """
        Extract user interests from various sources.

        Args:
            user_id: User ID

        Returns:
            Dictionary of user interests
        """
        interests = {
            'categories': [],
            'tags': [],
            'difficulties': [],
        }

        try:
            # Get from enrolled courses
            from apps.pages.lms.models.enrollment import Enrollment

            enrollments = Enrollment.objects.filter(
                student__user_id=user_id,
                is_active=True
            ).select_related('course')

            for enrollment in enrollments:
                course = enrollment.course

                # Add category
                if course.category and course.category.id not in interests['categories']:
                    interests['categories'].append(course.category.id)

                # Add tags
                for tag in course.tags.all():
                    if tag.id not in interests['tags']:
                        interests['tags'].append(tag.id)

                # Add difficulty
                if course.difficulty_level and course.difficulty_level not in interests['difficulties']:
                    interests['difficulties'].append(course.difficulty_level)

        except Exception as e:
            logger.error(f"Error getting user interests: {e}")

        return interests

    @classmethod
    def get_user_learning_path(
        cls,
        user_id: int,
        specialization_id: int = None,
        max_courses: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a learning path for a user.

        Args:
            user_id: User ID
            specialization_id: Optional specialization ID
            max_courses: Maximum courses in path

        Returns:
            Dictionary with learning path
        """
        cache_key = f"{cls.CACHE_PREFIX}:learning_path:{user_id}:{specialization_id}:{max_courses}"

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for user learning path: {user_id}")
            return cached_result

        # Get user's current skills and completed courses
        user_skills = cls._assess_user_skills(user_id)

        # Build learning path
        learning_path = {
            'user_skills': user_skills,
            'recommended_path': [],
            'prerequisites': [],
            'estimated_duration': 0,
            'difficulty_progression': 'beginner',
        }

        # Get courses based on user skills and goals
        recommended_courses = cls._get_path_courses(
            user_skills=user_skills,
            specialization_id=specialization_id,
            max_courses=max_courses
        )

        learning_path['recommended_path'] = recommended_courses

        # Calculate estimated duration
        total_duration = sum(course.duration_hours for course in recommended_courses)
        learning_path['estimated_duration'] = total_duration

        # Determine difficulty progression
        if recommended_courses:
            difficulties = [course.difficulty_level for course in recommended_courses]
            if 'advanced' in difficulties:
                learning_path['difficulty_progression'] = 'advanced'
            elif 'intermediate' in difficulties:
                learning_path['difficulty_progression'] = 'intermediate'

        cache.set(cache_key, learning_path, timeout=3600)  # 1 hour
        return learning_path

    @classmethod
    def _assess_user_skills(cls, user_id: int) -> Dict[str, Any]:
        """
        Assess user's current skills based on completed courses.

        Args:
            user_id: User ID

        Returns:
            Dictionary with skill assessment
        """
        from apps.pages.lms.models.enrollment import Enrollment

        # Get completed courses
        completed_courses = Enrollment.objects.filter(
            student__user_id=user_id,
            status='completed',
            is_active=True
        ).select_related('course')

        skills = {
            'completed_courses': [],
            'skill_areas': {},
            'average_rating': 0,
            'total_learning_hours': 0,
        }

        total_rating = 0
        total_courses = completed_courses.count()

        for enrollment in completed_courses:
            course = enrollment.course

            skills['completed_courses'].append({
                'id': course.id,
                'title': course.title,
                'category': str(course.category) if course.category else None,
                'difficulty': course.difficulty_level,
                'duration': course.duration_hours,
            })

            # Add to skill areas
            if course.category:
                category_name = str(course.category)
                skills['skill_areas'][category_name] = skills['skill_areas'].get(category_name, 0) + 1

            # Accumulate learning hours
            skills['total_learning_hours'] += course.duration_hours

            # Accumulate rating (if available)
            if course.average_rating:
                total_rating += course.average_rating

        # Calculate average rating
        if total_courses > 0:
            skills['average_rating'] = round(total_rating / total_courses, 2)

        return skills

    # -----------------------------------------------------------------
    # Enhanced Methods from Original CourseCacheManager
    # -----------------------------------------------------------------

    @classmethod
    def get_user_course_completion_analytics(
        cls,
        user_id: int,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Get course completion analytics for a user.

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            Dictionary with completion analytics
        """
        cache_key = f"{cls.CACHE_PREFIX}:user_completion:{user_id}:{days}"

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        from apps.pages.lms.models.enrollment import Enrollment

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get user enrollments
        enrollments = Enrollment.objects.filter(
            student__user_id=user_id,
            enrolled_at__range=[start_date, end_date]
        ).select_related('course')

        # Calculate completion statistics
        total_enrollments = enrollments.count()
        completed_enrollments = enrollments.filter(status='completed').count()

        # Calculate completion rate by difficulty
        difficulty_stats = {}
        for enrollment in enrollments:
            difficulty = enrollment.course.difficulty_level if enrollment.course else 'unknown'

            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {
                    'total': 0,
                    'completed': 0,
                    'in_progress': 0,
                }

            difficulty_stats[difficulty]['total'] += 1

            if enrollment.status == 'completed':
                difficulty_stats[difficulty]['completed'] += 1
            elif enrollment.status == 'active':
                difficulty_stats[difficulty]['in_progress'] += 1

        # Calculate monthly completion trend
        monthly_completions = list(
            enrollments.filter(status='completed')
            .annotate(month=TruncDate('completed_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')[-6:]  # Last 6 months
        )

        analytics = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days,
            },
            'overall': {
                'total_enrollments': total_enrollments,
                'completed_enrollments': completed_enrollments,
                'completion_rate': round(
                    (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0,
                    2
                ),
                'average_completion_time': None,  # Would need completion dates
            },
            'by_difficulty': difficulty_stats,
            'monthly_trend': monthly_completions,
            'recent_completions': list(
                enrollments.filter(status='completed')
                .order_by('-completed_at')[:5]
                .values(
                    'course__title',
                    'completed_at',
                    'course__difficulty_level',
                    'course__duration_hours'
                )
            ),
        }

        cache.set(cache_key, analytics, timeout=3600)  # 1 hour
        return analytics

    # -----------------------------------------------------------------
    # Helper Methods
    # -----------------------------------------------------------------

    @classmethod
    def _apply_filters(cls, queryset: QuerySet, filters: dict) -> QuerySet:
        """Apply filters to course queryset."""
        # Existing filters from original implementation
        if specialization_id := filters.get('specialization_id'):
            queryset = queryset.filter(specializations__id=specialization_id)

        if specialization_slug := filters.get('specialization_slug'):
            queryset = queryset.filter(specializations__slug=specialization_slug)

        if language := filters.get('language'):
            queryset = queryset.filter(language=language)

        if difficulty := filters.get('difficulty'):
            queryset = queryset.filter(difficulty_level=difficulty)

        if price_filter := filters.get('price'):
            if price_filter == 'free':
                queryset = queryset.filter(price=0)
            elif price_filter == 'paid':
                queryset = queryset.filter(price__gt=0)
            elif price_filter == 'discounted':
                queryset = queryset.filter(discount_percentage__gt=0)

        if duration := filters.get('duration'):
            if duration == 'short':
                queryset = queryset.filter(duration__lte=10)
            elif duration == 'medium':
                queryset = queryset.filter(duration__gt=10, duration__lte=30)
            elif duration == 'long':
                queryset = queryset.filter(duration__gt=30)

        if filters.get('featured_only'):
            queryset = queryset.filter(is_featured=True)

        if filters.get('has_certificate'):
            queryset = queryset.filter(has_certificate=True)

        if search_query := filters.get('search_query'):
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # New user-specific filters
        if user_id := filters.get('user_id'):
            # Filter by user enrollment status
            from apps.pages.lms.models.enrollment import Enrollment

            if filters.get('enrolled_only'):
                enrolled_course_ids = Enrollment.objects.filter(
                    student__user_id=user_id,
                    is_active=True
                ).values_list('course_id', flat=True)
                queryset = queryset.filter(id__in=enrolled_course_ids)

            if filters.get('not_enrolled'):
                enrolled_course_ids = Enrollment.objects.filter(
                    student__user_id=user_id,
                    is_active=True
                ).values_list('course_id', flat=True)
                queryset = queryset.exclude(id__in=enrolled_course_ids)

        return queryset.distinct()

    @classmethod
    def _generate_cache_key(cls, cache_type: str, params: dict) -> str:
        """Generate deterministic cache key."""
        raw_str = json.dumps(params, sort_keys=True)
        hashed = hashlib.md5(raw_str.encode()).hexdigest()[:12]
        return f"{cls.CACHE_PREFIX}:{cache_type}:{hashed}"
