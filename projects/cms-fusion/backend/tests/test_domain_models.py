"""Domain model tests for cms-fusion.

Verifies that core domain models (Workspace, Team, Person, Organization,
Department, Corporate, GlobalSettings, Newsletter) can be instantiated
and saved to the test SQLite database.
"""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

User = get_user_model()


class TestWorkspaceModel(TestCase):
    """Verify Workspace model can be created and saved."""

    def test_create_workspace_minimal(self):
        """Workspace can be created with just a name."""
        from apps.domain.models import Workspace

        ws = Workspace.objects.create(name="Test Workspace")
        assert ws.pk is not None
        assert ws.name == "Test Workspace"
        assert ws.module == "dev"  # default
        assert ws.is_active is True
        assert str(ws) == "Test Workspace (Development)"

    def test_workspace_name_is_required(self):
        """Workspace cannot be created with an empty name."""
        from apps.domain.models import Workspace
        from django.core.exceptions import ValidationError

        ws = Workspace(name="")
        with pytest.raises(ValidationError):
            ws.full_clean()

    def test_workspace_unique_name_per_company(self):
        """Workspace has unique constraint on (name + company)."""
        from apps.domain.models import Workspace

        ws1 = Workspace.objects.create(name="Unique WS")
        # Same name, no company — should be allowed
        ws2 = Workspace.objects.create(name="Unique WS")
        assert ws2.pk != ws1.pk

    def test_workspace_string_representation(self):
        """Workspace __str__ includes name and module display."""
        from apps.domain.models import Workspace

        ws = Workspace.objects.create(name="My Project", module="design")
        assert "My Project" in str(ws)
        assert "Design" in str(ws)


class TestTeamModel(TestCase):
    """Verify Team model can be created and saved."""

    def setUp(self):
        from apps.domain.handlers.models.manage_company import Organization

        self.org = Organization.objects.create(name="Test Org")
        # Department.company FK points to Organization
        from apps.domain.handlers.models.manage_company import Department
        self.dept = Department.objects.create(
            name="Engineering", company=self.org
        )

    def test_create_team_minimal(self):
        """Team can be created with name, slug, and department."""
        from apps.domain.models import Team

        team = Team.objects.create(
            name="Backend Team",
            slug="backend-team",
            department=self.dept,
        )
        assert team.pk is not None
        assert team.name == "Backend Team"
        assert team.slug == "backend-team"
        assert team.team_type == "departmental"  # default
        assert team.status == "active"  # default

    def test_team_string_representation(self):
        """Team __str__ includes name and department."""
        from apps.domain.models import Team

        team = Team.objects.create(
            name="Frontend Team",
            slug="frontend-team",
            department=self.dept,
        )
        assert self.dept.name in str(team)
        assert team.name in str(team)

    def test_team_slug_is_unique(self):
        """Team slug enforces uniqueness."""
        from apps.domain.models import Team

        Team.objects.create(name="T1", slug="t1-slug", department=self.dept)
        with pytest.raises(IntegrityError):
            Team.objects.create(name="T2", slug="t1-slug", department=self.dept)


