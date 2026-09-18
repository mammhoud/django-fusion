"""Course Center services — provisioning, querying, and lifecycle.

All schema-mutating operations are gated on ``TENANCY_ENABLED``."""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:
    from .models import CenterRegistration, CourseCenter

TENANCY_ENABLED: bool = getattr(settings, "TENANCY_ENABLED", False)

# Default roles seeded into every center's tenant schema
CENTER_ROLES = ["instructor", "student", "editor", "admin"]


def generate_verification_token() -> uuid.UUID:
    return uuid.uuid4()


class CenterQueryService:
    """Read-only queries against the center registry (public schema)."""

    @staticmethod
    def is_subdomain_available(subdomain: str) -> bool:
        from .models import CenterRegistration, CourseCenter

        taken = CourseCenter.objects.filter(slug=subdomain).exists()
        pending = CenterRegistration.objects.filter(
            subdomain=subdomain,
            status__in=[
                CenterRegistration.Status.PENDING,
                CenterRegistration.Status.VERIFIED,
            ],
        ).exists()
        return not (taken or pending)

    @staticmethod
    def active_centers():
        from .models import CourseCenter

        return CourseCenter.objects.filter(
            status=CourseCenter.Status.ACTIVE
        ).select_related("plan")


class ProvisioningService:
    """Create a fully functional Course Center with Wagtail site + seed data."""

    @classmethod
    def create_center(cls, registration: CenterRegistration) -> CourseCenter:
        """Provision a CourseCenter from an approved registration."""
        from .models import CourseCenter, CourseDomain

        plan = registration.plan
        trial_days = plan.trial_days
        trial_ends = timezone.now() + timedelta(days=trial_days) if trial_days else None

        with transaction.atomic():
            center = CourseCenter.objects.create(
                schema_name=registration.subdomain,
                slug=registration.subdomain,
                organization_name=registration.organization_name,
                plan=plan,
                tagline=registration.tagline,
                status=CourseCenter.Status.ACTIVE,
                trial_ends_at=trial_ends,
                settings={
                    "site_name": registration.organization_name,
                    "allow_self_signup": True,
                },
            )
            CourseDomain.objects.create(
                tenant=center,
                domain=f"{registration.subdomain}",
                is_primary=True,
            )

        if TENANCY_ENABLED:
            cls._seed_center_schema(center, registration.email)

        registration.status = CenterRegistration.Status.APPROVED
        registration.save(update_fields=["status"])

        cls._enqueue_welcome(center, registration.email)
        return center

    @staticmethod
    def _seed_center_schema(center: CourseCenter, admin_email: str) -> None:
        """Seed Wagtail site + home page + role groups + admin user."""
        try:
            from django_tenants.utils import tenant_context
        except ImportError:  # pragma: no cover
            return

        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group

        User = get_user_model()

        with tenant_context(center):
            # Seed the four role groups every center gets
            for group_name in CENTER_ROLES:
                Group.objects.get_or_create(name=group_name)

            # Create the center owner (admin) user with temp password
            password = User.objects.make_random_password()
            user = User.objects.create_user(
                username=admin_email,
                email=admin_email,
                password=password,
                is_staff=True,
                is_superuser=False,
            )
            admin_group = Group.objects.get(name="admin")
            user.groups.add(admin_group)

            _ensure_center_wagtail_site(center, user)

    @staticmethod
    def _enqueue_welcome(center: CourseCenter, email: str) -> None:
        """Enqueue welcome email via the task backend (best-effort)."""
        try:
            from django_fusion.tasks import enqueue

            enqueue(
                "email",
                "centers.send_welcome",
                email=email,
                center_slug=center.slug,
                organization_name=center.organization_name,
            )
        except Exception:
            pass


def _ensure_center_wagtail_site(center: CourseCenter, admin_user) -> None:
    """Create a Wagtail Site + HomePage inside the center's schema."""
    from wagtail.models import Page, Site

    from apps.pages.models import HomePage

    root_page = Page.get_first_root_node()
    if root_page is None:
        root_page = Page.add_root(title="Root")

    home = HomePage.objects.create(
        title=center.organization_name,
        slug="home",
        owner=admin_user,
    )
    root_page.add_child(instance=home)

    Site.objects.create(
        hostname=f"{center.slug}.dev.structa.cloud",
        site_name=center.organization_name,
        root_page=home,
        is_default_site=True,
    )