#!/usr/bin/env python3
"""
Scan for deprecated code across all Django packages.

This script identifies:
1. Commented-out code blocks
2. Unused imports (using autoflake)
3. Deprecated functions (marked with @deprecated or TODO: remove)
"""

import ast
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class DeprecatedItem:
    """Represents a deprecated code item."""
    file_path: str
    line_number: int
    item_type: str  # "commented_code", "unused_import", "deprecated_function"
    description: str
    code_snippet: str = ""
    severity: str = "medium"  # "low", "medium", "high"


@dataclass
class DeprecationReport:
    """Report of all deprecated code found."""
    commented_code: List[DeprecatedItem] = field(default_factory=list)
    unused_imports: List[DeprecatedItem] = field(default_factory=list)
    deprecated_functions: List[DeprecatedItem] = field(default_factory=list)

    def total_count(self) -> int:
        return len(self.commented_code) + len(self.unused_imports) + len(self.deprecated_functions)


class DeprecatedCodeScanner:
    """Scanner for deprecated code patterns."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.report = DeprecationReport()

    def scan_all_packages(self) -> DeprecationReport:
        """Scan all packages for deprecated code."""
        packages = ["django-osoul", "django-rseal", "django-seed", "django-grep"]

        for package in packages:
            package_path = self.root_dir / package
            if package_path.exists():
                print(f"Scanning {package}...")
                self.scan_package(package_path, package)

        return self.report

    def scan_package(self, package_path: Path, package_name: str):
        """Scan a single package."""
        # Find all Python files
        python_files = list(package_path.rglob("*.py"))

        for py_file in python_files:
            # Skip __pycache__ and .venv directories
            if "__pycache__" in str(py_file) or ".venv" in str(py_file) or ".git" in str(py_file):
                continue

            try:
                self.scan_file(py_file, package_name)
            except Exception as e:
                print(f"  Error scanning {py_file}: {e}")

    def scan_file(self, file_path: Path, package_name: str):
        """Scan a single file for deprecated code."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

        # Scan for commented-out code
        self.find_commented_code(file_path, lines, package_name)

        # Scan for deprecated decorators and TODO comments
        self.find_deprecated_markers(file_path, content, lines, package_name)

        # Scan for unused imports using AST
        self.find_unused_imports_ast(file_path, content, package_name)

    def find_commented_code(self, file_path: Path, lines: List[str], package_name: str):
        """Find commented-out code blocks."""
        consecutive_comments = []
        start_line = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check if line is a comment (but not docstring)
            if stripped.startswith('#'):
                # Check if it looks like code (has common code patterns)
                if self.looks_like_code(stripped[1:].strip()):
                    if not consecutive_comments:
                        start_line = i
                    consecutive_comments.append(line)
                else:
                    # Reset if it's just a regular comment
                    if len(consecutive_comments) >= 2:
                        self.add_commented_code_block(
                            file_path, start_line, consecutive_comments, package_name
                        )
                    consecutive_comments = []
            else:
                # End of comment block
                if len(consecutive_comments) >= 2:
                    self.add_commented_code_block(
                        file_path, start_line, consecutive_comments, package_name
                    )
                consecutive_comments = []

        # Check final block
        if len(consecutive_comments) >= 2:
            self.add_commented_code_block(
                file_path, start_line, consecutive_comments, package_name
            )

    def looks_like_code(self, text: str) -> bool:
        """Check if commented text looks like code."""
        # Patterns that suggest code
        code_patterns = [
            r'\bdef\s+\w+\s*\(',  # function definition
            r'\bclass\s+\w+',  # class definition
            r'\bimport\s+\w+',  # import statement
            r'\bfrom\s+\w+\s+import',  # from import
            r'\breturn\s+',  # return statement
            r'\bif\s+.*:',  # if statement
            r'\bfor\s+\w+\s+in\s+',  # for loop
            r'\bwhile\s+.*:',  # while loop
            r'\btry:',  # try block
            r'\bexcept\s+',  # except block
            r'=\s*\[.*\]',  # list assignment
            r'=\s*\{.*\}',  # dict assignment
            r'\w+\s*=\s*\w+\(',  # function call assignment
            r'\w+\.\w+\(',  # method call
        ]

        for pattern in code_patterns:
            if re.search(pattern, text):
                return True

        return False

    def add_commented_code_block(self, file_path: Path, start_line: int,
                                  comments: List[str], package_name: str):
        """Add a commented code block to the report."""
        rel_path = file_path.relative_to(self.root_dir)
        snippet = '\n'.join(comments[:5])  # First 5 lines
        if len(comments) > 5:
            snippet += f"\n... ({len(comments) - 5} more lines)"

        item = DeprecatedItem(
            file_path=str(rel_path),
            line_number=start_line,
            item_type="commented_code",
            description=f"Commented-out code block ({len(comments)} lines)",
            code_snippet=snippet,
            severity="medium"
        )
        self.report.commented_code.append(item)

    def find_deprecated_markers(self, file_path: Path, content: str,
                                lines: List[str], package_name: str):
        """Find @deprecated decorators and TODO: remove comments."""
        rel_path = file_path.relative_to(self.root_dir)

        # Find @deprecated decorators
        deprecated_pattern = r'@deprecated|@deprecate'
        for i, line in enumerate(lines, 1):
            if re.search(deprecated_pattern, line, re.IGNORECASE):
                # Get the next few lines for context
                context_lines = lines[i-1:min(i+3, len(lines))]
                snippet = '\n'.join(context_lines)

                item = DeprecatedItem(
                    file_path=str(rel_path),
                    line_number=i,
                    item_type="deprecated_function",
                    description="Function/class marked with @deprecated decorator",
                    code_snippet=snippet,
                    severity="high"
                )
                self.report.deprecated_functions.append(item)

        # Find TODO: remove comments
        todo_remove_pattern = r'#\s*TODO:?\s*(remove|delete|deprecated)'
        for i, line in enumerate(lines, 1):
            if re.search(todo_remove_pattern, line, re.IGNORECASE):
                item = DeprecatedItem(
                    file_path=str(rel_path),
                    line_number=i,
                    item_type="deprecated_function",
                    description="Code marked with TODO: remove comment",
                    code_snippet=line.strip(),
                    severity="high"
                )
                self.report.deprecated_functions.append(item)

    def find_unused_imports_ast(self, file_path: Path, content: str, package_name: str):
        """Find unused imports using AST analysis."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        # Collect all imports
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = (node.lineno, alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == '*':
                        continue
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = (node.lineno, f"{node.module}.{alias.name}")

        # Collect all name references
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Get the base name
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        # Find unused imports
        rel_path = file_path.relative_to(self.root_dir)
        for import_name, (line_no, full_name) in imports.items():
            if import_name not in used_names:
                item = DeprecatedItem(
                    file_path=str(rel_path),
                    line_number=line_no,
                    item_type="unused_import",
                    description=f"Unused import: {full_name}",
                    code_snippet=f"import {full_name}",
                    severity="low"
                )
                self.report.unused_imports.append(item)


def generate_markdown_report(report: DeprecationReport, output_file: Path):
    """Generate a markdown report of deprecated code."""
    with open(output_file, 'w') as f:
        f.write("# Deprecated Code Report\n\n")
        f.write("This report identifies deprecated code that should be removed during the refactoring process.\n\n")
        f.write(f"**Total Items Found**: {report.total_count()}\n\n")
        f.write("---\n\n")

        # Commented-out code
        f.write("## 1. Commented-Out Code Blocks\n\n")
        f.write(f"**Count**: {len(report.commented_code)}\n\n")
        if report.commented_code:
            f.write("| File | Line | Description | Severity |\n")
            f.write("|------|------|-------------|----------|\n")
            for item in sorted(report.commented_code, key=lambda x: x.file_path):
                f.write(f"| {item.file_path} | {item.line_number} | {item.description} | {item.severity} |\n")
            f.write("\n### Details\n\n")
            for item in sorted(report.commented_code, key=lambda x: x.file_path):
                f.write(f"#### {item.file_path}:{item.line_number}\n\n")
                f.write(f"```python\n{item.code_snippet}\n```\n\n")
        else:
            f.write("No commented-out code blocks found.\n\n")

        f.write("---\n\n")

        # Unused imports
        f.write("## 2. Unused Imports\n\n")
        f.write(f"**Count**: {len(report.unused_imports)}\n\n")
        if report.unused_imports:
            # Group by file
            by_file: Dict[str, List[DeprecatedItem]] = {}
            for item in report.unused_imports:
                if item.file_path not in by_file:
                    by_file[item.file_path] = []
                by_file[item.file_path].append(item)

            f.write("| File | Unused Imports Count |\n")
            f.write("|------|---------------------|\n")
            for file_path in sorted(by_file.keys()):
                f.write(f"| {file_path} | {len(by_file[file_path])} |\n")

            f.write("\n### Details\n\n")
            for file_path in sorted(by_file.keys()):
                f.write(f"#### {file_path}\n\n")
                for item in sorted(by_file[file_path], key=lambda x: x.line_number):
                    f.write(f"- Line {item.line_number}: `{item.description}`\n")
                f.write("\n")
        else:
            f.write("No unused imports found.\n\n")

        f.write("---\n\n")

        # Deprecated functions
        f.write("## 3. Deprecated Functions and Classes\n\n")
        f.write(f"**Count**: {len(report.deprecated_functions)}\n\n")
        if report.deprecated_functions:
            f.write("| File | Line | Description | Severity |\n")
            f.write("|------|------|-------------|----------|\n")
            for item in sorted(report.deprecated_functions, key=lambda x: x.file_path):
                f.write(f"| {item.file_path} | {item.line_number} | {item.description} | {item.severity} |\n")
            f.write("\n### Details\n\n")
            for item in sorted(report.deprecated_functions, key=lambda x: x.file_path):
                f.write(f"#### {item.file_path}:{item.line_number}\n\n")
                f.write(f"```python\n{item.code_snippet}\n```\n\n")
        else:
            f.write("No deprecated functions or classes found.\n\n")

        f.write("---\n\n")

        # Removal recommendations
        f.write("## Removal Recommendations\n\n")
        f.write("### High Priority (Remove Immediately)\n\n")
        high_priority = [item for item in report.deprecated_functions if item.severity == "high"]
        if high_priority:
            for item in high_priority:
                f.write(f"- [ ] {item.file_path}:{item.line_number} - {item.description}\n")
        else:
            f.write("None\n")
        f.write("\n")

        f.write("### Medium Priority (Remove During Refactoring)\n\n")
        medium_priority = report.commented_code
        if medium_priority:
            for item in medium_priority[:10]:  # Show first 10
                f.write(f"- [ ] {item.file_path}:{item.line_number} - {item.description}\n")
            if len(medium_priority) > 10:
                f.write(f"- ... and {len(medium_priority) - 10} more\n")
        else:
            f.write("None\n")
        f.write("\n")

        f.write("### Low Priority (Clean Up with Linter)\n\n")
        f.write(f"- [ ] Remove {len(report.unused_imports)} unused imports across all files\n")
        f.write("  - Recommended tool: `autoflake --remove-all-unused-imports --in-place --recursive libs/`\n")
        f.write("\n")


def main():
    """Main entry point."""
    libs_dir = Path(__file__).parent

    print("=" * 60)
    print("Deprecated Code Scanner")
    print("=" * 60)
    print()

    scanner = DeprecatedCodeScanner(libs_dir)
    report = scanner.scan_all_packages()

    print()
    print("=" * 60)
    print("Scan Complete")
    print("=" * 60)
    print(f"Commented-out code blocks: {len(report.commented_code)}")
    print(f"Unused imports: {len(report.unused_imports)}")
    print(f"Deprecated functions/classes: {len(report.deprecated_functions)}")
    print(f"Total items: {report.total_count()}")
    print()

    # Generate report
    output_file = libs_dir / "DEPRECATED_CODE.md"
    generate_markdown_report(report, output_file)
    print(f"Report saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
