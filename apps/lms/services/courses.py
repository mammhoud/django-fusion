from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.db.models import Prefetch, Q, QuerySet
from django.utils import timezone

from apps import logger
from apps.lms.models.courses import Course, Lesson, Module
from django_rseal.pipelines.services import (
    CRUDService,
)

from ..models.enrollment import Enrollment

User = get_user_model()


class CourseService(CRUDService):
    """
    Service for course operations with CRUD capabilities.
    """

    service_name = "course_service"

    CACHE_PREFIX = "course_service"
    DEFAULT_TIMEOUT = 3600  # 1 hour
    SEARCH_CACHE_TIMEOUT = 600  # 10 minutes

    def __init__(self):
        super().__init__(model_class=Course)

    def execute(self, operation: str, **kwargs) -> Any:
        """Execute course operation."""
        if operation == "enroll_user":
            return self.enroll_user(**kwargs)
        elif operation == "update_progress":
            return self.update_course_progress(**kwargs)
        elif operation == "get_dashboard":
            return self.get_user_course_dashboard(user=kwargs.get('user'))
        elif operation == "generate_report":
            return self.generate_course_completion_report(**kwargs)
        elif operation == "get_recommended":
            return self.get_user_recommended_courses(**kwargs)
        elif operation == "get_published":
            return self.get_published_courses_cached(**kwargs)
        elif operation == "get_by_slug":
            return self.get_course_by_slug_cached(**kwargs)
        else:
            return super().execute(operation, **kwargs)

    def enroll_user(
        self,
        user,
        course_id: str,
        **enrollment_data
    ) -> Tuple[bool, str, Any]:
        """
        Enroll a user in a course.

        Args:
            user: User to enroll
            course_id: Course ID
            **enrollment_data: Additional enrollment data

        Returns:
            Tuple of (success, message, enrollment)
        """
        try:
            course = self.get_by_pk(course_id)

            if not course:
                return False, "Course not found", None

            # Check if course is active
            if not course.is_active:
                return False, "Course is not currently active", None

            # Check if user is already enrolled
            existing_enrollment = Enrollment.objects.filter(
                content_object=user,
                course=course
            ).first()

            if existing_enrollment:
                if existing_enrollment.status == 'active':
                    return False, "You are already enrolled in this course", None
                elif existing_enrollment.status == 'completed':
                    return False, "You have already completed this course", None
                else:
                    # Reactivate enrollment
                    existing_enrollment.status = 'active'
                    existing_enrollment.save()
                    return True, "Enrollment reactivated", existing_enrollment

            # Create new enrollment
            enrollment = Enrollment.objects.create(
                content_object=user,
                course=course,
                **enrollment_data
            )

            # Activate enrollment
            enrollment.activate()

            # Update course enrollment count
            course.enrollment_count = course.enrollments.filter(status='active').count()
            course.save()

            # Invalidate cache
            cache_key = f"user_courses_{user.id}"
            cache.delete(cache_key)

            return True, "Successfully enrolled in course", enrollment

        except Exception as e:
            logger.error(f"Error enrolling in course: {e}")
            return False, f"Error enrolling in course: {str(e)}", None

    def update_course_progress(
        self,
        enrollment_id: str,
        progress: float,
        user=None
    ) -> Tuple[bool, str, Any]:
        """
        Update course progress.

        Args:
            enrollment_id: Enrollment ID
            progress: Progress percentage (0-100)
            user: Optional user for validation

        Returns:
            Tuple of (success, message, enrollment)
        """
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)

            # Validate user if provided
            if user and enrollment.content_object != user:
                return False, "You don't have permission to update this enrollment", None

            # Update progress
            enrollment.update_progress(progress)

            # Check for completion
            if progress >= 100 and enrollment.status == 'active':
                enrollment.complete()

                # Issue completion certificate if enabled
                if enrollment.course.issue_certificate_on_completion:
                    from apps.accounts.services import CertificateService

                    CertificateService.issue_certificate(
                        content_object=enrollment.content_object,
                        name=f"Completion: {enrollment.course.title}",
                        issuer=enrollment.course.institution or "System",
                        issue_date=timezone.now().date(),
                    )

            return True, "Progress updated successfully", enrollment

        except Enrollment.DoesNotExist:
            return False, "Enrollment not found", None
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            return False, f"Error updating progress: {str(e)}", None

    def get_user_course_dashboard(self, user) -> Dict[str, Any]:
        """
        Get course dashboard for a user.

        Args:
            user: The user

        Returns:
            Dictionary with dashboard data
        """
        cache_key = f"course_dashboard_{user.id}"
        dashboard_data = cache.get(cache_key)

        if dashboard_data is None:
            # Get user's enrollments
            enrollments = Enrollment.objects.filter(content_object=user)

            # Calculate metrics
            active_enrollments = enrollments.filter(status='active')
            completed_enrollments = enrollments.filter(status='completed')

            # Overall progress
            total_progress = 0
            for enrollment in active_enrollments:
                total_progress += enrollment.progress

            avg_progress = (
                total_progress / active_enrollments.count()
                if active_enrollments.count() > 0 else 0
            )

            # Recent activity
            recent_activity = list(
                enrollments.order_by('-last_accessed_at')[:5].values(
                    'course__title',
                    'progress',
                    'last_accessed_at',
                    'status'
                )
            )

            # Recommended courses
            recommended_courses = list(
                Course.objects.get_recommended_courses(user, 3).values(
                    'title', 'difficulty', 'enrollment_count', 'average_rating'
                )
            )

            dashboard_data = {
                'metrics': {
                    'active_courses': active_enrollments.count(),
                    'completed_courses': completed_enrollments.count(),
                    'average_progress': round(avg_progress, 2),
                    'total_enrollments': enrollments.count(),
                },
                'active_courses': list(
                    active_enrollments.order_by('-last_accessed_at')[:5].values(
                        'course__title',
                        'course__difficulty',
                        'progress',
                        'last_accessed_at'
                    )
                ),
                'recent_completions': list(
                    completed_enrollments.order_by('-completion_date')[:3].values(
                        'course__title',
                        'completion_date',
                        'grade',
                        'score'
                    )
                ),
                'recent_activity': recent_activity,
                'recommended_courses': recommended_courses,
            }

            cache.set(cache_key, dashboard_data, 300)  # 5 minutes

        return dashboard_data

    def generate_course_completion_report(
        self,
        course_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Generate a course completion report.

        Args:
            course_id: Course ID
            start_date: Report start date
            end_date: Report end date

        Returns:
            Dictionary with report data
        """
        try:
            course = self.get_by_pk(course_id)

            if not course:
                return {"error": "Course not found"}

            # Set default dates
            if not end_date:
                end_date = timezone.now()
            if not start_date:
                start_date = end_date - timedelta(days=90)  # Last 90 days

            # Get enrollments in date range
            enrollments = Enrollment.objects.filter(
                course=course,
                completion_date__range=[start_date, end_date],
                status='completed'
            )

            # Calculate statistics
            total_completions = enrollments.count()
            avg_completion_time = enrollments.aggregate(
                avg_time=models.Avg(
                    models.F('completion_date') - models.F('started_at')
                )
            )['avg_time']

            # Grade distribution
            grade_distribution = dict(
                enrollments.exclude(grade='').values('grade')
                .annotate(count=models.Count('id'))
                .order_by('-count')
            )

            # Completion by week
            from django.db.models.functions import TruncWeek

            weekly_completions = list(
                enrollments.annotate(week=TruncWeek('completion_date'))
                .values('week')
                .annotate(count=models.Count('id'))
                .order_by('week')
            )

            # Top performers
            top_performers = list(
                enrollments.order_by('-score')[:10].values(
                    'content_object__username',
                    'score',
                    'grade',
                    'completion_date'
                )
            )

            return {
                'course': {
                    'title': course.title,
                    'instructor': str(course.instructor),
                    'duration': course.duration_weeks,
                },
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                },
                'summary': {
                    'total_completions': total_completions,
                    'completion_rate': round(
                        (total_completions / course.enrollment_count * 100)
                        if course.enrollment_count > 0 else 0,
                        2
                    ),
                    'average_completion_time': avg_completion_time,
                    'average_score': enrollments.aggregate(
                        avg_score=models.Avg('score')
                    )['avg_score'] or 0,
                },
                'breakdown': {
                    'grade_distribution': grade_distribution,
                    'weekly_completions': weekly_completions,
                },
                'top_performers': top_performers,
                'detailed_stats': {
                    'score_stats': enrollments.aggregate(
                        min=models.Min('score'),
                        max=models.Max('score'),
                        avg=models.Avg('score'),
                        std=models.StdDev('score'),
                    ),
                    'progress_stats': enrollments.aggregate(
                        avg_progress=models.Avg('progress'),
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error generating course report: {e}")
            return {"error": str(e)}

    @staticmethod
    def _generate_cache_key(prefix: str, params: Dict[str, Any]) -> str:
        """Generate cache key from parameters."""
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{CourseService.CACHE_PREFIX}:{prefix}:{param_hash}"

    @staticmethod
    def _apply_filters(queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """Apply filters to queryset."""
        # Handle special filters
        if 'search' in filters:
            search = filters.pop('search')
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        if 'difficulty' in filters:
            difficulty = filters.pop('difficulty')
            if difficulty:
                queryset = queryset.filter(difficulty__in=difficulty)

        if 'duration_min' in filters:
            queryset = queryset.filter(duration_weeks__gte=filters.pop('duration_min'))

        if 'duration_max' in filters:
            queryset = queryset.filter(duration_weeks__lte=filters.pop('duration_max'))

        # Apply remaining filters
        if filters:
            queryset = queryset.filter(**filters)

        return queryset

    def get_user_recommended_courses(
        self,
        user_id: int,
        limit: int = 6,
        exclude_enrolled: bool = True,
        based_on_interests: bool = True
    ) -> List[Course]:
        """
        Get personalized course recommendations for a user.

        Args:
            user_id: User ID
            limit: Maximum courses to recommend
            exclude_enrolled: Exclude already enrolled courses
            based_on_interests: Base recommendations on user interests

        Returns:
            List of recommended courses
        """
        cache_key = f"{self.CACHE_PREFIX}:user_recommended:{user_id}:{limit}:{exclude_enrolled}:{based_on_interests}"

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for user recommended courses: {user_id}")
            return cached_result

        # Get user's enrolled courses
        enrolled_courses = []
        if exclude_enrolled:
            enrolled_course_ids = Enrollment.objects.filter(
                student__user_id=user_id,
                is_active=True
            ).values_list('course_id', flat=True)

            if enrolled_course_ids:
                enrolled_courses = list(enrolled_course_ids)

        # Get user interests (from tags, categories, or previous enrollments)
        user_interests = self._get_user_interests(user_id)

        # Base queryset
        queryset = self.manager.filter(
            is_published=True,
            is_active=True
        )

        # Exclude already enrolled courses
        if enrolled_courses:
            queryset = queryset.exclude(id__in=enrolled_courses)

        # Filter by user interests if available
        if based_on_interests and user_interests:
            # This could filter by category, tags, or similar courses
            queryset = queryset.filter(
                Q(category__in=user_interests.get('categories', [])) |
                Q(tags__in=user_interests.get('tags', []))
            ).distinct()

        # Order by popularity and rating
        recommended = list(
            queryset.order_by('-student_count', '-average_rating')[:limit]
        )

        cache.set(cache_key, recommended, timeout=self.SEARCH_CACHE_TIMEOUT)
        logger.debug(f"Cached recommended courses for user: {user_id}")

        return recommended

    def get_published_courses_cached(
        self,
        filters: Dict[str, Any] = None,
        ordering: List[str] = None,
        limit: int = None,
        offset: int = None,
        include_related: bool = False
    ) -> Dict[str, Any]:
        """
        Enhanced version with user-specific filtering.
        """
        # Generate cache key
        cache_params = {
            'filters': filters or {},
            'ordering': ordering or ['-publication_date'],
            'limit': limit,
            'offset': offset,
            'include_related': include_related,
        }

        cache_key = self._generate_cache_key('published', cache_params)

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for published courses: {cache_key}")
            return {**cached_result, 'from_cache': True}

        # Build queryset
        queryset = self.manager.filter(
            is_published=True,
            is_active=True
        )

        # Include related objects if requested
        if include_related:
            queryset = queryset.select_related(
                'instructor',
                'category'
            ).prefetch_related(
                'specializations',
                'tags'
            )

        # Apply filters
        if filters:
            queryset = self._apply_filters(queryset, filters)

        # Apply ordering
        if ordering:
            queryset = queryset.order_by(*ordering)

        # Get total count
        total_count = queryset.count()

        # Apply pagination
        if offset is not None:
            queryset = queryset[offset:]
        if limit is not None:
            queryset = queryset[:limit]

        courses = list(queryset)

        result = {
            'courses': courses,
            'total_count': total_count,
            'has_more': total_count > ((offset or 0) + len(courses)),
            'filters': filters,
            'from_cache': False,
        }

        cache.set(cache_key, result, timeout=self.SEARCH_CACHE_TIMEOUT)
        logger.debug(f"Cached published courses: {cache_key}")

        return result

    def get_course_by_slug_cached(
        self,
        slug: str,
        include_related: bool = True,
        user_id: int = None
    ) -> Course | None:
        """
        Enhanced with user enrollment status.

        Args:
            slug: Course slug
            include_related: Include related objects
            user_id: Optional user ID to check enrollment status

        Returns:
            Course instance or None
        """
        cache_key = f"{self.CACHE_PREFIX}:slug:{slug}:{include_related}:{user_id}"

        course = cache.get(cache_key)
        if course is not None:
            logger.debug(f"Cache hit for course slug: {slug}")
            return course

        try:
            if include_related:
                course = self.manager.select_related(
                    'instructor',
                    'category'
                ).prefetch_related(
                    Prefetch(
                        'modules',
                        queryset=Module.objects.order_by('order').prefetch_related(
                            Prefetch(
                                'lessons',
                                queryset=Lesson.objects.filter(is_active=True).order_by('order')
                            )
                        )
                    ),
                    'specializations',
                    'tags',
                ).get(
                    slug=slug,
                    is_published=True,
                    is_active=True
                )
            else:
                course = self.manager.get(
                    slug=slug,
                    is_published=True,
                    is_active=True
                )

            # Add user enrollment status if user_id provided
            if user_id:
                from apps.lms.models.enrollment import EnrollmentsManager

                enrollment = EnrollmentsManager().get_user_enrollment_for_course(
                    user_id=user_id,
                    course_id=course.id
                )

                course.user_enrollment = {
                    'is_enrolled': enrollment is not None,
                    'enrollment': enrollment,
                    'progress_percentage': enrollment.progress_percentage if enrollment else 0,
                    'status': enrollment.status if enrollment else 'not_enrolled',
                }

            cache.set(cache_key, course, timeout=self.DEFAULT_TIMEOUT)
            logger.debug(f"Cached course slug: {slug}")
            return course

        except Course.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching course by slug {slug}: {e}")
            return None

    @staticmethod
    def _get_user_interests(user_id: int) -> Dict[str, List]:
        """
        Get user interests for course recommendations.

        Args:
            user_id: User ID

        Returns:
            Dictionary of user interests
        """
        # This is a placeholder implementation
        # In a real application, you might:
        # 1. Get user's completed courses and extract their categories/tags
        # 2. Get user's profile interests
        # 3. Get user's search history

        return {
            'categories': [],
            'tags': [],
        }

    def _get_path_courses(
        self,
        user_skills: Dict[str, Any],
        specialization_id: int = None,
        max_courses: int = 5
    ) -> List[Course]:
        """
        Get courses for learning path based on user skills.

        Args:
            user_skills: User skills assessment
            specialization_id: Optional specialization ID
            max_courses: Maximum courses to return

        Returns:
            List of courses for learning path
        """
        # Determine next skill level
        skill_areas = user_skills.get('skill_areas', {})

        # If user has no skills, start with beginner courses
        if not skill_areas:
            queryset = self.manager.filter(
                is_published=True,
                is_active=True,
                difficulty_level='beginner'
            )

            if specialization_id:
                queryset = queryset.filter(specializations__id=specialization_id)

            return list(queryset.order_by('order')[:max_courses])

        # Find strongest skill area
        strongest_area = max(skill_areas.items(), key=lambda x: x[1])[0] if skill_areas else None

        # Get courses in strongest area at next difficulty level
        if strongest_area:
            # Determine next difficulty
            completed_courses = user_skills.get('completed_courses', [])

            # Find highest difficulty in completed courses
            max_difficulty = 'beginner'
            for course in completed_courses:
                if course['difficulty'] == 'intermediate':
                    max_difficulty = 'intermediate'
                elif course['difficulty'] == 'advanced':
                    max_difficulty = 'advanced'

            # Get next level courses
            if max_difficulty == 'beginner':
                next_difficulty = 'intermediate'
            elif max_difficulty == 'intermediate':
                next_difficulty = 'advanced'
            else:
                next_difficulty = 'advanced'  # Stay at advanced for mastery

        # Build queryset
        queryset = self.manager.filter(
            is_published=True,
            is_active=True
        )

        if strongest_area:
            queryset = queryset.filter(category__name=strongest_area)

        if 'next_difficulty' in locals():
            queryset = queryset.filter(difficulty_level=next_difficulty)

        if specialization_id:
            queryset = queryset.filter(specializations__id=specialization_id)

        return list(queryset.order_by('order')[:max_courses])

