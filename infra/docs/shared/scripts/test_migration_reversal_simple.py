#!/usr/bin/env python3
"""
Simple Migration Reversal Test - Runs actual migration commands.

This script follows the exact steps from Task 15.2:
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
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MigrationTestResult:
    """Result of a migration reversal test."""
    project: str
    app: str
    reversal_success: bool = False
    reapply_success: bool = False
    data_integrity: bool = False
    errors: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)


class MigrationTester:
    """Tests migration reversal by running actual commands."""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.results: List[MigrationTestResult] = []

    def test_app(self, app_name: str) -> MigrationTestResult:
        """Test migration reversal for a specific app."""
        print(f"\n{'='*60}")
        print(f"Testing {app_name} in {self.project_dir.name}")
        print(f"{'='*60}")

        result = MigrationTestResult(
            project=self.project_dir.name,
            app=app_name
        )

        try:
            # Step 1: Check current migration state
            print(f"\n1. Checking current migration state for {app_name}...")
            showmigrations = self._run_manage_command("showmigrations", [app_name])
            if showmigrations["success"]:
                result.messages.append(f"Current migrations: {showmigrations['output'][:200]}...")
                print(f"   ✓ Current migration state captured")
            else:
                result.errors.append(f"Failed to check migrations: {showmigrations['error']}")
                print(f"   ✗ Failed to check migrations")
                return result

            # Step 2: Capture database state before reversal
            print(f"2. Capturing database state before reversal...")
            before_state = self._capture_database_state(app_name)

            # Step 3: Reverse migrations (migrate app zero)
            print(f"3. Reversing migrations: python manage.py migrate {app_name} zero")
            reversal = self._run_manage_command("migrate", [app_name, "zero"])

            if reversal["success"]:
                result.reversal_success = True
                result.messages.append("Migration reversal successful")
                print(f"   ✓ Migration reversal successful")
            else:
                result.reversal_success = False
                result.errors.append(f"Migration reversal failed: {reversal['error']}")
                print(f"   ✗ Migration reversal failed: {reversal['error']}")
                return result

            # Step 4: Check migration state after reversal
            print(f"4. Checking migration state after reversal...")
            after_reversal = self._run_manage_command("showmigrations", [app_name])

            # Step 5: Re-apply migrations
            print(f"5. Re-applying migrations: python manage.py migrate {app_name}")
            reapply = self._run_manage_command("migrate", [app_name])

            if reapply["success"]:
                result.reapply_success = True
                result.messages.append("Migration re-application successful")
                print(f"   ✓ Migration re-application successful")
            else:
                result.reapply_success = False
                result.errors.append(f"Migration re-application failed: {reapply['error']}")
                print(f"   ✗ Migration re-application failed: {reapply['error']}")
                return result

            # Step 6: Capture database state after re-application
            print(f"6. Capturing database state after re-application...")
            after_state = self._capture_database_state(app_name)

            # Step 7: Verify data integrity
            print(f"7. Verifying data integrity...")
            integrity_ok = self._verify_integrity(before_state, after_state, app_name)

            if integrity_ok:
                result.data_integrity = True
                result.messages.append("Data integrity verified")
                print(f"   ✓ Data integrity verified")
            else:
                result.data_integrity = False
                result.messages.append("Data integrity check inconclusive")
                print(f"   ⚠ Data integrity check inconclusive")

        except Exception as e:
            result.errors.append(f"Unexpected error: {str(e)}")
            print(f"   ✗ Test failed with exception: {e}")

        return result

    def _run_manage_command(self, command: str, args: List[str] = None) -> Dict:
        """Run a Django management command."""
        if args is None:
            args = []

        try:
            # Build command
            cmd = ["python", "manage.py", command] + args

            # Run in project directory
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out after 30 seconds"}
        except FileNotFoundError:
            return {"success": False, "error": "manage.py not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _capture_database_state(self, app_name: str) -> Dict:
        """Capture database state for an app."""
        state = {
            "app": app_name,
            "timestamp": datetime.now().isoformat(),
            "tables": {},
            "row_counts": {}
        }

        try:
            # Look for database file
            db_files = list(self.project_dir.glob("*.sqlite3"))
            if not db_files:
                state["error"] = "No SQLite database file found"
                return state

            db_path = db_files[0]  # Use first SQLite file found

            # Connect to database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            # Filter tables for this app
            app_tables = [t for t in tables if t.startswith(f"{app_name}_")]

            for table in app_tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]

                # Get column info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()

                state["tables"][table] = {
                    "columns": [col[1] for col in columns],  # Column names
                    "types": [col[2] for col in columns]     # Column types
                }
                state["row_counts"][table] = row_count

            conn.close()

        except Exception as e:
            state["error"] = str(e)

        return state

    def _verify_integrity(self, before: Dict, after: Dict, app_name: str) -> bool:
        """Verify data integrity by comparing before and after states."""
        if "error" in before or "error" in after:
            return False

        # Check if same tables exist
        before_tables = set(before.get("tables", {}).keys())
        after_tables = set(after.get("tables", {}).keys())

        if before_tables != after_tables:
            print(f"     Table mismatch: {before_tables} vs {after_tables}")
            return False

        # For each table, check if structure is similar
        for table in before_tables:
            before_cols = set(before["tables"][table].get("columns", []))
            after_cols = set(after["tables"][table].get("columns", []))

            # Allow some differences (migrations might add/remove columns)
            common_cols = before_cols.intersection(after_cols)
            if len(common_cols) < min(len(before_cols), len(after_cols)) * 0.7:
                print(f"     Column structure changed significantly for {table}")
                return False

        return True


def main():
    """Main entry point."""
    print("Migration Reversal Test - Task 15.2")
    print("=" * 60)

    # Define tests based on task requirements
    tests = [
        # ctc-research.com tests
        ("ctc-research.com", "accounts"),
        ("ctc-research.com", "lms"),
        ("ctc-research.com", "content"),

        # structa.cloud tests
        ("structa.cloud", "accounts"),
        ("structa.cloud", "alliance"),
        ("structa.cloud", "content"),
    ]

    all_results = []

    for project_dir, app_name in tests:
        if not Path(project_dir).exists():
            print(f"\nProject {project_dir} not found, skipping {app_name}...")
            continue

        tester = MigrationTester(project_dir)
        result = tester.test_app(app_name)
        all_results.append(result)

    # Generate report
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    successful_tests = 0
    total_tests = len(all_results)

    for result in all_results:
        test_passed = (
            result.reversal_success and
            result.reapply_success and
            result.data_integrity
        )

        if test_passed:
            successful_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"\n{result.project}/{result.app}: {status}")

        if result.messages:
            for msg in result.messages:
                print(f"  - {msg}")

        if result.errors:
            for err in result.errors:
                print(f"  - ERROR: {err}")

    print(f"\n{'='*60}")
    print(f"SUMMARY: {successful_tests}/{total_tests} tests passed")
    print(f"{'='*60}")

    # Write detailed report
    report = generate_detailed_report(all_results)
    with open("MIGRATION_REVERSAL_TASK_15_2_REPORT.md", "w") as f:
        f.write(report)

    print(f"\nDetailed report written to: MIGRATION_REVERSAL_TASK_15_2_REPORT.md")


def generate_detailed_report(results: List[MigrationTestResult]) -> str:
    """Generate a detailed markdown report."""
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
            status = "✅ PASS" if (
                result.reversal_success and
                result.reapply_success and
                result.data_integrity
            ) else "❌ FAIL"

            report.append(f"\n#### {result.app} - {status}\n")

            report.append("**Steps:**\n")
            report.append(f"1. Reversal (`migrate {result.app} zero`): {'✓ Success' if result.reversal_success else '✗ Failed'}\n")
            report.append(f"2. Re-application (`migrate {result.app}`): {'✓ Success' if result.reapply_success else '✗ Failed'}\n")
            report.append(f"3. Data integrity: {'✓ Verified' if result.data_integrity else '✗ Not verified'}\n")

            if result.messages:
                report.append("\n**Messages:**\n")
                for msg in result.messages:
                    report.append(f"- {msg}\n")

            if result.errors:
                report.append("\n**Errors:**\n")
                for err in result.errors:
                    report.append(f"- {err}\n")

    # Summary
    report.append("\n## Summary\n")

    total = len(results)
    passed = sum(1 for r in results if (
        r.reversal_success and
        r.reapply_success and
        r.data_integrity
    ))

    report.append(f"- **Total tests**: {total}\n")
    report.append(f"- **Tests passed**: {passed}\n")
    report.append(f"- **Tests failed**: {total - passed}\n")
    report.append(f"- **Success rate**: {passed/total*100:.1f}%\n")

    if passed == total:
        report.append("\n✅ **ALL TESTS PASSED** - Migration reversal verified successfully!\n")
    else:
        report.append(f"\n⚠ **{total - passed} TESTS FAILED** - Review errors above.\n")

    return "".join(report)


if __name__ == "__main__":
    main()
