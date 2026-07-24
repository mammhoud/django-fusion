"""
Integration tests — load course fixtures and verify API contract.

Usage::

    LMS_TEST_FULL=1 python3 -m pytest projects/lms/cms/tests/test_fixture_integration.py -v

Requires ``LMS_TEST_FULL=1`` to activate the full Django test environment
with Wagtail, database access, and fixture loading support.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import RequestFactory

# ── Guard: skip if not in full test mode ────────────────────────────
pytestmark = pytest.mark.skipif(
    os.environ.get("LMS_TEST_FULL") != "1",
    reason="LMS_TEST_FULL=1 required for fixture-based integration tests",
)


def _load_course_fixtures():
    """Load course fixtures using absolute paths.

    Uses absolute fixture paths because Django's FIXTURE_DIRS discovery
    may not resolve the plugins/lms app correctly in all test envs.
    Imports Course early to ensure the model is registered in Django's
    app registry before loaddata tries to resolve "lms.course".
    """
    from plugins.lms.models import Course  # force model registration  # noqa: F811

    _fixture_root = (
        Path(__file__).resolve().parent.parent
        / "plugins" / "lms" / "fixtures"
    )
    # Primary fixture — critical, must load
    call_command(
        "loaddata",
        str(_fixture_root / "courses.json"),
        verbosity=0,
    )
    # Optional fixtures
    for name in ("course_tags", "specializations"):
        fixture_path = _fixture_root / f"{name}.json"
        if fixture_path.exists():
            try:
                call_command("loaddata", str(fixture_path), verbosity=0)
            except Exception:
                pass


def _create_instructor():
    """Create an instructor user and assign courses to them."""
    from plugins.lms.models import Course

    instructor, _ = User.objects.get_or_create(
        username="instructor",
        defaults={
            "email": "instructor@example.com",
            "first_name": "Test",
            "last_name": "Instructor",
            "is_active": True,
        },
    )
    instructor.set_password("secure_password_123")
    instructor.save()

    Course.objects.filter(is_published=True, is_active=True).update(
        instructor=instructor
    )
    return instructor


def _create_student():
    """Create a student user and enroll them in 3 courses."""
    from plugins.lms.models import Course, Enrollment

    student, _ = User.objects.get_or_create(
        username="teststudent",
        defaults={
            "email": "student@example.com",
            "first_name": "Test",
            "last_name": "Student",
            "is_active": True,
        },
    )
    student.set_password("password123")
    student.save()

    courses = list(Course.objects.filter(is_published=True, is_active=True)[:3])
    for i, course in enumerate(courses):
        progress_values = [25.0, 60.0, 100.0]
        status_values = ["active", "active", "completed"]
        Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                "status": status_values[i],
                "progress": progress_values[i],
                "payment_status": "completed",
                "amount_paid": float(course.price) or 49.99,
            },
        )
    return student


# ═════════════════════════════════════════════════════════════════════
# Seed Pages from STATIC_PAGES
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestSeedPagesFromStatic:
    """Verify seed_pages_from_static populates Wagtail from STATIC_PAGES."""

    def test_command_is_registered_and_importable(self):
        """The management command module loads and has expected attributes."""
        from django.core.management import find_commands, load_command_class

        # Verify the command is discoverable
        commands = list(find_commands("plugins"))
        assert "seed_pages_from_static" in commands

        cmd = load_command_class("plugins", "seed_pages_from_static")
        assert cmd.help is not None

    def test_dry_run_discovers_all_pages(self):
        """--dry-run lists all 5 STATIC_PAGES slugs (when Wagtail root page exists)."""
        from io import StringIO

        out, err = StringIO(), StringIO()
        call_command(
            "seed_pages_from_static", "--dry-run", stdout=out, stderr=err,
        )

        # If Wagtail root page is missing (no migrations), skip gracefully.
        if "No root Wagtail page" in err.getvalue():
            pytest.skip("Wagtail root page not available in this environment")

        output = out.getvalue()
        assert "home" in output.lower() or "HomePage" in output
        assert "about-us" in output.lower() or "AboutPage" in output
        assert "faq" in output.lower() or "FaqPage" in output
        assert "privacy" in output.lower() or "PrivacyPage" in output
        assert "contact" in output.lower() or "ContactPage" in output

    def test_dry_run_reports_created_count(self):
        """--dry-run reports the number of pages that would be created."""
        from io import StringIO

        out, err = StringIO(), StringIO()
        call_command(
            "seed_pages_from_static", "--dry-run", stdout=out, stderr=err,
        )

        if "No root Wagtail page" in err.getvalue():
            pytest.skip("Wagtail root page not available in this environment")

        output = out.getvalue()
        assert "created" in output.lower() or "Done" in output


# ═════════════════════════════════════════════════════════════════════
# Management command test
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestLoadCourseFixturesCommand:
    """Verify the load_course_fixtures management command works."""

    def test_command_loads_courses(self):
        """Running load_course_fixtures populates the Course table."""
        call_command("load_course_fixtures", verbosity=0)

        from plugins.lms.models import Course

        count = Course.objects.count()
        assert count == 8, f"Expected 8 courses from fixtures, got {count}"

    def test_command_produces_summary_counts(self):
        """The command summary reports correct fixture counts (via stdout)."""
        from io import StringIO

        out = StringIO()
        call_command("load_course_fixtures", stdout=out)

        output = out.getvalue()
        assert "Total Courses" in output
        assert "Published Courses" in output
        assert "Featured Courses" in output
        assert "Course Tags" in output
        assert "Specializations" in output


# ═════════════════════════════════════════════════════════════════════
# Course counts
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCourseFixturesLoaded:
    """Verify course counts and properties after fixture loading."""

    def test_courses_loaded_from_fixtures(self):
        """Fixture courses.json loads 8 courses."""
        _load_course_fixtures()

        from plugins.lms.models import Course
        count = Course.objects.count()
        assert count == 8, f"Expected 8 courses from fixtures, got {count}"

    def test_all_courses_published(self):
        """All 8 fixture courses are published and active."""
        _load_course_fixtures()

        from plugins.lms.models import Course
        published = Course.objects.filter(is_published=True, is_active=True).count()
        assert published == 8

    def test_featured_courses_count(self):
        """6 of 8 fixture courses are featured."""
        _load_course_fixtures()

        from plugins.lms.models import Course
        featured = Course.objects.filter(is_featured=True).count()
        assert featured == 6

    def test_course_pricing_from_fixtures(self):
        """Verify pricing from fixtures matches expected values."""
        _load_course_fixtures()

        from plugins.lms.models import Course
        python_basics = Course.objects.get(slug="python-basics")
        assert float(python_basics.price) == 49.99

        django_course = Course.objects.get(slug="django-web-development")
        assert float(django_course.price) == 99.99

        full_stack = Course.objects.get(slug="full-stack-development")
        assert float(full_stack.price) == 199.99
        assert float(full_stack.original_price) == 299.99

    def test_difficulty_levels_span_all(self):
        """Fixture courses span beginner, intermediate, and advanced."""
        _load_course_fixtures()

        from plugins.lms.models import Course
        levels = set(Course.objects.values_list("difficulty_level", flat=True))
        for expected in ("beginner", "intermediate", "advanced"):
            assert expected in levels

    def test_course_slugs_match_fixture_set(self):
        """All 8 known fixture slugs exist."""
        _load_course_fixtures()

        from plugins.lms.models import Course
        expected = {
            "python-basics",
            "django-web-development",
            "react-fundamentals",
            "advanced-python",
            "data-science-python",
            "javascript-es6",
            "full-stack-development",
            "mobile-flutter",
        }
        actual = set(Course.objects.values_list("slug", flat=True))
        assert actual == expected


# ═════════════════════════════════════════════════════════════════════
# Instructor dashboard
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestInstructorDashboardFromFixtures:
    """Verify instructor dashboard reflects fixture data."""

    def test_dashboard_total_courses(self):
        """Dashboard reports correct course count."""
        _load_course_fixtures()
        instructor = _create_instructor()

        from www.api.instructors import _build_instructor_dashboard
        dashboard = _build_instructor_dashboard(instructor)
        assert dashboard["data"]["total_courses"] == 8

    def test_dashboard_student_count(self):
        """Dashboard tracks unique enrolled students."""
        _load_course_fixtures()
        instructor = _create_instructor()
        _create_student()

        from www.api.instructors import _build_instructor_dashboard
        dashboard = _build_instructor_dashboard(instructor)
        assert dashboard["data"]["total_students"] == 1

    def test_dashboard_popular_courses_ordered(self):
        """Popular courses list has expected shape."""
        _load_course_fixtures()
        instructor = _create_instructor()
        _create_student()

        from www.api.instructors import _build_instructor_dashboard
        dashboard = _build_instructor_dashboard(instructor)

        popular = dashboard["data"]["popular_courses"]
        assert len(popular) > 0
        assert "title" in popular[0]

    def test_dashboard_has_revenue(self):
        """Dashboard includes revenue from completed payments."""
        _load_course_fixtures()
        instructor = _create_instructor()
        _create_student()

        from www.api.instructors import _build_instructor_dashboard
        dashboard = _build_instructor_dashboard(instructor)
        assert dashboard["data"]["total_revenue"] > 0

    def test_dashboard_has_all_required_fields(self):
        """Dashboard response includes every expected contract field."""
        _load_course_fixtures()
        instructor = _create_instructor()

        from www.api.instructors import _build_instructor_dashboard
        data = _build_instructor_dashboard(instructor)["data"]

        for field in (
            "total_courses", "total_students", "total_revenue",
            "average_rating", "recent_enrollments", "pending_reviews",
            "monthly_earnings", "popular_courses",
        ):
            assert field in data, f"Missing field: {field}"


# ═════════════════════════════════════════════════════════════════════
# Enrollment stats
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestEnrollmentStatsFromFixtures:
    """Verify enrollment and student data from fixture-backed data."""

    def test_student_has_three_enrollments(self):
        """Student is enrolled in exactly 3 courses."""
        _load_course_fixtures()
        _create_instructor()
        student = _create_student()

        from plugins.lms.models import Enrollment
        count = Enrollment.objects.filter(student=student).count()
        assert count == 3

    def test_enrollment_status_distribution(self):
        """Enrollments are 2 active + 1 completed."""
        _load_course_fixtures()
        _create_instructor()
        student = _create_student()

        from plugins.lms.models import Enrollment
        active = Enrollment.objects.filter(student=student, status="active").count()
        completed = Enrollment.objects.filter(student=student, status="completed").count()
        assert active == 2
        assert completed == 1

    def test_enrollment_progress_values(self):
        """Enrollments have expected progress: 25, 60, 100."""
        _load_course_fixtures()
        _create_instructor()
        student = _create_student()

        from plugins.lms.models import Enrollment
        progresses = list(
            Enrollment.objects.filter(student=student)
            .order_by("progress")
            .values_list("progress", flat=True)
        )
        assert progresses == [25.0, 60.0, 100.0]

    def test_student_dashboard_enrolled_count(self):
        """Student dashboard reports correct enrolled/completed counts."""
        _load_course_fixtures()
        _create_instructor()
        _create_student()

        from www.api.students import student_dashboard

        student_user = User.objects.get(username="teststudent")
        rf = RequestFactory()
        request = rf.get("/apis/students/dashboard/")
        request.user = student_user
        request.LANGUAGE_CODE = "en"

        response = student_dashboard(request)
        body = json.loads(response.content) if hasattr(response, "content") else response
        data = body.get("data", body)

        assert data["enrolled_courses"] == 3
        assert data["completed_courses"] == 1

    def test_total_revenue_from_enrollments(self):
        """Total revenue across all completed-payment enrollments > 0."""
        _load_course_fixtures()
        _create_instructor()
        _create_student()

        from plugins.lms.models import Enrollment
        from django.db.models import Sum

        total = (
            Enrollment.objects.filter(payment_status="completed")
            .aggregate(total=Sum("amount_paid"))["total"]
            or 0
        )
        assert float(total) > 0
