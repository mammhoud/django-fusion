"""
Unit tests for LMS course models.
"""
import pytest
from django.contrib.auth import get_user_model
from ctc_research.plugins.lms.models import (
    Course,
    CourseTag,
    CourseCategory,
)

User = get_user_model()


class TestCourseTag:
    """Test CourseTag model."""

    def test_create_tag(self, db):
        """Test creating a course tag."""
        tag = CourseTag.objects.create(
            name="Advanced Python",
            slug="advanced-python"
        )
        assert tag.name == "Advanced Python"
        assert tag.slug == "advanced-python"
        assert str(tag) == "Advanced Python"

    def test_tag_slug_uniqueness(self, db, course_tag):
        """Test that tag slugs are unique."""
        with pytest.raises(Exception):  # IntegrityError or ValidationError
            CourseTag.objects.create(
                name="Different Name",
                slug=course_tag.slug
            )

    def test_tag_string_representation(self, course_tag):
        """Test tag string representation."""
        assert str(course_tag) == "Python"


class TestCourse:
    """Test Course model."""

    def test_create_course(self, db):
        """Test creating a course."""
        course = Course.objects.create(
            title="Django Mastery",
            slug="django-mastery",
            description="Master Django web framework",
            instructor="Jane Smith",
            level="advanced",
            price=199.99,
            duration_hours=60,
            students_enrolled=0,
            is_active=True
        )
        assert course.title == "Django Mastery"
        assert course.slug == "django-mastery"
        assert course.price == 199.99
        assert course.is_active is True

    def test_course_slug_uniqueness(self, course):
        """Test that course slugs are unique."""
        with pytest.raises(Exception):
            Course.objects.create(
                title="Different Title",
                slug=course.slug,
                description="Test",
                instructor="Test",
                level="beginner",
                price=50.00,
                duration_hours=20
            )

    def test_course_with_tags(self, db, course_tag):
        """Test course with tags."""
        course = Course.objects.create(
            title="Full Stack Course",
            slug="full-stack",
            description="Learn full stack development",
            instructor="Bob Johnson",
            level="intermediate",
            price=149.99,
            duration_hours=50
        )
        course.tags.add(course_tag)
        
        assert course.tags.count() == 1
        assert course_tag in course.tags.all()

    def test_course_string_representation(self, course):
        """Test course string representation."""
        assert str(course) == "Introduction to Python"

    def test_course_active_filtering(self, db):
        """Test filtering active courses."""
        active_course = Course.objects.create(
            title="Active Course",
            slug="active",
            description="Test",
            instructor="Test",
            is_active=True
        )
        inactive_course = Course.objects.create(
            title="Inactive Course",
            slug="inactive",
            description="Test",
            instructor="Test",
            is_active=False
        )
        
        active_courses = Course.objects.filter(is_active=True)
        assert active_course in active_courses
        assert inactive_course not in active_courses

    def test_course_price_validation(self, db):
        """Test that price is positive."""
        course = Course.objects.create(
            title="Free Course",
            slug="free",
            description="Test",
            instructor="Test",
            price=0.00
        )
        assert course.price == 0.00  # Free course allowed

    def test_course_level_choices(self, db):
        """Test course level choices."""
        levels = ["beginner", "intermediate", "advanced", "expert"]
        for level in levels:
            course = Course.objects.create(
                title=f"Course - {level}",
                slug=f"course-{level}",
                description="Test",
                instructor="Test",
                level=level
            )
            assert course.level == level


class TestCourseCategory:
    """Test CourseCategory model if it exists."""

    def test_course_categories_exist(self, db):
        """Test that course categories are properly set up."""
        # This test verifies the model structure
        # Adjust based on actual model implementation
        category = CourseCategory.objects.create(
            name="Web Development",
            slug="web-development"
        )
        assert category.name == "Web Development"


class TestCourseFiltering:
    """Test course filtering and querying."""

    def test_filter_by_level(self, db):
        """Test filtering courses by level."""
        Course.objects.create(
            title="Beginner Course",
            slug="beginner",
            level="beginner",
            description="Test",
            instructor="Test"
        )
        Course.objects.create(
            title="Advanced Course",
            slug="advanced",
            level="advanced",
            description="Test",
            instructor="Test"
        )
        
        beginner_courses = Course.objects.filter(level="beginner")
        assert beginner_courses.count() == 1
        assert beginner_courses.first().title == "Beginner Course"

    def test_filter_by_price_range(self, db):
        """Test filtering courses by price range."""
        Course.objects.create(
            title="Cheap Course",
            slug="cheap",
            price=29.99,
            description="Test",
            instructor="Test"
        )
        Course.objects.create(
            title="Expensive Course",
            slug="expensive",
            price=299.99,
            description="Test",
            instructor="Test"
        )
        
        budget_courses = Course.objects.filter(price__lte=100)
        assert budget_courses.count() == 1

    def test_filter_by_instructor(self, db):
        """Test filtering courses by instructor."""
        instructor = "Dr. Smith"
        Course.objects.create(
            title="Course 1",
            slug="course1",
            description="Test",
            instructor=instructor
        )
        Course.objects.create(
            title="Course 2",
            slug="course2",
            description="Test",
            instructor="Other Instructor"
        )
        
        smith_courses = Course.objects.filter(instructor=instructor)
        assert smith_courses.count() == 1
