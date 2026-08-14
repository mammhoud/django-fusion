"""
Management command: load fusion fixtures into the Wagtail database.

Loads JSON fixture files from ``assets/fixtures/`` in dependency order
so that Wagtail models (locales, users, content types, pages, blocks)
are populated correctly.

Usage::

    # Load the canonical dump-data.json fixture (locales → users →
    # content types → pages → site → homepage blocks)
    python manage.py load_fusion_fixtures --category canonical

    # Same as --category canonical (used by CI)
    python manage.py load_fusion_fixtures --full
    python manage.py load_fusion_fixtures --category all

    # Load a single fixture file
    python manage.py load_fusion_fixtures --fixture dump-data.json

    # Preview without loading
    python manage.py load_fusion_fixtures --category canonical --dry-run
    python manage.py load_fusion_fixtures --full --dry-run

    # Skip missing fixture files (only relevant for legacy categories)
    python manage.py load_fusion_fixtures --category legacy --skip-missing

Fixture categories
------------------

Only ``dump-data.json`` is shipped with the active Precis project. The
``canonical`` category (and ``--full`` / ``--category all``) loads it.

Legacy categories (``test``, ``legacy``, ``seed``, ``production``,
``by-model``) reference historical CMS Fusion fixture paths that are not
shipped here; they exist so a checked-out legacy archive can still be
loaded explicitly with ``--skip-missing`` or ``--dir``. The default
``--category test`` is intentionally a safe no-op rather than silently
loading the historical dump — use ``--category canonical`` or
``--fixture dump-data.json`` explicitly.
"""
from __future__ import annotations

from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

# ── Fixture directory (relative to this command file) ────────────────
# Navigate up from apps/core/management/commands/ to the backend root.
# commands → management → core → apps → backend (4 parents)
FIXTURE_DIR = Path(__file__).resolve().parents[4] / "assets" / "fixtures"


# ── Fixture categories with dependency-ordered paths ─────────────────

FIXTURE_CATEGORIES: dict[str, list[str]] = {
    # The active Precis project keeps one canonical export at the fixture root.
    # Older categorized paths are intentionally not guessed here: they are not
    # shipped with this project and the historical dump contains legacy model
    # labels, so loading it must remain explicit via --fixture.
    # No categorized test fixture bundle is shipped in this project. Keep the
    # default command a safe no-op rather than silently loading the historical
    # dump; use --category canonical or --fixture dump-data.json explicitly.
    "test": [],
    "canonical": ["dump-data.json"],
    "legacy": [
        # Locales first — pages reference locale FK
        "test/locales.json",
        # Users needed for page ownership
        "test/users.json",
        # Content type choices and Wagtail image records
        "test/initial_choices.json",
        # Page tree — depends on locales existing
        "test/pages.json",
        # Site config — depends on page PK=3 existing (referenced as root_page)
        "test/site.json",
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
            choices=["test", "canonical", "legacy", "seed", "production", "by-model", "all"],
            default="test",
            help="Fixture category to load (default: test, which is empty here). Use 'canonical' for dump-data.json.",
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
            # In the active project the canonical dump is the only shipped
            # fixture. Keep --full useful for CI without inventing absent
            # historical seed directories.
            categories = ["canonical"]
        elif options["category"] == "all":
            categories = ["canonical"]
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
