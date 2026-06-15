#!/usr/bin/env python3
"""
Cross-project consistency checker for ctc-research.com and structa.cloud.

Usage:
    python3 scripts/check_consistency.py check_app_structure
    python3 scripts/check_consistency.py check_naming_conventions
"""

import ast
import re
import sys
from pathlib import Path

# Project roots
CTC = Path("ctc-research.com/apps")
STRUCTA = Path("structa.cloud/apps")

PROJECTS = {
    "ctc-research.com": CTC,
    "structa.cloud": STRUCTA,
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def collect_classes(directory: Path) -> list[dict]:
    """Return list of {file, class_name} for every class defined under directory."""
    results = []
    for py_file in directory.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                results.append({"file": py_file, "class_name": node.name})
    return results


def classes_in_subdir(app_root: Path, subdir: str) -> list[dict]:
    """Collect classes from a specific subdirectory of an app."""
    target = app_root / subdir
    if not target.exists():
        return []
    return collect_classes(target)


def get_app_dirs(project_root: Path) -> list[Path]:
    """Return all app directories (direct children that are packages)."""
    return [
        d for d in project_root.iterdir()
        if d.is_dir() and (d / "__init__.py").exists()
        and not d.name.startswith("_")
        and d.name not in ("templates", "templatetags", "migrations")
    ]


# ─────────────────────────────────────────────────────────────────────────────
# check_app_structure
# ─────────────────────────────────────────────────────────────────────────────

def check_app_structure():
    """Verify both projects have the expected app layout."""
    required_shared = {"accounts", "content", "blog"}
    issues = []

    for project_name, project_root in PROJECTS.items():
        app_names = {d.name for d in get_app_dirs(project_root)}
        missing = required_shared - app_names
        if missing:
            issues.append(f"[{project_name}] Missing required apps: {sorted(missing)}")

    if issues:
        print("❌ App structure issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ App structure is consistent across both projects.")
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Naming convention rules
# ─────────────────────────────────────────────────────────────────────────────

# Pattern: class name must end with one of these suffixes
SERVICE_SUFFIX = re.compile(r"Service$")
MANAGER_SUFFIX = re.compile(r"Manager$")
VIEW_SUFFIX = re.compile(r"(View|ListView|DetailView|CreateView|UpdateView|DeleteView|APIView|FormView|TemplateView)$")

# Classes that are intentionally exempt (base/abstract classes from packages)
EXEMPT_CLASSES = {
    # Package base classes
    "BaseService", "CRUDService", "TokenService",
    "BaseManager", "CachedManager",
    "PageHandler", "FragmentHandler",
    # Django/Wagtail built-ins
    "View", "ListView", "DetailView", "CreateView", "UpdateView", "DeleteView",
    "TemplateView", "FormView", "APIView",
    # Mixins
    "SearchMixin", "FilterMixin", "PaymentProcessingMixin", "LoginRequiredMixin",
}

# Classes that are intentionally different due to project-specific domains
DOMAIN_SPECIFIC_EXEMPT = {
    # structa.cloud has RoleHierarchyManager in services/ (it IS a manager, just placed in services)
    "RoleHierarchyManager",
    "GroupAccessControl",
    # Legacy/enhanced classes
    "EnhancedEnrollmentService",
}


def check_service_naming(project_name: str, project_root: Path) -> list[str]:
    """Check that all classes in services/ directories end with 'Service'."""
    issues = []
    for app_dir in get_app_dirs(project_root):
        services_dir = app_dir / "services"
        if not services_dir.exists():
            continue
        for entry in collect_classes(services_dir):
            cls = entry["class_name"]
            if cls in EXEMPT_CLASSES or cls in DOMAIN_SPECIFIC_EXEMPT:
                continue
            if not SERVICE_SUFFIX.search(cls):
                issues.append(
                    f"[{project_name}] {entry['file'].relative_to(Path('.'))} "
                    f"— class '{cls}' in services/ should end with 'Service'"
                )
    return issues


def check_manager_naming(project_name: str, project_root: Path) -> list[str]:
    """Check that all classes in managers/ directories end with 'Manager'."""
    issues = []
    for app_dir in get_app_dirs(project_root):
        managers_dir = app_dir / "managers"
        if not managers_dir.exists():
            continue
        for entry in collect_classes(managers_dir):
            cls = entry["class_name"]
            if cls in EXEMPT_CLASSES or cls in DOMAIN_SPECIFIC_EXEMPT:
                continue
            if not MANAGER_SUFFIX.search(cls):
                issues.append(
                    f"[{project_name}] {entry['file'].relative_to(Path('.'))} "
                    f"— class '{cls}' in managers/ should end with 'Manager'"
                )
    return issues


def check_view_naming(project_name: str, project_root: Path) -> list[str]:
    """Check that all classes in views/ directories end with a View suffix."""
    issues = []
    for app_dir in get_app_dirs(project_root):
        views_dir = app_dir / "views"
        if not views_dir.exists():
            continue
        for entry in collect_classes(views_dir):
            cls = entry["class_name"]
            if cls in EXEMPT_CLASSES or cls in DOMAIN_SPECIFIC_EXEMPT:
                continue
            if not VIEW_SUFFIX.search(cls):
                issues.append(
                    f"[{project_name}] {entry['file'].relative_to(Path('.'))} "
                    f"— class '{cls}' in views/ should end with 'View' (or ListView, DetailView, etc.)"
                )
    return issues


def check_cross_project_consistency() -> list[str]:
    """
    Check that classes with the same logical name use the same naming pattern
    across both projects.
    """
    issues = []

    # Collect service/manager/view class names per project
    def collect_by_subdir(subdir):
        result = {}
        for project_name, project_root in PROJECTS.items():
            names = set()
            for app_dir in get_app_dirs(project_root):
                target = app_dir / subdir
                if target.exists():
                    for entry in collect_classes(target):
                        names.add(entry["class_name"])
            result[project_name] = names
        return result

    services = collect_by_subdir("services")
    managers = collect_by_subdir("managers")
    views = collect_by_subdir("views")

    # Check for classes that exist in both projects but with different names
    # (e.g., CartService vs CartSvc)
    def find_near_duplicates(project_a_classes, project_b_classes, category):
        """Find classes that look like they should match but don't."""
        near_issues = []
        # Strip suffix to get the "base name"
        suffix_patterns = {
            "services": r"Service$",
            "managers": r"Manager$",
            "views": r"(View|ListView|DetailView|CreateView|UpdateView|DeleteView|APIView|FormView|TemplateView)$",
        }
        pattern = suffix_patterns.get(category, r"$")

        def base_name(cls_name):
            return re.sub(pattern, "", cls_name)

        bases_a = {base_name(c): c for c in project_a_classes if c not in EXEMPT_CLASSES}
        bases_b = {base_name(c): c for c in project_b_classes if c not in EXEMPT_CLASSES}

        common_bases = set(bases_a.keys()) & set(bases_b.keys())
        for base in common_bases:
            name_a = bases_a[base]
            name_b = bases_b[base]
            if name_a != name_b:
                near_issues.append(
                    f"Cross-project {category} mismatch: "
                    f"ctc-research.com uses '{name_a}' but structa.cloud uses '{name_b}'"
                )
        return near_issues

    project_names = list(PROJECTS.keys())
    p1, p2 = project_names[0], project_names[1]

    issues += find_near_duplicates(services[p1], services[p2], "services")
    issues += find_near_duplicates(managers[p1], managers[p2], "managers")
    issues += find_near_duplicates(views[p1], views[p2], "views")

    return issues


def check_services_directory_exists() -> list[str]:
    """
    Verify both projects have services in their apps.
    Accepts either a services/ directory or a services.py flat file.
    Apps with neither are flagged only if the other project's equivalent app has services.
    """
    issues = []

    # Collect which apps have services (dir or file) per project
    app_has_services: dict[str, dict[str, bool]] = {}
    for project_name, project_root in PROJECTS.items():
        app_has_services[project_name] = {}
        for app_dir in get_app_dirs(project_root):
            has_services = (
                (app_dir / "services").exists()
                or (app_dir / "services.py").exists()
            )
            app_has_services[project_name][app_dir.name] = has_services

    # Find apps that exist in both projects but only one has services
    all_app_names = set()
    for project_name in PROJECTS:
        all_app_names.update(app_has_services[project_name].keys())

    project_names = list(PROJECTS.keys())
    p1, p2 = project_names[0], project_names[1]

    for app_name in sorted(all_app_names):
        p1_has = app_has_services.get(p1, {}).get(app_name, None)
        p2_has = app_has_services.get(p2, {}).get(app_name, None)

        # Only flag if both projects have the app but one is missing services
        if p1_has is not None and p2_has is not None:
            if p1_has and not p2_has:
                issues.append(
                    f"[{p2}] App '{app_name}' is missing services/ or services.py "
                    f"(but {p1} has it)"
                )
            elif p2_has and not p1_has:
                issues.append(
                    f"[{p1}] App '{app_name}' is missing services/ or services.py "
                    f"(but {p2} has it)"
                )

    return issues


# ─────────────────────────────────────────────────────────────────────────────
# check_naming_conventions — main entry point for task 8.4
# ─────────────────────────────────────────────────────────────────────────────

def check_naming_conventions():
    """
    Verify both projects use the same patterns for services, handlers,
    managers, and views.

    Checks:
    1. Both projects have services/ directories in their apps
    2. Service classes end with 'Service'
    3. Manager classes end with 'Manager'
    4. View classes end with 'View' (or ListView, DetailView, etc.)
    5. Cross-project consistency (same logical class uses same name)
    """
    all_issues = []

    print("=" * 70)
    print("Naming Convention Check")
    print("=" * 70)

    # 1. services/ directories
    print("\n[1] Checking services/ directories exist in all apps...")
    dir_issues = check_services_directory_exists()
    if dir_issues:
        for issue in dir_issues:
            print(f"   ⚠️  {issue}")
        all_issues.extend(dir_issues)
    else:
        print("   ✅ All apps have services/ directories")

    # 2. Service class naming
    print("\n[2] Checking service class naming (XxxService)...")
    for project_name, project_root in PROJECTS.items():
        issues = check_service_naming(project_name, project_root)
        if issues:
            for issue in issues:
                print(f"   ❌ {issue}")
            all_issues.extend(issues)
    if not any("[2]" in str(i) for i in all_issues):
        print("   ✅ All service classes follow XxxService pattern")

    # 3. Manager class naming
    print("\n[3] Checking manager class naming (XxxManager)...")
    for project_name, project_root in PROJECTS.items():
        issues = check_manager_naming(project_name, project_root)
        if issues:
            for issue in issues:
                print(f"   ❌ {issue}")
            all_issues.extend(issues)
    if not any("managers/" in str(i) for i in all_issues):
        print("   ✅ All manager classes follow XxxManager pattern")

    # 4. View class naming
    print("\n[4] Checking view class naming (XxxView, XxxListView, etc.)...")
    for project_name, project_root in PROJECTS.items():
        issues = check_view_naming(project_name, project_root)
        if issues:
            for issue in issues:
                print(f"   ❌ {issue}")
            all_issues.extend(issues)
    if not any("views/" in str(i) for i in all_issues):
        print("   ✅ All view classes follow XxxView pattern")

    # 5. Cross-project consistency
    print("\n[5] Checking cross-project naming consistency...")
    cross_issues = check_cross_project_consistency()
    if cross_issues:
        for issue in cross_issues:
            print(f"   ❌ {issue}")
        all_issues.extend(cross_issues)
    else:
        print("   ✅ Both projects use consistent naming across services, managers, and views")

    # Summary
    print("\n" + "=" * 70)
    if all_issues:
        print(f"❌ Found {len(all_issues)} naming inconsistency/inconsistencies:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        return False
    else:
        print("✅ All naming conventions are consistent across both projects.")
        return True


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

COMMANDS = {
    "check_app_structure": check_app_structure,
    "check_naming_conventions": check_naming_conventions,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python3 scripts/check_consistency.py <command>")
        print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(1)

    command = sys.argv[1]
    success = COMMANDS[command]()
    sys.exit(0 if success else 1)
