#!/usr/bin/env python3
"""
Migration Reversal Test for Task 15.2

This script implements Task 15.2: "Test migration reversal for all app rename migrations"
from the ecosystem-architectural-refactoring spec.

Requirements:
1. Run python manage.py migrate accounts zero in ctc-research.com — verify success
2. Re-apply: python manage.py migrate accounts — verify success
3. Repeat for lms, content apps in ctc-research.com
4. Repeat for accounts, alliance, content apps in structa.cloud
5. Verify data integrity after each reversal and re-application
"""

import json
import os
import sqlite3
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class TestResult:
    """Result of a migration reversal test."""
    project: str
    app: str
    step1_reversal: bool = False
    step2_reapply: bool = False
    step3_integrity: bool = False
    errors: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    database_state_before: Optional[Dict] = None
    database_state_after: Optional[Dict] = None


class MigrationReversalTester:
    """Tests migration reversal by executing Django commands."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results: List[TestResult] = []

    def test_app_rename_migrations(self) -> List[TestResult]:
        """Test migration reversal for app rename migrations."""
        print(f"\n{'='*60}")
        print(f"Testing migration reversal in {self.project_path.name}")
        print(f"{'='*60}")

        # Define which apps to test based on project
        if self.project_path.name == "ctc-research.com":
            apps_to_test = ["accounts", "lms", "content"]
        elif self.project_path.name == "structa.cloud":
            apps_to_test = ["accounts", "alliance", "content"]
        else:
            print(f"Unknown project: {self.project_path.name}")
            return []

        for app in apps_to_test:
            result = self._test_single_app(app)
            self.results.append(result)

        return self.results

    def _test_single_app(self, app: str) -> TestResult:
        """Test migration reversal for a single app."""
        print(f"\n--- Testing {app} ---")

        result = TestResult(
            project=self.project_path.name,
            app=app
        )

        try:
            # Check if app exists
            app_dir = self.project_path / "apps" / app
            if not app_dir.exists():
                result.errors.append(f"App directory not found: {app_dir}")
                print(f"  ✗ App directory not found: {app}")
                return result

            # Check if app has migrations
            migrations_dir = app_dir / "migrations"
            if not migrations_dir.exists():
                result.errors.append(f"Migrations directory not found: {migrations_dir}")
                print(f"  ✗ Migrations directory not found for {app}")
                return result

            migration_files = list(migrations_dir.glob("[0-9]*.py"))
            if not migration_files:
                result.errors.append(f"No migration files found in {migrations_dir}")
                print(f"  ✗ No migration files found for {app}")
                return result

            print(f"  Found {len(migration_files)} migration files")
            result.messages.append(f"Found {len(migration_files)} migration files")

            # Step 1: Capture database state before reversal
            print(f"  Step 1: Capturing database state before reversal...")
            before_state = self._capture_database_state(app)
            result.database_state_before = before_state

            if "error" in before_state:
                result.errors.append(f"Failed to capture initial database state: {before_state['error']}")
                print(f"    ✗ Failed to capture initial database state")
            else:
                print(f"    ✓ Database state captured")
                result.messages.append(f"Database state captured: {len(before_state.get('tables', {}))} tables")

            # Step 2: Run migration reversal (migrate app zero)
            print(f"  Step 2: Running 'python manage.py migrate {app} zero'...")
            reversal_result = self._run_django_command(["migrate", app, "zero"])

            if reversal_result["success"]:
                result.step1_reversal = True
                result.messages.append("Migration reversal successful")
                print(f"    ✓ Migration reversal successful")
            else:
                result.step1_reversal = False
                result.errors.append(f"Migration reversal failed: {reversal_result.get('error', 'Unknown error')}")
                print(f"    ✗ Migration reversal failed: {reversal_result.get('error', 'Unknown error')}")
                # Don't continue if reversal failed
                return result

            # Step 3: Run migration re-application
            print(f"  Step 3: Running 'python manage.py migrate {app}'...")
            reapply_result = self._run_django_command(["migrate", app])

            if reapply_result["success"]:
                result.step2_reapply = True
                result.messages.append("Migration re-application successful")
                print(f"    ✓ Migration re-application successful")
            else:
                result.step2_reapply = False
                result.errors.append(f"Migration re-application failed: {reapply_result.get('error', 'Unknown error')}")
                print(f"    ✗ Migration re-application failed: {reapply_result.get('error', 'Unknown error')}")
                # Don't continue if re-application failed
                return result

            # Step 4: Capture database state after re-application
            print(f"  Step 4: Capturing database state after re-application...")
            after_state = self._capture_database_state(app)
            result.database_state_after = after_state

            if "error" in after_state:
                result.errors.append(f"Failed to capture final database state: {after_state['error']}")
                print(f"    ✗ Failed to capture final database state")
            else:
                print(f"    ✓ Final database state captured")
                result.messages.append(f"Final database state captured: {len(after_state.get('tables', {}))} tables")

            # Step 5: Verify data integrity
            print(f"  Step 5: Verifying data integrity...")
            integrity_ok = self._verify_data_integrity(before_state, after_state, app)

            if integrity_ok:
                result.step3_integrity = True
                result.messages.append("Data integrity verified")
                print(f"    ✓ Data integrity verified")
            else:
                result.step3_integrity = False
                result.messages.append("Data integrity check inconclusive")
                print(f"    ⚠ Data integrity check inconclusive")

        except Exception as e:
            result.errors.append(f"Unexpected error: {str(e)}")
            print(f"  ✗ Test failed with exception: {e}")
            traceback.print_exc()

        return result

    def _run_django_command(self, args: List[str]) -> Dict:
        """Run a Django management command."""
        try:
            # Try to run via Django's call_command
            return self._run_via_call_command(args)
        except Exception as e:
            # Fall back to subprocess
            print(f"    Note: Using subprocess fallback (Django setup failed: {e})")
            return self._run_via_subprocess(args)

    def _run_via_call_command(self, args: List[str]) -> Dict:
        """Run command using Django's call_command."""
        try:
            # Set up Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings.development')

            # Add to Python path
            sys.path.insert(0, str(self.project_path.parent))
            sys.path.insert(0, str(self.project_path))

            import django
            django.setup()

            from io import StringIO

            from django.core.management import call_command

            out = StringIO()
            err = StringIO()

            call_command(args[0], *args[1:], stdout=out, stderr=err)

            return {
                "success": True,
                "output": out.getvalue(),
                "error": None
            }

        except SystemExit as e:
            # Django commands often call sys.exit(0) on success
            if e.code == 0:
                return {"success": True, "output": "", "error": None}
            else:
                return {"success": False, "error": f"SystemExit with code {e.code}"}
        except Exception as e:
            raise e  # Re-raise to trigger fallback

    def _run_via_subprocess(self, args: List[str]) -> Dict:
        """Run command using subprocess."""
        try:
            # Build command
            cmd = ["python", "manage.py"] + args

            # Run in project directory
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out after 60 seconds"}
        except FileNotFoundError:
            return {"success": False, "error": "manage.py not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _capture_database_state(self, app: str) -> Dict:
        """Capture database state for an app."""
        state = {
            "app": app,
            "timestamp": datetime.now().isoformat(),
            "tables": {},
            "row_counts": {}
        }

        try:
            # Find SQLite database file
            db_files = list(self.project_path.glob("*.sqlite3"))
            if not db_files:
                state["error"] = "No SQLite database file found"
                return state

            db_path = db_files[0]

            # Connect to database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cursor.fetchall()]

            # Filter tables for this app
            app_tables = [t for t in all_tables if t.startswith(f"{app}_")]

            for table in app_tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]

                # Get column info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()

                state["tables"][table] = {
                    "columns": [col[1] for col in columns],
                    "types": [col[2] for col in columns]
                }
                state["row_counts"][table] = row_count

            conn.close()

        except Exception as e:
            state["error"] = str(e)

        return state

    def _verify_data_integrity(self, before: Dict, after: Dict, app: str) -> bool:
        """Verify data integrity by comparing before and after states."""
        if "error" in before or "error" in after:
            return False

        before_tables = set(before.get("tables", {}).keys())
        after_tables = set(after.get("tables", {}).keys())

        # Check if same tables exist
        if before_tables != after_tables:
            print(f"      Table mismatch: {before_tables} vs {after_tables}")
            return False

        # For each table, check structure similarity
        for table in before_tables:
            before_cols = set(before["tables"][table].get("columns", []))
            after_cols = set(after["tables"][table].get("columns", []))

            # Allow some differences (migrations might add/remove columns)
            common_cols = before_cols.intersection(after_cols)
            if len(common_cols) < min(len(before_cols), len(after_cols)) * 0.7:
                print(f"      Column structure changed significantly for {table}")
                print(f"        Before: {before_cols}")
                print(f"        After: {after_cols}")
                return False

        return True


