"""Seed a complete demo workspace so the product can be previewed with data.

The dataset itself lives in ``apps.core.demo.seed_workspace`` (shared with the
landing's Start free signup flow). This command provisions the demo accounts
and workspace, or seeds an existing user's personal workspace with ``--user``.
Idempotent: rerunning keeps existing demo records and adds nothing new.
"""
from __future__ import annotations

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.core.demo import ensure_user_workspace, seed_workspace
from apps.core.models import UserProfile, Workspace

DEMO_WORKSPACE_SLUG = "demo-workspace"
DEMO_EMAIL = "demo@loop.dev"
DEMO_PASSWORD = "demo-pass-123"

DEMO_MEMBERS = [
    ("sales", "Sales Manager", "sales_manager"),
    ("marketing", "Marketing Manager", "marketing_manager"),
    ("revops", "RevOps Manager", "revops_manager"),
]


class Command(BaseCommand):
    help = "Seed a complete demo workspace (users, pipeline, deals, posts, finance, attribution)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            help="Seed the personal workspace of an existing user (the Start free flow) instead of the demo workspace.",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        target = options.get("user")
        if target:
            user = User.objects.filter(username=target).first() or User.objects.filter(email=target).first()
            if user is None:
                raise CommandError(f"No user matches {target!r}.")
            workspace = ensure_user_workspace(user)
            self.stdout.write(self.style.SUCCESS(
                f"Seeded {workspace.name} (slug {workspace.slug}) with the demo dataset for {user}."
            ))
            return

        workspace, _ = Workspace.objects.get_or_create(
            slug=DEMO_WORKSPACE_SLUG,
            defaults={"name": "Demo Workspace", "currency": "USD"},
        )

        admin, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": DEMO_EMAIL, "is_staff": True, "first_name": "Demo", "last_name": "Admin"},
        )
        admin.email = DEMO_EMAIL
        admin.is_staff = True
        if created:
            admin.set_password(DEMO_PASSWORD)
        admin.save()
        profile, _ = UserProfile.objects.get_or_create(user=admin)
        profile.workspace = workspace
        profile.role = "super_admin"
        profile.title = "Workspace owner"
        profile.save()
        EmailAddress.objects.get_or_create(
            user=admin, email=DEMO_EMAIL, defaults={"verified": True, "primary": True}
        )

        for key, label, role in DEMO_MEMBERS:
            member, member_created = User.objects.get_or_create(
                username=key, defaults={"email": f"{key}@loop.dev", "first_name": label.split()[0], "last_name": label.split()[-1]}
            )
            if member_created:
                member.set_password(DEMO_PASSWORD)
            member.save()
            member_profile, _ = UserProfile.objects.get_or_create(user=member)
            member_profile.workspace = workspace
            member_profile.role = role
            member_profile.save()
            EmailAddress.objects.get_or_create(
                user=member, email=f"{key}@loop.dev", defaults={"verified": True, "primary": True}
            )

        counts = seed_workspace(workspace, owner=admin)

        self.stdout.write(self.style.SUCCESS(
            f"Demo workspace ready (slug {DEMO_WORKSPACE_SLUG}) with "
            f"{counts['deals']} deals, {counts['posts']} posts, {counts['companies']} companies, "
            f"and a {counts['finance']}-step finance trail. "
            f"Sign in with {DEMO_EMAIL} / {DEMO_PASSWORD}"
        ))
