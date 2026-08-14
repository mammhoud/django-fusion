"""Sync shared BackgroundTaskLog rows into the product TaskExecution record."""

from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Mirror shared BackgroundTaskLog rows into the product TaskExecution website record."

    def add_arguments(self, parser):
        parser.add_argument(
            "--site",
            default="",
            help="Site name filter (defaults to settings.FUSION_TASK_SITE_NAME / WEBSITE).",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        site = options.get("site") or getattr(settings, "FUSION_TASK_SITE_NAME", "") or ""
        from django_fusion.tasks.views import sync_website_record

        written = sync_website_record(site)
        self.stdout.write(
            self.style.SUCCESS(f"Synced {written} task record(s) for site {site or '(all)'}.")
        )
