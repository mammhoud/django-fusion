"""
Management command: load dump-data.json fixture into the Wagtail database.

Same pattern as the CMS Fusion ``load_data`` command.  See the CMS version
for full documentation.

Usage::

    python manage.py load_data
    python manage.py load_data --dry-run
"""
from __future__ import annotations

import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction
from django_fusion.management.commands.base import BaseCommand


class Command(BaseCommand):
    help = "Load dump-data.json fixture with prerequisite seeding."

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--dry-run",
            action="store_true",
            help="Preview without loading.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help=(
                "Replace existing Wagtail images, sites, and child pages before "
                "loading fixtures. Omit for a non-destructive load."
            ),
        )

    def handle(self, **options):
        dry_run = options["dry_run"]
        replace_existing = options["replace"]

        # Navigate: commands/ → management/ → core/ → apps/ → backend/
        backend_dir = Path(__file__).resolve().parents[4]
        fixture_path = str(backend_dir / "assets" / "fixtures" / "dump-data.json")

        self.stdout.write(
            self.style.MIGRATE_HEADING("\n📦 load_data — dump-data.json loader\n")
        )
        self.stdout.write(f"  Fixture: {fixture_path}")
        self.stdout.write(f"  Dry-run: {'✅' if dry_run else '❌'}")
        self.stdout.write(
            f"  Replace existing content: {'✅' if replace_existing else '❌'}\n"
        )

        if not Path(fixture_path).exists():
            raise CommandError(f"Fixture not found: {fixture_path}")

        # ── Step 1: Sync content types ──────────────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Content types … "), ending="")
        if not dry_run:
            try:
                with transaction.atomic():
                    for app_config in apps.get_app_configs():
                        create_contenttypes(
                            app_config, interactive=False, verbosity=0
                        )
            except Exception as exc:
                raise CommandError("Failed to sync Django content types") from exc
            self.stdout.write(self.style.SUCCESS("✅"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        # ── Step 2: Admin superuser ─────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Admin user … "), ending="")
        if not dry_run:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            username = os.environ.get("SUPERUSER_USERNAME", "admin")
            password = os.environ.get("SUPERUSER_PASSWORD")
            email = os.environ.get("SUPERUSER_EMAIL", "")
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.SUCCESS("✅ exists"))
            elif password:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
                self.stdout.write(self.style.SUCCESS("✅ created"))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️ skipped (set SUPERUSER_PASSWORD to create an admin user)"
                    )
                )
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        # ── Step 3: Fixture-required Collections ────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Collections … "), ending="")
        if not dry_run:
            from wagtail.models import Collection

            root = Collection.objects.filter(name="Root").first()
            if root is None:
                # Fresh DB (e.g. syncdb without migrations) has no Root
                # collection yet — create the tree root first.
                root = Collection.add_root(name="Root")
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

        # ── Step 4: Optionally clear existing data ──────────────
        self.stdout.write(
            self.style.HTTP_INFO("⏳ Existing content … "),
            ending="",
        )
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "🔍 (would replace)" if replace_existing else "✅ (preserved)"
                )
            )
        elif replace_existing:
            from django.db.utils import OperationalError
            from wagtail.models import Page, Site
            from wagtail.images.models import Image as WagtailImage

            WagtailImage.objects.all().delete()
            try:
                Site.objects.all().delete()
            except OperationalError:
                pass  # wagtailredirects table may not exist
            Page.objects.filter(depth__gt=1).delete()
            self.stdout.write(self.style.SUCCESS("✅ replaced"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ preserved"))

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

        # ── Step 5b: LMS app fixtures (courses, events, …) ─────
        # Keep course fixture ownership in the dedicated command so direct
        # reloads and full-data reloads cannot drift apart.
        self.stdout.write(
            self.style.HTTP_INFO("⏳ LMS app fixtures … "), ending=""
        )
        if not dry_run:
            try:
                call_command("load_course_fixtures", verbosity=0)
            except Exception as exc:
                raise CommandError("Failed to load LMS application fixtures") from exc
            self.stdout.write(self.style.SUCCESS("✅\n"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        # ── Step 6: Default Wagtail Site ────────────────────────
        self.stdout.write(self.style.HTTP_INFO("⏳ Default Site … "), ending="")
        if not dry_run:
            from wagtail.models import Page, Site

            home = Page.objects.filter(depth=2).order_by("path").first()
            hostname = os.environ.get("SITE_DOMAIN", "localhost").split(",", 1)[0].strip()
            port = int(os.environ.get("SITE_PORT", getattr(settings, "SITE_PORT", 5071)))
            if home and not Site.objects.filter(
                is_default_site=True
            ).exists():
                Site.objects.create(
                    hostname=hostname,
                    port=port,
                    root_page=home,
                    is_default_site=True,
                    site_name=getattr(settings, "WAGTAIL_SITE_NAME", "Fusion LMS"),
                )
            elif home:
                site = Site.objects.filter(is_default_site=True).first()
                if site and (site.hostname != hostname or site.port != port):
                    site.hostname = hostname
                    site.port = port
                    site.root_page = home
                    site.save(update_fields=["hostname", "port", "root_page"])
            self.stdout.write(self.style.SUCCESS("✅"))
        else:
            self.stdout.write(self.style.WARNING("🔍 (skipped)"))

        self.stdout.write(self.style.MIGRATE_HEADING("\n📊 Summary\n"))
        self.stdout.write("  • Content types: synced\n")
        self.stdout.write("  • Admin user: ensured when SUPERUSER_PASSWORD is set\n")
        self.stdout.write("  • Collections: created\n")
        self.stdout.write(
            f"  • Existing data: {'replaced' if replace_existing else 'preserved'}\n"
        )
        self.stdout.write(
            "  • Fixture: loaded (dump-data + LMS + medical research catalog fixtures)\n"
        )
        self.stdout.write("  • Wagtail Site: configured\n")
        self.stdout.write(self.style.SUCCESS("🎉 Done!\n"))
