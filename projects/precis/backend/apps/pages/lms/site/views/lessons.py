import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django_fusion.routes.pages.handler import PageHandler

from apps.pages.lms.management.services.courses import CourseService
from apps.pages.lms.models import Course, Lesson, LessonProgress

logger = logging.getLogger(__name__)


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
        """Return course progress from the canonical lesson-progress records."""
        lessons = Lesson.objects.filter(module__course=course, is_active=True)
        total_lessons = lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=user,
            lesson__in=lessons,
            status=LessonProgress.StatusChoices.COMPLETED,
        ).count()

        return {
            'percentage': (completed_lessons / total_lessons * 100)
            if total_lessons
            else 0,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
        }

    def get_completed_lessons(self, user, course):
        """Return IDs of lessons completed by the current user."""
        return set(
            LessonProgress.objects.filter(
                user=user,
                lesson__module__course=course,
                status=LessonProgress.StatusChoices.COMPLETED,
            ).values_list('lesson_id', flat=True)
        )


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
        """Mark a lesson complete in the canonical progress model."""
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'status': LessonProgress.StatusChoices.COMPLETED,
                'progress': 100.0,
                'completed_at': timezone.now(),
            },
        )
        if not created and progress.status != LessonProgress.StatusChoices.COMPLETED:
            progress.status = LessonProgress.StatusChoices.COMPLETED
            progress.progress = 100.0
            progress.completed_at = timezone.now()
            progress.save(update_fields=['status', 'progress', 'completed_at'])

        logger.info("Lesson marked as completed: %s for user %s", lesson.title, user.username)

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
        """Return the next lesson after the user's latest completed lesson."""
        last_progress = LessonProgress.objects.filter(
            user=user,
            lesson__module__course=course,
            status=LessonProgress.StatusChoices.COMPLETED,
        ).order_by('-completed_at').first()
        if last_progress is None:
            return None

        lessons = list(
            Lesson.objects.filter(
                module__course=course,
                is_active=True,
            ).order_by('module__order', 'order')
        )
        for index, lesson in enumerate(lessons):
            if lesson.id == last_progress.lesson_id:
                return lessons[index + 1] if index + 1 < len(lessons) else lesson
        return None

    def redirect_to_lesson(self, course_slug, lesson_id):
        from django.shortcuts import redirect
        from django.urls import reverse
        url = reverse('course_watch', kwargs={'slug': course_slug, 'lesson_id': lesson_id})
        return redirect(url)