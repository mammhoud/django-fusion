"""
Pytest configuration for LMS tests.
"""
import pytest
from django.contrib.auth import get_user_model
from ctc_research.plugins.lms.models import (
    Course,
    CourseTag,
    CourseEnrollmentLead,
)

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def admin_user(db):
    """Create a test admin user."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123"
    )


@pytest.fixture
def course_tag(db):
    """Create a test course tag."""
    return CourseTag.objects.create(
        name="Python",
        slug="python"
    )


@pytest.fixture
def course(db, course_tag):
    """Create a test course."""
    course = Course.objects.create(
        title="Introduction to Python",
        slug="intro-to-python",
        description="Learn Python basics",
        instructor="John Doe",
        level="beginner",
        price=99.99,
        duration_hours=40,
        students_enrolled=0,
        is_active=True
    )
    course.tags.add(course_tag)
    return course


@pytest.fixture
def enrollment_lead(db, user, course):
    """Create a test enrollment lead."""
    return CourseEnrollmentLead.objects.create(
        course=course,
        user=user,
        email="lead@example.com",
        status="pending"
    )
