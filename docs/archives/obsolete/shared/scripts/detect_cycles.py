#!/usr/bin/env python3
"""
Circular Dependency Detector for Ecosystem Architectural Refactoring

This script detects circular dependencies between Python modules using networkx.
It builds a dependency graph and finds cycles that need to be broken.
"""

import ast
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx


@dataclass
class CircularDependency:
    """Represents a circular dependency cycle found in the codebase."""
    cycle: List[str]  # List of module names in the cycle
    break_suggestion: str  # Suggestion for breaking the cycle

class CircularDependencyDetector:
    """Detects circular dependencies between Python modules."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.module_to_path: Dict[str, str] = {}
        self.path_to_module: Dict[str, str] = {}

    def build_dependency_graph(self, directory: str) -> nx.DiGraph:
        """Build a directed graph of module dependencies."""
        directory = Path(directory)

        # First pass: collect all Python modules
        for py_file in directory.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            module_name = self._path_to_module_name(py_file)
            self.module_to_path[module_name] = str(py_file)
            self.path_to_module[str(py_file)] = module_name
            self.graph.add_node(module_name)

        # Second pass: add edges based on imports
        for py_file in directory.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            source_module = self.path_to_module[str(py_file)]
            imports = self._extract_imports(py_file)

            for import_name in imports:
                target_module = self._resolve_import(import_name, py_file)
                if target_module and target_module in self.graph:
                    self.graph.add_edge(source_module, target_module)

        return self.graph

    def find_cycles(self) -> List[CircularDependency]:
        """Find all circular dependency cycles in the graph."""
        cycles = []

        try:
            # Find all simple cycles
            simple_cycles = list(nx.simple_cycles(self.graph))
        except nx.NetworkXNoCycle:
            return []

        for cycle in simple_cycles:
            if len(cycle) > 1:  # Skip self-imports
                cycles.append(CircularDependency(
                    cycle=cycle,
                    break_suggestion=self._suggest_cycle_break(cycle)
                ))

        return cycles

    def _should_skip_file(self, filepath: Path) -> bool:
        """Determine if a file should be skipped from analysis."""
        # Skip test files, migrations, and __pycache__
        skip_patterns = [
            "__pycache__",
            "migrations",
            "test",
            "tests",
            ".pytest_cache",
            ".ruff_cache",
            ".hypothesis"
        ]

        file_str = str(filepath)
        return any(pattern in file_str for pattern in skip_patterns)

    def _path_to_module_name(self, filepath: Path) -> str:
        """Convert a file path to a module name."""
        # Convert path to relative module path
        rel_path = str(filepath).replace('.py', '')
        # Replace path separators with dots
        module_name = rel_path.replace('/', '.').replace('\\', '.')
        # Remove leading dots
        while module_name.startswith('.'):
            module_name = module_name[1:]
        return module_name

    def _extract_imports(self, filepath: Path) -> List[str]:
        """Extract all imports from a Python file."""
        imports = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, FileNotFoundError):
            return []

        try:
            tree = ast.parse(content, filename=str(filepath))
        except (SyntaxError, IndentationError):
            return []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def _resolve_import(self, import_name: str, source_file: Path) -> Optional[str]:
        """Resolve an import to a module name."""
        # Handle relative imports
        if import_name.startswith('.'):
            # This is a relative import, need to resolve relative to source_file
            source_dir = source_file.parent
            levels = 0
            while import_name.startswith('.'):
                levels += 1
                import_name = import_name[1:]

            # Build relative path
            target_path = source_dir
            for _ in range(levels - 1):
                target_path = target_path.parent

            # Try to find the module
            if import_name:
                # There's a module name after the dots
                possible_paths = [
                    target_path / f"{import_name}.py",
                    target_path / import_name / "__init__.py"
                ]
            else:
                # Just a relative import to parent directory
                possible_paths = [target_path / "__init__.py"]

            for possible_path in possible_paths:
                if possible_path.exists():
                    return self._path_to_module_name(possible_path)

        # Handle absolute imports
        # Try to find the module in our collected modules
        for module in self.module_to_path:
            if module.endswith(import_name) or f".{import_name}" in module:
                return module

        return None

    def _suggest_cycle_break(self, cycle: List[str]) -> str:
        """Suggest how to break a circular dependency cycle."""
        if len(cycle) == 2:
            return f"Break bidirectional dependency between {cycle[0]} and {cycle[1]}. Consider extracting shared interface or using dependency injection."
        else:
            return f"Break cycle by extracting shared functionality from {cycle[0]} to a new module, or refactor to use event-based communication."

def main():
    """Main function to run circular dependency detector."""
    import argparse

    parser = argparse.ArgumentParser(description='Detect circular dependencies')
    parser.add_argument('directory', help='Directory to scan for circular dependencies')
    parser.add_argument('--output', '-o', help='Output file for cycles')

    args = parser.parse_args()

    detector = CircularDependencyDetector()
    print(f"Building dependency graph for {args.directory}...")
    detector.build_dependency_graph(args.directory)

    print("Finding cycles...")
    cycles = detector.find_cycles()

    if cycles:
        print(f"\nFound {len(cycles)} circular dependency cycles:")
        for i, cycle in enumerate(cycles, 1):
            print(f"\nCycle {i}:")
            print("  → ".join(cycle.cycle))
            print(f"  Suggestion: {cycle.break_suggestion}")

        # Write to file if output specified
        if args.output:
            with open(args.output, 'w') as f:
                f.write("# Circular Dependency Cycles\n\n")
                for i, cycle in enumerate(cycles, 1):
                    f.write(f"## Cycle {i}\n")
                    f.write(f"Path: {' → '.join(cycle.cycle)}\n")
                    f.write(f"Suggestion: {cycle.break_suggestion}\n\n")
    else:
        print("No circular dependency cycles found!")

if __name__ == "__main__":
    main()
