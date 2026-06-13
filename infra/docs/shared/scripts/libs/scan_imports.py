#!/usr/bin/env python3
"""
Scan all packages for cross-package import violations and print a report.
Usage: python scripts/libs/scan_imports.py
"""
import ast
import sys
from pathlib import Path

LIBS = Path(__file__).parent.parent.parent / "libs"

RULES = {
    "django-osoul": {
        "src": "django-osoul/src",
        "forbidden": ["wagtail", "celery", "django_q", "openai", "anthropic", "faker", "mcp", "django_rseal", "django_grep", "crafts_ai"],
    },
    "crafts-ai": {
        "src": "nawaai/crafts_ai",
        "forbidden": ["django"],
    },
    "django-rseal": {
        "src": "django-rseal/src",
        "forbidden": ["django_grep"],
    },
    "django-grep": {
        "src": "django-grep/src",
        "forbidden": [],  # can import from all
    },
}


def get_imports(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def main():
    violations = []
    for pkg, rule in RULES.items():
        src_dir = LIBS / rule["src"]
        if not src_dir.exists():
            continue
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            for imp in get_imports(py_file):
                for forbidden in rule["forbidden"]:
                    if imp == forbidden or imp.startswith(f"{forbidden}."):
                        rel = py_file.relative_to(LIBS)
                        violations.append((pkg, str(rel), imp, forbidden))

    if violations:
        print(f"\n{'='*60}")
        print(f"BOUNDARY VIOLATIONS FOUND: {len(violations)}")
        print(f"{'='*60}")
        for pkg, file, imp, forbidden in violations:
            print(f"  [{pkg}] {file}")
            print(f"    imports '{imp}' (forbidden: '{forbidden}')")
        sys.exit(1)
    else:
        print("✓ All package boundaries respected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
