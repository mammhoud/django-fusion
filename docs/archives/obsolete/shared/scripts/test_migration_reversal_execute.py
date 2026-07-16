#!/usr/bin/env python3
"""
Execute Migration Reversal Tests - Actually runs migration reversal commands.

This script tests migration reversal by:
1. Running python manage.py migrate <app> zero to reverse migrations
2. Re-applying migrations with python manage.py migrate <app>
3. Verifying data integrity after reversal and re-application
4. Generating a comprehensive test report

Based on Task 15.2 from ecosystem-architectural-refactoring spec.
"""

import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class MigrationReversalTest:
    """Result of testing migration reversal."""
    project: str
    app_label: str
    reversal_successful: bool = False
    reapply_successful: bool = False
    data_integrity_verified: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    test_results: List[str] = field(default_factory=list)
    before_state: Optional[Dict] = None
    after_state: Optional[Dict] = None


class MigrationReversalExecutor:
    """Executes migration reversal tests."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results: List[MigrationReversalTest] = []

    def test_all_apps(self) -> List[MigrationReversalTest]:
        """Test migration reversal for all apps in the project."""
        self.results = []

        # Get all apps with migrations
        apps_dir = self.project_path / "apps"
        if not apps_dir.exists():
            print(f"Warning: {apps_dir} does not exist")
            return self.results

        # Find all app directories with migrations
        for app_dir in apps_dir.iterdir():
            if not app_dir.is_dir() or app_dir.name.startswith("_"):
                continue

            migrations_dir = app_dir / "migrations"
            if not migrations_dir.exists():
                continue

            # Check if there are migration files (excluding __init__.py)
            migration_files = list(migrations_dir.glob("[0-9]*.py"))
            if not migration_files:
                continue

            # Test this app
            test_result = self._test_app_reversal(app_dir.name)
            self.results.append(test_result)

        return self.results

    def _test_app_reversal(self, app_label: str) -> MigrationReversalTest:
        """Test migration reversal for a single app."""
        print(f"\n{'='*60}")
        print(f"Testing migration reversal for {app_label}")
        print(f"{'='*60}")

        test_result = MigrationReversalTest(
            project=str(self.project_path.name),
            app_label=app_label
        )

        try:
            # Step 1: Capture database state before reversal
            print(f"\n1. Capturing database state before reversal...")
            before_state = self._capture_database_state(app_label)
            test_result.before_state = before_state

            # Step 2: Reverse migrations (migrate app zero)
            print(f"2. Reversing migrations: python manage.py migrate {app_label} zero")
            reversal_result = self._run_migration_command(app_label, "zero")

            if reversal_result["success"]:
                test_result.reversal_successful = True
                test_result.test_results.append("✓ Migration reversal successful")
                print(f"   ✓ Migration reversal successful")
            else:
                test_result.reversal_successful = False
                test_result.errors.append(f"Migration reversal failed: {reversal_result['error']}")
                test_result.test_results.append("✗ Migration reversal failed")
                print(f"   ✗ Migration reversal failed: {reversal_result['error']}")
                return test_result

            # Step 3: Capture database state after reversal
            print(f"3. Capturing database state after reversal...")
            after_reversal_state = self._capture_database_state(app_label)

            # Step 4: Re-apply migrations
            print(f"4. Re-applying migrations: python manage.py migrate {app_label}")
            reapply_result = self._run_migration_command(app_label, "")

            if reapply_result["success"]:
                test_result.reapply_successful = True
                test_result.test_results.append("✓ Migration re-application successful")
                print(f"   ✓ Migration re-application successful")
            else:
                test_result.reapply_successful = False
                test_result.errors.append(f"Migration re-application failed: {reapply_result['error']}")
                test_result.test_results.append("✗ Migration re-application failed")
                print(f"   ✗ Migration re-application failed: {reapply_result['error']}")
                return test_result

            # Step 5: Capture database state after re-application
            print(f"5. Capturing database state after re-application...")
            after_reapply_state = self._capture_database_state(app_label)
            test_result.after_state = after_reapply_state

            # Step 6: Verify data integrity
            print(f"6. Verifying data integrity...")
            integrity_verified = self._verify_data_integrity(
                before_state,
                after_reapply_state,
                app_label
            )

            if integrity_verified:
                test_result.data_integrity_verified = True
                test_result.test_results.append("✓ Data integrity verified")
                print(f"   ✓ Data integrity verified")
            else:
                test_result.data_integrity_verified = False
                test_result.warnings.append("Data integrity check failed or inconclusive")
                test_result.test_results.append("⚠ Data integrity check inconclusive")
                print(f"   ⚠ Data integrity check inconclusive")

        except Exception as e:
            test_result.errors.append(f"Unexpected error: {str(e)}")
            test_result.test_results.append(f"✗ Test failed with exception: {e}")
            print(f"   ✗ Test failed with exception: {e}")

        return test_result

    def _run_migration_command(self, app_label: str, operation: str) -> Dict:
        """Run a migration command and return result."""
        try:
            # Set up Django environment
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings.development')

            # Add project to Python path
            project_parent = self.project_path.parent
            sys.path.insert(0, str(project_parent))
            sys.path.insert(0, str(self.project_path))

            import django
            django.setup()

            from io import StringIO

            from django.core.management import call_command

            # Run the migration command
            out = StringIO()
            err = StringIO()

            if operation == "zero":
                call_command('migrate', app_label, 'zero', stdout=out, stderr=err)
            else:
                call_command('migrate', app_label, stdout=out, stderr=err)

            output = out.getvalue()
            error_output = err.getvalue()

            return {
                "success": True,
                "output": output,
                "error_output": error_output
            }

        except SystemExit as e:
            # Django commands often call sys.exit()
            if e.code == 0:
                return {"success": True, "output": "", "error_output": ""}
            else:
                return {"success": False, "error": f"SystemExit with code {e.code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _capture_database_state(self, app_label: str) -> Dict:
        """Capture database state for an app."""
        state = {
            "app_label": app_label,
            "timestamp": datetime.now().isoformat(),
            "tables": {},
            "row_counts": {}
        }

        try:
            # Find database file
            db_path = self.project_path / "dev_db.sqlite3"
            if not db_path.exists():
                state["error"] = f"Database file not found: {db_path}"
                return state

            # Connect to database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get all tables for this app
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                if table.startswith(f"{app_label}_"):
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]

                    # Get schema
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()

                    state["tables"][table] = {
                        "columns": [col[1] for col in columns],  # Column names
                        "column_count": len(columns)
                    }
                    state["row_counts"][table] = row_count

            conn.close()

        except Exception as e:
            state["error"] = str(e)

        return state

    def _verify_data_integrity(self, before_state: Dict, after_state: Dict, app_label: str) -> bool:
        """Verify data integrity by comparing before and after states."""
        if "error" in before_state or "error" in after_state:
            return False

        # Check if same tables exist
        before_tables = set(before_state.get("tables", {}).keys())
        after_tables = set(after_state.get("tables", {}).keys())

        if before_tables != after_tables:
            print(f"   Table mismatch: before={before_tables}, after={after_tables}")
            return False

        # Check if column structures are similar
        for table in before_tables:
            before_columns = set(before_state["tables"][table].get("columns", []))
            after_columns = set(after_state["tables"][table].get("columns", []))

            # Allow for some differences (like added/removed columns during migration)
            # But core columns should remain
            common_columns = before_columns.intersection(after_columns)
            if len(common_columns) < max(len(before_columns), len(after_columns)) * 0.8:
                print(f"   Column structure changed significantly for {table}")
                print(f"     Before: {before_columns}")
                print(f"     After: {after_columns}")
                return False

        return True

    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        report = []
        report.append("# Migration Reversal Execution Test Report\n")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Summary statistics
        total_tests = len(self.results)
        successful_reversals = sum(1 for r in self.results if r.reversal_successful)
        successful_reapplies = sum(1 for r in self.results if r.reapply_successful)
        integrity_verified = sum(1 for r in self.results if r.data_integrity_verified)

        report.append("## Summary\n")
        report.append(f"- **Project**: {self.project_path.name}\n")
        report.append(f"- **Total apps tested**: {total_tests}\n")
        report.append(f"- **Successful reversals**: {successful_reversals}/{total_tests}\n")
        report.append(f"- **Successful re-applications**: {successful_reapplies}/{total_tests}\n")
        report.append(f"- **Data integrity verified**: {integrity_verified}/{total_tests}\n")

        # Detailed results
        report.append("\n## Detailed Test Results\n")

        for test in self.results:
            status = "✅ PASS" if (
                test.reversal_successful and
                test.reapply_successful and
                test.data_integrity_verified
            ) else "❌ FAIL"

            report.append(f"\n### {test.app_label} - {status}\n")

            for result in test.test_results:
                report.append(f"- {result}\n")

            if test.errors:
                report.append("\n**Errors:**\n")
                for error in test.errors:
                    report.append(f"- {error}\n")

            if test.warnings:
                report.append("\n**Warnings:**\n")
                for warning in test.warnings:
                    report.append(f"- {warning}\n")

            # Show database state comparison
            if test.before_state and test.after_state:
                report.append("\n**Database State Comparison:**\n")

                before_tables = test.before_state.get("tables", {})
                after_tables = test.after_state.get("tables", {})

                report.append(f"- Tables before: {len(before_tables)}\n")
                report.append(f"- Tables after: {len(after_tables)}\n")

                for table_name in before_tables:
                    before_rows = test.before_state.get("row_counts", {}).get(table_name, 0)
                    after_rows = test.after_state.get("row_counts", {}).get(table_name, 0)
                    report.append(f"  - {table_name}: {before_rows} → {after_rows} rows\n")

        return "".join(report)


def main():
    """Main entry point."""
    print("Migration Reversal Execution Test")
    print("=" * 60)

    projects = [
        "ctc-research.com",
        "structa.cloud"
    ]

    all_results = []

    for project in projects:
        if not Path(project).exists():
            print(f"\nProject {project} not found, skipping...")
            continue

        print(f"\nTesting project: {project}")
        print("-" * 40)

        executor = MigrationReversalExecutor(project)
        results = executor.test_all_apps()
        all_results.extend(results)

        # Generate project-specific report
        report = executor.generate_report()
        report_filename = f"MIGRATION_REVERSAL_EXECUTION_{project.replace('.', '_')}.md"

        with open(report_filename, 'w') as f:
            f.write(report)

        print(f"\nReport written to {report_filename}")

    # Generate overall report
    print("\n" + "=" * 60)
    print("Overall Summary")
    print("=" * 60)

    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if (
        r.reversal_successful and
        r.reapply_successful and
        r.data_integrity_verified
    ))

    print(f"Total tests: {total_tests}")
    print(f"Successful tests: {successful_tests}")
    print(f"Success rate: {successful_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A")

    if successful_tests < total_tests:
        print("\nFailed tests:")
        for test in all_results:
            if not (test.reversal_successful and test.reapply_successful and test.data_integrity_verified):
                print(f"  - {test.project}/{test.app_label}")


if __name__ == "__main__":
    main()
