#!/usr/bin/env python
"""
Migration Validator - Validates all migrations have reverse operations.

This script scans all migrations in both projects and identifies any migrations
that don't have reverse operations (i.e., migrations that only have forward
operations but no corresponding reverse logic).
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class MigrationInfo:
    """Information about a single migration."""
    app_label: str
    migration_name: str
    file_path: str
    has_reverse: bool
    operations: List[str]
    issues: List[str]


class MigrationValidator:
    """Validates all migrations have reverse operations."""

    def __init__(self):
        self.results: List[MigrationInfo] = []
        self.projects = [
            "ctc-research.com",
            "structa.cloud"
        ]

    def check_all_migrations(self) -> List[MigrationInfo]:
        """
        Scan both projects for migrations and check for reverse operations.

        Returns:
            List of MigrationInfo objects for all migrations found
        """
        self.results = []

        for project in self.projects:
            self._scan_project(project)

        return self.results

    def _scan_project(self, project: str) -> None:
        """Scan a single project for migrations."""
        project_path = Path(project)

        # Scan both apps/ and projects/ directories
        scan_dirs = [
            project_path / "apps",
            project_path / "core"
        ]

        for base_dir in scan_dirs:
            if not base_dir.exists():
                continue

            # Recursively find all migration directories
            for migrations_dir in base_dir.rglob("migrations"):
                # Skip virtual environment directories
                if ".venv" in str(migrations_dir) or ".pytest_cache" in str(migrations_dir):
                    continue

                # Get app name from parent directory
                app_dir = migrations_dir.parent
                app_name = app_dir.name

                # Skip if this is a __pycache__ directory
                if app_name == "__pycache__":
                    continue

                # Scan all migration files
                for migration_file in sorted(migrations_dir.glob("*.py")):
                    if migration_file.name.startswith("_"):
                        continue

                    migration_info = self._analyze_migration(
                        project,
                        app_name,
                        migration_file
                    )
                    self.results.append(migration_info)

    def _analyze_migration(
        self,
        project: str,
        app_name: str,
        migration_file: Path
    ) -> MigrationInfo:
        """
        Analyze a single migration file for reverse operations.

        Args:
            project: Project name (ctc-research.com or structa.cloud)
            app_name: App name (accounts, lms, content, etc.)
            migration_file: Path to the migration file

        Returns:
            MigrationInfo object with analysis results
        """
        migration_name = migration_file.stem

        with open(migration_file, 'r') as f:
            content = f.read()

        # Extract operations
        operations = self._extract_operations(content)

        # Check for reverse operations
        has_reverse = self._check_reverse_operations(content, operations)

        # Identify issues
        issues = self._identify_issues(content, operations, has_reverse)

        return MigrationInfo(
            app_label=app_name,
            migration_name=migration_name,
            file_path=str(migration_file),
            has_reverse=has_reverse,
            operations=operations,
            issues=issues
        )

    def _extract_operations(self, content: str) -> List[str]:
        """Extract operation names from migration file."""
        # Look for operations in the operations list
        operations = []

        # Match patterns like: migrations.CreateModel(...), migrations.AddField(...), etc.
        pattern = r'migrations\.(\w+)\('
        matches = re.findall(pattern, content)

        for match in matches:
            if match not in operations:
                operations.append(match)

        return operations

    def _check_reverse_operations(self, content: str, operations: List[str]) -> bool:
        """
        Check if migration has reverse operations.

        A migration has reverse operations if:
        1. It doesn't use RunPython with state_operations only
        2. It doesn't use RunSQL with reverse_sql
        3. All operations are reversible (CreateModel, AddField, etc. are reversible)
        """
        # Check for RunPython without reverse
        if "RunPython(" in content:
            # Check if it has a reverse function
            # Django supports: RunPython(forward_func, reverse_func) pattern
            # or RunPython(code=forward_func, reverse_code=reverse_func) pattern
            lines = content.split('\n')
            runpython_found = False
            has_reverse = False

            for line in lines:
                if "RunPython(" in line:
                    runpython_found = True
                    # Check for reverse_code= or reverse= parameter
                    if "reverse_code=" in line or "reverse=" in line:
                        has_reverse = True
                        break
                    # Check for RunPython(func1, func2) pattern (two arguments)
                    # Count commas in the RunPython call
                    if line.count(',') >= 1:
                        # Could be RunPython(forward, reverse) pattern
                        has_reverse = True
                        break

            if runpython_found and not has_reverse:
                return False

        # Check for RunSQL without reverse
        if "RunSQL(" in content:
            # Check if it has reverse_sql
            if "reverse_sql=" not in content:
                return False

        # Check for operations that are not reversible
        non_reversible = [
            "RunPython",  # Only if no reverse
            "RunSQL",     # Only if no reverse_sql
        ]

        # If we have only reversible operations, it's reversible
        reversible_operations = [
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
        ]

        # If all operations are reversible, return True
        for op in operations:
            if op not in reversible_operations and op not in non_reversible:
                # Unknown operation, assume it's reversible
                continue

        return True

    def _identify_issues(
        self,
        content: str,
        operations: List[str],
        has_reverse: bool
    ) -> List[str]:
        """Identify specific issues with the migration."""
        issues = []

        if not has_reverse:
            issues.append("Migration does not have reverse operations")

        # Check for RunPython without reverse
        if "RunPython(" in content:
            lines = content.split('\n')
            runpython_found = False
            has_reverse_in_runpython = False

            for line in lines:
                if "RunPython(" in line:
                    runpython_found = True
                    # Check for reverse_code= or reverse= parameter
                    if "reverse_code=" in line or "reverse=" in line:
                        has_reverse_in_runpython = True
                        break
                    # Check for RunPython(func1, func2) pattern (two arguments)
                    if line.count(',') >= 1:
                        has_reverse_in_runpython = True
                        break

            if runpython_found and not has_reverse_in_runpython:
                issues.append("RunPython operation without reverse_code or reverse function")

        # Check for RunSQL without reverse
        if "RunSQL(" in content and "reverse_sql=" not in content:
            issues.append("RunSQL operation without reverse_sql")

        return issues

    def generate_report(self) -> str:
        """Generate a report of all migrations and their reversal status."""
        report = []
        report.append("# Migration Safety Report\n")
        report.append(f"Total migrations scanned: {len(self.results)}\n")

        # Count by status
        reversible = sum(1 for m in self.results if m.has_reverse)
        non_reversible = len(self.results) - reversible

        report.append(f"Reversible migrations: {reversible}\n")
        report.append(f"Non-reversible migrations: {non_reversible}\n")

        if non_reversible > 0:
            report.append("\n## Non-Reversible Migrations\n")
            for migration in self.results:
                if not migration.has_reverse:
                    report.append(f"\n### {migration.app_label}/{migration.migration_name}\n")
                    report.append(f"File: {migration.file_path}\n")
                    report.append(f"Operations: {', '.join(migration.operations)}\n")
                    if migration.issues:
                        report.append("Issues:\n")
                        for issue in migration.issues:
                            report.append(f"- {issue}\n")

        report.append("\n## All Migrations\n")

        # Group by app
        by_app: Dict[str, List[MigrationInfo]] = {}
        for migration in self.results:
            if migration.app_label not in by_app:
                by_app[migration.app_label] = []
            by_app[migration.app_label].append(migration)

        for app_label in sorted(by_app.keys()):
            report.append(f"\n### {app_label}\n")
            for migration in by_app[app_label]:
                status = "✓ Reversible" if migration.has_reverse else "✗ Non-Reversible"
                report.append(f"- {migration.migration_name}: {status}\n")
                if migration.operations:
                    report.append(f"  Operations: {', '.join(migration.operations)}\n")

        return "".join(report)


def main():
    """Main entry point."""
    validator = MigrationValidator()

    print("Scanning migrations...")
    results = validator.check_all_migrations()

    print(f"Found {len(results)} migrations")

    # Print summary
    reversible = sum(1 for m in results if m.has_reverse)
    non_reversible = len(results) - reversible

    print(f"Reversible: {reversible}")
    print(f"Non-reversible: {non_reversible}")

    if non_reversible > 0:
        print("\nNon-reversible migrations:")
        for migration in results:
            if not migration.has_reverse:
                print(f"  - {migration.app_label}/{migration.migration_name}")
                for issue in migration.issues:
                    print(f"    - {issue}")

    # Generate report
    report = validator.generate_report()

    # Write report
    report_path = Path("MIGRATION_SAFETY_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nReport written to {report_path}")


if __name__ == "__main__":
    main()
