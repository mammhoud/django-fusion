"""Run an email sync for one account, a workspace, or every active account.

Usage::

    python manage.py sync_email --account 12
    python manage.py sync_email --workspace 3
    python manage.py sync_email            # every active account
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.core.email_sync import sync_account
from apps.core.models import EmailAccount


class Command(BaseCommand):
    help = "Sync connected Gmail/Outlook accounts into the CRM timeline."

    def add_arguments(self, parser):
        parser.add_argument("--account", type=int, help="Sync one account by pk.")
        parser.add_argument("--workspace", type=int, help="Sync all active accounts in one workspace.")

    def handle(self, *args, **options):
        queryset = EmailAccount.objects.filter(is_active=True)
        if options.get("account"):
            queryset = queryset.filter(pk=options["account"])
        elif options.get("workspace"):
            queryset = queryset.filter(workspace_id=options["workspace"])

        count = 0
        for account in queryset.select_related("workspace"):
            result = sync_account(account)
            self.stdout.write(
                f"{account} → {result.status} (synced {result.synced}, "
                f"matched {result.matched}, skipped {result.skipped})"
                + (f": {result.detail}" if result.detail else "")
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Synced {count} account(s)."))
