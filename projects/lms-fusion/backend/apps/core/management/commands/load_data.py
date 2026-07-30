"""
Management command: load dump-data.json fixture into the Wagtail database.

Same pattern as the CMS Fusion ``load_data`` command.  See the CMS version
for full documentation.

Usage::

    python manage.py load_data
    python manage.py load_data --dry-run
"""
from __future__ import annotations

from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Load dump-data.json fixture with prerequisite seeding."

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--dry-run",
            action="store_true",
            help="Preview without loading.",
        )

    def handle(self, **options):
        dry_run = options["dry_run"]

        # Navigate: commands/ → management/ → core/ → apps/ → backend/
        backend_dir = Path(__file__).resolve().parents[4]
        fixture_path = str(backend_dir / "assets" / "fixtures" / "dump-data.json")

        self.stdout.write(
            self.style.MIGRATE_HEADING("\n📦 load_data — dump-data.json loader\n")
        )
        self.stdout.write(f"  Fixture: {fixture_path}")
        self.stdout.write(f"  Dry-run: {'✅' if dry_run else '❌'}\n")

        if not Path(fixture_path).exists():
            raise CommandError(f"Fixture not found: {fixture_path}")

        # ── Step 1: Sync content types ──────────────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Content types … "), ending="")
        if not dry_run:
            from django.db import transaction

            for app_config in apps.get_app_configs():
                try:
                    with transaction.atomic():
                        create_contenttypes(
                            app_config, interactive=False, verbosity=0
                        )
                except Exception:
                    pass
            self.stdout.write(self.style.SUCCESS("✅"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        # ── Step 2: Admin superuser ─────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Admin user … "), ending="")
        if not dry_run:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    username="admin",
                    email="admin@example.com",
                    password="admin123",
                )
                self.stdout.write(self.style.SUCCESS("✅ created"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ exists"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        # ── Step 3: Fixture-required Collections ────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Collections … "), ending="")
        if not dry_run:
            from wagtail.models import Collection

            root = Collection.get_first_root_node()
            children = root.get_children()
            media = children.filter(name="Media").first()
            if not media:
                media = root.add_child(name="Media")
            if not media.get_children().filter(
                name="Main Photos (assets)"
            ).exists():
                media.add_child(name="Main Photos (assets)")
            self.stdout.write(self.style.SUCCESS("✅"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        # ── Step 4: Clear auto-created data ─────────────────────
        self.stdout.write(
            self.style.HTTP_INFO("⏳ Clearing default pages/sites/images … "),
            ending="",
        )
        if not dry_run:
            from django.db.utils import OperationalError
            from wagtail.models import Page, Site
            from wagtail.images.models import Image as WagtailImage

            WagtailImage.objects.all().delete()
            try:
                Site.objects.all().delete()
            except OperationalError:
                pass  # wagtailredirects table may not exist
            Page.objects.filter(depth__gt=1).delete()
            self.stdout.write(self.style.SUCCESS("✅"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        # ── Step 5: Load fixture ────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("📥 Loading fixture … "), ending="")
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))
            self.stdout.write(
                "\n" + self.style.WARNING(
                    "DRY RUN — no data was loaded. Run without --dry-run.\n"
                )
            )
            return

        try:
            call_command("loaddata", fixture_path, verbosity=0)
            self.stdout.write(self.style.SUCCESS("✅\n"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"❌\n"))
            raise CommandError(f"Failed to load fixture: {exc}") from exc

        # ── Step 6: Default Wagtail Site ────────────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Default Site … "), ending="")
        if not dry_run:
            from wagtail.models import Page, Site

            home = Page.objects.filter(depth=2).order_by("path").first()
            port = getattr(settings, "SITE_PORT", 5071)
            if home and not Site.objects.filter(
                is_default_site=True
            ).exists():
                Site.objects.create(
                    hostname="localhost",
                    port=port,
                    root_page=home,
                    is_default_site=True,
                    site_name="Fusion LMS",
                )
            self.stdout.write(self.style.SUCCESS("✅"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        self.stdout.write(self.style.MIGRATE_HEADING("\n📊 Summary\n"))
        self.stdout.write("  • Content types: synced\n")
        self.stdout.write("  • Admin user: created\n")
        self.stdout.write("  • Collections: created\n")
        self.stdout.write("  • Default data: cleared\n")
        self.stdout.write("  • Fixture: loaded\n")
        self.stdout.write("  • Wagtail Site: configured\n")
        self.stdout.write(self.style.SUCCESS("🎉 Done!\n"))
