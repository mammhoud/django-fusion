#!/usr/bin/env python3
"""
Simplified Duplication Analyzer without networkx dependency
"""

import ast
import difflib
import hashlib
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class ModuleInfo:
    path: str
    content: str
    normalized: str
    imports: List[str]
    classes: List[str]
    functions: List[str]
    line_count: int

class SimpleDuplicationAnalyzer:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.modules = {}
        self.results = []

    def analyze_directory(self, directory: str):
        """Analyze all Python files in directory and subdirectories."""
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs_to_remove = []
            for d in dirs:
                if d.startswith('.') or d in ['__pycache__', 'node_modules', '.git']:
                    dirs_to_remove.append(d)
            for d in dirs_to_remove:
                dirs.remove(d)

            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        print(f"Found {len(python_files)} Python files in {directory}")
        return python_files

    def parse_file(self, filepath: str) -> ModuleInfo:
        """Parse a Python file and extract information."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return None

        try:
            tree = ast.parse(content, filename=filepath)
        except:
            return None

        # Extract imports
        imports = []
        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)

        # Normalize content for comparison
        normalized = self._normalize_code(content)

        return ModuleInfo(
            path=filepath,
            content=content,
            normalized=normalized,
            imports=imports,
            classes=classes,
            functions=functions,
            line_count=len(content.splitlines())
        )

    def _normalize_code(self, code: str) -> str:
        """Normalize code by removing comments, docstrings, and extra whitespace."""
        # Simple normalization: remove comments and extra whitespace
        lines = []
        for line in code.split('\n'):
            # Remove inline comments
            if '#' in line:
                line = line.split('#')[0]
            line = line.strip()
            if line:
                lines.append(line)
        return ' '.join(lines)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two normalized code strings."""
        if not text1 or not text2:
            return 0.0

        # Simple similarity using difflib
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def analyze(self, directories: List[str]):
        """Analyze directories for duplication."""
        all_files = []
        for directory in directories:
            if os.path.exists(directory):
                all_files.extend(self.analyze_directory(directory))

        print(f"Found {len(all_files)} Python files")

        # Parse all files
        modules = {}
        for filepath in all_files:
            module_info = self.parse_file(filepath)
            if module_info:
                modules[filepath] = module_info
                self.modules[filepath] = module_info

        print(f"Successfully parsed {len(modules)} files")

        # Compare all pairs
        filepaths = list(modules.keys())
        for i in range(len(filepaths)):
            for j in range(i+1, len(filepaths)):
                file1 = filepaths[i]
                file2 = filepaths[j]

                sim = self.calculate_similarity(
                    modules[file1].normalized,
                    modules[file2].normalized
                )

                if sim >= self.threshold:
                    self.results.append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': sim,
                        'category': self._categorize(modules[file1], modules[file2])
                    })

        return self.results

    def _categorize(self, mod1: ModuleInfo, mod2: ModuleInfo) -> str:
        """Categorize the duplication."""
        # Check for Wagtail/Celery imports
        all_imports = set(mod1.imports + mod2.imports)
        has_wagtail = any('wagtail' in imp.lower() for imp in all_imports)
        has_celery = any('celery' in imp.lower() for imp in all_imports)

        if has_wagtail or has_celery:
            return "extract-to-rseal"
        else:
            return "extract-to-osoul"

    def generate_report(self) -> str:
        """Generate a markdown report."""
        lines = [
            "# Duplication Analysis Report",
            f"Generated: {self._get_timestamp()}",
            f"Threshold: {self.threshold}",
            f"Total files analyzed: {len(self.modules)}",
            f"Duplicated pairs found: {len(self.results)}",
            "",
            "## Duplicated Files",
            ""
        ]

        for i, result in enumerate(self.results, 1):
            lines.extend([
                f"### Pair {i}",
                f"- **Similarity**: {result['similarity']:.1%}",
                f"- **File 1**: `{result['file1']}`",
                f"- **File 2**: `{result['file2']}`",
                f"- **Category**: {result['category']}",
                ""
            ])

        return '\n'.join(lines)

    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze code duplication')
    parser.add_argument('--threshold', type=float, default=0.7, help='Similarity threshold')
    parser.add_argument('--output', default='DUPLICATION_REPORT.md', help='Output file')
    parser.add_argument('directories', nargs='+', help='Directories to analyze')

    args = parser.parse_args()

    analyzer = SimpleDuplicationAnalyzer(threshold=args.threshold)

    print(f"Analyzing directories: {args.directories}")
    results = analyzer.analyze(args.directories)

    report = analyzer.generate_report()

    with open(args.output, 'w') as f:
        f.write(report)

    print(f"Report written to {args.output}")
    print(f"Found {len(results)} duplicated pairs")

if __name__ == '__main__':
    main()
