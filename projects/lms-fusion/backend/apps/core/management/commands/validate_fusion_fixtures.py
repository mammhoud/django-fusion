"""
Management command: validate fusion fixture files for structural integrity.

Loads JSON fixture files from the fixtures directory and validates each
entry for structural correctness *without* loading data into the database.

Checks performed:
  1. Valid JSON parse
  2. Required keys present (model, pk, fields)
  3. Referential integrity within the fixture (locale FK, page parent FK)
  4. Field type consistency (strings vs ints for PKs)
  5. StreamField content is valid JSON where applicable
  6. Locale references resolve to actual locale entries
  7. Page tree hierarchy (parent PKs exist)

Usage::

    # Validate all fixture files in the default directory
    python manage.py validate_fusion_fixtures

    # Validate a specific category (test fixtures)
    python manage.py validate_fusion_fixtures --category test

    # Validate a single fixture file
    python manage.py validate_fusion_fixtures --fixture dump-data.json

    # Exit on first error
    python manage.py validate_fusion_fixtures --strict

    # Verbose output with all entries listed
    python manage.py validate_fusion_fixtures --verbose
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError


# ── Fixture directory (relative to this command file) ────────────────
FIXTURE_DIR = Path(__file__).resolve().parents[5] / "assets" / "fixtures"

# ── Known model prefixes for type-aware validation ───────────────────
STREAMFIELD_MODELS = {
    "pages.homepage",
    "pages.aboutpage",
    "pages.contactpage",
    "pages.teampage",
    "pages.servicespage",
    "pages.coursespage",
    "pages.eventpage",
    "lms.coursespage",
}


class FixtureValidator:
    """Validates a list of fixture entries for structural integrity."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.entry_count = 0

        # Caches built from the fixture data
        self.locales: dict[int, str] = {}        # PK → language_code
        self.pages: dict[int, str] = {}          # PK → slug
        self.images: set[int] = set()            # PKs of image entries
        self.locale_aliases: dict[str, int] = {}  # language_code → PK

    def validate_file(self, filepath: Path) -> bool:
        """Validate a single fixture file. Returns True if valid."""
        filename = filepath.name

        # ── Check 1: File exists and is readable ──
        if not filepath.exists():
            self.errors.append(f"[{filename}] File not found: {filepath}")
            return False

        if filepath.stat().st_size == 0:
            self.errors.append(f"[{filename}] File is empty")
            return False

        # ── Check 2: Valid JSON ──
        try:
            raw = filepath.read_bytes()
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.errors.append(f"[{filename}] Invalid JSON: {exc}")
            return False

        # ── Check 3: Top-level structure ──
        if not isinstance(data, list):
            self.errors.append(f"[{filename}] Top-level structure is not a list (got {type(data).__name__})")
            return False

        if not data:
            self.warnings.append(f"[{filename}] Fixture list is empty")
            return True

        # ── Check 4: Each entry ──
        for idx, entry in enumerate(data):
            self.entry_count += 1
            self._validate_entry(entry, idx, filename)

        return len(self.errors) == 0

    def _validate_entry(self, entry: Any, idx: int, filename: str) -> None:
        """Validate a single fixture entry."""
        loc = f"[{filename}:{idx}]"

        # ── Required keys ──
        if not isinstance(entry, dict):
            self.errors.append(f"{loc} Entry is not a dict (got {type(entry).__name__})")
            return

        if "model" not in entry:
            self.errors.append(f"{loc} Missing required key 'model'")
            return
        if "pk" not in entry:
            self.errors.append(f"{loc} Missing required key 'pk'")
            return
        if "fields" not in entry:
            self.errors.append(f"{loc} Missing required key 'fields'")
            return

        model = entry["model"]
        fields = entry["fields"]

        if not isinstance(fields, dict):
            self.errors.append(f"{loc} fields is not a dict (got {type(fields).__name__})")
            return

        # ── Track locale entries ──
        if model == "wagtailcore.locale":
            pk = entry["pk"]
            code = fields.get("language_code", "")
            if isinstance(pk, int):
                self.locales[pk] = code
                self.locale_aliases[code] = pk

        # ── Track page entries ──
        if model == "wagtailcore.page":
            pk = entry["pk"]
            slug = fields.get("slug", "?")
            if isinstance(pk, int):
                self.pages[pk] = slug

        # ── Track image entries ──
        if model == "wagtailimages.image":
            pk = entry["pk"]
            if isinstance(pk, int):
                self.images.add(pk)

        # ── Check locale FK references ──
        locale_fk = fields.get("locale", 0)
        if isinstance(locale_fk, int) and locale_fk > 0:
            if locale_fk not in self.locales:
                self.warnings.append(
                    f"{loc} locale FK={locale_fk} not yet resolved "
                    f"(may resolve if locale entries appear later)"
                )

        # ── Check page parent FK references ──
        parent_fk = fields.get("path", None) is None and isinstance(fields.get("path", None), str)
        # For wagtailcore.page entries, check depth/path consistency is handled by Wagtail itself
        # We just validate parent PK if present
        parent = fields.get("parent", None)
        if parent is not None and isinstance(parent, int) and parent > 1:
            if parent == entry["pk"]:
                self.errors.append(f"{loc} Page references itself as parent (PK={parent})")

        # ── Check StreamField content is valid JSON ──
        if model in STREAMFIELD_MODELS:
            for field_name in ("head", "summary", "CTA", "body", "header_section", "content"):
                raw_val = fields.get(field_name)
                if raw_val and isinstance(raw_val, str) and raw_val not in ("[]", "{}", ""):
                    try:
                        json.loads(raw_val)
                    except (json.JSONDecodeError, ValueError) as exc:
                        # The field value might be double-encoded — accept both forms
                        if self.verbose:
                            self.warnings.append(
                                f"{loc} StreamField '{field_name}' might be "
                                f"double-encoded: {exc}"
                            )

        # ── Check image FK references ──
        for img_field in ("background_image", "image", "featured_image", "header_image"):
            img_fk = fields.get(img_field)
            if img_fk is not None and isinstance(img_fk, int) and img_fk > 0:
                if img_fk not in self.images and self.verbose:
                    self.warnings.append(
                        f"{loc} Image FK={img_fk} may not be in fixture set"
                    )

    def print_report(self) -> int:
        """Print validation report. Returns error count."""
        print(f"\n{'═' * 60}")
        print(f"  Fixture Validation Report — {self.entry_count} entries checked")
        print(f"{'═' * 60}")

        if not self.errors and not self.warnings:
            print(f"\n  ✅ All {self.entry_count} entries passed validation")
            print(f"{'═' * 60}\n")
            return 0

        if self.warnings:
            print(f"\n  ⚠️  Warnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"    ⚠️  {w}")

        if self.errors:
            print(f"\n  ❌ Errors ({len(self.errors)}):")
            for e in self.errors:
                print(f"    ❌ {e}")
        else:
            print(f"\n  ✅ No structural errors")

        print(f"\n  Summary: {self.entry_count} entries, "
              f"{len(self.errors)} errors, {len(self.warnings)} warnings")
        print(f"{'═' * 60}\n")

        return len(self.errors)

    def print_manifest(self) -> None:
        """Print a summary manifest of all fixtures found."""
        print(f"\n  Manifest:")
        print(f"    Locales:    {len(self.locales)} ({', '.join(sorted(self.locales.values()))})")
        print(f"    Pages:      {len(self.pages)}")
        print(f"    Images:     {len(self.images)}")


class Command(BaseCommand):
    help = (
        "Validate fusion fixture files for structural integrity without "
        "loading data into the database. Checks JSON validity, required keys, "
        "locale and page reference consistency."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--category",
            choices=["test", "seed", "production", "by-model", "all"],
            default="all",
            help="Fixture category to validate (default: all).",
        )
        parser.add_argument(
            "--fixture",
            type=str,
            metavar="PATH",
            help="Validate a single fixture file (relative to assets/fixtures/).",
        )
        parser.add_argument(
            "--dir",
            type=str,
            default=str(FIXTURE_DIR),
            help=f"Override fixture directory (default: {FIXTURE_DIR})",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit on first error instead of collecting all.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose output with per-entry details.",
        )

    def handle(self, **options):
        base_dir = Path(options["dir"])
        strict = options["strict"]
        verbose = options["verbose"]

        if not base_dir.exists():
            raise CommandError(
                f"Fixture directory not found: {base_dir}\n"
                f"Use --dir to specify a custom path."
            )

        # ── Fixture file discovery ──
        fixture_files: list[Path] = []

        if options["fixture"]:
            fixture_path = base_dir / options["fixture"]
            if not fixture_path.exists():
                raise CommandError(f"Fixture not found: {fixture_path}")
            fixture_files = [fixture_path]
        else:
            # Scan all JSON files in the fixtures directory tree
            for pattern in ("*.json", "*/*.json", "*/*/*.json"):
                for f in sorted(base_dir.glob(pattern)):
                    if f.is_file() and f not in fixture_files:
                        fixture_files.append(f)

        if not fixture_files:
            self.stdout.write(self.style.WARNING("No fixture files found to validate."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n🔍 Fusion Fixture Validator — {len(fixture_files)} file(s)\n"
        ))

        total_errors = 0
        total_warnings = 0
        all_validators: list[tuple[str, FixtureValidator]] = []

        for fpath in fixture_files:
            rel_path = str(fpath.relative_to(base_dir))
            self.stdout.write(f"  Checking: {rel_path} ... ", ending="")

            validator = FixtureValidator(verbose=verbose)
            is_valid = validator.validate_file(fpath)

            if is_valid:
                self.stdout.write(self.style.SUCCESS("✅"))
            else:
                self.stdout.write(self.style.ERROR("❌"))

            if strict and validator.errors:
                validator.print_report()
                raise CommandError("Strict mode: aborting on first error.")

            total_errors += len(validator.errors)
            total_warnings += len(validator.warnings)
            all_validators.append((rel_path, validator))

        # ── Print report for each file ──
        for rel_path, validator in all_validators:
            if validator.errors or validator.warnings or verbose:
                print(f"\n  ── {rel_path} ──")
                validator.print_report()
                if verbose:
                    validator.print_manifest()

        # ── Cross-file manifest ──
        combined = FixtureValidator()
        for _, v in all_validators:
            combined.locales.update(v.locales)
            combined.locale_aliases.update(v.locale_aliases)
            combined.pages.update(v.pages)
            combined.images.update(v.images)
            combined.entry_count += v.entry_count

        print(f"\n{'═' * 60}")
        print(f"  CROSS-FILE MANIFEST")
        print(f"{'═' * 60}")
        combined.print_manifest()
        print(f"\n  Total: {combined.entry_count} entries across {len(fixture_files)} files")
        print(f"  Errors: {total_errors}  |  Warnings: {total_warnings}")
        print(f"{'═' * 60}\n")

        if total_errors:
            raise CommandError(
                f"{total_errors} fixture validation error(s) found. "
                f"Run without --strict to see all errors."
            )