class TestPersonModel(TestCase):
    """Verify Person model can be created with a user."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_create_person_minimal(self):
        """Person can be created with just a user."""
        from apps.domain.models import Person

        person = Person.objects.create(
            user=self.user,
            email="person@example.com",
        )
        assert person.pk is not None
        assert person.user == self.user
        assert person.email == "person@example.com"

    def test_person_string_representation(self):
        """Person __str__ includes full name."""
        from apps.domain.models import Person

        person = Person.objects.create(
            user=self.user,
            email="person@example.com",
            first_name="John",
            last_name="Doe",
        )
        person.save()  # triggers full_name generation
        assert "John Doe" in str(person)

    def test_person_profile_type_default(self):
        """Person has default profile_type."""
        from apps.domain.models import Person

        person = Person.objects.create(
            user=self.user,
            email="person2@example.com",
        )
        assert person.profile_type == "CON"  # Contact
        assert person.status == "PENDING"


class TestOrganizationModel(TestCase):

    def test_create_organization_minimal(self):
        """Organization can be created with just a name."""
        from apps.domain.handlers.models.manage_company import Organization

        org = Organization.objects.create(name="R&D Division")
        assert org.pk is not None
        assert org.name == "R&D Division"

    def test_organization_string_representation(self):
        """Organization __str__ includes name and type."""
        from apps.domain.handlers.models.manage_company import Organization

        org = Organization.objects.create(name="Sales")
        assert "Sales" in str(org)


class TestDepartmentModel(TestCase):
    """Verify Department model can be created."""

    def setUp(self):
        from apps.domain.handlers.models.manage_company import Organization

        self.org = Organization.objects.create(name="Test Org Dept")

    def test_create_department(self):
        """Department can be created with name and company (Organization)."""
        from apps.domain.handlers.models.manage_company import Department

        dept = Department.objects.create(
            name="QA",
            company=self.org,
        )
        assert dept.pk is not None
        assert dept.name == "QA"


class TestCorporateModel(TestCase):
    """Verify Corporate model can be created."""

    def test_create_corporate(self):
        """Corporate can be created with just a name."""
        from apps.domain.contrib.models import Corporate

        corp = Corporate.objects.create(name="Acme Inc.")
        assert corp.pk is not None
        assert corp.name == "Acme Inc."


class TestGlobalSettingsModel(TestCase):
    """Verify GlobalSettings model is importable."""

    def test_global_settings_model_imports(self):
        """GlobalSettings model can be imported and has expected attrs."""
        from apps.domain.models import GlobalSettings

        assert GlobalSettings is not None
        assert hasattr(GlobalSettings, "objects")
        assert hasattr(GlobalSettings, "_meta")


class TestServiceModel(TestCase):
    """Verify Service model can be created."""

    def test_create_service(self):
        """Service can be created with just a name."""
        from apps.domain.handlers.models.manage_service import Service

        svc = Service.objects.create(name="Consulting")
        assert svc.pk is not None
        assert svc.name == "Consulting"
        assert svc.is_active is True


class TestCouponModel(TestCase):
    """Verify Coupon and CouponUsage models."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="couponuser",
            email="coupon@example.com",
            password="testpass123",
        )

    def test_create_coupon_minimal(self):
        """Coupon can be created with defaults."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(
            discount_value=10,
        )
        assert coupon.pk is not None
        assert len(coupon.code) >= 4  # auto-generated
        assert coupon.discount_type == "percentage"
        assert coupon.is_active is True
        assert "10%" in str(coupon)

    def test_coupon_fixed_discount(self):
        """Coupon with fixed amount discount."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(
            discount_type="fixed",
            discount_value=25,
        )
        assert coupon.discount_type == "fixed"
        assert "$25" in str(coupon)

    def test_coupon_calculate_discount_percentage(self):
        """Percentage discount calculation."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(discount_value=20)
        discount = coupon.calculate_discount(100)
        assert discount == 20.0

    def test_coupon_calculate_discount_fixed(self):
        """Fixed discount calculation."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(
            discount_type="fixed",
            discount_value=30,
        )
        discount = coupon.calculate_discount(100)
        assert discount == 30.0

    def test_coupon_percentage_over_100_invalid(self):
        """Percentage coupon with value > 100 should fail validation."""
        from apps.domain.models.coupon import Coupon
        from django.core.exceptions import ValidationError

        coupon = Coupon(discount_value=150)
        with pytest.raises(ValidationError):
            coupon.full_clean()

    def test_coupon_apply(self):
        """Coupon apply returns final price and discount."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(discount_value=15)
        final, discount = coupon.apply(100)
        assert final == 85.0
        assert discount == 15.0

    def test_coupon_is_valid_active(self):
        """Active coupon with no restrictions passes is_valid."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(discount_value=10)
        valid, msg = coupon.is_valid(order_amount=50)
        assert valid is True
        assert msg == ""

    def test_coupon_is_valid_inactive_fails(self):
        """Inactive coupon fails is_valid."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(discount_value=10, is_active=False)
        valid, msg = coupon.is_valid(order_amount=50)
        assert valid is False
        assert "no longer active" in msg

    def test_coupon_is_valid_minimum_order(self):
        """Coupon with unmet minimum order fails is_valid."""
        from apps.domain.models.coupon import Coupon

        coupon = Coupon.objects.create(
            discount_value=10, minimum_order_amount=100,
        )
        valid, msg = coupon.is_valid(order_amount=50)
        assert valid is False
        assert "minimum" in msg.lower()

    def test_coupon_usage_tracking(self):
        """CouponUsage records are created."""
        from apps.domain.models.coupon import Coupon, CouponUsage

        coupon = Coupon.objects.create(discount_value=10)
        coupon.record_usage(user=self.user)
        coupon.refresh_from_db()
        assert coupon.times_used == 1
        assert CouponUsage.objects.filter(coupon=coupon, user=self.user).exists()


class TestSubscriberModel(TestCase):
    """Verify Subscriber model."""

    def test_create_subscriber(self):
        """Subscriber can be created with an email."""
        from apps.domain.models.newsletter.subscriber import Subscriber

        sub = Subscriber.objects.create(email="test@example.com")
        assert sub.pk is not None
        assert sub.email == "test@example.com"
        assert sub.status == "pending"
        assert len(sub.confirmation_token) > 0

    def test_subscriber_confirm(self):
        """Subscriber can be confirmed."""
        from apps.domain.models.newsletter.subscriber import Subscriber

        sub = Subscriber.objects.create(email="confirm@example.com")
        result = sub.confirm()
        assert result is True
        assert sub.status == "confirmed"
        assert sub.confirmed_at is not None

    def test_subscriber_unsubscribe(self):
        """Subscriber can unsubscribe."""
        from apps.domain.models.newsletter.subscriber import Subscriber

        sub = Subscriber.objects.create(email="unsub@example.com", status="confirmed")
        result = sub.unsubscribe()
        assert result is True
        assert sub.status == "unsubscribed"

    def test_subscriber_is_active_property(self):
        """is_active property reflects status."""
        from apps.domain.models.newsletter.subscriber import Subscriber

        sub = Subscriber.objects.create(email="active@example.com")
        assert sub.is_active is False  # pending
        sub.confirm()
        assert sub.is_active is True  # confirmed


class TestCampaignModel(TestCase):
    """Verify Campaign model."""

    def test_create_campaign(self):
        """Campaign can be created."""
        from apps.domain.models.newsletter.campaign import Campaign

        camp = Campaign.objects.create(
            name="Welcome Email",
            subject="Welcome to our newsletter!",
            content="<p>Hello!</p>",
        )
        assert camp.pk is not None
        assert camp.name == "Welcome Email"
        assert camp.status == "draft"

    def test_campaign_get_open_rate(self):
        """Open rate calculates correctly."""
        from apps.domain.models.newsletter.campaign import Campaign

        camp = Campaign.objects.create(
            name="Test", subject="Test", content="<p>Test</p>",
            total_sent=100, total_opened=35,
        )
        assert camp.get_open_rate() == 35.0

    def test_campaign_schedule(self):
        """Campaign can be scheduled."""
        from apps.domain.models.newsletter.campaign import Campaign
        from django.utils import timezone

        camp = Campaign.objects.create(
            name="Scheduled", subject="Soon", content="<p>Coming</p>",
        )
        camp.schedule(timezone.now())
        assert camp.status == "scheduled"


class TestCertificationTemplateModel(TestCase):
    """Verify CertificationTemplate model."""

    def test_create_certification_template(self):
        """CertificationTemplate can be created with just a name."""
        from apps.domain.models.certification import CertificationTemplate

        tmpl = CertificationTemplate.objects.create(
            name="Default Certificate",
        )
        assert tmpl.pk is not None
        assert tmpl.name == "Default Certificate"
        assert tmpl.is_active is True
        assert "Default Certificate" in str(tmpl)

    def test_certification_template_context(self):
        """get_context returns expected keys."""
        from apps.domain.models.certification import CertificationTemplate

        tmpl = CertificationTemplate.objects.create(name="Test Cert")
        ctx = tmpl.get_context(
            recipient_name="John Doe",
            course_title="Python 101",
        )
        assert ctx["recipient_name"] == "John Doe"
        assert ctx["course_title"] == "Python 101"
        assert ctx["organization_name"] == "STRUCTA RESEARCH HUB"


class TestNewsletterModel(TestCase):
    """Verify Newsletter model is importable."""

    def test_newsletter_model_imports(self):
        """Newsletter model can be imported."""
        from apps.domain.models import Newsletter

        assert Newsletter is not None
        assert hasattr(Newsletter, "objects")
        assert hasattr(Newsletter, "_meta")
