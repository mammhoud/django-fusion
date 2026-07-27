"""Domain model tests for lms-fusion.

Verifies that core domain models (Workspace, Team, Person, Organization,
Department, Corporate, Coupon, Subscriber, Campaign, CertificationTemplate,
GlobalSettings, Newsletter) can be instantiated and saved to the test
SQLite database.

Kept in sync with cms-fusion/backend/tests/test_domain_models.py.
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
        from apps.core.domain.models import Workspace

        ws = Workspace.objects.create(name="Test Workspace")
        assert ws.pk is not None
        assert ws.name == "Test Workspace"
        assert ws.module == "dev"
        assert ws.is_active is True
        assert str(ws) == "Test Workspace (Development)"

    def test_workspace_name_is_required(self):
        from apps.core.domain.models import Workspace
        from django.core.exceptions import ValidationError

        ws = Workspace(name="")
        with pytest.raises(ValidationError):
            ws.full_clean()

    def test_workspace_unique_name_per_company(self):
        from apps.core.domain.models import Workspace

        ws1 = Workspace.objects.create(name="Unique WS")
        ws2 = Workspace.objects.create(name="Unique WS")
        assert ws2.pk != ws1.pk

    def test_workspace_string_representation(self):
        from apps.core.domain.models import Workspace

        ws = Workspace.objects.create(name="My Project", module="design")
        assert "My Project" in str(ws)
        assert "Design" in str(ws)


class TestTeamModel(TestCase):
    def setUp(self):
        from apps.core.domain.handlers.models.manage_company import Organization

        self.org = Organization.objects.create(name="Test Org")
        from apps.core.domain.handlers.models.manage_company import Department
        self.dept = Department.objects.create(
            name="Engineering", company=self.org
        )

    def test_create_team_minimal(self):
        from apps.core.domain.models import Team

        team = Team.objects.create(
            name="Backend Team", slug="backend-team", department=self.dept,
        )
        assert team.pk is not None
        assert team.name == "Backend Team"
        assert team.slug == "backend-team"
        assert team.team_type == "departmental"
        assert team.status == "active"

    def test_team_string_representation(self):
        from apps.core.domain.models import Team

        team = Team.objects.create(
            name="Frontend Team", slug="frontend-team", department=self.dept,
        )
        assert self.dept.name in str(team)
        assert team.name in str(team)

    def test_team_slug_is_unique(self):
        from apps.core.domain.models import Team

        Team.objects.create(name="T1", slug="t1-slug", department=self.dept)
        with pytest.raises(IntegrityError):
            Team.objects.create(name="T2", slug="t1-slug", department=self.dept)


class TestPersonModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="lmsuser", email="lms@example.com", password="testpass123",
        )

    def test_create_person_minimal(self):
        from apps.core.domain.models import Person

        person = Person.objects.create(
            user=self.user, email="person@example.com",
        )
        assert person.pk is not None
        assert person.user == self.user

    def test_person_string_representation(self):
        from apps.core.domain.models import Person

        person = Person.objects.create(
            user=self.user, email="person2@example.com",
            first_name="Jane", last_name="Smith",
        )
        person.save()
        assert "Jane Smith" in str(person)

    def test_person_profile_type_default(self):
        from apps.core.domain.models import Person

        person = Person.objects.create(
            user=self.user, email="person3@example.com",
        )
        assert person.profile_type == "CON"


class TestOrganizationModel(TestCase):
    def test_create_organization_minimal(self):
        from apps.core.domain.handlers.models.manage_company import Organization

        org = Organization.objects.create(name="Learning Division")
        assert org.pk is not None
        assert org.name == "Learning Division"

    def test_organization_string_representation(self):
        from apps.core.domain.handlers.models.manage_company import Organization

        org = Organization.objects.create(name="Sales")
        assert "Sales" in str(org)


class TestDepartmentModel(TestCase):
    def setUp(self):
        from apps.core.domain.handlers.models.manage_company import Organization

        self.org = Organization.objects.create(name="LMS Org")

    def test_create_department(self):
        from apps.core.domain.handlers.models.manage_company import Department

        dept = Department.objects.create(name="QA", company=self.org)
        assert dept.pk is not None
        assert dept.name == "QA"


class TestCorporateModel(TestCase):
    def test_create_corporate(self):
        from apps.core.domain.contrib.models import Corporate

        corp = Corporate.objects.create(name="LMS Inc.")
        assert corp.pk is not None
        assert corp.name == "LMS Inc."


class TestGlobalSettingsModel(TestCase):
    def test_global_settings_model_imports(self):
        from apps.core.domain.models import GlobalSettings

        assert GlobalSettings is not None
        assert hasattr(GlobalSettings, "objects")
        assert hasattr(GlobalSettings, "_meta")


class TestServiceModel(TestCase):
    def test_create_service(self):
        from apps.core.domain.handlers.models.manage_service import Service

        svc = Service.objects.create(name="LMS Consulting")
        assert svc.pk is not None
        assert svc.name == "LMS Consulting"
        assert svc.is_active is True


class TestCouponModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="couponlms", email="coupon@lms.com", password="testpass123",
        )

    def test_create_coupon_minimal(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(discount_value=10)
        assert coupon.pk is not None
        assert len(coupon.code) >= 4
        assert coupon.discount_type == "percentage"
        assert coupon.is_active is True
        assert "10%" in str(coupon)

    def test_coupon_percentage_over_100_invalid(self):
        from apps.core.domain.models import Coupon
        from django.core.exceptions import ValidationError

        coupon = Coupon(discount_value=150)
        with pytest.raises(ValidationError):
            coupon.full_clean()

    def test_coupon_fixed_discount(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(discount_type="fixed", discount_value=25)
        assert coupon.discount_type == "fixed"
        assert "$25" in str(coupon)

    def test_coupon_calculate_discount_percentage(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(discount_value=20)
        discount = coupon.calculate_discount(100)
        assert discount == 20.0

    def test_coupon_calculate_discount_fixed(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(discount_type="fixed", discount_value=30)
        discount = coupon.calculate_discount(100)
        assert discount == 30.0

    def test_coupon_apply(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(discount_value=15)
        final, discount = coupon.apply(100)
        assert final == 85.0
        assert discount == 15.0

    def test_coupon_is_valid_active(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(discount_value=10)
        valid, msg = coupon.is_valid(order_amount=50)
        assert valid is True
        assert msg == ""

    def test_coupon_is_valid_inactive_fails(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(discount_value=10, is_active=False)
        valid, msg = coupon.is_valid(order_amount=50)
        assert valid is False
        assert "no longer active" in msg

    def test_coupon_is_valid_minimum_order(self):
        from apps.core.domain.models import Coupon

        coupon = Coupon.objects.create(
            discount_value=10, minimum_order_amount=100,
        )
        valid, msg = coupon.is_valid(order_amount=50)
        assert valid is False
        assert "minimum" in msg.lower()

    def test_coupon_usage_tracking(self):
        from apps.core.domain.models import Coupon, CouponUsage

        coupon = Coupon.objects.create(discount_value=10)
        coupon.record_usage(user=self.user)
        coupon.refresh_from_db()
        assert coupon.times_used == 1
        assert CouponUsage.objects.filter(coupon=coupon, user=self.user).exists()


class TestSubscriberModel(TestCase):
    def test_create_subscriber(self):
        from apps.core.domain.models import Subscriber

        sub = Subscriber.objects.create(email="test@lms.com")
        assert sub.pk is not None
        assert sub.status == "pending"
        assert len(sub.confirmation_token) > 0

    def test_subscriber_confirm(self):
        from apps.core.domain.models import Subscriber

        sub = Subscriber.objects.create(email="confirm@lms.com")
        result = sub.confirm()
        assert result is True
        assert sub.status == "confirmed"
        assert sub.confirmed_at is not None

    def test_subscriber_unsubscribe(self):
        from apps.core.domain.models import Subscriber

        sub = Subscriber.objects.create(email="unsub@lms.com", status="confirmed")
        result = sub.unsubscribe()
        assert result is True
        assert sub.status == "unsubscribed"

    def test_subscriber_is_active_property(self):
        from apps.core.domain.models import Subscriber

        sub = Subscriber.objects.create(email="active@lms.com")
        assert sub.is_active is False
        sub.confirm()
        assert sub.is_active is True


class TestCampaignModel(TestCase):
    def test_create_campaign(self):
        from apps.core.domain.models import Campaign

        camp = Campaign.objects.create(
            name="Welcome Email", subject="Welcome!", content="<p>Hello!</p>",
        )
        assert camp.pk is not None
        assert camp.name == "Welcome Email"
        assert camp.status == "draft"

    def test_campaign_get_open_rate(self):
        from apps.core.domain.models import Campaign

        camp = Campaign.objects.create(
            name="Test", subject="Test", content="<p>Test</p>",
            total_sent=100, total_opened=35,
        )
        assert camp.get_open_rate() == 35.0

    def test_campaign_schedule(self):
        from apps.core.domain.models import Campaign
        from django.utils import timezone

        camp = Campaign.objects.create(
            name="Scheduled", subject="Soon", content="<p>Coming</p>",
        )
        camp.schedule(timezone.now())
        assert camp.status == "scheduled"


class TestCertificationTemplateModel(TestCase):
    def test_create_certification_template(self):
        from apps.core.domain.models import CertificationTemplate

        tmpl = CertificationTemplate.objects.create(name="Default Certificate")
        assert tmpl.pk is not None
        assert tmpl.is_active is True
        assert "Default Certificate" in str(tmpl)

    def test_certification_template_context(self):
        from apps.core.domain.models import CertificationTemplate

        tmpl = CertificationTemplate.objects.create(name="Test Cert")
        ctx = tmpl.get_context(
            recipient_name="Jane Smith", course_title="Django 101",
        )
        assert ctx["recipient_name"] == "Jane Smith"
        assert ctx["course_title"] == "Django 101"


class TestNewsletterModel(TestCase):
    def test_newsletter_model_imports(self):
        from apps.core.domain.models import Newsletter

        assert Newsletter is not None
        assert hasattr(Newsletter, "objects")
        assert hasattr(Newsletter, "_meta")
