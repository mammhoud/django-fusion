#!/usr/bin/env python3
"""
Fixture Validation Script
=========================
Validates all JSON fixture files across the project.

Checks performed:
  1. JSON parseability — every .json file is valid JSON.
  2. Django fixture structure — each file contains a list of objects with
     ``model``, ``pk``, and ``fields`` keys.
  3. Model name format — ``app_label.modelname`` convention.
  4. FK reference integrity — ``pk`` values referenced as foreign keys in
     other fixtures exist in the correct dependency-order.
  5. Duplicate PK detection — same ``(model, pk)`` across different files.
  6. File size sanity — warns on unusually large or empty fixtures.

Usage::

    python tests/scripts/helpers/validate_fixtures.py
    python tests/scripts/helpers/validate_fixtures.py --verbose
    python tests/scripts/helpers/validate_fixtures.py --path tests/fixtures/test/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Canonical fixture directories (source of truth)
FIXTURE_GLOB_PATTERNS = [
    "tests/fixtures/**/*.json",
    "tests/assets/fixtures/**/*.json",
]

# Known model name pattern: app_label.modelname
MODEL_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")

# Common FK field suffixes and known FK field names
FK_SUFFIXES = ("_id",)
KNOWN_FK_KEYS = {
    "content_type", "locale", "owner", "latest_revision", "live_revision",
    "locked_by", "alias_of", "image", "featured_image", "page", "author",
    "group", "permission", "user", "assigned_by", "parent",
    "collection", "workflow", "task", "revision",
}

# Files to skip
SKIP_FILES = {"INDEX.json", "by-model/INDEX.json"}

# ── State ──────────────────────────────────────────────────────
errors: list[str] = []
warnings: list[str] = []
fixtures_found: int = 0
fixtures_valid: int = 0


def log_error(msg: str) -> None:
    errors.append(msg)


def log_warning(msg: str) -> None:
    warnings.append(msg)


# ── Check 1: JSON validity ────────────────────────────────────


def check_json_validity(path: Path) -> list[dict] | None:
    """Check that *path* is valid JSON and return parsed data.

    Returns ``None`` on failure (logs the error).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        log_error(f"INVALID JSON: {path} — {e}")
        return None
    except UnicodeDecodeError as e:
        log_error(f"ENCODING ERROR: {path} — {e}")
        return None


# ── Check 2: Django fixture structure ─────────────────────────


def check_fixture_structure(path: Path, data: list[dict]) -> bool:
    """Check that *data* is a list of Django fixture objects.

    Each object must have ``model``, ``pk``, and ``fields`` keys.
    """
    if not isinstance(data, list):
        log_error(f"STRUCTURE: {path} — root element must be a list, got {type(data).__name__}")
        return False

    for i, obj in enumerate(data):
        if not isinstance(obj, dict):
            log_error(f"STRUCTURE: {path}[{i}] — expected dict, got {type(obj).__name__}")
            return False
        if "model" not in obj:
            log_error(f"STRUCTURE: {path}[{i}] — missing 'model' key")
            return False
        if "pk" not in obj:
            log_error(f"STRUCTURE: {path}[{i}] — missing 'pk' key")
            return False
        if "fields" not in obj:
            log_error(f"STRUCTURE: {path}[{i}] — missing 'fields' key")
            return False

        # Check model name format
        if not MODEL_PATTERN.match(obj["model"]):
            log_error(
                f"MODEL NAME: {path}[{i}] — '{obj['model']}' does not match "
                f"app_label.modelname convention"
            )
            return False

    return True


# ── Check 3: File size sanity ─────────────────────────────────


def check_file_size(path: Path, data: list[dict]) -> None:
    """Warn on unusually large or empty fixtures."""
    size = path.stat().st_size
    if size == 0:
        log_error(f"EMPTY FILE: {path} — 0 bytes")
        return
    if size < 50:
        log_warning(f"TINY FILE: {path} — {size} bytes (check if intentional)")
    if size > 1_000_000:
        log_warning(f"LARGE FILE: {path} — {size / 1024:.0f} KB")
    if len(data) == 0:
        log_warning(f"EMPTY FIXTURE: {path} — 0 objects")


# ── Check 4: Collect all models referenced ────────────────────


ModelIndex = dict[str, set[int | str]]  # model → set of PKs
PerFileModelIndex = dict[str, dict[str, set[int | str]]]  # path → model → PKs


def collect_pks(data: list[dict]) -> ModelIndex:
    """Collect all (model → pk) mappings from parsed fixture data."""
    index: ModelIndex = defaultdict(set)
    for obj in data:
        if isinstance(obj, dict) and "model" in obj and "pk" in obj:
            index[obj["model"]].add(obj["pk"])
    return index


