"""
Management command to verify Django model definitions match actual database columns.

Usage:
    python manage.py check_schema                          # Check all models
    python manage.py check_schema --table full_products    # Check specific table
    python manage.py check_schema --fix                    # Auto-add missing columns
    python manage.py check_schema --json                   # JSON output
    python manage.py check_schema --verbose                # Show all fields, not just mismatches
    python manage.py check_schema --auto-create           # Create missing tables via schema_editor
    python manage.py check_schema --auto-create --fix     # Create missing tables AND add missing columns

Exit codes:
    0 — All schemas match (or only mismatches auto-fixed with --fix or --auto-create)
    1 — One or more schema mismatches found
"""

from __future__ import annotations

import json
import sys
from collections.abc import Generator

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, models


# ══════════════════════════════════════════════════════════════════════
# Django field type → SQL type (for ALTER TABLE and comparison)
# ══════════════════════════════════════════════════════════════════════

FIELD_TYPE_MAP: dict[type, str] = {
    models.CharField: "varchar",
    models.TextField: "text",
    models.IntegerField: "integer",
    models.BigIntegerField: "bigint",
    models.PositiveIntegerField: "integer",
    models.PositiveSmallIntegerField: "integer",
    models.SmallIntegerField: "integer",
    models.BooleanField: "bool",
    models.NullBooleanField: "bool",
    models.DateField: "date",
    models.DateTimeField: "datetime",
    models.TimeField: "time",
    models.DecimalField: "decimal",
    models.FloatField: "real",
    models.URLField: "varchar",
    models.EmailField: "varchar",
    models.SlugField: "varchar",
    models.UUIDField: "varchar",
    models.JSONField: "text",
    models.BinaryField: "blob",
    models.GenericIPAddressField: "char",
    models.FileField: "varchar",
    models.ImageField: "varchar",
    models.ForeignKey: "bigint",
    models.OneToOneField: "bigint",
}


def _col_type_for_field(field: models.Field) -> str:
    """Return the expected SQL column type for a Django model field.

    Returns a lowercase type string (e.g. ``"varchar"``, ``"integer"``, ``"decimal"``).
    For fields with choices (like CharField with max_length), includes the type
    prefix that SQLite uses (e.g. ``"varchar"`` matches SQLite's ``"varchar(200)"``
    by comparing only the type prefix).
    """
    for cls, sql_type in FIELD_TYPE_MAP.items():
        if isinstance(field, cls):
            return sql_type
    return "text"  # fallback


# ══════════════════════════════════════════════════════════════════════
# Command
# ══════════════════════════════════════════════════════════════════════


