from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    Certificate,
    Course,
    Enrollment,
    Lesson,
    LessonProgress,
    LessonResource,
    Module,
    ModuleProgress,
    Review,
)


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

    # ── Precis-aligned metadata + routes ───────────────────────────────

    def test_seeded_course_carries_learning_metadata(self):
        """The seed populates objectives/requirements/audience + taxonomy."""
        from apps.learning.management.commands.seed_learning import Command

        Command().handle()
        course = Course.objects.get(slug="ship-django-products")
        self.assertTrue(course.objectives)
        self.assertTrue(course.requirements)
        self.assertTrue(course.target_audience)
        self.assertEqual(
            course.specializations.filter(is_active=True).first().slug, "practical-web-development"
        )
        self.assertEqual(course.tags.count(), 3)

        # Second run stays idempotent — no duplicate taxonomy rows.
        Command().handle()
        self.assertEqual(course.specializations.count(), 1)
        self.assertEqual(course.tags.count(), 3)

    def test_course_search_api_returns_seeded_course(self):
        from apps.learning.management.commands.seed_learning import Command

        Command().handle()
        response = self.client.get("/learning/api/courses/search/", {"q": "Django"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        slugs = {item["slug"] for item in data["results"]}
        self.assertIn("ship-django-products", slugs)
        match = next(
            item for item in data["results"] if item["slug"] == "ship-django-products"
        )
        self.assertIn("Django", match["tags"])
        self.assertIn("Practical Web Development", match["specializations"])
        self.assertEqual(match["lesson_count"], 12)

    def test_course_watch_requires_verified_enrollment(self):
        url = reverse("learning:course_watch", kwargs={"slug": self.course.slug})
        # Anonymous → login redirect (non-HTMX).
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Authenticated but not enrolled → back to the course dossier.
        self.client.force_login(self.learner)
        response = self.client.get(url)
        self.assertRedirects(response, reverse("learning:course", kwargs={"slug": self.course.slug}))

    def test_course_watch_renders_first_lesson_for_enrolled_learner(self):
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.get(
            reverse("learning:course_watch", kwargs={"slug": self.course.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First deploy")
        self.assertContains(response, "MARK COMPLETE")

    # ── Module progress UI + auto-advance in the lesson reader ─────────

    def test_lesson_reader_renders_module_progress(self):
        """The reader shows the per-module panel with lesson states."""
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.get(
            reverse(
                "learning:course_watch_lesson",
                kwargs={"slug": self.course.slug, "lesson_id": self.lesson_one.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "[ MODULE / FOUNDATIONS ]")
        self.assertContains(response, "learning-module-progress__bar")
        self.assertContains(response, "First deploy")
        self.assertContains(response, "Second deploy")
        self.assertContains(response, "CURRENT")
        self.assertContains(response, "0/2 LESSONS")

    def test_completing_lesson_syncs_module_progress(self):
        """Completing a lesson updates the module record + reader states."""
        self.client.force_login(self.learner)
        enrollment = Enrollment.objects.create(user=self.learner, course=self.course)
        self.client.post(
            reverse("learning:complete_lesson", kwargs={"lesson_id": self.lesson_one.pk}),
            HTTP_HX_REQUEST="true",
        )
        module_progress = ModuleProgress.objects.get(
            enrollment=enrollment, module=self.module
        )
        self.assertEqual(module_progress.progress_percentage, 50.0)
        self.assertEqual(module_progress.status, ModuleProgress.StatusChoices.IN_PROGRESS)
        # The reader for the next lesson now marks lesson one complete.
        response = self.client.get(
            reverse(
                "learning:course_watch_lesson",
                kwargs={"slug": self.course.slug, "lesson_id": self.lesson_two.pk},
            )
        )
        self.assertContains(response, "COMPLETE ✓")
        self.assertContains(response, "1/2 LESSONS")

    def test_complete_lesson_auto_advances_to_next_lesson(self):
        """Reader completion redirects (HX-Redirect) to the next lesson."""
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.post(
            reverse("learning:complete_lesson", kwargs={"lesson_id": self.lesson_one.pk}),
            {"auto_advance": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["HX-Redirect"],
            reverse(
                "learning:course_watch_lesson",
                kwargs={"slug": self.course.slug, "lesson_id": self.lesson_two.pk},
            ),
        )

    def test_complete_last_lesson_auto_advances_to_dossier(self):
        """Completing the final lesson lands back on the course dossier."""
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.post(
            reverse("learning:complete_lesson", kwargs={"lesson_id": self.lesson_two.pk}),
            {"auto_advance": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Redirect"], self.course.get_absolute_url())

    def test_marking_incomplete_with_auto_advance_does_not_redirect(self):
        """Un-completing a lesson never auto-advances (stays on the reader)."""
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        # Complete it first, then toggle it back with auto_advance present.
        self.client.post(
            reverse("learning:complete_lesson", kwargs={"lesson_id": self.lesson_one.pk}),
            HTTP_HX_REQUEST="true",
        )
        response = self.client.post(
            reverse("learning:complete_lesson", kwargs={"lesson_id": self.lesson_one.pk}),
            {"auto_advance": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("HX-Redirect", response)

    def test_complete_lesson_without_auto_advance_stays_inline(self):
        """Dossier toggles (no auto_advance) keep the inline fragment behavior."""
        self.client.force_login(self.learner)
        Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.post(
            reverse("learning:complete_lesson", kwargs={"lesson_id": self.lesson_one.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("HX-Redirect", response)

    def test_course_continue_resumes_first_incomplete_lesson(self):
        self.client.force_login(self.learner)
        enrollment = Enrollment.objects.create(user=self.learner, course=self.course)
        LessonProgress.objects.create(
            enrollment=enrollment, lesson=self.lesson_one, completed=True
        )
        response = self.client.get(
            reverse("learning:course_continue", kwargs={"slug": self.course.slug})
        )
        self.assertRedirects(
            response,
            reverse(
                "learning:course_watch_lesson",
                kwargs={"slug": self.course.slug, "lesson_id": self.lesson_two.pk},
            ),
        )

    def test_lesson_navigate_returns_neighbors(self):
        self.client.force_login(self.learner)
        response = self.client.get(
            reverse("learning:lesson_navigate", kwargs={"lesson_id": self.lesson_one.pk})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["prev_id"], None)
        self.assertEqual(data["next_id"], self.lesson_two.pk)

    def test_enrollment_list_and_status_update(self):
        self.client.force_login(self.learner)
        enrollment = Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.get(reverse("learning:enrollment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)

        response = self.client.post(
            reverse("learning:enrollment_status_update", kwargs={"enrollment_id": enrollment.pk}),
            {"status": "cancelled"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "cancelled")

    def test_enrollment_lead_form_captures_lead(self):
        self.client.force_login(self.learner)
        response = self.client.post(
            reverse("learning:course_enrollment_form", kwargs={"course_id": self.course.pk}),
            {"full_name": "Test Learner", "email": "lead@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        self.assertTrue(
            self.course.enrollment_leads.filter(email="lead@example.com").exists()
        )

    # ── Ported Precis features: ModuleProgress, LessonResource, reviews ──

    def test_module_progress_lifecycle(self):
        """ModuleProgress tracks start → in_progress → completed (Precis parity)."""
        self.client.force_login(self.learner)
        enrollment = Enrollment.objects.create(user=self.learner, course=self.course)
        progress = ModuleProgress.objects.create(
            enrollment=enrollment, module=self.module
        )
        self.assertEqual(progress.status, ModuleProgress.StatusChoices.NOT_STARTED)
        self.assertEqual(progress.progress_percentage, 0.0)

        progress.start()
        self.assertEqual(progress.status, ModuleProgress.StatusChoices.IN_PROGRESS)
        self.assertIsNotNone(progress.started_at)

        progress.update_progress(50)
        self.assertEqual(progress.progress_percentage, 50.0)
        self.assertEqual(progress.status, ModuleProgress.StatusChoices.IN_PROGRESS)

        progress.complete()
        self.assertEqual(progress.status, ModuleProgress.StatusChoices.COMPLETED)
        self.assertEqual(progress.progress_percentage, 100.0)
        self.assertIsNotNone(progress.completed_at)

    def test_module_progress_calculates_from_lesson_completions(self):
        """ModuleProgress.calculate_progress derives % from completed lessons."""
        self.client.force_login(self.learner)
        enrollment = Enrollment.objects.create(user=self.learner, course=self.course)
        progress = ModuleProgress.objects.create(
            enrollment=enrollment, module=self.module
        )
        # 1 of 2 lessons completed → 50%
        LessonProgress.objects.create(
            enrollment=enrollment, lesson=self.lesson_one, completed=True
        )
        self.assertEqual(progress.calculate_progress(), 50.0)
        self.assertEqual(progress.status, ModuleProgress.StatusChoices.IN_PROGRESS)

        LessonProgress.objects.create(
            enrollment=enrollment, lesson=self.lesson_two, completed=True
        )
        self.assertEqual(progress.calculate_progress(), 100.0)
        self.assertEqual(progress.status, ModuleProgress.StatusChoices.COMPLETED)

    def test_lesson_resource_port(self):
        """LessonResource exists and surfaces in the detail serializer."""
        resource = LessonResource.objects.create(
            lesson=self.lesson_one,
            title="Slides: first deploy",
            resource_type="slides",
            is_free=True,
        )
        self.assertEqual(str(resource), "Slides: first deploy — First deploy")
        # The module tree in the full serializer exposes the resource.
        from apps.learning.schemas.course import course_detail_to_dict

        payload = course_detail_to_dict(self.course)
        module_payload = next(m for m in payload["modules"] if m["id"] == self.module.pk)
        lesson_payload = next(
            l for l in module_payload["lessons"] if l["id"] == self.lesson_one.pk
        )
        self.assertEqual(len(lesson_payload["resources"]), 1)
        self.assertEqual(lesson_payload["resources"][0]["title"], "Slides: first deploy")
        self.assertEqual(lesson_payload["resources"][0]["resource_type"], "slides")

    def test_reviews_publishing_queryset_and_rating(self):
        """Only published reviews count toward rating/reviews_count (Precis parity)."""
        Review.objects.create(
            course=self.course, user=self.learner, rating=5, body="Great", is_published=True
        )
        Review.objects.create(
            course=self.course, user=self.instructor, rating=1, body="Draft", is_published=False
        )
        self.assertEqual(self.course.reviews.published().count(), 1)
        self.assertEqual(self.course.reviews_count, 1)
        self.assertEqual(self.course.average_rating, 5.0)
        # Unpublishing removes it from the public aggregate.
        Review.objects.filter(user=self.learner).update(is_published=False)
        self.assertEqual(self.course.reviews_count, 0)
        self.assertEqual(self.course.average_rating, 0.0)

    # ── Review / rating / resource surfacing in templates ─────────────

    def test_course_detail_surfaces_published_reviews_and_rating(self):
        """Detail dossier shows published reviews + hero rating; drafts hidden."""
        Review.objects.create(
            course=self.course, user=self.learner, rating=5, body="Great", is_published=True
        )
        Review.objects.create(
            course=self.course, user=self.instructor, rating=1, body="Draft", is_published=False
        )
        response = self.client.get(
            reverse("learning:course", kwargs={"slug": self.course.slug})
        )
        self.assertEqual(response.status_code, 200)
        # Hero metric strip: stars + average + review count.
        self.assertContains(response, "data-course-rating=\"5.0\"")
        self.assertContains(response, "★★★★★")
        self.assertContains(response, "1 REVIEWS")
        # Reviews section: published review visible, draft hidden.
        self.assertContains(response, "Course reviews")
        self.assertContains(response, "Great")
        self.assertContains(response, "learner@example.com")
        self.assertNotContains(response, "Draft")

    def test_course_detail_surfaces_lesson_resources(self):
        """Syllabus rows render lesson resources with type + FREE badge."""
        resource = LessonResource.objects.create(
            lesson=self.lesson_one,
            title="Slides: first deploy",
            resource_type="slides",
            is_free=True,
            file="lesson_resources/slides.pdf",
        )
        response = self.client.get(
            reverse("learning:course", kwargs={"slug": self.course.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-course-resources-count=\"1\"")
        self.assertContains(response, "Slides: first deploy")
        self.assertContains(response, "SLIDES")
        self.assertContains(response, "FREE")
        self.assertContains(response, resource.file.url)

    def test_catalog_cards_show_published_rating(self):
        """Catalog cards surface the annotated published rating (no N+1)."""
        Review.objects.create(
            course=self.course, user=self.learner, rating=5, body="Great", is_published=True
        )
        Review.objects.create(
            course=self.course, user=self.instructor, rating=1, body="Draft", is_published=False
        )
        from apps.learning.management.services.courses import CourseService

        courses = {c.slug: c for c in CourseService.catalog()}
        course = courses[self.course.slug]
        self.assertEqual(course.average_rating, 5.0)
        self.assertEqual(course.reviews_count, 1)
        self.assertEqual(course.rating_stars, "★★★★★")
        response = self.client.get(reverse("learning:catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "★★★★★")
        self.assertContains(response, "/ 1 REVIEWS")

    def test_course_detail_api_full_shape(self):
        """GET /learning/api/courses/<slug>/ returns the full Precis-shaped payload."""
        Review.objects.create(
            course=self.course, user=self.learner, rating=5, body="Great", is_published=True
        )
        Enrollment.objects.create(user=self.learner, course=self.course)
        response = self.client.get(
            reverse("learning:course_detail_api", kwargs={"slug": self.course.slug})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["slug"], self.course.slug)
        self.assertEqual(data["rating"], 5.0)
        self.assertEqual(data["reviews_count"], 1)
        self.assertEqual(data["enrollment_count"], 1)
        self.assertEqual(data["is_free"], True)
        self.assertEqual(len(data["modules"]), 1)
        self.assertEqual(len(data["modules"][0]["lessons"]), 2)
        self.assertEqual(len(data["reviews"]), 1)
        self.assertEqual(data["reviews"][0]["rating"], 5)

    def test_course_detail_api_404_for_unknown_slug(self):
        response = self.client.get(
            reverse("learning:course_detail_api", kwargs={"slug": "does-not-exist"})
        )
        self.assertEqual(response.status_code, 404)

    def test_review_snippet_viewset_helpers(self):
        """Admin display helpers render stars + publish state."""
        review = Review.objects.create(
            course=self.course, user=self.learner, rating=4, body="Nice", is_published=True
        )
        self.assertEqual(review.stars, "★★★★☆")
        self.assertEqual(review.short_body, "Nice")

    def test_course_response_pydantic_schema(self):
        """The typed CourseResponse schema validates the public JSON contract."""
        from apps.learning.schemas.courses import CourseResponse

        payload = CourseResponse(
            id=self.course.pk,
            title=self.course.title,
            slug=self.course.slug,
            skill_level="intermediate",
            rating=4.5,
            enrolled_count=3,
        )
        self.assertEqual(payload.slug, self.course.slug)
        self.assertEqual(payload.rating, 4.5)
        self.assertEqual(payload.enrolled_count, 3)
        self.assertEqual(payload.price_type, "Free")

    def test_review_to_dict_shape(self):
        """review_to_dict emits the Precis ReviewSchema shape."""
        from apps.learning.schemas.review import review_to_dict

        review = Review.objects.create(
            course=self.course, user=self.learner, rating=4, body="Nice", is_published=True
        )
        data = review_to_dict(review)
        self.assertEqual(data["course"]["slug"], self.course.slug)
        self.assertEqual(data["rating"], 4)
        self.assertEqual(data["comment"], "Nice")
        self.assertEqual(data["stars"], "★★★★☆")