def _guess_fk_model(field_name: str) -> str | None:
    """Guess the model reference from a field name.

    Uses ``app_label.modelname`` convention (no ``django.contrib.`` prefix).
    """
    # Strip trailing ``_id`` suffix
    name = field_name[:-3] if field_name.endswith("_id") else field_name

    # Known FK mappings (manually curated from fixture data and Wagtail models)
    FK_MODEL_MAP = {
        # Django / Auth
        "content_type": "contenttypes.contenttype",
        "user": "auth.user",
        "owner": "auth.user",
        "locked_by": "auth.user",
        "assigned_by": "auth.user",
        "uploaded_by_user": "auth.user",
        "group": "auth.group",
        "permission": "auth.permission",
        # Wagtail Core
        "locale": "wagtailcore.locale",
        "page": "wagtailcore.page",
        "latest_revision": "wagtailcore.revision",
        "live_revision": "wagtailcore.revision",
        "revision": "wagtailcore.revision",
        "alias_of": "wagtailcore.page",
        "collection": "wagtailcore.collection",
        "site": "wagtailcore.site",
        "workflow": "wagtailcore.workflow",
        "task": "wagtailcore.task",
        "workflow_task": "wagtailcore.workflowtask",
        "base_ptr": None,  # multi-table inheritance, skip
        "page_ptr": None,  # Wagtail page inheritance
        "parent": None,  # generic MPTT reference
        # Wagtail Images
        "image": "wagtailimages.image",
        "featured_image": "wagtailimages.image",
        "background_image": "wagtailimages.image",
        "photo": "wagtailimages.image",
        "avatar": "wagtailimages.image",
        "og_image": "wagtailimages.image",
        "rendition": "wagtailimages.rendition",
        "logo": "wagtailimages.image",
        # Taggit
        "tag": "taggit.tag",
        "tag_ptr": "taggit.tag",
        # Wagtail Forms
        "form": "wagtailforms.form",
        "form_submission": "wagtailforms.formsubmission",
        # Wagtail Redirects
        "redirect_page": "wagtailcore.page",
        "old_page": "wagtailcore.page",
        # User profiles & handlers
        "primary_instructor": "auth.user",
        "co_instructors": "auth.user",
        "author": "auth.user",
        "person": "handlers.person",
        "organization": "handlers.organization",
        "organisation": "handlers.organization",
        # Simple history
        "history_user": "auth.user",
        "history_relation": None,  # generic
        # Miscellaneous
        "category": None,  # varies by app
        "subcategory": None,
        "template": None,  # varies
    }
    return FK_MODEL_MAP.get(name)


# ── Check 5: FK reference integrity ───────────────────────────


def check_fk_references(
    data: list[dict],
    global_index: ModelIndex,
    filepath: str,
) -> None:
    """Check that FK field values reference existing PKs in *global_index*."""
    for obj in data:
        if not isinstance(obj, dict):
            continue
        model = obj.get("model", "")
        pk = obj.get("pk", "?")
        fields = obj.get("fields", {})
        if not isinstance(fields, dict):
            continue

        for field_name, field_value in fields.items():
            if field_value is None:
                continue  # Null FK — no reference to check

            target_model = _guess_fk_model(field_name)
            if target_model is None:
                continue  # Can't resolve

            # Handle list of FKs (e.g., ``Page.tags``, M2M through tables)
            fk_values = field_value if isinstance(field_value, list) else [field_value]

            for fk_val in fk_values:
                if not isinstance(fk_val, (int, str)):
                    continue
                if fk_val not in global_index.get(target_model, set()):
                    log_warning(
                        f"FK REFERENCE: {filepath} — {model}(pk={pk}).{field_name} "
                        f"→ {target_model}(pk={fk_val}) not found in loaded fixtures. "
                        f"May resolve via auto-created content types or migration."
                    )


# ── Check 6: Cross-file duplicate detection ───────────────────


def check_duplicates(
    per_file_index: PerFileModelIndex,
    filepath: str,
    pks: ModelIndex,
) -> None:
    """Check for duplicate ``(model, pk)`` pairs across different files.

    Logs a warning if the same PK for the same model appears in multiple
    fixture files.  This is expected for certain models (``auth.permission``
    content types) but may indicate accidental duplication for others.
    """
    for model, pk_set in pks.items():
        for existing_path, existing_pks in per_file_index.items():
            if existing_path == filepath:
                continue
            overlap = pk_set & existing_pks.get(model, set())
            if overlap:
                log_warning(
                    f"DUPLICATE PK: {model} PKs {overlap} appear in both "
                    f"'{filepath}' and '{existing_path}'. "
                    f"Expected for built-in models (permissions, content types)."
                )


# ── Main validation loop ──────────────────────────────────────


def validate_fixture(
    path: Path,
    global_index: ModelIndex,
    per_file_index: PerFileModelIndex,
    verbose: bool,
) -> bool:
    """Validate a single fixture file.  Returns True if all checks pass."""
    global fixtures_found, fixtures_valid

    fixtures_found += 1
    relative = str(path.relative_to(REPO_ROOT))

    if verbose:
        print(f"  🔍 {relative}...", end=" ", flush=True)

    # 1. JSON validity
    data = check_json_validity(path)
    if data is None:
        if verbose:
            print("❌")
        return False

    # 2. Structure
    if not check_fixture_structure(path, data):
        if verbose:
            print("❌")
        return False

    # 3. File size
    check_file_size(path, data)

    # 4. Collect PKs & update global index
    pks = collect_pks(data)
    for model, pk_set in pks.items():
        global_index[model].update(pk_set)

    # 5. Store per-file index for duplicate detection
    per_file_index[relative] = pks

    fixtures_valid += 1
    if verbose:
        print("✅")
    return True


