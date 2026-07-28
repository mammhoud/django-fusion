"""
check_thin_layer.py — Audit project apps for business logic that belongs in packages.

A "thin layer" project should only contain:
  - settings/
  - URLs (urls.py, configs/urls.py)
  - Project-specific models (no base classes, no reusable logic)
  - Templates and static files
  - Thin service subclasses (delegating to package base classes)

Everything else is a violation and should be moved to a package.
"""

import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Violation:
    file: str
    line: int
    kind: str          # "business_logic_class" | "business_logic_function" | "standalone_service"
    name: str
    detail: str


@dataclass
class ThinLayerReport:
    project: str
    violations: list[Violation] = field(default_factory=list)

    def add(self, v: Violation):
        self.violations.append(v)

    @property
    def count(self):
        return len(self.violations)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PACKAGE_BASES = {
    # django_fusion
    "django_fusion",
    # crafts_ai
    "crafts_ai",
    # django_fusion
    "django_fusion",
    # nawaai
    "nawaai",
}

# Files/dirs that are always allowed in projects
ALLOWED_PATHS = {
    "settings", "configs", "urls.py", "wsgi.py", "asgi.py",
    "manage.py", "migrations", "templates", "static", "staticfiles",
    "media", "fixtures", "locale", "tests", "conftest.py",
    "__init__.py", "apps.py", "admin.py",
}

# Module names that are thin-layer by nature
THIN_MODULE_NAMES = {
    "urls", "settings", "wsgi", "asgi", "apps", "admin",
    "conftest", "factories", "fixtures",
}

# Class base names that indicate a thin subclass (acceptable)
THIN_BASE_INDICATORS = {
    "Base", "Abstract", "Mixin", "ServiceBase", "ManagerBase",
    "ViewBase", "HandlerBase", "FormBase",
}


def _is_thin_subclass(node: ast.ClassDef) -> bool:
    """Return True if the class is a thin subclass of a package base."""
    for base in node.bases:
        base_str = ast.unparse(base) if hasattr(ast, "unparse") else ""
        for pkg in PACKAGE_BASES:
            if pkg in base_str:
                return True
        # Check for known thin base names
        if isinstance(base, ast.Name):
            for indicator in THIN_BASE_INDICATORS:
                if indicator in base.id:
                    return True
        elif isinstance(base, ast.Attribute):
            for indicator in THIN_BASE_INDICATORS:
                if indicator in base.attr:
                    return True
    return False


def _has_package_import(tree: ast.Module) -> bool:
    """Return True if the module imports from any package."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = ""
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module += alias.name
            for pkg in PACKAGE_BASES:
                if pkg in module:
                    return True
    return False


def _count_methods(node: ast.ClassDef) -> int:
    return sum(1 for n in ast.walk(node) if isinstance(n, ast.FunctionDef))


def _is_allowed_path(rel_path: str) -> bool:
    parts = Path(rel_path).parts
    for part in parts:
        if part in ALLOWED_PATHS:
            return True
    stem = Path(rel_path).stem
    return stem in THIN_MODULE_NAMES


# ---------------------------------------------------------------------------
# Core checker
# ---------------------------------------------------------------------------

class ThinLayerChecker:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.report = ThinLayerReport(project=project_root)

    def check(self) -> ThinLayerReport:
        apps_dir = self.root / "apps"
        if not apps_dir.exists():
            return self.report

        for py_file in apps_dir.rglob("*.py"):
            rel = str(py_file.relative_to(self.root))
            if _is_allowed_path(rel):
                continue
            if "migrations" in rel:
                continue
            if "tests" in rel:
                continue
            self._check_file(py_file, rel)

        return self.report

    def _check_file(self, path: Path, rel: str):
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            return

        has_pkg_import = _has_package_import(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._check_class(node, rel, has_pkg_import)
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions (not methods) are checked
                if isinstance(node, ast.FunctionDef):
                    self._check_function(node, rel, tree)

    def _check_class(self, node: ast.ClassDef, rel: str, has_pkg_import: bool):
        # Skip thin subclasses
        if _is_thin_subclass(node):
            return

        method_count = _count_methods(node)

        # Classes with significant logic (>3 methods) that don't delegate to packages
        if method_count > 3 and not has_pkg_import:
            self.report.add(Violation(
                file=rel,
                line=node.lineno,
                kind="business_logic_class",
                name=node.name,
                detail=f"{method_count} methods — no package delegation detected",
            ))
        elif method_count > 6:
            # Even with package imports, very large classes are suspicious
            self.report.add(Violation(
                file=rel,
                line=node.lineno,
                kind="business_logic_class",
                name=node.name,
                detail=f"{method_count} methods — consider extracting to package",
            ))

    def _check_function(self, node: ast.FunctionDef, rel: str, tree: ast.Module):
        # Only flag top-level functions (module-level, not inside classes)
        # that are substantial (>10 lines)
        func_lines = (node.end_lineno or node.lineno) - node.lineno
        if func_lines > 10:
            self.report.add(Violation(
                file=rel,
                line=node.lineno,
                kind="business_logic_function",
                name=node.name,
                detail=f"{func_lines} lines — standalone function with business logic",
            ))


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def write_report(reports: list[ThinLayerReport], output_path: str):
    lines = ["# Thin Layer Violations Report\n"]
    lines.append("## Summary\n")

    total = sum(r.count for r in reports)
    lines.append(f"**Total violations**: {total}\n")
    for r in reports:
        lines.append(f"- **{r.project}**: {r.count} violations\n")

    lines.append("\n---\n")

    for report in reports:
        lines.append(f"\n## Project: {report.project}\n")
        lines.append(f"**Violations**: {report.count}\n\n")

        if not report.violations:
            lines.append("✅ No violations found.\n")
            continue

        # Group by file
        by_file: dict[str, list[Violation]] = {}
        for v in report.violations:
            by_file.setdefault(v.file, []).append(v)

        for file, violations in sorted(by_file.items()):
            lines.append(f"### `{file}`\n")
            for v in violations:
                lines.append(f"- **Line {v.line}** `{v.name}` ({v.kind}): {v.detail}\n")
            lines.append("\n")

    Path(output_path).write_text("".join(lines), encoding="utf-8")
    print(f"Report written to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    projects = [
        "ctc-research.com",
        "structa.cloud",
    ]

    reports = []
    for project in projects:
        if not Path(project).exists():
            print(f"Skipping {project} — directory not found")
            continue
        print(f"Checking {project}...")
        checker = ThinLayerChecker(project)
        report = checker.check()
        reports.append(report)
        print(f"  Found {report.count} violations")

    write_report(reports, "THIN_LAYER_VIOLATIONS.md")
    print("\nDone.")

    total = sum(r.count for r in reports)
    if "--fail-on-violation" in sys.argv and total > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
