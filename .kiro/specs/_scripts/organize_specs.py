#!/usr/bin/env python3
"""
Spec Organization Script

Organizes specs into appropriate directories based on their status:
- completed/: Specs with 100% task completion
- in-progress/: Specs with 0% < completion < 100%
- deferred/: Specs deferred for future work
- archive/: Legacy specs

Usage:
    python organize_specs.py [--dry-run] [--status STATUS]
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path to import analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))
from analyze_specs import SpecAnalyzer, SpecStatus


class SpecOrganizer:
    """Organizes specs into status-based directories."""

    def __init__(self, specs_dir: str = ".kiro/specs", organized_dir: str = ".kiro/specs-organized"):
        self.specs_dir = Path(specs_dir)
        self.organized_dir = Path(organized_dir)
        self.analyzer = SpecAnalyzer(specs_dir)

        # Ensure organized directory structure exists
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all organized directories exist."""
        directories = [
            self.organized_dir / "completed",
            self.organized_dir / "in-progress",
            self.organized_dir / "deferred",
            self.organized_dir / "archive",
            self.organized_dir / "reports",
            self.organized_dir / "templates",
            self.organized_dir / "scripts"
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)

    def analyze_specs(self) -> Dict[str, SpecStatus]:
        """Analyze all specs and return their status."""
        return self.analyzer.analyze_all_specs()

    def get_spec_destination(self, status: SpecStatus) -> Path:
        """Determine where a spec should be organized based on its status."""
        if status.completion_percentage == 100:
            return self.organized_dir / "completed" / status.name
        elif status.completion_percentage > 0:
            return self.organized_dir / "in-progress" / status.name
        else:
            return self.organized_dir / "deferred" / status.name

    def organize_spec(self, spec_name: str, status: SpecStatus, dry_run: bool = False) -> bool:
        """Organize a single spec into the appropriate directory."""
        source_dir = self.specs_dir / spec_name
        dest_dir = self.get_spec_destination(status)

        if not source_dir.exists():
            print(f"⚠️  Spec directory not found: {source_dir}")
            return False

        if source_dir == dest_dir:
            print(f"ℹ️  Spec already in correct location: {spec_name}")
            return True

        print(f"📦 Organizing: {spec_name}")
        print(f"   Source: {source_dir}")
        print(f"   Destination: {dest_dir}")
        print(f"   Status: {status.completion_percentage:.1f}% complete")

        if dry_run:
            print("   🚫 Dry run - no changes made")
            return True

        try:
            # Copy spec to organized directory
            if dest_dir.exists():
                print(f"   ⚠️  Destination already exists, removing: {dest_dir}")
                shutil.rmtree(dest_dir)

            shutil.copytree(source_dir, dest_dir)
            print(f"   ✅ Copied to {dest_dir}")

            # Create symlink back to original location for backward compatibility
            symlink_path = self.specs_dir / spec_name
            if symlink_path.exists():
                if symlink_path.is_symlink():
                    symlink_path.unlink()
                else:
                    # Don't delete original if it's not a symlink
                    print(f"   ℹ️  Original directory kept (not a symlink): {symlink_path}")

            # Create symlink from original to organized location
            symlink_path.symlink_to(dest_dir, target_is_directory=True)
            print(f"   🔗 Created symlink: {symlink_path} → {dest_dir}")

            return True

        except Exception as e:
            print(f"   ❌ Error organizing {spec_name}: {e}")
            return False

    def organize_all_specs(self, dry_run: bool = False) -> Dict[str, bool]:
        """Organize all specs based on their status."""
        specs = self.analyze_specs()
        results = {}

        print(f"🔍 Analyzing {len(specs)} specs...")
        print()

        for spec_name, status in specs.items():
            success = self.organize_spec(spec_name, status, dry_run)
            results[spec_name] = success
            print()

        return results

    def organize_by_status(self, target_status: str, dry_run: bool = False) -> Dict[str, bool]:
        """Organize only specs with a specific status."""
        specs = self.analyze_specs()
        results = {}

        # Map status strings to completion percentages
        status_map = {
            "completed": 100,
            "in-progress": (0, 100),  # Range
            "not-started": 0,
            "deferred": 0  # Treat not-started as deferred
        }

        if target_status not in status_map:
            print(f"❌ Invalid status: {target_status}")
            print(f"   Valid options: {', '.join(status_map.keys())}")
            return {}

        target_value = status_map[target_status]

        print(f"🔍 Finding specs with status: {target_status}")
        print()

        count = 0
        for spec_name, status in specs.items():
            should_organize = False

            if target_status == "completed":
                should_organize = status.completion_percentage == 100
            elif target_status == "in-progress":
                should_organize = 0 < status.completion_percentage < 100
            elif target_status in ["not-started", "deferred"]:
                should_organize = status.completion_percentage == 0

            if should_organize:
                count += 1
                success = self.organize_spec(spec_name, status, dry_run)
                results[spec_name] = success
                print()

        print(f"📊 Found {count} specs with status '{target_status}'")
        return results

    def generate_organization_report(self, results: Dict[str, bool]) -> str:
        """Generate a report of the organization results."""
        total = len(results)
        successful = sum(1 for success in results.values() if success)
        failed = total - successful

        report = []
        report.append("# Spec Organization Report")
        report.append("")
        report.append("## Summary")
        report.append(f"- **Total Specs**: {total}")
        report.append(f"- **✅ Successful**: {successful}")
        report.append(f"- **❌ Failed**: {failed}")
        report.append("")

        if successful > 0:
            report.append("## Successfully Organized")
            for spec_name, success in results.items():
                if success:
                    report.append(f"- ✅ `{spec_name}`")
            report.append("")

        if failed > 0:
            report.append("## Failed to Organize")
            for spec_name, success in results.items():
                if not success:
                    report.append(f"- ❌ `{spec_name}`")
            report.append("")

        # Directory structure
        report.append("## Current Organization Structure")
        report.append("")
        report.append("```")
        self.print_directory_tree(self.organized_dir, report, max_depth=3)
        report.append("```")
        report.append("")

        return "\n".join(report)

    def print_directory_tree(self, directory: Path, report: List[str], prefix: str = "", max_depth: int = 3, current_depth: int = 0):
        """Print directory tree structure."""
        if current_depth >= max_depth:
            return

        try:
            items = sorted(directory.iterdir())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1

                if item.is_dir():
                    report.append(f"{prefix}{'└── ' if is_last else '├── '}{item.name}/")
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    self.print_directory_tree(item, report, new_prefix, max_depth, current_depth + 1)
                else:
                    report.append(f"{prefix}{'└── ' if is_last else '├── '}{item.name}")
        except Exception as e:
            report.append(f"{prefix}⚠️  Error reading directory: {e}")

    def cleanup_old_links(self, dry_run: bool = False):
        """Clean up broken symlinks in the specs directory."""
        print("🧹 Cleaning up broken symlinks...")
        print()

        broken_links = []
        if self.specs_dir.exists():
            for item in self.specs_dir.iterdir():
                if item.is_symlink() and not item.exists():
                    broken_links.append(item)

        if not broken_links:
            print("✅ No broken symlinks found")
            return

        print(f"Found {len(broken_links)} broken symlinks:")
        for link in broken_links:
            print(f"  - {link.name}")

        if dry_run:
            print("🚫 Dry run - no changes made")
            return

        print()
        print("Removing broken symlinks...")
        for link in broken_links:
            try:
                link.unlink()
                print(f"  ✅ Removed: {link.name}")
            except Exception as e:
                print(f"  ❌ Failed to remove {link.name}: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Organize specs into status-based directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--status", choices=["completed", "in-progress", "not-started", "deferred", "all"],
                       default="all", help="Only organize specs with this status")
    parser.add_argument("--cleanup", action="store_true", help="Clean up broken symlinks")

    args = parser.parse_args()

    organizer = SpecOrganizer()

    if args.cleanup:
        organizer.cleanup_old_links(args.dry_run)
        return

    print("=" * 60)
    print("SPEC ORGANIZATION TOOL")
    print("=" * 60)
    print()

    if args.dry_run:
        print("🚫 DRY RUN MODE - No changes will be made")
        print()

    if args.status == "all":
        results = organizer.organize_all_specs(args.dry_run)
    else:
        results = organizer.organize_by_status(args.status, args.dry_run)

    print("=" * 60)
    print("ORGANIZATION COMPLETE")
    print("=" * 60)
    print()

    # Generate and print report
    report = organizer.generate_organization_report(results)
    print(report)

    # Save report to file
    report_file = organizer.organized_dir / "reports" / "organization_report.md"
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report, encoding='utf-8')

    print(f"📄 Report saved to: {report_file}")

    if not args.dry_run:
        print()
        print("💡 Next steps:")
        print("1. Review the organized spec directories")
        print("2. Update any references to moved specs")
        print("3. Run the analysis script to update status reports:")
        print("   python3 .kiro/specs-organized/analyze_specs.py")

if __name__ == "__main__":
    main()
