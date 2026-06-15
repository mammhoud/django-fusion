"""
Unit tests for LMS enrollment models.
"""
import pytest
from django.contrib.auth import get_user_model
from ctc_research.plugins.lms.models import (
    Course,
    CourseEnrollmentLead,
)

User = get_user_model()


class TestCourseEnrollmentLead:
    """Test CourseEnrollmentLead model."""

    def test_create_enrollment_lead(self, db, user, course):
        """Test creating an enrollment lead."""
        lead = CourseEnrollmentLead.objects.create(
            course=course,
            user=user,
            email="student@example.com",
            status="pending"
        )
        assert lead.course == course
        assert lead.user == user
        assert lead.email == "student@example.com"
        assert lead.status == "pending"

    def test_enrollment_lead_string_representation(self, enrollment_lead):
        """Test enrollment lead string representation."""
        expected = f"{enrollment_lead.user} - {enrollment_lead.course}"
        assert str(enrollment_lead) == expected

    def test_enrollment_lead_status_choices(self, db, user, course):
        """Test enrollment lead status choices."""
        statuses = ["pending", "interested", "enrolled", "completed", "canceled"]
        for status in statuses:
            lead = CourseEnrollmentLead.objects.create(
                course=course,
                user=user,
                email=f"{status}@example.com",
                status=status
            )
            assert lead.status == status

    def test_enrollment_lead_timestamps(self, db, user, course):
        """Test enrollment lead timestamps."""
        lead = CourseEnrollmentLead.objects.create(
            course=course,
            user=user,
            email="test@example.com",
            status="pending"
        )
        assert lead.created_at is not None
        assert lead.updated_at is not None

    def test_duplicate_enrollment_prevention(self, db, user, course):
        """Test that duplicate enrollments are prevented."""
        CourseEnrollmentLead.objects.create(
            course=course,
            user=user,
            email="duplicate@example.com",
            status="pending"
        )
        
        # Try to create another lead for same user/course
        # This should either raise an error or update existing
        with pytest.raises(Exception):  # IntegrityError
            CourseEnrollmentLead.objects.create(
                course=course,
                user=user,
                email="duplicate2@example.com",
                status="pending"
            )

    def test_enrollment_lead_email_field(self, enrollment_lead):
        """Test enrollment lead email field."""
        assert "@" in enrollment_lead.email
        assert enrollment_lead.email == "lead@example.com"

    def test_filter_by_status(self, db, user, course):
        """Test filtering enrollment leads by status."""
        CourseEnrollmentLead.objects.create(
            course=course,
            user=user,
            email="pending@example.com",
            status="pending"
        )
        CourseEnrollmentLead.objects.create(
            course=course,
            user=user,
            email="enrolled@example.com",
            status="enrolled"
        )
        
        pending = CourseEnrollmentLead.objects.filter(status="pending")
        enrolled = CourseEnrollmentLead.objects.filter(status="enrolled")
        
        assert pending.count() == 1
        assert enrolled.count() == 1

    def test_filter_by_course(self, db, user):
        """Test filtering enrollment leads by course."""
        course1 = Course.objects.create(
            title="Course 1",
            slug="course1",
            description="Test",
            instructor="Test"
        )
        course2 = Course.objects.create(
            title="Course 2",
            slug="course2",
            description="Test",
            instructor="Test"
        )
        
        CourseEnrollmentLead.objects.create(
            course=course1,
            user=user,
            email="lead1@example.com",
            status="pending"
        )
        CourseEnrollmentLead.objects.create(
            course=course2,
            user=user,
            email="lead2@example.com",
            status="pending"
        )
        
        course1_leads = CourseEnrollmentLead.objects.filter(course=course1)
        assert course1_leads.count() == 1

    def test_filter_by_user(self, db, course):
        """Test filtering enrollment leads by user."""
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass"
        )
        
        CourseEnrollmentLead.objects.create(
            course=course,
            user=user1,
            email="lead1@example.com",
            status="pending"
        )
        CourseEnrollmentLead.objects.create(
            course=course,
            user=user2,
            email="lead2@example.com",
            status="pending"
        )
        
        user1_leads = CourseEnrollmentLead.objects.filter(user=user1)
        assert user1_leads.count() == 1


class TestEnrollmentWorkflow:
    """Test enrollment workflow and transitions."""

    def test_enrollment_status_progression(self, db, user, course):
        """Test typical enrollment status progression."""
        lead = CourseEnrollmentLead.objects.create(
            course=course,
            user=user,
            email="workflow@example.com",
            status="pending"
        )
        
        # Simulate status transitions
        lead.status = "interested"
        lead.save()
        assert lead.status == "interested"
        
        lead.status = "enrolled"
        lead.save()
        assert lead.status == "enrolled"
        
        lead.status = "completed"
        lead.save()
        assert lead.status == "completed"

    def test_enrollment_cancellation(self, db, user, course):
        """Test canceling an enrollment."""
        lead = CourseEnrollmentLead.objects.create(
            course=course,
            user=user,
            email="cancel@example.com",
            status="enrolled"
        )
        
        lead.status = "canceled"
        lead.save()
        
        assert lead.status == "canceled"
        
        # Verify cancellation is recorded
        canceled_leads = CourseEnrollmentLead.objects.filter(status="canceled")
        assert canceled_leads.count() == 1
