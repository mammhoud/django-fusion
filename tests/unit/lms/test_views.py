"""
Unit and integration tests for LMS views.
"""
import pytest
from django.urls import reverse
from django.test import Client
from ctc_research.plugins.lms.models import Course


class TestCourseViews:
    """Test course catalog views."""

    def test_catalog_view_basic(self, db, client, course):
        """Test course catalog view loads."""
        url = reverse("course_catalog")
        response = client.get(url)
        assert response.status_code == 200

    def test_catalog_contains_course(self, db, client, course):
        """Test that course appears in catalog."""
        url = reverse("course_catalog")
        response = client.get(url)
        assert course.title.encode() in response.content

    def test_catalog_grid_view(self, db, client, course):
        """Test grid view of courses."""
        url = reverse("course_catalog")
        response = client.get(url, {"view": "grid"})
        assert response.status_code == 200

    def test_catalog_list_view(self, db, client, course):
        """Test list view of courses."""
        url = reverse("course_catalog")
        response = client.get(url, {"view": "list"})
        assert response.status_code == 200

    def test_course_search(self, db, client, course):
        """Test course search functionality."""
        url = reverse("course_catalog")
        response = client.get(url, {"search": "Python"})
        assert response.status_code == 200

    def test_course_filter_by_level(self, db, client):
        """Test filtering courses by level."""
        Course.objects.create(
            title="Beginner Python",
            slug="beginner-python",
            level="beginner",
            description="Test",
            instructor="Test"
        )
        
        url = reverse("course_catalog")
        response = client.get(url, {"level": "beginner"})
        assert response.status_code == 200


class TestEnrollmentViews:
    """Test enrollment views."""

    def test_enrollment_modal_loads(self, db, client, course):
        """Test enrollment modal loads."""
        url = reverse("enroll_modal", kwargs={"course_id": course.id})
        response = client.get(url)
        assert response.status_code == 200

    def test_enrollment_form_submit(self, db, client, user, course):
        """Test enrolling in a course."""
        client.force_login(user)
        url = reverse("enroll", kwargs={"course_id": course.id})
        
        response = client.post(url, {
            "email": "student@example.com"
        })
        
        assert response.status_code in [200, 302]  # Success or redirect

    def test_enrollment_requires_login(self, db, client, course):
        """Test that enrollment requires authentication."""
        url = reverse("enroll", kwargs={"course_id": course.id})
        response = client.post(url, {
            "email": "student@example.com"
        })
        
        # Should redirect to login
        assert response.status_code in [302, 401]


class TestHTMXCourseComponents:
    """Test HTMX course components."""

    def test_course_grid_partial(self, db, client, course):
        """Test HTMX course grid partial."""
        url = reverse("course_grid")
        response = client.get(url)
        assert response.status_code == 200
        assert b"django/templates/courses/_grid.html" or b"course" in response.content

    def test_course_list_partial(self, db, client, course):
        """Test HTMX course list partial."""
        url = reverse("course_list")
        response = client.get(url)
        assert response.status_code == 200

    def test_search_results_partial(self, db, client, course):
        """Test HTMX search results partial."""
        url = reverse("course_search_results")
        response = client.get(url, {"q": "Python"})
        assert response.status_code == 200

    def test_filters_partial(self, db, client):
        """Test HTMX filters partial."""
        url = reverse("course_filters")
        response = client.get(url)
        assert response.status_code == 200

    def test_pagination_partial(self, db, client):
        """Test HTMX pagination partial."""
        # Create multiple courses for pagination
        for i in range(15):
            Course.objects.create(
                title=f"Course {i}",
                slug=f"course-{i}",
                description="Test",
                instructor="Test"
            )
        
        url = reverse("course_pagination")
        response = client.get(url, {"page": 1})
        assert response.status_code == 200


class TestHTMXEnrollmentComponents:
    """Test HTMX enrollment components."""

    def test_enrollment_form_partial(self, db, client, course):
        """Test HTMX enrollment form partial."""
        url = reverse("enrollment_form", kwargs={"course_id": course.id})
        response = client.get(url)
        assert response.status_code == 200

    def test_enrollment_status_partial(self, db, client, user, enrollment_lead):
        """Test HTMX enrollment status partial."""
        client.force_login(user)
        url = reverse("enrollment_status", kwargs={"enrollment_id": enrollment_lead.id})
        response = client.get(url)
        assert response.status_code == 200
