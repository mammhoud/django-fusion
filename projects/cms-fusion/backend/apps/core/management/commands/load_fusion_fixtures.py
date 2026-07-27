"""
Management command: load fusion test fixtures in dependency order.

Usage:
    python manage.py load_fusion_fixtures
    python manage.py load_fusion_fixtures --full  # also load homepage content
"""
from __future__ import annotations

from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand

FIXTURE_DIR = Path(__file__).resolve().parents[4] / "assets" / "fixtures"

# Order matters — Wagtail needs locales, users, and content types before pages
TEST_FIXTURES = [
    "test/locales.json",
    "test/users.json",
    "test/initial_choices.json",
    "test/pages.json",
]

# Homepage content fixtures for full data load
SEED_FIXTURES = [
    "seed/homepage_content.json",
]


class Command(BaseCommand):
    help = "Load fusion test fixtures in dependency order (locales → users → pages)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Also load seed homepage content fixtures",
        )
        parser.add_argument(
            "--dir",
            type=str,
            default=str(FIXTURE_DIR),
            help="Override fixture directory path",
        )

    def handle(self, **options):
        base_dir = Path(options["dir"])
        fixtures = list(TEST_FIXTURES)

        if options["full"]:
            fixtures += SEED_FIXTURES

        for rel_path in fixtures:
            fixture_path = base_dir / rel_path
            if not fixture_path.exists():
                self.stderr.write(f"Skipping missing fixture: {fixture_path}")
                continue

            self.stdout.write(f"Loading: {rel_path}")
            call_command("loaddata", str(fixture_path), verbosity=1)

        self.stdout.write(self.style.SUCCESS("Fixtures loaded successfully."))
