"""
Management command: load fusion fixtures into the Wagtail database.

Loads JSON fixture files from ``assets/fixtures/`` in dependency order
so that Wagtail models (locales, users, content types, pages, blocks)
are populated correctly.

Usage::

    # Load test fixtures (locales → users → pages)
    python manage.py load_fusion_fixtures

    # Load everything including seed content
    python manage.py load_fusion_fixtures --full

    # Load only a specific category
    python manage.py load_fusion_fixtures --category test
    python manage.py load_fusion_fixtures --category seed
    python manage.py load_fusion_fixtures --category production
    python manage.py load_fusion_fixtures --category by-model

    # Preview without loading
    python manage.py load_fusion_fixtures --dry-run
    python manage.py load_fusion_fixtures --full --dry-run

    # Load a single fixture file
    python manage.py load_fusion_fixtures --fixture test/locales.json

    # Skip missing fixture files
    python manage.py load_fusion_fixtures --full --skip-missing

Fixture dependency order
------------------------

1. **locales** — Language records (en, ar, fr, de, es, pt-br)
2. **users** — User accounts (needed for page ownership)
3. **initial_choices** — Content type choices and Wagtail image records
4. **pages** — Wagtail page tree (home, about, contact, team, courses)
5. **seed content** — Homepage blocks (sliders, features, about, CTA)
6. **by-model** — Individual model dumps (auth, wagtailcore, handlers, modules)
7. **production** — Cleaned production dumps (locales + pages)
"""
from __future__ import annotations

from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

# ── Fixture directory (relative to this command file) ────────────────
# Navigate up from apps/core/management/commands/ to the fusion project root.
# commands → management → core → apps → backend → cms-fusion (parents[5])
FIXTURE_DIR = Path(__file__).resolve().parents[5] / "assets" / "fixtures"


# ── Fixture categories with dependency-ordered paths ─────────────────

FIXTURE_CATEGORIES: dict[str, list[str]] = {
    "test": [
        "test/locales.json",
        "test/users.json",
        "test/initial_choices.json",
        "test/pages.json",
    ],
    "seed": [
        "seed/homepage_content.json",
    ],
    "production": [
        "production/just-locales.json",
        "production/cleaned-dump-data.json",
    ],
    "by-model": [
        "by-model/auth/auth-user.json",
        "by-model/auth/group_dummy.json",
        "by-model/wagtailcore/pages-homepage.json",
        "by-model/wagtailcore/wagtailcore-page.json",
        "by-model/wagtailcore/lms-coursespage.json",
        "by-model/wagtailimages/image.json",
    ],
}


class Command(BaseCommand):
    help = (
        "Load fusion fixture data from assets/fixtures/ into the Wagtail database "
        "in dependency order. Run with --dry-run to preview without loading."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--category",
            choices=["test", "seed", "production", "by-model", "all"],
            default="test",
            help="Fixture category to load (default: test). Use 'all' for everything.",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Load test + seed fixtures (cannot be used with --category).",
        )
        parser.add_argument(
            "--fixture",
            type=str,
            metavar="PATH",
            help="Load a single fixture file (relative to assets/fixtures/).",
        )
        parser.add_argument(
            "--dir",
            type=str,
            default=str(FIXTURE_DIR),
            help=f"Override fixture directory (default: {FIXTURE_DIR})",
        )
        parser.add_argument(
            "-n", "--dry-run",
            action="store_true",
            help="Preview fixtures without loading anything.",
        )
        parser.add_argument(
            "--skip-missing",
            action="store_true",
            help="Skip missing fixture files instead of raising an error.",
        )

    def handle(self, **options):
        base_dir = Path(options["dir"])
        dry_run = options["dry_run"]
        skip_missing = options["skip_missing"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n📦 Fusion Fixture Loader\n"))

        if not base_dir.exists():
            raise CommandError(
                f"Fixture directory not found: {base_dir}\n"
                f"Use --dir to specify a custom path."
            )

        # ── Single fixture mode ──────────────────────────────────
        if options["fixture"]:
            fixture_path = base_dir / options["fixture"]
            self._load_single(fixture_path, dry_run)
            return

        # ── Determine which categories to load ───────────────────
        if options["full"]:
            if options["category"] != "test":
                raise CommandError(
                    "--full and --category are mutually exclusive. "
                    "Use --full alone or --category <name> alone."
                )
            categories = ["test", "seed"]
        elif options["category"] == "all":
            categories = list(FIXTURE_CATEGORIES.keys())
        else:
            categories = [options["category"]]

        # ── Collect all fixture paths in order ───────────────────
        all_fixtures: list[tuple[str, Path]] = []
        for cat in categories:
            cat_fixtures = FIXTURE_CATEGORIES.get(cat, [])
            for rel_path in cat_fixtures:
                fpath = base_dir / rel_path
                all_fixtures.append((rel_path, fpath))

        # ── Dry-run: just list ───────────────────────────────────
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 DRY RUN — {len(all_fixtures)} fixture(s) would be loaded:\n"
                )
            )
            for rel_path, fpath in all_fixtures:
                status = "✅" if fpath.exists() else "❌ MISSING"
                size = (
                    f"({fpath.stat().st_size / 1024:.1f} KB)"
                    if fpath.exists()
                    else ""
                )
                self.stdout.write(f"  {status}  {rel_path}  {size}")
            self.stdout.write("")
            return

        # ── Load fixtures ────────────────────────────────────────
        self.stdout.write(
            self.style.HTTP_INFO(
                f"📥 Loading {len(all_fixtures)} fixture(s) "
                f"from category: {', '.join(categories)}\n"
            )
        )

        loaded = 0
        skipped = 0
        errors = 0

        for rel_path, fpath in all_fixtures:
            if not fpath.exists():
                if skip_missing:
                    self.stdout.write(f"  ⏭️  Skipping missing: {rel_path}")
                    skipped += 1
                    continue
                errors += 1
                self.stderr.write(self.style.ERROR(f"  ❌ Missing fixture: {fpath}"))
                continue

            try:
                self.stdout.write(f"  📥 {rel_path} ... ", ending="")
                call_command("loaddata", str(fpath), verbosity=0)
                self.stdout.write(self.style.SUCCESS("✅"))
                loaded += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"❌ {exc!s:.80}"))
                errors += 1

        # ── Summary ──────────────────────────────────────────────
        summary_parts = [f"✅ Loaded: {loaded}"]
        if skipped:
            summary_parts.append(f"⏭️  Skipped: {skipped}")
        if errors:
            summary_parts.append(f"❌ Errors: {errors}")
        self.stdout.write(
            self.style.SUCCESS(f"\n{' | '.join(summary_parts)}\n")
        )

        if errors and not skip_missing:
            raise CommandError(
                f"{errors} fixture(s) failed to load. "
                f"Use --skip-missing to ignore missing files."
            )

    # ── Helpers ──────────────────────────────────────────────────

    def _load_single(self, fixture_path: Path, dry_run: bool) -> None:
        """Load a single fixture file."""
        if not fixture_path.exists():
            raise CommandError(f"Fixture not found: {fixture_path}")

        if dry_run:
            size = fixture_path.stat().st_size / 1024
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 DRY RUN — would load: {fixture_path.name} ({size:.1f} KB)\n"
                )
            )
            return

        self.stdout.write(f"  📥 Loading: {fixture_path.name} ... ", ending="")
        try:
            call_command("loaddata", str(fixture_path), verbosity=1)
            self.stdout.write(self.style.SUCCESS("✅\n"))
        except Exception as exc:
            raise CommandError(f"Failed to load fixture: {exc}") from exc
