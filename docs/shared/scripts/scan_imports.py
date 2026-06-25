#!/usr/bin/env python3
"""scan_imports.py — Scan for cross-package boundary violations."""
import re
import sys
from pathlib import Path

LIBS = Path(__file__).resolve().parents[3] / "applications" / "libs"

RULES = {
    "django-osoul": {
        "path": LIBS / "django-osoul/src/django_osoul",
        "forbidden": [r"^from wagtail", r"^import wagtail", r"^from celery",
                      r"^import celery", r"^from crafts_ai", r"^import crafts_ai"],
    },
    "crafts-ai": {
        "path": LIBS / "crafts-ai/src/crafts_ai",
        "forbidden": [r"^from django", r"^import django"],
    },
}

violations = []
for pkg, rule in RULES.items():
    base = rule["path"]
    if not base.exists():
        continue
    patterns = [re.compile(p) for p in rule["forbidden"]]
    for py_file in base.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        # comp/blocks and comp/templatetags are Wagtail UI components — wagtail imports expected
        rel = str(py_file.relative_to(base))
        # comp/blocks, comp/templatetags, and contrib/admin are Wagtail UI components
        if "comp/blocks" in rel or "comp/templatetags" in rel or "contrib/admin" in rel:
            continue
        for lineno, line in enumerate(py_file.read_text(errors="replace").splitlines(), 1):
            # Only check top-level imports (no leading whitespace)
            if line and line[0] in (' ', '\t', '#', '"', "'"):
                continue
            stripped = line.strip()
            for pat in patterns:
                if pat.match(stripped):
                    violations.append(f"{pkg}: {py_file.relative_to(LIBS)}:{lineno}: {line.rstrip()}")

if violations:
    print(f"❌ {len(violations)} violation(s) found:")
    for v in violations:
        print(f"  {v}")
    sys.exit(1)
else:
    print("✅ Zero import violations")
    sys.exit(0)
