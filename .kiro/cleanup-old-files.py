#!/usr/bin/env python3
"""
Script to clean up old and duplicate files after organizing specs.
"""

import os
import re
import shutil
from pathlib import Path

def find_duplicate_files(base_path):
    """Find potentially duplicate files across categories."""
    file_signatures = {}
    duplicates = []

    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Create a simple signature (first 500 chars + file size)
                    signature = f"{len(content)}:{content[:500]}"

                    if signature in file_signatures:
                        duplicates.append((file_path, file_signatures[signature]))
                    else:
                        file_signatures[signature] = file_path
                except Exception as e:
                    print(f"  ⚠️  Could not read {file_path}: {e}")

    return duplicates

def find_incomplete_specs(base_path):
    """Find specs missing key files."""
    incomplete = []

    categories = ['auth', 'docs', 'integration', 'fixes', 'modernization', 'features']

    for category in categories:
        category_path = os.path.join(base_path, category)
        if not os.path.exists(category_path):
            continue

        for spec_dir in os.listdir(category_path):
            spec_path = os.path.join(category_path, spec_dir)
            if not os.path.isdir(spec_path):
                continue

            # Check for key files
            key_files = {
                'requirements.md': False,
                'design.md': False,
                'tasks.md': False,
                'bugfix.md': False  # For bugfix specs
            }

            for file_name in key_files.keys():
                if os.path.exists(os.path.join(spec_path, file_name)):
                    key_files[file_name] = True

            # Determine spec type
            is_bugfix = 'bugfix.md' in [f for f in os.listdir(spec_path) if f.endswith('.md')]

            # Check completeness
            missing = []
            if is_bugfix:
                if not key_files['bugfix.md']:
                    missing.append('bugfix.md')
                if not key_files['design.md']:
                    missing.append('design.md')
                if not key_files['tasks.md']:
                    missing.append('tasks.md')
            else:
                if not key_files['requirements.md']:
                    missing.append('requirements.md')
                if not key_files['design.md']:
                    missing.append('design.md')
                if not key_files['tasks.md']:
                    missing.append('tasks.md')

            if missing:
                incomplete.append({
                    'path': spec_path,
                    'category': category,
                    'missing': missing,
                    'is_bugfix': is_bugfix
                })

    return incomplete

def find_old_backup_files(base_path):
    """Find old backup or temporary files."""
    old_patterns = [
        r'\.bak$',
        r'\.old$',
        r'\.tmp$',
        r'~$',  # Backup files ending with ~
        r'^\.',  # Hidden files
        r'\.swp$',  # Vim swap files
        r'\.swo$',  # Vim swap files
    ]

    old_files = []

    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            file_path = os.path.join(root, file)

            # Check against patterns
            for pattern in old_patterns:
                if re.search(pattern, file):
                    old_files.append(file_path)
                    break

            # Also check for files that might be old versions
            if file.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if 'OLD' in first_line.upper() or 'BACKUP' in first_line.upper():
                        old_files.append(file_path)

    return old_files

def cleanup_original_specs_dir():
    """Clean up the original specs directory."""
    original_dir = "../specs"  # Relative to .kiro/specs-organized

    if not os.path.exists(original_dir):
        print("  ℹ️  Original specs directory already cleaned up")
        return []

    # List remaining files
    remaining_files = []
    for root, dirs, files in os.walk(original_dir):
        for file in files:
            file_path = os.path.join(root, file)
            remaining_files.append(file_path)

    return remaining_files

def main():
    base_path = "."

    print("=" * 60)
    print("CLEANUP AND ORGANIZATION CHECK")
    print("=" * 60)

    print("\n🔍 Checking for duplicate files...")
    duplicates = find_duplicate_files(base_path)

    if duplicates:
        print(f"Found {len(duplicates)} potential duplicates:")
        for dup1, dup2 in duplicates[:10]:  # Show first 10
            print(f"  • {os.path.relpath(dup1, base_path)}")
            print(f"    duplicates {os.path.relpath(dup2, base_path)}")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")
    else:
        print("  ✓ No duplicate files found")

    print("\n🔍 Checking for incomplete specs...")
    incomplete = find_incomplete_specs(base_path)

    if incomplete:
        print(f"Found {len(incomplete)} incomplete specs:")
        for spec in incomplete:
            print(f"  • {os.path.relpath(spec['path'], base_path)}")
            print(f"    Category: {spec['category']}, Type: {'Bugfix' if spec['is_bugfix'] else 'Feature'}")
            print(f"    Missing: {', '.join(spec['missing'])}")
    else:
        print("  ✓ All specs appear complete")

    print("\n🔍 Checking for old/backup files...")
    old_files = find_old_backup_files(base_path)

    if old_files:
        print(f"Found {len(old_files)} old/backup files:")
        for file in old_files[:10]:  # Show first 10
            print(f"  • {os.path.relpath(file, base_path)}")
        if len(old_files) > 10:
            print(f"  ... and {len(old_files) - 10} more")
    else:
        print("  ✓ No old/backup files found")

    print("\n🔍 Checking original specs directory...")
    original_files = cleanup_original_specs_dir()

    if original_files:
        print(f"Found {len(original_files)} files in original specs directory:")
        for file in original_files:
            print(f"  • {file}")
    else:
        print("  ✓ Original specs directory is clean")

    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"• Duplicate files: {len(duplicates)}")
    print(f"• Incomplete specs: {len(incomplete)}")
    print(f"• Old/backup files: {len(old_files)}")
    print(f"• Files in original dir: {len(original_files)}")

    print("\n💡 Recommendations:")
    if duplicates:
        print("  - Review duplicate files and remove unnecessary copies")
    if incomplete:
        print("  - Complete the incomplete specs by adding missing files")
    if old_files:
        print("  - Remove old backup files to clean up the workspace")
    if original_files:
        print("  - Clean up the original specs directory")

    print("\n⚠️  Note: This script only identifies issues.")
    print("   Review the findings before taking any cleanup actions.")
    print("=" * 60)

if __name__ == "__main__":
    main()
