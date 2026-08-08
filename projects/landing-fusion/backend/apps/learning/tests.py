from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Certificate, Course, Enrollment, Lesson, LessonProgress, Module


class LearningCoreTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.instructor = User.objects.create_user("teacher@example.com", "teacher@example.com", "pass-1234")
        cls.learner = User.objects.create_user("learner@example.com", "learner@example.com", "pass-1234")
        cls.course = Course.objects.create(
            title="Shipping with Django",
            short_description="A practical course.",
            instructor=cls.instructor,
            is_published=True,
            has_certificate=True,
        )
        cls.paid_course = Course.objects.create(
            title="Paid Django Operations",
            short_description="A paid course.",
            instructor=cls.instructor,
            is_published=True,
            price="49.00",
        )
        cls.module = Module.objects.create(course=cls.course, title="Foundations", order=1)
        cls.lesson_one = Lesson.objects.create(module=cls.module, title="First deploy", order=1, is_active=True)
        cls.lesson_two = Lesson.objects.create(module=cls.module, title="Second deploy", order=2, is_active=True)

    def test_catalog_is_public_and_filterable(self):
        response = self.client.get(reverse("learning:catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shipping with Django")
        response = self.client.get(reverse("learning:catalog"), {"q": "missing"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Shipping with Django")
        self.assertNotContains(response, "<html")

    def test_course_detail_is_public(self):
        response = self.client.get(reverse("learning:course", kwargs={"slug": self.course.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Syllabus")
        self.assertContains(response, "First deploy")
        self.assertNotContains(response, "Open YouTube channel")

    def test_enrollment_requires_auth_and_htmx_opens_login(self):
        url = reverse("learning:enroll", kwargs={"slug": self.course.slug})
        response = self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 401)
        self.assertIn("fusion:open-login", response["HX-Trigger"])

    def test_paid_enrollment_does_not_grant_access(self):
        self.client.force_login(self.learner)
        response = self.client.post(
            reverse("learning:enroll", kwargs={"slug": self.paid_course.slug}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Checkout is not available yet")
        self.assertFalse(
            Enrollment.objects.filter(user=self.learner, course=self.paid_course).exists()
        )
        browser_response = self.client.post(
            reverse("learning:enroll", kwargs={"slug": self.paid_course.slug})
        )
        self.assertEqual(browser_response.status_code, 402)

    def test_enrollment_and_progress_issue_certificate(self):
        self.client.force_login(self.learner)
        enroll = self.client.post(reverse("learning:enroll", kwargs={"slug": self.course.slug}), HTTP_HX_REQUEST="true")
        self.assertEqual(enroll.status_code, 200)
        enrollment = Enrollment.objects.get(user=self.learner, course=self.course)
        self.assertEqual(enrollment.progress, 0)

        for lesson in (self.lesson_one, self.lesson_two):
            response = self.client.post(
                reverse("learning:complete_lesson", kwargs={"lesson_id": lesson.pk}),
                HTTP_HX_REQUEST="true",
            )
            self.assertEqual(response.status_code, 200)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress, 100)
        self.assertEqual(enrollment.status, Enrollment.Status.COMPLETED)
        self.assertTrue(Certificate.objects.filter(user=self.learner, course=self.course).exists())

    def test_course_detail_reflects_completed_lessons(self):
        self.client.force_login(self.learner)
        enrollment = Enrollment.objects.create(user=self.learner, course=self.course)
        LessonProgress.objects.create(enrollment=enrollment, lesson=self.lesson_one, completed=True)
        response = self.client.get(reverse("learning:course", kwargs={"slug": self.course.slug}))
        self.assertContains(response, "Completed · toggle")
        self.assertContains(response, "Mark complete")

    def test_dashboard_and_profile_use_authenticated_user(self):
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        dashboard = self.client.get(reverse("learning:dashboard"))
        profile = self.client.get(reverse("learning:profile"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, "Shipping with Django")
        self.assertEqual(profile.status_code, 200)
        self.assertContains(profile, "Account settings")

    def test_course_instructor_channel_renders_safely(self):
        self.course.youtube_channel_url = "https://www.youtube.com/@mammhoud"
        self.course.youtube_channel_name = "Mahmoud Ezzat · @mammhoud"
        self.course.save(update_fields=["youtube_channel_url", "youtube_channel_name"])
        response = self.client.get(reverse("learning:course", kwargs={"slug": self.course.slug}))
        self.assertContains(response, "Mahmoud Ezzat · @mammhoud")
        self.assertContains(response, 'href="https://www.youtube.com/@mammhoud"')
        self.assertContains(response, 'rel="noopener noreferrer"')

    def test_seeded_course_contract_is_idempotent(self):
        from apps.learning.management.commands.seed_learning import Command

        Command().handle()
        course = Course.objects.get(slug="ship-django-products")
        self.assertTrue(course.is_published)
        self.assertTrue(course.is_featured)
        self.assertTrue(course.has_certificate)
        self.assertEqual(course.youtube_channel_url, "https://www.youtube.com/@mammhoud")
        self.assertEqual(course.modules.count(), 4)
        self.assertEqual(course.lesson_count, 12)

        # A second seed must preserve the editor-managed course and not create
        # duplicate modules or lessons.
        Command().handle()
        self.assertEqual(Course.objects.filter(slug="ship-django-products").count(), 1)
        self.assertEqual(Course.objects.get(slug="ship-django-products").modules.count(), 4)
        self.assertEqual(Course.objects.get(slug="ship-django-products").lesson_count, 12)

    def test_auth_status_includes_learning_summary(self):
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.get("/apis/auth/status/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["learning"]["active"], 1)
