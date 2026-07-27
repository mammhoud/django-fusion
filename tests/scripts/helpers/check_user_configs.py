#!/usr/bin/env python
"""
Fixtures User Consistency Checker
==================================
Scans auth.user records in JSON fixture files and reports inconsistencies:

- Users named "superadmin" without is_staff=True or is_superuser=True
- Users with is_superuser=True but is_staff=False (unusual for Wagtail admin)
- Users with is_staff=True but no groups (potential permission issues)
- Duplicate emails across users
- Users with groups that don't exist in auth.group fixtures

Usage::

    python tests/scripts/helpers/check_user_configs.py
    python tests/scripts/helpers/check_user_configs.py --fix
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

FIXTURE_GLOB_PATTERNS = [
    "tests/fixtures/**/*.json",
    "projects/*/assets/fixtures/**/*.json",
]


def find_fixture_files() -> list[Path]:
    """Find all JSON fixture files in the repo."""
    files: list[Path] = []
    for pattern in FIXTURE_GLOB_PATTERNS:
        matched = list(REPO_ROOT.glob(pattern))
        files.extend(matched)
    return sorted(set(files))


def extract_users(data: list[dict]) -> list[dict]:
    """Extract auth.user records from parsed fixture data."""
    return [item for item in data if isinstance(item, dict) and item.get("model") == "auth.user"]


def load_json(path: Path) -> list[dict]:
    """Safely load a JSON fixture file, returning [] on error."""
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return []


def check_user_consistency(
    users: list[dict], group_ids: set[int]
) -> list[dict]:
    """
    Check a list of auth.user records for consistency issues.

    Returns a list of issue dicts with keys:
        pk, username, email, issue, severity
    """
    issues: list[dict] = []
    email_seen: dict[str, int] = {}

    for user in users:
        fields = user.get("fields", {})
        pk = user.get("pk")
        username = fields.get("username", "?")
        email = fields.get("email", "?")
        is_superuser = fields.get("is_superuser", False)
        is_staff = fields.get("is_staff", False)
        user_groups = fields.get("groups", [])

        # 1. superadmin without appropriate flags
        if username == "superadmin":
            if not is_staff:
                issues.append({
                    "pk": pk, "username": username, "email": email,
                    "issue": "superadmin user must have is_staff=True",
                    "severity": "ERROR",
                })
            if not is_superuser:
                issues.append({
                    "pk": pk, "username": username, "email": email,
                    "issue": "superadmin user should also have is_superuser=True",
                    "severity": "WARNING",
                })

        # 2. superuser without staff (blocks Wagtail admin access)
        if is_superuser and not is_staff:
            issues.append({
                "pk": pk, "username": username, "email": email,
                "issue": "is_superuser=True but is_staff=False — cannot access Wagtail admin",
                "severity": "WARNING",
            })

        # 3. staff without groups
        if is_staff and not user_groups:
            issues.append({
                "pk": pk, "username": username, "email": email,
                "issue": "is_staff=True but belongs to no groups",
                "severity": "INFO",
            })

        # 4. Duplicate emails
        if email and email in email_seen:
            issues.append({
                "pk": pk, "username": username, "email": email,
                "issue": f"Duplicate email shared with user pk={email_seen[email]}",
                "severity": "WARNING",
            })
        elif email:
            email_seen[email] = pk

        # 5. Groups that don't exist
        for gid in user_groups:
            if gid not in group_ids:
                issues.append({
                    "pk": pk, "username": username, "email": email,
                    "issue": f"References non-existent group pk={gid}",
                    "severity": "ERROR",
                })

    return issues


def collect_group_ids(fixtures_paths: list[Path]) -> set[int]:
    """Collect all auth.group PKs from fixture files."""
    group_ids: set[int] = set()
    for path in fixtures_paths:
        data = load_json(path)
        for item in data:
            if isinstance(item, dict) and item.get("model") == "auth.group":
                group_ids.add(item.get("pk"))
    return group_ids


def auto_fix(users: list[dict], group_ids: set[int]) -> int:
    """Auto-fix known issues in user records. Returns count of fixes applied."""
    fixes = 0
    for user in users:
        fields = user.get("fields", {})
        pk = user.get("pk")
        username = fields.get("username", "")

        # Fix: superadmin should have is_staff
        if username == "superadmin" and not fields.get("is_staff"):
            fields["is_staff"] = True
            print(f"  ✓ Fixed superadmin pk={pk}: is_staff → True")
            fixes += 1

    return fixes


def process_file(
    path: Path, group_ids: set[int], fix: bool = False
) -> tuple[list[dict], int]:
    """Process a single fixture file. Returns (issues, fixes_applied)."""
    data = load_json(path)
    if not data:
        return [], 0

    users = extract_users(data)
    if not users:
        return [], 0

    issues = check_user_consistency(users, group_ids)
    fixes_applied = 0

    if fix:
        fixes_applied = auto_fix(users, group_ids)
        if fixes_applied > 0:
            # Re-serialize the modified data
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            print(f"  ✅ Updated {path}")

    return issues, fixes_applied


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check fixture user configurations for consistency issues."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix known issues (superadmin is_staff, etc.)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all issues including INFO level",
    )
    args = parser.parse_args()

    fixture_files = find_fixture_files()
    print(f"🔍 Found {len(fixture_files)} fixture file(s) to scan")
    print()

    # Collect all group IDs first for cross-referencing
    group_ids = collect_group_ids(fixture_files)
    print(f"👥 Found {len(group_ids)} auth.group record(s)")
    print()

    total_issues: list[dict] = []
    total_fixes = 0

    for path in fixture_files:
        issues, fixes = process_file(path, group_ids, fix=args.fix)
        total_issues.extend(issues)
        total_fixes += fixes
        relative = path.relative_to(REPO_ROOT)

        if issues:
            for issue in issues:
                if issue["severity"] == "INFO" and not args.verbose:
                    continue
                sev = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(
                    issue["severity"], "·"
                )
                print(
                    f"  {sev} [{issue['severity']:7s}] "
                    f"{relative} — pk={issue['pk']} "
                    f"\"{issue['username']}\": {issue['issue']}"
                )

    print()
    if total_issues:
        errors = [i for i in total_issues if i["severity"] == "ERROR"]
        warnings = [i for i in total_issues if i["severity"] == "WARNING"]
        infos = [i for i in total_issues if i["severity"] == "INFO"]
        print(f"📊 Summary: {len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info(s)")
    else:
        print("✅ No consistency issues found")

    if args.fix:
        print(f"🔧 Applied {total_fixes} auto-fix(es)")

    return 1 if any(i["severity"] == "ERROR" for i in total_issues) else 0


if __name__ == "__main__":
    sys.exit(main())
