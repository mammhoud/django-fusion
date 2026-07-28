#!/usr/bin/env python3
"""Import reachability check for ctc-research and lms-demo plugins."""
import ast
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
SITES = ["ctc-research", "lms-demo"]
ERRORS = []

def check_file(filepath: Path, site_root: Path) -> None:
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        ERRORS.append(f"SYNTAX ERROR in {filepath}: {e}")
        return

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if not isinstance(node, ast.ImportFrom) or not node.level:
            continue

        parts = filepath.relative_to(site_root).parent.parts
        level = node.level
        base_parts = list(parts[: len(parts) - (level - 1)])
        if node.module:
            base_parts += node.module.split(".")

        candidate = site_root.joinpath(*base_parts)
        if not (candidate.exists() or candidate.with_suffix(".py").exists()):
            ERRORS.append(
                f"BROKEN IMPORT at {filepath}:{node.lineno} — "
                f"resolves to non-existent path: {candidate}"
            )

for site in SITES:
    site_root = WORKSPACE / site
    if not site_root.exists():
        continue
    for py_file in site_root.rglob("*.py"):
        if ".venv" in py_file.parts or "__pycache__" in py_file.parts:
            continue
        check_file(py_file, site_root)

if ERRORS:
    print("Import reachability check FAILED")
    for err in ERRORS:
        print(f"  {err}")
    sys.exit(1)

print("Import reachability check passed")
sys.exit(0)
