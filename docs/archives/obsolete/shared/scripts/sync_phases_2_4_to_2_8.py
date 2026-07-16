#!/usr/bin/env python3
"""
Comprehensive sync script for phases 2.4-2.8 website synchronization.
Syncs files from ctc-research.com to structa.cloud with branding updates.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
SOURCE_BASE = Path("ctc-research.com")
TARGET_BASE = Path("structa.cloud")

# Branding replacements
BRANDING_REPLACEMENTS = {
    "CTC Research": "Structa",
    "ctc-research.com": "structa.cloud",
    "ctc-research": "structa",
    "support@example.com": "support@example.com",
}

# Phase file mappings
PHASE_FILES = {
    "2.4": {
        "name": "LMS Enhancements",
        "source_dirs": [
            "apps/LMS/models",
            "apps/LMS/managers",
            "apps/LMS/services",
            "apps/LMS/views",
            "apps/LMS/snippets",
            "apps/LMS/templatetags",
            "apps/LMS/blocks",
        ],
        "source_files": [
            "apps/LMS/__init__.py",
            "apps/LMS/admin.py",
            "apps/LMS/apps.py",
            "apps/LMS/urls.py",
            "apps/LMS/wagtail_hooks.py",
            "apps/LMS/services_legacy.py",
        ],
    },
    "2.5": {
        "name": "CI/Infrastructure",
        "source_files": [
            "docker-compose.yml",
            "docker-compose.override.yml",
            "docker-compose.test.yml",
            ".dockerignore",
        ],
    },
    "2.6": {
        "name": "Configuration",
        "source_dirs": [
            "configs/base",
            "configs/settings",
        ],
        "source_files": [
            "configs/__init__.py",
            "configs/__main__.py",
            "configs/cli.py",
        ],
    },
    "2.7": {
        "name": "Testing Infrastructure",
        "source_dirs": [
            "tests",
        ],
    },
    "2.8": {
        "name": "Frontend & Styling",
        "source_dirs": [
            "apps/templates",
        ],
    },
}


def update_branding(content: str) -> str:
    """Update branding in file content."""
    for old, new in BRANDING_REPLACEMENTS.items():
        content = content.replace(old, new)
    return content


def sync_file(source: Path, target: Path) -> bool:
    """Sync a single file with branding updates."""
    try:
        # Create target directory if needed
        target.parent.mkdir(parents=True, exist_ok=True)

        # Read source file
        with open(source, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Update branding
        content = update_branding(content)

        # Write to target
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error syncing {source}: {e}")
        return False


def sync_directory(source_dir: Path, target_dir: Path) -> Tuple[int, int]:
    """Sync entire directory recursively."""
    files_synced = 0
    lines_added = 0

    if not source_dir.exists():
        return files_synced, lines_added

    for source_file in source_dir.rglob("*"):
        if source_file.is_file() and not source_file.name.startswith('.'):
            # Calculate relative path
            rel_path = source_file.relative_to(source_dir.parent)
            target_file = target_dir.parent / rel_path

            if sync_file(source_file, target_file):
                files_synced += 1
                try:
                    with open(target_file, 'r') as f:
                        lines_added += len(f.readlines())
                except:
                    pass

    return files_synced, lines_added


def sync_phase(phase: str) -> Dict:
    """Sync all files for a specific phase."""
    phase_config = PHASE_FILES.get(phase)
    if not phase_config:
        return {"success": False, "error": f"Phase {phase} not found"}

    results = {
        "phase": phase,
        "name": phase_config["name"],
        "files_synced": 0,
        "lines_added": 0,
        "errors": [],
    }

    # Sync individual files
    for file_path in phase_config.get("source_files", []):
        source = SOURCE_BASE / file_path
        target = TARGET_BASE / file_path

        if source.exists():
            if sync_file(source, target):
                results["files_synced"] += 1
                try:
                    with open(target, 'r') as f:
                        results["lines_added"] += len(f.readlines())
                except:
                    pass
            else:
                results["errors"].append(f"Failed to sync {file_path}")

    # Sync directories
    for dir_path in phase_config.get("source_dirs", []):
        source_dir = SOURCE_BASE / dir_path
        target_dir = TARGET_BASE / dir_path

        files, lines = sync_directory(source_dir, target_dir)
        results["files_synced"] += files
        results["lines_added"] += lines

    return results


def main():
    """Execute synchronization for all phases."""
    print("=" * 70)
    print("PHASE 2.4-2.8 WEBSITE SYNCHRONIZATION")
    print("=" * 70)

    all_results = []
    total_files = 0
    total_lines = 0

    for phase in ["2.4", "2.5", "2.6", "2.7", "2.8"]:
        print(f"\nSyncing Phase {phase}...")
        result = sync_phase(phase)
        all_results.append(result)

        if result.get("errors"):
            print(f"  ⚠️  Errors: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"     - {error}")
        else:
            print(f"  ✅ Files synced: {result['files_synced']}")
            print(f"  ✅ Lines added: {result['lines_added']}")
            total_files += result['files_synced']
            total_lines += result['lines_added']

    print("\n" + "=" * 70)
    print("SYNCHRONIZATION SUMMARY")
    print("=" * 70)
    print(f"Total files synced: {total_files}")
    print(f"Total lines added: {total_lines}")
    print("\nPhase Details:")
    for result in all_results:
        print(f"  Phase {result['phase']}: {result['files_synced']} files, {result['lines_added']} lines")

    return all_results


if __name__ == "__main__":
    main()
