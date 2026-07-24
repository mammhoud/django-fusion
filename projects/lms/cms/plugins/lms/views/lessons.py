import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

logger = logging.getLogger(__name__)
from django_fusion.site.interface.page_handler import PageHandler

from ..models import Course, Lesson
from ..management.services.courses import CourseService


class CourseWatchView(LoginRequiredMixin, PageHandler):
    """
    View for watching course lessons with navigation and progress tracking
    """
    page_title = "Course Learning"
    template_name = "learning.html"
    layout_path = "learning/skeleton.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request, **kwargs)
        course_slug = kwargs.get("slug")
        lesson_id = kwargs.get("lesson_id")

        # Get course using service
        course = CourseService.get_course_by_slug(course_slug, use_cache=True, include_details=True)
        if not course:
            raise Http404("Course not found")

        # Get current lesson using service
        current_lesson = CourseService.get_lesson_by_id(
            lesson_id,
            course_slug=course_slug,
            use_cache=True
        )
        if not current_lesson:
            raise Http404("Lesson not found")

        # Get navigation lessons using service
        next_lesson = CourseService.get_next_lesson(current_lesson, use_cache=True)
        previous_lesson = CourseService.get_previous_lesson(current_lesson, use_cache=True)

        # Get user progress
        user_progress = self.get_user_progress(request.user, course)
        completed_lessons = self.get_completed_lessons(request.user, course)

        # Build context
        context.update({
            'course': course,
            'modules': course.modules.all(),
            'lesson': current_lesson,
            'previous_lesson': previous_lesson,
            'next_lesson': next_lesson,
            'user_progress': user_progress,
            'completed_lessons': completed_lessons,
        })

        logger.info(f"Course watch loaded: {course.title} - Lesson: {current_lesson.title}")
        return self.render_to_response(context)


    def get_user_progress(self, user, course):
        """
        Get user progress for the course
        Override this method based on your progress tracking implementation
        """
        # Example implementation - adjust based on your models
        try:
            from ..models import UserProgress
            progress = UserProgress.objects.get(user=user, course=course)
            return {
                'percentage': progress.percentage,
                'completed_lessons': progress.completed_lessons_count,
                'total_lessons': progress.total_lessons,
            }
        except:
            # Fallback if no progress tracking
            total_lessons = Lesson.objects.filter(module__course=course, is_active=True).count()
            return {
                'percentage': 0,
                'completed_lessons': 0,
                'total_lessons': total_lessons,
            }

    def get_completed_lessons(self, user, course):
        """
        Get list of completed lesson IDs for this user and course
        """
        # Example implementation - adjust based on your models
        try:
            from plugins.lms.models import LessonCompletion
            completed_lessons = LessonCompletion.objects.filter(
                user=user,
                lesson__module__course=course
            ).values_list('lesson_id', flat=True)
            return set(completed_lessons)
        except:
            return set()


class LessonNavigationView(LoginRequiredMixin, PageHandler):
    """
    View for handling lesson navigation and completion
    """
    template_name = "courses/components/lesson_navigation.html"

    def post(self, request, *args, **kwargs):
        """
        Handle lesson completion and navigation
        """
        lesson_id = kwargs.get('lesson_id')
        action = request.POST.get('action')

        lesson = get_object_or_404(Lesson, id=lesson_id)

        if action == 'complete':
            self.mark_lesson_complete(request.user, lesson)
        elif action == 'navigate':
            next_lesson_id = request.POST.get('next_lesson_id')
            return self.redirect_to_lesson(lesson.module.course.slug, next_lesson_id)

        return self.redirect_to_lesson(lesson.module.course.slug, lesson_id)

    def mark_lesson_complete(self, user, lesson):
        """
        Mark a lesson as completed for the user
        """
        try:
            from plugins.lms.models import LessonCompletion
            completion, created = LessonCompletion.objects.get_or_create(
                user=user,
                lesson=lesson,
                defaults={'completed_at': timezone.now()}
            )
            if created:
                logger.info(f"Lesson marked as completed: {lesson.title} for user {user.username}")
        except Exception as e:
            logger.error(f"Error marking lesson as complete: {e}")

    def redirect_to_lesson(self, course_slug, lesson_id):
        """
        Redirect to specific lesson
        """
        from django.shortcuts import redirect
        from django.urls import reverse

        url = reverse('course_watch', kwargs={'slug': course_slug, 'lesson_id': lesson_id})
        return redirect(url)


class CourseContinueView(LoginRequiredMixin, PageHandler):
    """
    View for continuing course from last watched lesson
    """
    def get(self, request, *args, **kwargs):
        course_slug = kwargs.get('slug')
        course = get_object_or_404(Course, slug=course_slug, is_published=True)

        # Get last watched lesson for this user and course
        last_lesson = self.get_last_watched_lesson(request.user, course)

        if last_lesson:
            return self.redirect_to_lesson(course_slug, last_lesson.id)
        else:
            # Start from first lesson
            first_lesson = Lesson.objects.filter(
                module__course=course,
                is_active=True
            ).order_by('module__order', 'order').first()

            if first_lesson:
                return self.redirect_to_lesson(course_slug, first_lesson.id)
            else:
                # No lessons available
                from django.contrib import messages
                messages.warning(request, "This course doesn't have any lessons yet.")
                return redirect('course_detail', slug=course_slug)

    def get_last_watched_lesson(self, user, course):
        """
        Get the last watched lesson for user in this course
        """
        try:
            from plugins.lms.models import LessonCompletion
            # Get the most recently completed lesson
            last_completion = LessonCompletion.objects.filter(
                user=user,
                lesson__module__course=course
            ).order_by('-completed_at').first()

            if last_completion:
                # Get next lesson after the last completed one
                all_lessons = Lesson.objects.filter(
                    module__course=course,
                    is_active=True
                ).order_by('module__order', 'order')

                lesson_list = list(all_lessons)
                for idx, lesson in enumerate(lesson_list):
                    if lesson.id == last_completion.lesson.id:
                        if idx < len(lesson_list) - 1:
                            return lesson_list[idx + 1]  # Next lesson
                        else:
                            return last_completion.lesson  # Last lesson
            return None
        except:
            return None

    def redirect_to_lesson(self, course_slug, lesson_id):
        from django.shortcuts import redirect
        from django.urls import reverse
        url = reverse('course_watch', kwargs={'slug': course_slug, 'lesson_id': lesson_id})
        return redirect(url)