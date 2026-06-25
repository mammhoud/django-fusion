#!/usr/bin/env python3
"""
Boundary Checker for Ecosystem Architectural Refactoring

This script checks for boundary violations across the ecosystem:
1. crafts-ai-no-django: crafts-ai must be pure Python with zero Django imports
2. osoul-no-wagtail: django_osoul must not import wagtail, celery, or crafts_ai
3. rseal-no-projects: crafts_ai must not import project-specific code
4. grep-test-only: django_osoul must not be imported by production code
"""

import ast
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class BoundaryViolation:
    """Represents a boundary violation found in the codebase."""
    filepath: str
    line_number: int
    import_statement: str
    rule_violated: str
    fix_suggestion: str

class BoundaryChecker:
    """Checks for boundary violations across the ecosystem."""

    def __init__(self):
        self.violations: List[BoundaryViolation] = []
        self.rules = {
            "crafts-ai-no-django": {
                "source": "crafts-ai",
                "forbidden_modules": ["django", "wagtail", "celery", "crafts_ai"],
                "message": "crafts-ai must be pure Python with zero Django imports"
            },
            "osoul-no-wagtail": {
                "source": "django_osoul",
                "forbidden_modules": ["wagtail", "celery", "crafts_ai"],
                "message": "django_osoul must not import wagtail, celery, or crafts_ai"
            },
            "rseal-no-projects": {
                "source": "crafts_ai",
                "forbidden_modules": ["apps.", "ctc-research", "structa.cloud"],
                "message": "crafts_ai must not import project-specific code"
            },
            "grep-test-only": {
                "source": ["django_osoul", "crafts_ai", "apps"],
                "forbidden_modules": ["django_osoul"],
                "message": "django_osoul is test-only and must not be imported by production code"
            }
        }

    def check_file(self, filepath: str) -> List[BoundaryViolation]:
        """Check a single file for boundary violations."""
        violations = []
        filepath_str = str(filepath)

        try:
            with open(filepath_str, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, FileNotFoundError):
            return []

        # Skip non-Python files
        if not filepath_str.endswith('.py'):
            return []

        # Parse the Python file
        try:
            tree = ast.parse(content, filename=filepath_str)
        except (SyntaxError, IndentationError):
            return []  # Skip files with syntax errors

        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    import_name = name.name
                    violations.extend(self._check_import(filepath_str, import_name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    violations.extend(self._check_import(filepath_str, node.module, node.lineno))

        return violations

    def _check_import(self, filepath: str, import_name: str, line_no: int) -> List[BoundaryViolation]:
        """Check if an import violates any boundary rules."""
        violations = []
        filepath_str = str(filepath)

        # Determine which package this file belongs to
        source_package = self._get_package_from_path(filepath)
        if not source_package:
            return []

        # Check each rule
        for rule_name, rule in self.rules.items():
            # Check if this file is from a source that has this rule
            if rule_name == "crafts-ai-no-django":
                if "crafts-ai" not in source_package:
                    continue
            elif rule_name == "osoul-no-wagtail":
                if "django_osoul" not in source_package:
                    continue
            elif rule_name == "rseal-no-projects":
                if "crafts_ai" not in source_package:
                    continue
            elif rule_name == "grep-test-only":
                # Check if this is production code importing django_osoul
                if "django_osoul" in source_package or "test" in source_package:
                    continue  # django_osoul can import itself or test code can import it
                if "django_osoul" in import_name:
                    violations.append(BoundaryViolation(
                        filepath=filepath,
                        line_number=line_no,
                        import_statement=import_name,
                        rule_violated=rule_name,
                        fix_suggestion=f"Remove import of django_osoul from production code"
                    ))
                continue

            # Check if this import violates the rule
            forbidden_modules = rule["forbidden_modules"]
            for forbidden in forbidden_modules:
                if forbidden in import_name or (forbidden + "." in import_name):
                    violations.append(BoundaryViolation(
                        filepath=filepath,
                        line_number=line_no,
                        import_statement=import_name,
                        rule_violated=rule_name,
                        fix_suggestion=f"Remove import of {import_name} - {rule['message']}"
                    ))

        return violations

    def _get_package_from_path(self, filepath: str) -> str:
        """Extract package name from filepath."""
        path_str = str(filepath)

        if "crafts-ai" in path_str:
            return "crafts-ai"
        elif "django_osoul" in path_str:
            return "django_osoul"
        elif "crafts_ai" in path_str:
            return "crafts_ai"
        elif "django_osoul" in path_str:
            return "django_osoul"
        elif "apps" in path_str or "ctc-research" in path_str or "structa.cloud" in path_str:
            return "apps"
        return "unknown"

    def check_directory(self, directory: str) -> List[BoundaryViolation]:
        """Check all Python files in a directory."""
        all_violations = []
        directory = Path(directory)

        for py_file in directory.rglob("*.py"):
            violations = self.check_file(py_file)
            all_violations.extend(violations)

        return all_violations

def main():
    """Main function to run boundary checker."""
    import argparse

    parser = argparse.ArgumentParser(description='Check for boundary violations')
    parser.add_argument('directory', help='Directory to scan for violations')
    parser.add_argument('--output', '-o', help='Output file for violations')

    args = parser.parse_args()

    checker = BoundaryChecker()
    violations = checker.check_directory(args.directory)

    # Output violations
    if violations:
        print(f"Found {len(violations)} boundary violations:")
        for v in violations:
            print(f"\nFile: {v.filepath}:{v.line_number}")
            print(f"  Import: {v.import_statement}")
            print(f"  Rule Violated: {v.rule_violated}")
            print(f"  Suggestion: {v.fix_suggestion}")

        # Write to file if output specified
        if args.output:
            with open(args.output, 'w') as f:
                for v in violations:
                    f.write(f"{v.filepath}:{v.line_number}: {v.rule_violated}: {v.import_statement}\n")
    else:
        print("No boundary violations found!")

if __name__ == "__main__":
    main()