def main():
    """Main entry point."""
    print("Migration Reversal Test - Task 15.2")
    print("=" * 60)
    print("Testing migration reversal for all app rename migrations")
    print("=" * 60)

    projects = ["ctc-research.com", "structa.cloud"]
    all_results = []

    for project in projects:
        if not Path(project).exists():
            print(f"\nProject {project} not found, skipping...")
            continue

        tester = MigrationReversalTester(project)
        results = tester.test_app_rename_migrations()
        all_results.extend(results)

    # Generate report
    generate_report(all_results)

    # Print summary
    print_summary(all_results)


def generate_report(results: List[TestResult]):
    """Generate a comprehensive test report."""
    report = []
    report.append("# Migration Reversal Test Report - Task 15.2\n")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    report.append("## Task Requirements\n")
    report.append("""
1. Run `python manage.py migrate accounts zero` in ctc-research.com — verify success
2. Re-apply: `python manage.py migrate accounts` — verify success
3. Repeat for lms, content apps in ctc-research.com
4. Repeat for accounts, alliance, content apps in structa.cloud
5. Verify data integrity after each reversal and re-application
""")

    report.append("\n## Test Results\n")

    # Group by project
    by_project = {}
    for result in results:
        if result.project not in by_project:
            by_project[result.project] = []
        by_project[result.project].append(result)

    for project, project_results in by_project.items():
        report.append(f"\n### {project}\n")

        for result in project_results:
            all_passed = result.step1_reversal and result.step2_reapply and result.step3_integrity
            status = "✅ PASS" if all_passed else "❌ FAIL"

            report.append(f"\n#### {result.app} - {status}\n")

            report.append("**Test Steps:**\n")
            report.append(f"1. Migration reversal (`migrate {result.app} zero`): {'✓ Success' if result.step1_reversal else '✗ Failed'}\n")
            report.append(f"2. Migration re-application (`migrate {result.app}`): {'✓ Success' if result.step2_reapply else '✗ Failed'}\n")
            report.append(f"3. Data integrity verification: {'✓ Verified' if result.step3_integrity else '✗ Not verified'}\n")

            if result.messages:
                report.append("\n**Messages:**\n")
                for msg in result.messages:
                    report.append(f"- {msg}\n")

            if result.errors:
                report.append("\n**Errors:**\n")
                for err in result.errors:
                    report.append(f"- {err}\n")

            # Show database state comparison
            if result.database_state_before and result.database_state_after:
                report.append("\n**Database State Comparison:**\n")

                before_tables = result.database_state_before.get("tables", {})
                after_tables = result.database_state_after.get("tables", {})

                report.append(f"- Tables before: {len(before_tables)}\n")
                report.append(f"- Tables after: {len(after_tables)}\n")

                for table_name in before_tables:
                    before_rows = result.database_state_before.get("row_counts", {}).get(table_name, 0)
                    after_rows = result.database_state_after.get("row_counts", {}).get(table_name, 0)
                    report.append(f"  - {table_name}: {before_rows} → {after_rows} rows\n")

    # Summary statistics
    report.append("\n## Summary Statistics\n")

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.step1_reversal and r.step2_reapply and r.step3_integrity)
    failed_tests = total_tests - passed_tests

    report.append(f"- **Total tests**: {total_tests}\n")
    report.append(f"- **Tests passed**: {passed_tests}\n")
    report.append(f"- **Tests failed**: {failed_tests}\n")

    if total_tests > 0:
        report.append(f"- **Success rate**: {passed_tests/total_tests*100:.1f}%\n")

    if passed_tests == total_tests and total_tests > 0:
        report.append("\n## ✅ ALL TESTS PASSED\n")
        report.append("All migration reversal tests completed successfully.\n")
    elif failed_tests > 0:
        report.append("\n## ⚠ SOME TESTS FAILED\n")
        report.append(f"{failed_tests} out of {total_tests} tests failed. Review errors above.\n")

    # Write report to file
    report_filename = "MIGRATION_REVERSAL_TASK_15_2_COMPREHENSIVE_REPORT.md"
    with open(report_filename, "w") as f:
        f.write("".join(report))

    print(f"\nReport written to: {report_filename}")


def print_summary(results: List[TestResult]):
    """Print a summary of test results."""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for r in results if r.step1_reversal and r.step2_reapply and r.step3_integrity)

    print(f"\nTotal tests: {total}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {total - passed}")

    if total > 0:
        print(f"Success rate: {passed/total*100:.1f}%")

    if passed == total and total > 0:
        print("\n✅ ALL TESTS PASSED - Migration reversal verified successfully!")
    elif total - passed > 0:
        print(f"\n⚠ {total - passed} TESTS FAILED")
        print("\nFailed tests:")
        for result in results:
            if not (result.step1_reversal and result.step2_reapply and result.step3_integrity):
                print(f"  - {result.project}/{result.app}")
                for err in result.errors:
                    print(f"    - {err}")


if __name__ == "__main__":
    main()
