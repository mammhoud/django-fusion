import logging

from django.db import models
from django.db.models.aggregates import Count
from django.http import HttpRequest
from django.utils import timezone
from django_osoul.site import PageHandler
from django_rseal.models import (
    PersonTag,
)

from plugins.lms.models import Course, Enrollment
from plugins.lms.models.courses.progress import LessonProgress

logger = logging.getLogger(__name__)


class DashboardView(PageHandler):
    """
    Enhanced dashboard view using the new manager system.
    """
    page_title = "Learning Dashboard"
    template_name = "base_profile.html"
    fragment_name = "profile.dashboard"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get comprehensive dashboard data using enhanced managers.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                # Get user enrollments with analytics
                enrollments = Enrollment.objects.get_user_enrollments(
                    user=request.user,
                    status='active',
                    include_course_details=True
                )

                enrollment_analytics = Enrollment.objects.get_enrollment_analytics(request.user)

                # Get learning path recommendations
                learning_path = Enrollment.objects.get_learning_path(
                    user=request.user,
                    max_courses=3
                )

                # Get course recommendations
                course_recommendations = Course.objects.get_recommended_courses_for_user(
                    user=request.user,
                    limit=4
                )

                # Get popular courses
                popular_courses = Course.objects.get_popular_courses_with_stats(
                    limit=3,
                    days=30
                )

                # Get tag analytics
                tag_analytics = self._get_tag_analytics(request.user)

                # Get recent activity
                recent_activity = self._get_recent_activity(request.user)

                # Get learning statistics
                learning_stats = self._get_learning_statistics(request.user)

                context.update({
                    'enrollments': enrollments,
                    'enrollment_analytics': enrollment_analytics,
                    'learning_path': learning_path,
                    'course_recommendations': course_recommendations,
                    'popular_courses': popular_courses,
                    'tag_analytics': tag_analytics,
                    'recent_activity': recent_activity,
                    'learning_stats': learning_stats,
                    'quick_actions': self._get_quick_actions(request.user),
                })

            except Exception as e:
                logger.error(f"Error getting enhanced dashboard context: {e}")
                self.show_notification(
                    message="Error loading dashboard",
                    level="error",
                    title="Error",
                    duration=5000,
                    request=request
                )

        return context

    def _get_tag_analytics(self, user):
        """Get tag analytics for dashboard."""
        from django.db.models import Count

        user_tags = PersonTag.objects.filter(
            tagged_persons__content_object__user=user,
            tagged_persons__content_object__is_active=True
        ).annotate(
            usage_count=Count('tagged_persons')
        ).order_by('-usage_count')[:10]

        return {
            'total_tags': user_tags.count(),
            'top_tags': user_tags,
            'tag_cloud': self._generate_tag_cloud(user_tags),
        }

    def _get_recent_activity(self, user):
        """Get recent learning activity."""
        activities = []

        # Recent course progress
        recent_enrollments = Enrollment.objects.filter(
            user=user,
            last_accessed_at__isnull=False
        ).order_by('-last_accessed_at')[:5]

        for enrollment in recent_enrollments:
            activities.append({
                'type': 'course_progress',
                'title': f'Progress in {enrollment.course.title}',
                'description': f'Progress: {enrollment.progress}%',
                'timestamp': enrollment.last_accessed_at,
                'icon': 'trending-up',
                'color': 'blue',
                'url': f'/courses/{enrollment.course.id}/',
            })

        # Recent lesson completions
        from plugins.accounts.models import LessonProgress

        recent_lessons = LessonProgress.objects.filter(
            user=user,
            completed_at__isnull=False
        ).select_related('lesson', 'lesson__module', 'lesson__module__course').order_by('-completed_at')[:5]

        for progress in recent_lessons:
            activities.append({
                'type': 'lesson_completion',
                'title': f'Completed: {progress.lesson.title}',
                'description': progress.lesson.module.course.title,
                'timestamp': progress.completed_at,
                'icon': 'check-circle',
                'color': 'green',
                'url': f'/courses/{progress.lesson.module.course.id}/lessons/{progress.lesson.id}/',
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:10]

    def _get_learning_statistics(self, user):
        """Get learning statistics."""
        from django.db.models import Avg, Sum

        enrollments = Enrollment.objects.filter(user=user)

        stats = enrollments.aggregate(
            total_courses=Count('id'),
            completed_courses=Count('id', filter=models.Q(status='completed')),
            active_courses=Count('id', filter=models.Q(status='active')),
            total_learning_time=Sum('total_learning_time'),
            avg_progress=Avg('progress', filter=models.Q(status='active')),
        )

        # Calculate streak
        streak = self._calculate_learning_streak(user)

        stats['learning_streak'] = streak
        stats['completion_rate'] = (
            stats['completed_courses'] / stats['total_courses'] * 100
            if stats['total_courses'] > 0 else 0
        )

        return stats

    def _calculate_learning_streak(self, user):
        """Calculate consecutive days of learning."""
        from datetime import timedelta

        today = timezone.now().date()
        streak = 0

        for i in range(30):  # Check last 30 days
            check_date = today - timedelta(days=i)

            # Check if user had any learning activity on this date
            had_activity = Enrollment.objects.filter(
                user=user,
                last_accessed_at__date=check_date
            ).exists() or LessonProgress.objects.filter(
                user=user,
                last_accessed_at__date=check_date
            ).exists()

            if had_activity:
                streak += 1
            else:
                break

        return streak

    def _get_quick_actions(self, user):
        """Get quick actions for dashboard."""
        actions = []

        # Continue learning
        latest_enrollment = Enrollment.objects.filter(
            user=user,
            status='active'
        ).order_by('-last_accessed_at').first()

        if latest_enrollment and latest_enrollment.progress < 100:
            actions.append({
                'title': 'Continue Learning',
                'description': f'Continue {latest_enrollment.course.title}',
                'icon': 'play-circle',
                'url': f'/courses/{latest_enrollment.course.id}/continue/',
                'color': 'primary',
                'priority': 1,
            })

        # Find new courses
        actions.append({
            'title': 'Browse Courses',
            'description': 'Discover new learning opportunities',
            'icon': 'compass',
            'url': '/courses/',
            'color': 'success',
            'priority': 2,
        })

        # Manage tags
        from plugins.accounts.models import Person
        person = Person.objects.filter(user=user).first()
        if person and person.tagged_items.count() < 5:
            actions.append({
                'title': 'Add Tags',
                'description': 'Tag your profile for better recommendations',
                'icon': 'tag',
                'url': '/profile/tags/',
                'color': 'warning',
                'priority': 3,
            })

        # View achievements
        completed_courses = Enrollment.objects.filter(
            user=user,
            status='completed'
        ).count()

        if completed_courses > 0:
            actions.append({
                'title': 'View Achievements',
                'description': f'You have completed {completed_courses} courses',
                'icon': 'award',
                'url': '/achievements/',
                'color': 'info',
                'priority': 4,
            })

        # Sort by priority
        actions.sort(key=lambda x: x['priority'])
        return actions