class Command(BaseCommand):
    """Verifies Django model tables match actual database columns."""

    help = "Check that all Django model tables have the expected columns in the database."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--table",
            type=str,
            default="",
            help="Check only this specific table (db_table name, e.g. full_products).",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            default=False,
            help="Auto-add missing columns using ALTER TABLE (SQLite only).",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            default=False,
            help="Output results as JSON.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            default=False,
            help="Show all fields, not just mismatches.",
        )
        parser.add_argument(
            "--app-label",
            type=str,
            default="",
            help="Check only models from this app label (e.g. pos_full).",
        )
        parser.add_argument(
            "--auto-create",
            action="store_true",
            default=False,
            help="Auto-create missing tables using Django's schema_editor.create_model().",
        )

    def handle(self, *args, **options) -> None:
        table_filter = options.get("table", "").strip()
        app_label_filter = options.get("app_label", "").strip()
        auto_fix = options.get("fix", False)
        auto_create = options.get("auto_create", False)
        as_json = options.get("json", False)
        verbose = options.get("verbose", False)

        results: dict[str, dict] = {}  # table_name → {model, columns, mismatches, ok}

        for model in self._iter_managed_models(app_label_filter):
            db_table = model._meta.db_table
            if table_filter and db_table != table_filter:
                continue
            if db_table in results:
                continue

            self._check_model_schema(model, results, verbose)

        # ── Reporting ──
        total = len(results)
        ok_count = sum(1 for r in results.values() if r["ok"])
        fail_count = total - ok_count
        total_missing = sum(len(r["missing"]) for r in results.values())

        if as_json:
            output = {
                "total_tables": total,
                "ok": ok_count,
                "mismatches": fail_count,
                "total_missing_columns": total_missing,
                "tables": {
                    name: {
                        "model": f"{r['model'].__module__}.{r['model'].__qualname__}",
                        "db_table": name,
                        "ok": r["ok"],
                        "total_columns": r["total_columns"],
                        "expected_columns": r["expected_count"],
                        "missing": [m["column"] for m in r["missing"]],
                    }
                    for name, r in results.items()
                },
            }
            self.stdout.write(json.dumps(output, indent=2))
        else:
            self._print_report(results, fail_count, total, total_missing)

        if auto_fix and total_missing > 0:
            self._apply_fixes(results)

        if auto_create:
            created = self._create_missing_tables(results)
            if created > 0:
                # Re-check after creating tables so exit code is accurate
                self.stdout.write(self.style.SUCCESS(f"\n  Re-checking schema after creating {created} table(s)...\n"))
                results.clear()
                for model in self._iter_managed_models(app_label_filter):
                    db_table = model._meta.db_table
                    if table_filter and db_table != table_filter:
                        continue
                    if db_table in results:
                        continue
                    self._check_model_schema(model, results, verbose)
                # Recalculate
                total = len(results)
                ok_count = sum(1 for r in results.values() if r["ok"])
                fail_count = total - ok_count
                total_missing = sum(len(r["missing"]) for r in results.values())
                if not as_json:
                    self._print_report(results, fail_count, total, total_missing)

        # Exit code
        # If --auto-create resolved ALL issues, exit cleanly even if
        # auto_fix wasn't used.  Otherwise only suppress exit 1 when
        # the user explicitly asked us to fix things.
        auto_create_resolved = auto_create and created > 0 and fail_count == 0
        if fail_count > 0 and not auto_fix and not auto_create_resolved:
            sys.exit(1)

    # ── Helpers ────────────────────────────────────────────────────

    def _iter_managed_models(
        self, app_label_filter: str
    ) -> Generator:
        """Yield all managed Django models (non-abstract, non-proxy)."""
        for app_config in apps.get_app_configs():
            if app_label_filter and app_config.label != app_label_filter:
                continue
            for model in app_config.get_models():
                if model._meta.abstract or model._meta.proxy:
                    continue
                if not model._meta.managed:
                    continue
                yield model

    def _check_model_schema(
        self, model, results: dict, verbose: bool
    ) -> None:
        """Compare one model's fields against its database table."""
        db_table = model._meta.db_table
        missing: list[dict] = []
        expected_fields: list[dict] = []
        db_columns: set[str] = set()
        field_count = 0

        db_columns = set()
        with connection.cursor() as cursor:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{db_table}'")
            if not cursor.fetchone():
                results[db_table] = {
                    "model": model,
                    "ok": False,
                    "total_columns": 0,
                    "expected_count": 0,
                    "missing": [{"column": "(entire table)", "expected_type": "TABLE"}],
                    "note": "TABLE DOES NOT EXIST",
                }
                return

            # Get actual DB columns via PRAGMA
            cursor.execute(f'PRAGMA table_info("{db_table}")')
            db_columns = {row[1] for row in cursor.fetchall()}

        # Iterate model fields
        for field in model._meta.local_fields:
            if field.column is None:
                continue
            field_count += 1
            col_name = field.column
            expected_type = _col_type_for_field(field)

            expected_fields.append({
                "column": col_name,
                "expected_type": expected_type,
                "nullable": field.null,
                "has_default": field.has_default(),
            })

            if col_name not in db_columns:
                missing.append({
                    "column": col_name,
                    "expected_type": expected_type,
                    "field": field.attname,
                })

        results[db_table] = {
            "model": model,
            "ok": len(missing) == 0,
            "total_columns": len(db_columns),
            "expected_count": field_count,
            "missing": missing,
            "expected_fields": expected_fields if verbose else [],
            "db_columns": sorted(db_columns) if verbose else [],
        }

    def _print_report(
        self, results: dict, fail_count: int, total: int, total_missing: int
    ) -> None:
        """Print a human-readable report to stdout."""
        sep = "─" * 72

        self.stdout.write(sep)
        self.stdout.write("  Schema Verification Report")
        self.stdout.write(sep)

        for table_name, info in sorted(results.items()):
            model_name = f"{info['model'].__module__}.{info['model'].__qualname__}"

            if info.get("note") == "TABLE DOES NOT EXIST":
                self.stdout.write(
                    self.style.ERROR(f"\n  ❌ {table_name}")
                )
                self.stdout.write(f"     Model : {model_name}")
                self.stdout.write(f"     Table  : {table_name}")
                self.stdout.write(f"     Status : TABLE DOES NOT EXIST")
                continue

            if info["ok"]:
                label = self.style.SUCCESS("  ✅")
            else:
                label = self.style.WARNING("  ⚠️ ")

            self.stdout.write(f"\n{label} {table_name}")
            self.stdout.write(f"     Model  : {model_name}")
            self.stdout.write(
                f"     Columns: {info['total_columns']} in DB, "
                f"{info['expected_count']} expected"
            )

            if info["missing"]:
                self.stdout.write(
                    self.style.ERROR(
                        f"     Missing : {len(info['missing'])} column(s)"
                    )
                )
                for m in info["missing"]:
                    self.stdout.write(
                        f"       - {m['column']} ({m['expected_type']})  "
                        f"[field: {m['field']}]"
                    )

            if info.get("expected_fields") and info["ok"]:
                # Verbose mode: show all expected fields
                for ef in info["expected_fields"]:
                    nullable_mark = "NULL" if ef["nullable"] else "NOT NULL"
                    default_mark = "default" if ef["has_default"] else "no default"
                    self.stdout.write(
                        f"       · {ef['column']:30s} {ef['expected_type']:10s} "
                        f"{nullable_mark:10s} ({default_mark})"
                    )

        self.stdout.write(sep)
        if fail_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ All {total} table(s) match their model definitions."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠️  {fail_count}/{total} table(s) have mismatches "
                    f"({total_missing} missing column(s) total)."
                )
            )
            self.stdout.write(
                "  Run with --fix to auto-add missing columns (SQLite only)."
            )
        self.stdout.write(sep)

    def _apply_fixes(self, results: dict) -> None:
        """Auto-add missing columns via ALTER TABLE."""
        self.stdout.write("\n  Applying fixes...")
        fixes_applied = 0

        with connection.cursor() as cursor:
            for table_name, info in sorted(results.items()):
                if not info["missing"]:
                    continue
                if info.get("note") == "TABLE DOES NOT EXIST":
                    self.stdout.write(
                        f"    ⏭️  Cannot create table {table_name} — "
                        f"run 'python manage.py migrate' instead."
                    )
                    continue

                for m in info["missing"]:
                    col_name = m["column"]
                    col_type = m["expected_type"]

                    # Map type to SQLite-compatible default value
                    default_map = {
                        "varchar": "''",
                        "text": "''",
                        "integer": "0",
                        "bigint": "0",
                        "bool": "0",
                        "decimal": "0",
                        "real": "0.0",
                        "datetime": "NULL",
                        "date": "NULL",
                        "time": "NULL",
                        "char": "''",
                        "blob": "NULL",
                    }
                    default = default_map.get(col_type, "NULL")
                    not_null = "" if default == "NULL" else "NOT NULL"

                    sql = (
                        f'ALTER TABLE "{table_name}" '
                        f'ADD COLUMN "{col_name}" {col_type} '
                        f'{not_null} DEFAULT {default}'
                    )
                    try:
                        cursor.execute(sql)
                        fixes_applied += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"    ✅ Added {table_name}.{col_name} ({col_type})"
                            )
                        )
                    except Exception as exc:
                        self.stdout.write(
                            self.style.ERROR(
                                f"    ❌ Failed to add {table_name}.{col_name}: {exc}"
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(f"\n  Applied {fixes_applied} fix(es).")
        )

    def _create_missing_tables(self, results: dict) -> int:
        """Create entirely missing database tables using Django's schema editor.

        Iterates over results marked as "TABLE DOES NOT EXIST" and calls
        ``schema_editor.create_model()`` for each.  Also creates intermediate
        tables (like ``django_content_type``) that are required as FK targets.
        """
        self.stdout.write("\n  Creating missing tables...")
        created = 0

        from django.db import connection

        # Build dependency order: models whose FKs point to other missing
        # tables need those tables created first.  Use a simple topological
        # sort by counting how many FK targets are also missing.
        missing_models: list[tuple] = []  # (model, table_name, info)
        for table_name, info in results.items():
            if info.get("note") == "TABLE DOES NOT EXIST":
                missing_models.append((info["model"], table_name, info))

        if not missing_models:
            self.stdout.write("    No missing tables to create.")
            return 0

        # Sort: models with fewer FK dependencies on other missing tables first
        def _dependency_count(item) -> int:
            model = item[0]
            count = 0
            for field in model._meta.local_fields:
                if field.remote_field and field.remote_field.model:
                    target = field.remote_field.model
                    if target is not model and any(
                        t[0]._meta.db_table == target._meta.db_table
                        for t in missing_models
                    ):
                        count += 1
            return count

        missing_models.sort(key=_dependency_count)

        with connection.schema_editor() as schema_editor:
            for model, table_name, info in missing_models:
                try:
                    schema_editor.create_model(model)
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    ✅ Created table {table_name} "
                            f"({model.__name__})"
                        )
                    )
                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR(
                            f"    ❌ Failed to create {table_name}: {exc}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(f"\n  Created {created} missing table(s).")
        )
        return created