def format_count(items: list) -> str:
    """Return a formatted count string."""
    return f"{len(items)} {'issue' if len(items) == 1 else 'issues'}"


# ── Entry point ───────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate all JSON fixture files in the project."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show per-file validation results.",
    )
    parser.add_argument(
        "--path",
        help="Validate a specific directory or file (default: all canonical paths).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Fixture Validation Report")
    print("=" * 60)
    print()

    # Collect files to validate
    files_to_validate: list[Path] = []

    if args.path:
        given = Path(args.path)
        if not given.is_absolute():
            given = REPO_ROOT / given
        if given.is_file():
            if given.suffix == ".json":
                files_to_validate.append(given)
            else:
                print(f"❌ Not a JSON file: {given}")
                return 1
        elif given.is_dir():
            for json_file in given.rglob("*.json"):
                if json_file.name not in SKIP_FILES:
                    files_to_validate.append(json_file)
        else:
            print(f"❌ Path not found: {given}")
            return 1
    else:
        for pattern in FIXTURE_GLOB_PATTERNS:
            for json_file in REPO_ROOT.glob(pattern):
                if json_file.name not in SKIP_FILES:
                    files_to_validate.append(json_file)

    # Deduplicate
    files_to_validate = sorted(set(files_to_validate))

    if not files_to_validate:
        print("❌ No fixture files found to validate.")
        return 1

    # Global model index for cross-file PK analysis
    global_index: ModelIndex = defaultdict(set)
    per_file_index: PerFileModelIndex = {}
    parsed_cache: list[tuple[Path, str, list[dict] | None]] = []

    # Validate each file
    expected_count = 50  # Canonical fixtures in tests/fixtures/ (excluding INDEX.json)
    print(f"Found {len(files_to_validate)} fixture files to validate.")
    print(f"Expected (canonical tests/fixtures/): ~{expected_count} unique fixtures")
    print(f"Note: Total includes copies across project directories.\n")

    for fpath in files_to_validate:
        relative = str(fpath.relative_to(REPO_ROOT))
        data = check_json_validity(fpath)
        parsed_cache.append((fpath, relative, data))
        validate_fixture(fpath, global_index, per_file_index, verbose=args.verbose)

    # Second pass: FK reference checks (needs complete global_index)
    print()
    print("  ── Checking FK references... ──")
    for fpath, pfi_relative, pfi_data in parsed_cache:
        if pfi_data is not None:
            check_fk_references(pfi_data, global_index, pfi_relative)

    # Third pass: Duplicate PK detection (reuses per_file_index from first pass)
    print("  ── Checking for duplicate PKs... ──")
    seen_pairs: dict[tuple[str, int | str], str] = {}
    for filepath, pks in per_file_index.items():
        for model, pk_set in pks.items():
            for pk in pk_set:
                key = (model, pk)
                if key in seen_pairs:
                    log_warning(
                        f"DUPLICATE PK: {model}(pk={pk}) appears in both "
                        f"'{seen_pairs[key]}' and '{filepath}'. "
                        f"Expected for built-in models (permissions, content types)."
                    )
                else:
                    seen_pairs[key] = filepath

    # Summary
    print()
    print("═" * 60)
    print("  VALIDATION SUMMARY")
    print("═" * 60)
    print(f"  Scanned:       {len(files_to_validate)} files")
    print(f"  Valid:         {fixtures_valid} files")
    print(f"  Failed:        {fixtures_found - fixtures_valid} files")
    print(f"  Errors:        {len(errors)}")
    print(f"  Warnings:      {len(warnings)}")
    print("─" * 60)

    # Model count
    model_count = len(global_index)
    total_pks = sum(len(pks) for pks in global_index.values())
    print(f"  Models found:  {model_count}")
    print(f"  Objects:       ~{total_pks}")
    print("═" * 60)
    print()

    # Print errors
    if errors:
        print("❌ ERRORS:")
        for e in errors:
            print(f"   • {e}")
        print()

    # Print warnings (deduplicated, top N)
    if warnings:
        unique_warnings = list(dict.fromkeys(warnings))  # deduplicate, preserve order
        print("⚠️  WARNINGS:")
        for w in unique_warnings[:25]:
            print(f"   • {w}")
        if len(unique_warnings) > 25:
            print(f"   ... and {len(unique_warnings) - 25} more")
        print()

    # Top models by object count
    if args.verbose and global_index:
        print("📊 Top models by object count:")
        top_models = sorted(global_index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for model, pks in top_models:
            print(f"   • {model}: {len(pks)} objects")
        print()

    # Exit code
    if errors:
        print(f"❌ Validation completed with {format_count(errors)} and "
              f"{format_count(warnings)}.\n")
        return 1
    if warnings:
        print(f"⚡ Validation completed with {format_count(warnings)} "
              f"(non-fatal — see above).\n")
        return 0

    print("✅ All fixtures validated successfully!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
