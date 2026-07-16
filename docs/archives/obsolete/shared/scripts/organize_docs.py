#!/usr/bin/env python3
"""
Script to organize documentation files into docs/ directory.
This helps implement Phase 17: Documentation Organization and Cleanup.
"""

import re
import shutil
from pathlib import Path
from typing import Dict, List


class DocumentationOrganizer:
    """Organize documentation files into categories."""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.docs_dir = self.base_dir / "docs"

        # Define categories and their patterns
        self.categories = {
            "architecture": [
                "ARCHITECTURE", "BOUNDARY", "CIRCULAR", "DOMAIN",
                "DEPENDENCY", "MIGRATION", "STRUCTURE"
            ],
            "reports": [
                "REPORT", "SUMMARY", "COMPLETION", "RECOVERY",
                "BACKUP", "LOG", "VALIDATION", "VERIFICATION"
            ],
            "testing": [
                "TEST", "COVERAGE", "PBT", "HYPOTHESIS", "FIXTURE"
            ],
            "development": [
                "TASK", "SPEC", "REQUIREMENT", "DESIGN", "PLAN",
                "PHASE", "WORKFLOW", "GUIDE", "CHECKLIST"
            ],
            "deployment": [
                "DEPLOYMENT", "DOCKER", "CI", "CD", "PRODUCTION",
                "STAGING", "ENVIRONMENT", "CONFIG"
            ]
        }

    def categorize_file(self, filename: str) -> str:
        """Determine which category a file belongs to."""
        filename_upper = filename.upper()

        for category, patterns in self.categories.items():
            for pattern in patterns:
                if pattern in filename_upper:
                    return category

        # Default category for uncategorized files
        return "misc"

    def organize_files(self, dry_run: bool = True) -> Dict:
        """Organize all .md files into docs/ directory."""
        print("="*60)
        print("Organizing Documentation Files")
        print("="*60)

        # Find all .md files in base directory (excluding README.md)
        md_files = list(self.base_dir.glob("*.md"))
        md_files = [f for f in md_files if f.name != "README.md"]

        print(f"Found {len(md_files)} .md files to organize")

        # Create docs directory structure
        if not dry_run:
            self.docs_dir.mkdir(exist_ok=True)
            for category in list(self.categories.keys()) + ["misc"]:
                (self.docs_dir / category).mkdir(exist_ok=True)

        # Organize files
        results = {
            "total_files": len(md_files),
            "organized_files": 0,
            "by_category": {},
            "errors": []
        }

        for md_file in md_files:
            category = self.categorize_file(md_file.name)
            target_dir = self.docs_dir / category
            target_file = target_dir / md_file.name

            results["by_category"][category] = results["by_category"].get(category, 0) + 1

            if dry_run:
                print(f"  {md_file.name} → docs/{category}/")
            else:
                try:
                    shutil.move(str(md_file), str(target_file))
                    print(f"  ✓ Moved {md_file.name} to docs/{category}/")
                    results["organized_files"] += 1
                except Exception as e:
                    error_msg = f"Failed to move {md_file.name}: {e}"
                    print(f"  ✗ {error_msg}")
                    results["errors"].append(error_msg)

        return results

    def create_docs_index(self) -> str:
        """Create docs/README.md with table of contents."""
        index_content = """# Documentation Index

This directory contains organized documentation for the ecosystem-wide architectural refactoring project.

## Categories

"""

        # Add category descriptions
        category_descriptions = {
            "architecture": "Architecture documentation, boundary rules, dependency graphs, and migration guides",
            "reports": "Completion reports, validation reports, recovery reports, and logs",
            "testing": "Testing documentation, test reports, coverage reports, and PBT specifications",
            "development": "Task specifications, requirements, design documents, and development guides",
            "deployment": "Deployment guides, Docker configuration, CI/CD pipelines, and environment setup",
            "misc": "Miscellaneous documentation files"
        }

        for category, description in category_descriptions.items():
            category_dir = self.docs_dir / category
            if category_dir.exists():
                files = list(category_dir.glob("*.md"))
                index_content += f"\n### {category.title()}\n"
                index_content += f"{description}\n\n"

                if files:
                    for file in sorted(files):
                        index_content += f"- [{file.name}]({category}/{file.name})\n"
                else:
                    index_content += "*(No files in this category yet)*\n"

        # Add scripts documentation
        index_content += """
### Scripts

Documentation for available scripts:

- [run_all_tests.py](../scripts/run_all_tests.py) - Run all tests for both websites
- [verify_test_parity.py](../scripts/verify_test_parity.py) - Verify test parity between websites
- [organize_docs.py](../scripts/organize_docs.py) - Organize documentation files

## Project Structure

```
docs/
├── architecture/     # Architecture documentation
├── reports/         # Completion and validation reports
├── testing/         # Testing documentation
├── development/     # Development guides and specs
├── deployment/      # Deployment guides
└── misc/           # Miscellaneous documentation
```

## Usage

To organize documentation files:

```bash
# Dry run (show what would be moved)
python3 scripts/organize_docs.py --dry-run

# Actually organize files
python3 scripts/organize_docs.py
```

## Notes

- README.md remains in the base directory
- All other .md files are moved to appropriate categories
- File references may need updating after organization
"""

        return index_content

    def run(self, dry_run: bool = True):
        """Main execution method."""
        if dry_run:
            print("DRY RUN - No files will be moved")
            print("-"*60)

        results = self.organize_files(dry_run)

        print(f"\n{'='*60}")
        print("Organization Summary")
        print(f"{'='*60}")
        print(f"Total files: {results['total_files']}")
        print(f"Files organized: {results['organized_files']}")

        if results['by_category']:
            print("\nBy category:")
            for category, count in sorted(results['by_category'].items()):
                print(f"  {category}: {count} files")

        if results['errors']:
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  - {error}")

        if not dry_run:
            # Create docs index
            index_file = self.docs_dir / "README.md"
            index_content = self.create_docs_index()
            index_file.write_text(index_content)
            print(f"\nCreated docs index: {index_file}")

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Organize documentation files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    parser.add_argument("--run", action="store_true", help="Actually organize files")

    args = parser.parse_args()

    # Default to dry-run if neither flag is specified
    dry_run = not args.run if args.run else True

    organizer = DocumentationOrganizer()
    organizer.run(dry_run=dry_run)


if __name__ == "__main__":
    main()
