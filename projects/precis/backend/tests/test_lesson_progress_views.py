"""Regression tests for canonical lesson-progress view behavior."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.pages.lms.models import Course, Lesson, LessonProgress, Module
from apps.pages.lms.site.views.lessons import (
    CourseContinueView,
    CourseWatchView,
    LessonNavigationView,
)


class LessonProgressViewTests(TestCase):
    """Ensure lesson views use LessonProgress consistently."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="lesson-progress-user",
            email="lesson-progress@example.com",
            password="test-password",
        )
        cls.course = Course.objects.create(
            title="Progress Test Course",
            slug="progress-test-course",
            instructor=cls.user,
            is_published=True,
            is_active=True,
        )
        cls.module = Module.objects.create(
            course=cls.course,
            title="Progress Test Module",
            order=1,
        )
        cls.first_lesson = Lesson.objects.create(
            module=cls.module,
            title="First Lesson",
            slug="progress-first-lesson",
            order=1,
            is_active=True,
        )
        cls.second_lesson = Lesson.objects.create(
            module=cls.module,
            title="Second Lesson",
            slug="progress-second-lesson",
            order=2,
            is_active=True,
        )

    def test_course_progress_comes_from_lesson_progress(self):
        view = CourseWatchView()

        initial = view.get_user_progress(self.user, self.course)
        self.assertEqual(initial["total_lessons"], 2)
        self.assertEqual(initial["completed_lessons"], 0)
        self.assertEqual(initial["percentage"], 0)

        LessonProgress.objects.create(
            user=self.user,
            lesson=self.first_lesson,
            status=LessonProgress.StatusChoices.COMPLETED,
            progress=100,
        )

        progress = view.get_user_progress(self.user, self.course)
        self.assertEqual(progress["completed_lessons"], 1)
        self.assertEqual(progress["percentage"], 50)
        self.assertEqual(
            view.get_completed_lessons(self.user, self.course),
            {self.first_lesson.pk},
        )

    def test_mark_complete_updates_existing_lesson_progress(self):
        progress = LessonProgress.objects.create(
            user=self.user,
            lesson=self.first_lesson,
            status=LessonProgress.StatusChoices.IN_PROGRESS,
            progress=40,
        )

        LessonNavigationView().mark_lesson_complete(self.user, self.first_lesson)

        progress.refresh_from_db()
        self.assertEqual(progress.status, LessonProgress.StatusChoices.COMPLETED)
        self.assertEqual(progress.progress, 100)
        self.assertIsNotNone(progress.completed_at)

    def test_continue_returns_next_lesson_after_latest_completion(self):
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.first_lesson,
            status=LessonProgress.StatusChoices.COMPLETED,
            progress=100,
        )

        next_lesson = CourseContinueView().get_last_watched_lesson(
            self.user,
            self.course,
        )

        self.assertEqual(next_lesson, self.second_lesson)
