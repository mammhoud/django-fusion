"""Seed deterministic records for the optional Playwright browser suite."""
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.core.models import UserProfile, WorkflowDefinition, Workspace
from apps.crm.models import Company, Pipeline, PipelineStage
from apps.marketing.models import Campaign, SocialChannel

# Shared with tests/e2e/task-center.spec.mjs so the browser suite can log in
# and reach the auth-gated Task Center. Seeding (not signup) means the account
# is created without triggering allauth email-verification flows.
PLAYWRIGHT_USER = "playwright"
PLAYWRIGHT_EMAIL = "playwright@loop.dev"
PLAYWRIGHT_PASSWORD = "playwright-pass-123"


class Command(BaseCommand):
    help = "Create deterministic Loop-CRM records for Playwright browser tests."

    def handle(self, *args, **options):
        workspace, _ = Workspace.objects.get_or_create(
            slug="playwright-workspace",
            defaults={"name": "Playwright workspace", "currency": "USD"},
        )
        company, _ = Company.objects.get_or_create(
            workspace=workspace,
            name="Playwright Account",
            defaults={"industry": "Testing", "city": "Chicago"},
        )
        pipeline, _ = Pipeline.objects.get_or_create(
            workspace=workspace,
            name="Playwright pipeline",
            defaults={"is_default": True},
        )
        PipelineStage.objects.get_or_create(
            pipeline=pipeline,
            name="Qualified",
            defaults={"stage_type": "qualified", "probability": 40},
        )
        SocialChannel.objects.get_or_create(
            workspace=workspace,
            platform="linkedin",
            account_name="Playwright channel",
        )
        Campaign.objects.get_or_create(
            workspace=workspace,
            name="Playwright campaign",
        )
        User = get_user_model()
        operator, _ = User.objects.get_or_create(
            username=PLAYWRIGHT_USER,
            defaults={"email": PLAYWRIGHT_EMAIL, "is_staff": True},
        )
        operator.email = PLAYWRIGHT_EMAIL
        operator.is_staff = True
        operator.set_password(PLAYWRIGHT_PASSWORD)
        operator.save()
        # allauth's email login method resolves users through EmailAddress,
        # so the seeded operator needs a verified primary address (creating it
        # directly skips the confirmation-mail flow that real signups use).
        EmailAddress.objects.update_or_create(
            email=PLAYWRIGHT_EMAIL,
            defaults={"user": operator, "verified": True, "primary": True},
        )
        profile, _ = UserProfile.objects.get_or_create(user=operator, defaults={"workspace": workspace})
        profile.workspace = workspace
        profile.role = "super_admin"
        profile.save(update_fields=["workspace", "role"])
        workflow = WorkflowDefinition.objects.filter(slug="lead-capture", workspace__isnull=True).first()
        if workflow is None:
            self.stderr.write("Workflow templates are missing; run migrations before Playwright.")
            return
        self.stdout.write(self.style.SUCCESS(f"Playwright data ready in workspace {workspace.slug} (company {company.pk}, operator {operator.username})."))
