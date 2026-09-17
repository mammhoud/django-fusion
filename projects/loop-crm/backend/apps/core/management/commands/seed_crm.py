"""Seed the complete sales CRM fixture without requiring the full demo shell."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.core.demo import ensure_user_workspace, seed_workspace
from apps.core.models import Workspace


class Command(BaseCommand):
    help = "Seed a complete CRM fixture: pipeline, companies, contacts, deals, and activities."

    def add_arguments(self, parser):
        parser.add_argument("--user", help="Seed the existing user's workspace.")
        parser.add_argument("--workspace", dest="workspace_slug", help="Seed an existing workspace by slug.")

    def handle(self, *args, **options):
        User = get_user_model()
        user = None
        if options.get("user"):
            target = options["user"]
            user = User.objects.filter(username=target).first() or User.objects.filter(email=target).first()
            if user is None:
                raise CommandError(f"No user matches {target!r}.")
            workspace = user.profile.workspace if getattr(user, "profile", None) and user.profile.workspace_id else None
            if workspace is None:
                ensure_user_workspace(user)
                user.profile.refresh_from_db()
                workspace = user.profile.workspace
        elif options.get("workspace_slug"):
            workspace = Workspace.objects.filter(slug=options["workspace_slug"]).first()
            if workspace is None:
                raise CommandError(f"No workspace matches {options['workspace_slug']!r}.")
            user = User.objects.filter(profile__workspace=workspace).order_by("pk").first()
            if user is None:
                raise CommandError("The workspace has no member to own fixture records.")
        else:
            user = User.objects.filter(username="demo").first()
            if user is None:
                raise CommandError("Create the demo account first with `seed_demo`, or pass --user.")
            user.profile.refresh_from_db()
            workspace = user.profile.workspace

        counts = seed_workspace(workspace, owner=user)
        self.stdout.write(self.style.SUCCESS(
            "CRM fixture ready for %(workspace)s: %(companies)s companies, %(contacts)s contacts, "
            "%(deals)s deals, %(activities)s activities, %(pipelines)s pipeline." % {
                "workspace": workspace.slug,
                **counts,
            }
        ))
