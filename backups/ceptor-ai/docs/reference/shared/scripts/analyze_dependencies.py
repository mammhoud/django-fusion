"""
DependencyAnalyzer — scans all pyproject.toml files and identifies version conflicts.

Usage:
    python scripts/analyze_dependencies.py                  # find version conflicts
    python scripts/analyze_dependencies.py find_unused      # find unused dependencies
"""

from __future__ import annotations

import ast
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

#!/usr/bin/env python3
"""
Dependency Analysis Script for Django Libs Monorepo Refactoring

This script analyzes Python imports across all packages to:
1. Generate a dependency graph
2. Identify circular dependencies
3. Document forbidden dependencies per DEPENDENCY_RULES
4. Create DEPENDENCY_ANALYSIS.md report
"""

import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Dependency rules from design document
DEPENDENCY_RULES = {
    "django-fusion": {
        "required": ["Django"],
        "forbidden": ["wagtail", "celery", "django-q", "openai", "anthropic", "faker", "mcp"],
        "can_import_from": []
    },
    "crafts-ai": {
        "required": ["Django", "django-fusion", "wagtail", "celery", "faker", "toposort"],
        "optional": {"ai": ["crafts-ai"], "mcp": ["mcp"]},
        "can_import_from": ["django-fusion"]
    },
    "crafts-ai": {
        "required": ["Faker", "toposort", "hypothesis"],
        "optional": {"openai": ["openai"], "anthropic": ["anthropic"], "mcp": ["mcp"]},
        "forbidden": ["Django"],
        "can_import_from": []
    },
    "django-fusion": {
        "required": ["Django", "django-fusion", "crafts-ai", "pytest", "pytest-django"],
        "optional": {"selenium": ["selenium"], "playwright": ["playwright"]},
        "can_import_from": ["django-fusion", "crafts-ai", "crafts-ai"]
    }
}


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import statements from Python files."""

    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])
        self.generic_visit(node)


def get_python_files(directory: Path) -> List[Path]:
    """Recursively find all Python files in a directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache',
                                                  'node_modules', '.venv', 'venv',
                                                  '.egg-info', 'dist', 'build'}]
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    return python_files


