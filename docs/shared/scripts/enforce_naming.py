#!/usr/bin/env python3
"""
Enforce snake_case naming conventions for Python modules across the ecosystem.

Usage:
    python scripts/enforce_naming.py check_module_names
    python scripts/enforce_naming.py check_class_names
    python scripts/enforce_naming.py check_function_names
"""

import ast
import os
import re
import sys
from pathlib import Path

# Directories to scan
SCAN_DIRS = [
    "ctc-research.com/apps/",
    "structa.cloud/apps/",
    "venv/libs/django-fusion/src/",
    "venv/libs/crafts-ai/src/",
    "venv/libs/django-fusion/src/",
    "applications/libs/crafts-ai/src/",
]

# Directories to skip
SKIP_DIRS = {"__pycache__", "migrations", ".git", ".venv", "node_modules"}


def is_snake_case(name: str) -> bool:
    """Return True if name is valid snake_case (lowercase letters, digits, underscores only)."""
    return bool(re.match(r'^[a-z][a-z0-9_]*$', name)) or name.startswith('_')


def to_snake_case(name: str) -> str:
    """Convert a CamelCase or mixedCase name to snake_case."""
    # Insert underscore before uppercase letters
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def find_python_files(directories: list[str]) -> list[Path]:
    """Find all Python files in the given directories, skipping excluded dirs."""
    files = []
    for directory in directories:
        base = Path(directory)
        if not base.exists():
            continue
        for root, dirs, filenames in os.walk(base):
            # Prune skip dirs in-place
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(Path(root) / filename)
    return files


def check_module_names() -> list[dict]:
    """
    Check all Python module filenames for snake_case compliance.
    Returns list of violations with file path and suggested rename.
    """
    violations = []
    files = find_python_files(SCAN_DIRS)

    for filepath in sorted(files):
        stem = filepath.stem  # filename without .py
        # Skip dunder files like __init__, __main__
        if stem.startswith('__') and stem.endswith('__'):
            continue
        # Skip files starting with dot (hidden)
        if stem.startswith('.'):
            continue
        if not is_snake_case(stem):
            suggested = to_snake_case(stem)
            violations.append({
                'file': str(filepath),
                'current': stem,
                'suggested': suggested,
                'new_path': str(filepath.parent / f"{suggested}.py"),
            })

    return violations


def check_class_names() -> list[dict]:
    """
    Check all class names for PascalCase compliance.
    Returns list of violations.
    """
    violations = []
    files = find_python_files(SCAN_DIRS)

    for filepath in sorted(files):
        try:
            source = filepath.read_text(encoding='utf-8', errors='replace')
            tree = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                name = node.name
                # Strip leading underscores for private/internal classes (e.g. _Foo, __Foo)
                # These are intentional Python conventions for private classes
                check_name = name.lstrip('_')
                if not check_name:
                    continue
                # PascalCase: starts with uppercase, no underscores (except leading/trailing)
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', check_name):
                    violations.append({
                        'file': str(filepath),
                        'line': node.lineno,
                        'name': name,
                        'type': 'class',
                    })

    return violations


def check_function_names() -> list[dict]:
    """
    Check all function/method names for snake_case compliance.
    Returns list of violations.
    """
    violations = []
    files = find_python_files(SCAN_DIRS)

    for filepath in sorted(files):
        try:
            source = filepath.read_text(encoding='utf-8', errors='replace')
            tree = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = node.name
                # Skip dunder methods
                if name.startswith('__') and name.endswith('__'):
                    continue
                # Skip private single-underscore prefix
                check_name = name.lstrip('_')
                if check_name and not re.match(r'^[a-z][a-z0-9_]*$', check_name):
                    violations.append({
                        'file': str(filepath),
                        'line': node.lineno,
                        'name': name,
                        'type': 'function',
                    })

    return violations


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/enforce_naming.py <command>")
        print("Commands: check_module_names, check_class_names, check_function_names")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'check_module_names':
        violations = check_module_names()
        if violations:
            print(f"Found {len(violations)} module naming violation(s):\n")
            for v in violations:
                print(f"  VIOLATION: {v['file']}")
                print(f"    Current:   {v['current']}.py")
                print(f"    Suggested: {v['suggested']}.py")
                print()
            sys.exit(1)
        else:
            print("✓ All module names are snake_case compliant.")
            sys.exit(0)

    elif command == 'check_class_names':
        violations = check_class_names()
        if violations:
            print(f"Found {len(violations)} class naming violation(s):\n")
            for v in violations:
                print(f"  VIOLATION: {v['file']}:{v['line']} — class {v['name']!r}")
            sys.exit(1)
        else:
            print("✓ All class names are PascalCase compliant.")
            sys.exit(0)

    elif command == 'check_function_names':
        violations = check_function_names()
        if violations:
            print(f"Found {len(violations)} function naming violation(s):\n")
            for v in violations:
                print(f"  VIOLATION: {v['file']}:{v['line']} — {v['type']} {v['name']!r}")
            sys.exit(1)
        else:
            print("✓ All function names are snake_case compliant.")
            sys.exit(0)

    else:
        print(f"Unknown command: {command!r}")
        print("Commands: check_module_names, check_class_names, check_function_names")
        sys.exit(1)


if __name__ == '__main__':
    main()
