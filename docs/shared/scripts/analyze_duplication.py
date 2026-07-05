#!/usr/bin/env python3
"""
Duplication Analyzer for Ecosystem-Wide Architectural Refactoring

Scans all Python modules across ctc-research.com/apps/, structa.cloud/apps/,
and venv/libs/ packages to detect code duplication (≥70% similarity threshold).
Uses AST-based comparison for semantic similarity.
"""

import ast
import hashlib
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

import networkx as nx


@dataclass
class DuplicationResult:
    """Result of duplication analysis between two files."""
    file_a: str
    file_b: str
    similarity: float  # 0.0 to 1.0
    duplicated_lines: List[Tuple[int, int]]  # [(start_a, end_a), (start_b, end_b)]
    category: str  # "extract-to-osoul", "extract-to-rseal", "extract-to-grep", "already-extracted", "project-specific"
    target_package: str
    target_module: str


@dataclass
class ModuleInfo:
    """Information about a Python module."""
    path: str
    ast_tree: ast.AST
    normalized_ast: str
    imports: List[str]
    classes: List[str]
    functions: List[str]
    lines: int


class DuplicationAnalyzer:
    """
    Scans all Python modules for code similarity and duplication.
    Uses AST-based comparison for semantic similarity.
    """

    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold  # 70% similarity threshold
        self.results: List[DuplicationResult] = []
        self.modules: Dict[str, ModuleInfo] = {}
        self.import_graph = nx.DiGraph()

    def scan_directories(self, paths: List[str]) -> List[DuplicationResult]:
        """Scan multiple directories for duplicated code."""
        print(f"Scanning {len(paths)} directories for Python modules...")

        # Collect all Python files
        python_files = []
        for path in paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    # Skip hidden directories and virtual environments
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.venv', 'node_modules']]
                    for file in files:
                        if file.endswith('.py'):
                            python_files.append(os.path.join(root, file))

        print(f"Found {len(python_files)} Python files")

        # Parse and analyze each file
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"  Parsing file {i}/{len(python_files)}...")
            try:
                self._parse_module(file_path)
            except (SyntaxError, UnicodeDecodeError) as e:
                print(f"  Warning: Could not parse {file_path}: {e}")
                continue

        print(f"Successfully parsed {len(self.modules)} modules")

        # Compare all pairs
        print("Comparing modules for duplication...")
        module_paths = list(self.modules.keys())
        for i in range(len(module_paths)):
            for j in range(i + 1, len(module_paths)):
                file_a = module_paths[i]
                file_b = module_paths[j]
                similarity = self._compare_modules(file_a, file_b)

                if similarity >= self.threshold:
                    result = self._create_duplication_result(file_a, file_b, similarity)
                    self.results.append(result)

        print(f"Found {len(self.results)} duplicated pairs (similarity ≥ {self.threshold})")
        return self.results

    def _parse_module(self, file_path: str) -> None:
        """Parse a Python file and extract AST information."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            # Try with different encoding or skip problematic files
            return

        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)

        # Extract class and function names
        classes = []
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)

        # Normalize AST (remove comments, docstrings, whitespace)
        normalized = self._normalize_ast(tree)

        self.modules[file_path] = ModuleInfo(
            path=file_path,
            ast_tree=tree,
            normalized_ast=normalized,
            imports=imports,
            classes=classes,
            functions=functions,
            lines=len(content.splitlines())
        )

        # Add to import graph
        self.import_graph.add_node(file_path)
        for imp in imports:
            # Simplified import tracking
            self.import_graph.add_edge(file_path, imp)

    def _normalize_ast(self, tree: ast.AST) -> str:
        """Normalize AST by removing formatting differences."""
        # Remove docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    # Remove docstrings
                    node.value = ast.Constant(value="", kind=None)

        # Convert back to code and normalize
        normalized_code = ast.unparse(tree)

        # Remove extra whitespace and normalize line endings
        lines = []
        for line in normalized_code.splitlines():
            line = line.strip()
            if line:  # Skip empty lines
                lines.append(line)

        return '\n'.join(lines)

    def _compare_modules(self, file_a: str, file_b: str) -> float:
        """
        Compare two modules and return similarity score (0.0 to 1.0).
        Uses normalized AST string comparison.
        """
        if file_a not in self.modules or file_b not in self.modules:
            return 0.0

        module_a = self.modules[file_a]
        module_b = self.modules[file_b]

        # Simple string similarity using longest common subsequence
        str_a = module_a.normalized_ast
        str_b = module_b.normalized_ast

        if not str_a or not str_b:
            return 0.0

        # Use sequence matcher for similarity
        import difflib
        similarity = difflib.SequenceMatcher(None, str_a, str_b).ratio()

        return similarity

    def _create_duplication_result(self, file_a: str, file_b: str, similarity: float) -> DuplicationResult:
        """Create a DuplicationResult with categorization."""
        # Determine category based on file locations
        category, target_package, target_module = self._categorize_duplication(file_a, file_b)

        # Estimate duplicated lines (simplified)
        lines_a = self.modules[file_a].lines
        lines_b = self.modules[file_b].lines
        avg_lines = (lines_a + lines_b) // 2
        duplicated_lines = [(1, avg_lines), (1, avg_lines)]  # Simplified

        return DuplicationResult(
            file_a=file_a,
            file_b=file_b,
            similarity=similarity,
            duplicated_lines=duplicated_lines,
            category=category,
            target_package=target_package,
            target_module=target_module
        )

    def _categorize_duplication(self, file_a: str, file_b: str) -> Tuple[str, str, str]:
        """Categorize duplication and determine target package."""
        # Check if either file is already in a package
        if 'venv/libs/django-fusion' in file_a or 'venv/libs/django-fusion' in file_b:
            return "already-extracted", "django_fusion", ""
        elif 'venv/libs/crafts-ai' in file_a or 'venv/libs/crafts-ai' in file_b:
            return "already-extracted", "crafts_ai", ""
        elif 'venv/libs/django-fusion' in file_a or 'venv/libs/django-fusion' in file_b:
            return "already-extracted", "django_fusion", ""
        elif 'applications/libs/crafts-ai' in file_a or 'applications/libs/crafts-ai' in file_b:
            return "already-extracted", "crafts-ai", ""

        # Analyze imports to determine category
        imports_a = set(self.modules[file_a].imports)
        imports_b = set(self.modules[file_b].imports)
        all_imports = imports_a.union(imports_b)

        # Check for Wagtail imports
        has_wagtail = any('wagtail' in imp.lower() for imp in all_imports)
        has_celery = any('celery' in imp.lower() for imp in all_imports)
        has_crafts_ai = any('crafts_ai' in imp for imp in all_imports)

        # Check for test-related imports
        has_pytest = any('pytest' in imp.lower() for imp in all_imports)
        has_unittest = any('unittest' in imp.lower() for imp in all_imports)
        has_hypothesis = any('hypothesis' in imp.lower() for imp in all_imports)

        # Determine category
        if has_wagtail or has_celery or has_crafts_ai:
            return "extract-to-rseal", "crafts_ai", self._determine_module_path(file_a)
        elif has_pytest or has_unittest or has_hypothesis:
            return "extract-to-grep", "django_fusion", self._determine_module_path(file_a)
        elif 'apps/handlers' in file_a or 'apps/handlers' in file_b:
            # Handler logic - check if it's pure Django or has Wagtail
            if has_wagtail:
                return "extract-to-rseal", "crafts_ai", "handlers"
            else:
                return "extract-to-osoul", "django_fusion", "handlers"
        else:
            # Default to osoul for foundation logic
            return "extract-to-osoul", "django_fusion", self._determine_module_path(file_a)

    def _determine_module_path(self, file_path: str) -> str:
        """Determine the module path within target package."""
        # Extract relative path from project root
        if 'ctc-research.com/apps/' in file_path:
            rel_path = file_path.split('ctc-research.com/apps/')[1]
        elif 'structa.cloud/apps/' in file_path:
            rel_path = file_path.split('structa.cloud/apps/')[1]
        else:
            # For files in packages or other locations
            rel_path = os.path.basename(file_path)

        # Remove .py extension and convert to module path
        if rel_path.endswith('.py'):
            rel_path = rel_path[:-3]

        # Convert path separators to dots
        module_path = rel_path.replace('/', '.').replace('\\', '.')

        return module_path

    def generate_report(self) -> str:
        """Generate comprehensive duplication report."""
        report_lines = [
            "# Duplication Report",
            "",
            f"Generated: {self._get_timestamp()}",
            "",
            "## Summary",
            "",
            f"- Total files scanned: {len(self.modules)}",
            f"- Duplicated pairs found: {len(self.results)}",
            f"- Similarity threshold: {self.threshold}",
            "",
            "## Categories",
        ]

        # Count by category
        categories = defaultdict(int)
        for result in self.results:
            categories[result.category] += 1

        for category, count in sorted(categories.items()):
            report_lines.append(f"- {category}: {count} pairs")

        report_lines.append("")
        report_lines.append("## Duplication Details")
        report_lines.append("")

        # Sort by similarity (highest first)
        sorted_results = sorted(self.results, key=lambda x: x.similarity, reverse=True)

        for i, result in enumerate(sorted_results, 1):
            report_lines.append(f"### {i}. {os.path.basename(result.file_a)} ↔ {os.path.basename(result.file_b)}")
            report_lines.append("")
            report_lines.append(f"**Similarity**: {result.similarity:.1%}")
            report_lines.append("")
            report_lines.append("**Locations**:")
            report_lines.append(f"- `{result.file_a}`")
            report_lines.append(f"- `{result.file_b}`")
            report_lines.append("")
            report_lines.append(f"**Target**: `{result.target_package}.{result.target_module}`")
            report_lines.append("")
            report_lines.append(f"**Category**: {result.category}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        return '\n'.join(report_lines)

    def _get_timestamp(self) -> str:
        """Get current timestamp for report."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point for the duplication analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze code duplication across the ecosystem')
    parser.add_argument('--threshold', type=float, default=0.70,
                       help='Similarity threshold (default: 0.70)')
    parser.add_argument('--output', type=str, default='DUPLICATION_REPORT.md',
                       help='Output file path (default: DUPLICATION_REPORT.md)')
    parser.add_argument('--fail-on-violation', action='store_true',
                       help='Exit with error code if duplication is found')

    args = parser.parse_args()

    # Define directories to scan
    directories = [
        'ctc-research.com/apps/',
        'structa.cloud/apps/',
        'venv/libs/django-fusion/',
        'venv/libs/crafts-ai/',
        'venv/libs/django-fusion/',
        'applications/libs/crafts-ai/'
    ]

    # Filter out directories that don't exist
    existing_dirs = [d for d in directories if os.path.exists(d)]

    if not existing_dirs:
        print("Error: No directories found to scan")
        sys.exit(1)

    print(f"Starting duplication analysis with threshold {args.threshold}")
    print(f"Scanning directories: {existing_dirs}")

    analyzer = DuplicationAnalyzer(threshold=args.threshold)
    results = analyzer.scan_directories(existing_dirs)

    # Generate report
    report = analyzer.generate_report()

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report written to {args.output}")

    # Exit with error code if duplication found and fail-on-violation is set
    if args.fail_on_violation and results:
        print(f"Error: Found {len(results)} duplicated pairs (threshold: {args.threshold})")
        sys.exit(1)

    print("Analysis complete")


if __name__ == '__main__':
    main()