def analyze_imports(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        return analyzer.imports
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return set()


def get_package_imports(package_dir: Path, package_name: str) -> Dict[str, Set[str]]:
    """Get all imports for a package, organized by file."""
    imports_by_file = {}
    python_files = get_python_files(package_dir)

    for file_path in python_files:
        imports = analyze_imports(file_path)
        if imports:
            relative_path = file_path.relative_to(package_dir)
            imports_by_file[str(relative_path)] = imports

    return imports_by_file


def get_all_package_imports(libs_dir: Path) -> Dict[str, Dict[str, Set[str]]]:
    """Get imports for all packages."""
    packages = {}

    for package_name in ["django-fusion", "crafts-ai", "django-seed", "django-fusion"]:
        package_dir = libs_dir / package_name
        if package_dir.exists():
            print(f"Analyzing {package_name}...")
            packages[package_name] = get_package_imports(package_dir, package_name)

    return packages


def build_dependency_graph(package_imports: Dict[str, Dict[str, Set[str]]]) -> Dict[str, Set[str]]:
    """Build a dependency graph showing which packages depend on which."""
    graph = defaultdict(set)

    # Map module names to package names
    module_to_package = {
        "django_fusion": "django-fusion",
        "crafts_ai": "crafts-ai",
        "django_seed": "django-seed",
        "craftsai": "django-seed",
        "django_fusion": "django-fusion"
    }

    for package_name, files in package_imports.items():
        for file_path, imports in files.items():
            for imp in imports:
                # Check if this import is from another package in our monorepo
                if imp in module_to_package:
                    target_package = module_to_package[imp]
                    if target_package != package_name:
                        graph[package_name].add(target_package)

    return dict(graph)


def detect_circular_dependencies(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Detect circular dependencies in the dependency graph."""
    cycles = []

    def dfs(node: str, path: List[str], visited: Set[str]) -> None:
        if node in path:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            if cycle not in cycles and list(reversed(cycle)) not in cycles:
                cycles.append(cycle)
            return

        if node in visited:
            return

        visited.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            dfs(neighbor, path.copy(), visited)

    for node in graph:
        dfs(node, [], set())

    return cycles


def check_forbidden_dependencies(package_imports: Dict[str, Dict[str, Set[str]]]) -> Dict[str, List[Tuple[str, str]]]:
    """Check for forbidden dependencies according to DEPENDENCY_RULES."""
    violations = defaultdict(list)

    for package_name, files in package_imports.items():
        if package_name not in DEPENDENCY_RULES:
            continue

        rules = DEPENDENCY_RULES[package_name]
        forbidden = rules.get("forbidden", [])

        # Collect all unique imports for this package
        all_imports = set()
        for imports in files.values():
            all_imports.update(imports)

        # Check for forbidden imports
        for imp in all_imports:
            for forbidden_dep in forbidden:
                if imp.lower() == forbidden_dep.lower() or imp.lower().startswith(forbidden_dep.lower() + '.'):
                    # Find which files have this import
                    violating_files = [f for f, imps in files.items() if imp in imps]
                    for file_path in violating_files:
                        violations[package_name].append((forbidden_dep, file_path))

    return dict(violations)


def get_external_dependencies(package_imports: Dict[str, Dict[str, Set[str]]]) -> Dict[str, Set[str]]:
    """Get external (non-monorepo) dependencies for each package."""
    internal_modules = {"django_fusion", "crafts_ai", "django_seed", "craftsai", "django_fusion"}
    stdlib_modules = {
        "os", "sys", "re", "json", "ast", "pathlib", "typing", "collections",
        "datetime", "time", "logging", "unittest", "io", "copy", "functools",
        "itertools", "operator", "string", "math", "random", "uuid", "hashlib",
        "base64", "urllib", "http", "email", "mimetypes", "warnings", "abc",
        "dataclasses", "enum", "contextlib", "tempfile", "shutil", "subprocess",
        "threading", "multiprocessing", "queue", "socket", "ssl", "csv", "xml",
        "html", "argparse", "configparser", "pickle", "shelve", "sqlite3"
    }

    external_deps = {}

    for package_name, files in package_imports.items():
        all_imports = set()
        for imports in files.values():
            all_imports.update(imports)

        # Filter out internal and stdlib modules
        external = {imp for imp in all_imports
                   if imp not in internal_modules and imp not in stdlib_modules}
        external_deps[package_name] = external

    return external_deps


def generate_mermaid_graph(graph: Dict[str, Set[str]]) -> str:
    """Generate a Mermaid diagram of the dependency graph."""
    lines = ["```mermaid", "graph TD"]

    # Define nodes with colors
    colors = {
        "django-fusion": "#90EE90",
        "crafts-ai": "#87CEEB",
        "django-seed": "#FFB6C1",
        "django-fusion": "#FFD700"
    }

    # Add edges
    for source, targets in sorted(graph.items()):
        for target in sorted(targets):
            lines.append(f"    {source.replace('-', '_')}[{source}] --> {target.replace('-', '_')}[{target}]")

    # Add styling
    for package, color in colors.items():
        lines.append(f"    style {package.replace('-', '_')} fill:{color}")

    lines.append("```")
    return "\n".join(lines)


def generate_report(
    graph: Dict[str, Set[str]],
    cycles: List[List[str]],
    violations: Dict[str, List[Tuple[str, str]]],
    external_deps: Dict[str, Set[str]],
    package_imports: Dict[str, Dict[str, Set[str]]]
) -> str:
    """Generate the DEPENDENCY_ANALYSIS.md report."""

    report = []
    report.append("# Dependency Analysis Report")
    report.append("")
    report.append("**Generated**: Automated analysis of Python imports across all packages")
    report.append("")
    report.append("**Purpose**: Analyze current dependency structure and identify violations of dependency rules")
    report.append("")
    report.append("---")
    report.append("")

    # Summary
    report.append("## Summary")
    report.append("")
    report.append(f"- **Packages Analyzed**: {len(package_imports)}")
    report.append(f"- **Circular Dependencies Found**: {len(cycles)}")
    report.append(f"- **Forbidden Dependency Violations**: {sum(len(v) for v in violations.values())}")
    report.append("")

    # Dependency Graph
    report.append("## Dependency Graph")
    report.append("")
    report.append("### Current Package Dependencies")
    report.append("")
    report.append(generate_mermaid_graph(graph))
    report.append("")

    # Package-by-Package Analysis
    report.append("## Package-by-Package Analysis")
    report.append("")

    for package_name in sorted(package_imports.keys()):
        report.append(f"### {package_name}")
        report.append("")

        # Dependencies
        deps = graph.get(package_name, set())
        if deps:
            report.append("**Internal Dependencies**:")
            for dep in sorted(deps):
                report.append(f"- {dep}")
        else:
            report.append("**Internal Dependencies**: None")
        report.append("")

        # External dependencies
        ext_deps = external_deps.get(package_name, set())
        if ext_deps:
            report.append("**External Dependencies**:")
            for dep in sorted(ext_deps):
                report.append(f"- {dep}")
        else:
            report.append("**External Dependencies**: None (stdlib only)")
        report.append("")

        # File count
        file_count = len(package_imports[package_name])
        report.append(f"**Python Files Analyzed**: {file_count}")
        report.append("")

    # Circular Dependencies
    report.append("## Circular Dependencies")
    report.append("")
    if cycles:
        report.append(f"**Status**: ⚠️ {len(cycles)} circular dependency chain(s) detected")
        report.append("")
        for i, cycle in enumerate(cycles, 1):
            report.append(f"### Cycle {i}")
            report.append("")
            report.append("```")
            report.append(" → ".join(cycle))
            report.append("```")
            report.append("")
    else:
        report.append("**Status**: ✅ No circular dependencies detected")
        report.append("")

    # Forbidden Dependencies
    report.append("## Forbidden Dependency Violations")
    report.append("")

    if violations:
        report.append(f"**Status**: ⚠️ {sum(len(v) for v in violations.values())} violation(s) found")
        report.append("")

        for package_name, package_violations in sorted(violations.items()):
            report.append(f"### {package_name}")
            report.append("")

            # Group by forbidden dependency
            by_dep = defaultdict(list)
            for dep, file_path in package_violations:
                by_dep[dep].append(file_path)

            for dep, files in sorted(by_dep.items()):
                report.append(f"**Forbidden Dependency**: `{dep}`")
                report.append("")
                report.append("Files with violations:")
                for file_path in sorted(set(files)):
                    report.append(f"- `{file_path}`")
                report.append("")
    else:
        report.append("**Status**: ✅ No forbidden dependency violations detected")
        report.append("")

    # Dependency Rules Reference
    report.append("## Dependency Rules Reference")
    report.append("")
    report.append("From design document:")
    report.append("")

    for package_name, rules in sorted(DEPENDENCY_RULES.items()):
        report.append(f"### {package_name}")
        report.append("")

        if "required" in rules:
            report.append("**Required Dependencies**:")
            for dep in rules["required"]:
                report.append(f"- {dep}")
            report.append("")

        if "forbidden" in rules:
            report.append("**Forbidden Dependencies**:")
            for dep in rules["forbidden"]:
                report.append(f"- {dep}")
            report.append("")

        if "optional" in rules:
            report.append("**Optional Dependencies**:")
            for extra, deps in rules["optional"].items():
                report.append(f"- `{extra}`: {', '.join(deps)}")
            report.append("")

        if "can_import_from" in rules:
            if rules["can_import_from"]:
                report.append("**Can Import From**:")
                for dep in rules["can_import_from"]:
                    report.append(f"- {dep}")
            else:
                report.append("**Can Import From**: None (standalone)")
            report.append("")

    # Recommendations
    report.append("## Recommendations")
    report.append("")

    if cycles:
        report.append("### Circular Dependencies")
        report.append("")
        report.append("**Action Required**: Resolve circular dependencies before proceeding with refactoring.")
        report.append("")
        report.append("**Resolution Strategy**:")
        report.append("1. Identify shared code causing circular dependency")
        report.append("2. Extract shared code to common package (django-fusion)")
        report.append("3. Update both packages to depend on common package")
        report.append("4. Verify no circular dependencies remain")
        report.append("")

    if violations:
        report.append("### Forbidden Dependencies")
        report.append("")
        report.append("**Action Required**: Remove or refactor code using forbidden dependencies.")
        report.append("")
        report.append("**Resolution Strategy**:")
        report.append("1. Review each violation and determine if dependency is truly needed")
        report.append("2. Move code requiring forbidden dependency to appropriate package")
        report.append("3. Use optional dependencies where appropriate")
        report.append("4. Verify all forbidden dependencies removed")
        report.append("")

    if not cycles and not violations:
        report.append("**Status**: ✅ Dependency structure is clean and ready for refactoring")
        report.append("")
        report.append("All packages follow the dependency rules specified in the design document.")
        report.append("")

    # Appendix
    report.append("## Appendix: Detailed Import Analysis")
    report.append("")

    for package_name in sorted(package_imports.keys()):
        report.append(f"### {package_name} - All Imports")
        report.append("")

        all_imports = set()
        for imports in package_imports[package_name].values():
            all_imports.update(imports)

        if all_imports:
            for imp in sorted(all_imports):
                report.append(f"- `{imp}`")
        else:
            report.append("- No imports found")
        report.append("")

    return "\n".join(report)


def main():
    """Main entry point."""
    # Get the libs directory
    script_dir = Path(__file__).parent
    libs_dir = script_dir

    print("=" * 60)
    print("Django Libs Monorepo - Dependency Analysis")
    print("=" * 60)
    print()

    # Analyze all packages
    print("Step 1: Analyzing imports from all packages...")
    package_imports = get_all_package_imports(libs_dir)
    print(f"✓ Analyzed {sum(len(files) for files in package_imports.values())} Python files")
    print()

    # Build dependency graph
    print("Step 2: Building dependency graph...")
    graph = build_dependency_graph(package_imports)
    print(f"✓ Built dependency graph with {len(graph)} packages")
    print()

    # Detect circular dependencies
    print("Step 3: Detecting circular dependencies...")
    cycles = detect_circular_dependencies(graph)
    if cycles:
        print(f"⚠️  Found {len(cycles)} circular dependency chain(s)")
    else:
        print("✓ No circular dependencies detected")
    print()

    # Check forbidden dependencies
    print("Step 4: Checking for forbidden dependencies...")
    violations = check_forbidden_dependencies(package_imports)
    if violations:
        total_violations = sum(len(v) for v in violations.values())
        print(f"⚠️  Found {total_violations} forbidden dependency violation(s)")
    else:
        print("✓ No forbidden dependency violations")
    print()

    # Get external dependencies
    print("Step 5: Analyzing external dependencies...")
    external_deps = get_external_dependencies(package_imports)
    print("✓ Identified external dependencies")
    print()

    # Generate report
    print("Step 6: Generating DEPENDENCY_ANALYSIS.md...")
    report = generate_report(graph, cycles, violations, external_deps, package_imports)

    output_path = libs_dir / "DEPENDENCY_ANALYSIS.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ Report saved to {output_path}")
    print()

    # Summary
    print("=" * 60)
    print("Analysis Complete")
    print("=" * 60)
    print()
    print(f"Packages analyzed: {len(package_imports)}")
    print(f"Circular dependencies: {len(cycles)}")
    print(f"Forbidden dependency violations: {sum(len(v) for v in violations.values())}")
    print()

    if cycles or violations:
        print("⚠️  Issues found - review DEPENDENCY_ANALYSIS.md for details")
        return 1
    else:
        print("✅ Dependency structure is clean")
        return 0


if __name__ == "__main__":
    sys.exit(main())

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class VersionSpec:
    """A single version constraint for a package in a specific project."""
    package: str          # normalised package name (lowercase, dashes)
    constraint: str       # raw constraint string, e.g. ">=4.2"
    source_file: str      # path to the pyproject.toml that declared it


@dataclass
class VersionConflict:
    """Two or more projects declare the same package with different constraints."""
    package: str
    specs: List[VersionSpec]
    recommended: str      # recommended unified constraint


@dataclass
class UnusedDependency:
    package: str
    source_file: str
    reason: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PYPROJECT_FILES = [
    "ctc-research.com/pyproject.toml",
    "structa.cloud/pyproject.toml",
    "venv/libs/django-fusion/pyproject.toml",
    "venv/libs/crafts-ai/pyproject.toml",
    "venv/libs/django-fusion/pyproject.toml",
    "applications/libs/crafts-ai/pyproject.toml",
]

# Map pyproject path → source root(s) to scan for imports
SOURCE_ROOTS: Dict[str, List[str]] = {
    "ctc-research.com/pyproject.toml": ["ctc-research.com"],
    "structa.cloud/pyproject.toml": ["structa.cloud"],
    "venv/libs/django-fusion/pyproject.toml": ["venv/libs/django-fusion/src"],
    "venv/libs/crafts-ai/pyproject.toml": ["venv/libs/crafts-ai/src"],
    "venv/libs/django-fusion/pyproject.toml": ["venv/libs/django-fusion/src"],
    "applications/libs/crafts-ai/pyproject.toml": ["applications/libs/crafts-ai"],
}


def _norm(name: str) -> str:
    """Normalise package name: lowercase, replace underscores/dots with dashes."""
    return re.sub(r"[_.]", "-", name.lower())


def _parse_constraint(dep: str) -> Tuple[str, str]:
    """
    Split a dependency string like 'Django>=4.0' into (normalised_name, constraint).
    Handles extras like 'sentry-sdk[django]>=2.0'.
    """
    # Strip extras
    dep_no_extras = re.sub(r"\[.*?\]", "", dep)
    # Split on first operator
    m = re.match(r"^([A-Za-z0-9_.\-]+)\s*([><=!~,\s].*)?$", dep_no_extras.strip())
    if not m:
        return _norm(dep_no_extras.strip()), ""
    name = _norm(m.group(1))
    constraint = (m.group(2) or "").strip()
    return name, constraint


def _load_toml(path: str) -> Optional[dict]:
    if tomllib is None:
        # Fallback: very simple TOML parser for the [project] dependencies list
        return _simple_toml_parse(path)
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"  [WARN] Could not parse {path}: {e}", file=sys.stderr)
        return None


def _simple_toml_parse(path: str) -> Optional[dict]:
    """Minimal TOML parser that extracts [project].dependencies only."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    result: dict = {"project": {"dependencies": []}}
    in_deps = False
    deps: List[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_deps = True
            continue
        if in_deps:
            if stripped == "]":
                in_deps = False
                continue
            # Remove trailing comma and quotes
            dep = stripped.strip('",').strip("'")
            if dep and not dep.startswith("#"):
                deps.append(dep)

    result["project"]["dependencies"] = deps
    return result


def _extract_deps(data: dict) -> List[str]:
    """Return the list of dependency strings from parsed TOML data."""
    return data.get("project", {}).get("dependencies", [])


# ---------------------------------------------------------------------------
# Version comparison helpers
# ---------------------------------------------------------------------------

def _parse_version_number(v: str) -> Tuple[int, ...]:
    """Parse '5.0.1' → (5, 0, 1)."""
    parts = re.findall(r"\d+", v)
    return tuple(int(p) for p in parts) if parts else (0,)


def _most_restrictive(constraints: List[str]) -> str:
    """
    Given a list of constraints like ['>=4.0', '>=5.0', ''], return the most
    restrictive one (highest lower bound for >= constraints).
    Falls back to the first non-empty constraint if mixed operators.
    """
    if not constraints:
        return ""

    # Filter out empty
    non_empty = [c for c in constraints if c]
    if not non_empty:
        return ""

    # Collect >= lower bounds
    ge_bounds: List[Tuple[Tuple[int, ...], str]] = []
    others: List[str] = []

    for c in non_empty:
        m = re.match(r"^>=\s*([\d.]+)", c)
        if m:
            ge_bounds.append((_parse_version_number(m.group(1)), c))
        else:
            others.append(c)

    if ge_bounds:
        # Pick the highest lower bound
        ge_bounds.sort(key=lambda x: x[0], reverse=True)
        return ge_bounds[0][1]

    # If all are pinned (==) or other operators, return the first
    return non_empty[0]


# ---------------------------------------------------------------------------
# DependencyAnalyzer
# ---------------------------------------------------------------------------

class DependencyAnalyzer:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root)

    # ------------------------------------------------------------------
    # 1. Collect all declared dependencies
    # ------------------------------------------------------------------

    def collect_all_deps(self) -> Dict[str, List[VersionSpec]]:
        """
        Returns a dict mapping normalised package name → list of VersionSpec
        (one per pyproject.toml that declares it).
        """
        all_deps: Dict[str, List[VersionSpec]] = {}

        for rel_path in PYPROJECT_FILES:
            abs_path = self.root / rel_path
            if not abs_path.exists():
                print(f"  [SKIP] {rel_path} not found", file=sys.stderr)
                continue

            data = _load_toml(str(abs_path))
            if data is None:
                continue

            for dep_str in _extract_deps(data):
                dep_str = dep_str.strip()
                if not dep_str or dep_str.startswith("#"):
                    continue
                name, constraint = _parse_constraint(dep_str)
                spec = VersionSpec(
                    package=name,
                    constraint=constraint,
                    source_file=rel_path,
                )
                all_deps.setdefault(name, []).append(spec)

        return all_deps

    # ------------------------------------------------------------------
    # 2. Find version conflicts
    # ------------------------------------------------------------------

    def find_conflicts(self) -> List[VersionConflict]:
        """
        A conflict exists when the same package appears in ≥2 files with
        different constraint strings.
        """
        all_deps = self.collect_all_deps()
        conflicts: List[VersionConflict] = []

        for pkg, specs in sorted(all_deps.items()):
            if len(specs) < 2:
                continue
            unique_constraints = {s.constraint for s in specs}
            if len(unique_constraints) > 1:
                recommended = _most_restrictive(list(unique_constraints))
                conflicts.append(VersionConflict(
                    package=pkg,
                    specs=specs,
                    recommended=recommended,
                ))

        return conflicts

    # ------------------------------------------------------------------
    # 3. Find unused dependencies (conservative)
    # ------------------------------------------------------------------

    def _collect_imports_in_dir(self, directory: str) -> Set[str]:
        """Walk a directory and collect all top-level import names."""
        imports: Set[str] = set()
        root = self.root / directory
        if not root.exists():
            return imports

        for py_file in root.rglob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source, filename=str(py_file))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

        return imports

    def find_unused_dependencies(self) -> List[UnusedDependency]:
        """
        Conservative: only flag a dependency as unused if its import name
        cannot be found anywhere in the source tree AND it is not a known
        runtime-only dependency (DB backends, auth backends, etc.).
        """
        # Packages that are runtime-only and should never be flagged as unused
        RUNTIME_ONLY = {
            "psycopg", "psycopg-binary", "psycopg2", "psycopg2-binary",
            "gunicorn", "uvicorn", "whitenoise", "watchfiles",
            "django-prometheus", "sentry-sdk",
            "django-debug-toolbar", "django-silk",
            "bumpver", "virtualenv",
            "django-allauth",  # registered via INSTALLED_APPS
            "django-bird", "django-browser-reload",
            "django-colorfield", "django-crispy-forms",
            "django-embed-video", "django-environ",
            "django-extensions", "django-heroicons",
            "django-htmx", "django-import-export",
            "django-ninja", "django-ninja-extra", "django-ninja-jwt",
            "django-redis", "django-simple-history",
            "django-structlog", "django-stubs",
            "django-tables2", "django-unfold",
            "django-webpack-loader", "django-paypal",
            "django-storages", "django-rq",
            "wagtail", "wagtail-font-awesome-svg",
            "wagtail-newsletter", "wagtail-transfer",
            "wagtailfontawesome",
            "celery",
            "django-fusion", "crafts-ai", "django-fusion", "crafts-ai",
        }

        # Map package name → typical Python import name
        IMPORT_NAME_MAP = {
            "django": "django",
            "faker": "faker",
            "toposort": "toposort",
            "hypothesis": "hypothesis",
            "pytest": "pytest",
            "pytest-django": "pytest_django",
            "pytest-cov": "pytest_cov",
            "pytest-selenium": "pytest_selenium",
            "selenium": "selenium",
            "celery": "celery",
            "mcp": "mcp",
            "openai": "openai",
            "anthropic": "anthropic",
            "requests": "requests",
            "click": "click",
            "colorlog": "colorlog",
            "fire": "fire",
            "marshmallow": "marshmallow",
            "pydantic": "pydantic",
            "pydantic-settings": "pydantic_settings",
            "structlog": "structlog",
            "twilio": "twilio",
            "jinja2": "jinja2",
            "stripe": "stripe",
            "jwt": "jwt",
            "fido2": "fido2",
            "ninja": "ninja",
            "livereload": "livereload",
            "draftjs-exporter": "draftjs_exporter",
            "dynaconf": "dynaconf",
            "environ": "environ",
            "yml": "yml",
            "python-json-logger": "pythonjsonlogger",
            "pyrefly": "pyrefly",
            "black": "black",
            "flake8": "flake8",
            "isort": "isort",
            "mypy": "mypy",
            "django-filter": "django_filters",
            "django-taggit": "taggit",
            "wagtail-modelcluster": "modelcluster",
            "django-allauth": "allauth",
        }

        unused: List[UnusedDependency] = []

        for rel_path in PYPROJECT_FILES:
            abs_path = self.root / rel_path
            if not abs_path.exists():
                continue

            data = _load_toml(str(abs_path))
            if data is None:
                continue

            # Collect all imports in the source roots for this project
            source_dirs = SOURCE_ROOTS.get(rel_path, [])
            all_imports: Set[str] = set()
            for src_dir in source_dirs:
                all_imports |= self._collect_imports_in_dir(src_dir)

            for dep_str in _extract_deps(data):
                dep_str = dep_str.strip()
                if not dep_str or dep_str.startswith("#"):
                    continue
                name, _ = _parse_constraint(dep_str)

                if name in RUNTIME_ONLY:
                    continue

                import_name = IMPORT_NAME_MAP.get(name, name.replace("-", "_"))

                if import_name not in all_imports:
                    unused.append(UnusedDependency(
                        package=name,
                        source_file=rel_path,
                        reason=f"import '{import_name}' not found in source tree",
                    ))

        return unused


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    analyzer = DependencyAnalyzer(workspace_root=".")

    if len(sys.argv) > 1 and sys.argv[1] in ("find_unused", "find_unused_dependencies"):
        print("=== Unused Dependencies ===\n")
        unused = analyzer.find_unused_dependencies()
        if not unused:
            print("No unused dependencies found.")
        else:
            current_file = None
            for u in sorted(unused, key=lambda x: (x.source_file, x.package)):
                if u.source_file != current_file:
                    print(f"\n{u.source_file}:")
                    current_file = u.source_file
                print(f"  - {u.package}: {u.reason}")
        return

    # Default: find conflicts
    print("=== Dependency Version Conflicts ===\n")
    conflicts = analyzer.find_conflicts()
    if not conflicts:
        print("No version conflicts found.")
    else:
        for c in conflicts:
            print(f"Package: {c.package}")
            print(f"  Recommended: {c.recommended}")
            for s in c.specs:
                print(f"    {s.source_file}: {s.constraint or '(unpinned)'}")
            print()

    print(f"\nTotal conflicts: {len(conflicts)}")


if __name__ == "__main__":
    main()
