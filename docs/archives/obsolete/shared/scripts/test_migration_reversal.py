#!/usr/bin/env python
"""
Test Migration Reversal - Validates that migrations can be reversed.

This script tests migration reversal by:
1. Analyzing migration files to ensure they use reversible operations
2. Checking for RunPython/RunSQL with proper reverse operations
3. Documenting the reversal status for each migration
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class MigrationReversalTest:
    """Result of testing a migration for reversal capability."""
    app_label: str
    migration_name: str
    file_path: str
    is_reversible: bool
    test_results: List[str]
    issues: List[str]


class MigrationReversalTester:
    """Tests migration reversal capability."""

    def __init__(self):
        self.results: List[MigrationReversalTest] = []
        self.projects = [
            "ctc-research.com",
            "structa.cloud"
        ]

    def test_all_migrations(self) -> List[MigrationReversalTest]:
        """Test all migrations for reversal capability."""
        self.results = []

        for project in self.projects:
            self._test_project(project)

        return self.results

    def _test_project(self, project: str) -> None:
        """Test all migrations in a project."""
        apps_dir = Path(project) / "apps"

        if not apps_dir.exists():
            print(f"Warning: {apps_dir} does not exist")
            return

        # Find all app directories
        for app_dir in apps_dir.iterdir():
            if not app_dir.is_dir() or app_dir.name.startswith("_"):
                continue

            migrations_dir = app_dir / "migrations"
            if not migrations_dir.exists():
                continue

            # Test all migration files
            for migration_file in sorted(migrations_dir.glob("*.py")):
                if migration_file.name.startswith("_"):
                    continue

                test_result = self._test_migration(
                    project,
                    app_dir.name,
                    migration_file
                )
                self.results.append(test_result)

    def _test_migration(
        self,
        project: str,
        app_name: str,
        migration_file: Path
    ) -> MigrationReversalTest:
        """Test a single migration for reversal capability."""
        migration_name = migration_file.stem

        with open(migration_file, 'r') as f:
            content = f.read()

        test_results = []
        issues = []

        # Test 1: Check for RunPython without reverse
        if "RunPython(" in content:
            if "reverse_code=" in content or "reverse=" in content:
                test_results.append("✓ RunPython has reverse_code")
            else:
                test_results.append("✗ RunPython missing reverse_code")
                issues.append("RunPython operation without reverse_code")

        # Test 2: Check for RunSQL without reverse
        if "RunSQL(" in content:
            if "reverse_sql=" in content:
                test_results.append("✓ RunSQL has reverse_sql")
            else:
                test_results.append("✗ RunSQL missing reverse_sql")
                issues.append("RunSQL operation without reverse_sql")

        # Test 3: Check for state_operations only (non-reversible)
        if "state_operations=" in content and "operations=" not in content:
            test_results.append("✗ Uses state_operations only (non-reversible)")
            issues.append("Migration uses state_operations only")

        # Test 4: Extract and validate operations
        operations = self._extract_operations(content)
        reversible_ops = self._check_operations_reversible(operations)

        if reversible_ops:
            test_results.append(f"✓ All {len(operations)} operations are reversible")
        else:
            test_results.append(f"✗ Some operations may not be reversible")
            issues.append(f"Non-reversible operations found: {operations}")

        # Test 5: Check for data migrations
        if "RunPython" in content or "RunSQL" in content:
            test_results.append("⚠ Data migration detected - verify reverse logic manually")

        is_reversible = len(issues) == 0

        return MigrationReversalTest(
            app_label=app_name,
            migration_name=migration_name,
            file_path=str(migration_file),
            is_reversible=is_reversible,
            test_results=test_results,
            issues=issues
        )

    def _extract_operations(self, content: str) -> List[str]:
        """Extract operation names from migration file."""
        operations = []
        pattern = r'migrations\.(\w+)\('
        matches = re.findall(pattern, content)

        for match in matches:
            if match not in operations:
                operations.append(match)

        return operations

    def _check_operations_reversible(self, operations: List[str]) -> bool:
        """Check if all operations are reversible."""
        reversible_operations = [
            "swappable_dependency",  # Not an operation, just a dependency marker
            "CreateModel",
            "DeleteModel",
            "RenameModel",
            "AlterModelOptions",
            "AlterModelTable",
            "AddField",
            "RemoveField",
            "RenameField",
            "AlterField",
            "AddConstraint",
            "RemoveConstraint",
            "AddIndex",
            "RemoveIndex",
            "AlterUniqueTogether",
            "AlterIndexTogether",
            "AlterOrderWithRespectTo",
            "RunPython",  # If has reverse
            "RunSQL",     # If has reverse_sql
        ]

        for op in operations:
            if op not in reversible_operations:
                return False

        return True

    def generate_report(self) -> str:
        """Generate a report of migration reversal tests."""
        report = []
        report.append("# Migration Reversal Test Report\n")
        report.append(f"Total migrations tested: {len(self.results)}\n")

        # Count by status
        reversible = sum(1 for m in self.results if m.is_reversible)
        non_reversible = len(self.results) - reversible

        report.append(f"Reversible migrations: {reversible}\n")
        report.append(f"Non-reversible migrations: {non_reversible}\n")

        if non_reversible > 0:
            report.append("\n## Non-Reversible Migrations\n")
            for migration in self.results:
                if not migration.is_reversible:
                    report.append(f"\n### {migration.app_label}/{migration.migration_name}\n")
                    report.append(f"File: {migration.file_path}\n")
                    if migration.issues:
                        report.append("Issues:\n")
                        for issue in migration.issues:
                            report.append(f"- {issue}\n")

        report.append("\n## Detailed Test Results\n")

        # Group by app
        by_app: Dict[str, List[MigrationReversalTest]] = {}
        for migration in self.results:
            if migration.app_label not in by_app:
                by_app[migration.app_label] = []
            by_app[migration.app_label].append(migration)

        for app_label in sorted(by_app.keys()):
            report.append(f"\n### {app_label}\n")
            for migration in by_app[app_label]:
                status = "✓ Reversible" if migration.is_reversible else "✗ Non-Reversible"
                report.append(f"\n#### {migration.migration_name}: {status}\n")
                for test_result in migration.test_results:
                    report.append(f"- {test_result}\n")

        return "".join(report)


def main():
    """Main entry point."""
    tester = MigrationReversalTester()

    print("Testing migration reversal capability...")
    results = tester.test_all_migrations()

    print(f"Tested {len(results)} migrations")

    # Print summary
    reversible = sum(1 for m in results if m.is_reversible)
    non_reversible = len(results) - reversible

    print(f"Reversible: {reversible}")
    print(f"Non-reversible: {non_reversible}")

    if non_reversible > 0:
        print("\nNon-reversible migrations:")
        for migration in results:
            if not migration.is_reversible:
                print(f"  - {migration.app_label}/{migration.migration_name}")
                for issue in migration.issues:
                    print(f"    - {issue}")

    # Generate report
    report = tester.generate_report()

    # Write report
    report_path = Path("MIGRATION_REVERSAL_TEST_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nReport written to {report_path}")


if __name__ == "__main__":
    main()
