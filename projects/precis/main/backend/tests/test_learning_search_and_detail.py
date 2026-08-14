"""
Regression tests for the ``/learning/`` search + course detail routes.

These routes live in ``apps.learning`` (moved from ``apps.pages.lms``). The
tests hit the real root URLconf via explicit paths (same as the e2e suite) and
lock the pre-existing fixes in ``CourseService`` (category/title lookups) and
``CourseSearchAPIView`` (page_obj derivation) plus the detail template name.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.learning.models import (
    Course,
    CourseCategory,
    CourseTag,
    Lesson,
    Module,
    Specialization,
)


class LearningSearchAndDetailRoutesTestCase(TestCase):
    """Regression tests for search API + course detail rendering."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.instructor = User.objects.create_user("t@example.com", "t@example.com", "pass-1234")
        cls.category = CourseCategory.objects.create(
            title="Clinical Research", slug="clinical-research"
        )
        cls.tag = CourseTag.objects.create(name="Biostatistics")
        cls.spec = Specialization.objects.create(
            title="Medical AI & Digital Health", slug="medical-ai-digital-health"
        )
        cls.course = Course.objects.create(
            title="Medical AI & Clinical Data Analytics",
            slug="medical-ai-clinical-data-analytics",
            short_description="Apply clinical data analytics in practice.",
            description="Full course description.",
            objectives="Build predictive models\nInterpret clinical data",
            requirements="Python basics",
            target_audience="Clinical researchers",
            instructor=cls.instructor,
            is_published=True,
            is_active=True,
            duration=6,
        )
        cls.course.categories.add(cls.category)
        cls.course.tags.add(cls.tag)
        cls.course.specializations.add(cls.spec)
        cls.module = Module.objects.create(course=cls.course, title="Module 1", order=1)
        cls.lesson = Lesson.objects.create(
            module=cls.module, title="Lesson 1", slug="lesson-1", order=1, is_active=True
        )

    def test_search_api_returns_json_results(self):
        """/learning/api/courses/search/ returns JSON with page math (no 500)."""
        response = self.client.get("/learning/api/courses/search/", {"q": "clinical"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["total"], 1)
        self.assertGreaterEqual(data["pages"], 1)
        self.assertIsInstance(data["courses"], list)

    def test_search_service_filters_by_category_title(self):
        """CourseService search resolves the categories M2M (title lookup)."""
        from apps.learning.management.services.courses import CourseService

        results = CourseService().get_published_courses_cached(
            filters={"search": "clinical"}
        )
        self.assertEqual(results["total_count"], 1)
        self.assertEqual(results["courses"][0].slug, self.course.slug)

    def test_course_detail_renders_template(self):
        """/learning/course/<slug>/ renders learning/course.html (no 500)."""
        response = self.client.get(
            f"/learning/course/{self.course.slug}/"
        )
        self.assertEqual(response.status_code, 200)
        # ``&`` is HTML-escaped to ``&amp;`` in the rendered page, so assert on
        # a plain substring of the title instead of the raw ``&``-containing one.
        self.assertContains(response, "Medical AI")
        self.assertContains(response, "Course Curriculum")

    def test_course_detail_404_for_unknown_slug(self):
        response = self.client.get("/learning/course/does-not-exist/")
        self.assertEqual(response.status_code, 404)
