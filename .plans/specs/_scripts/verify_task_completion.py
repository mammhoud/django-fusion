#!/usr/bin/env python3
"""
Task Completion Verification Script

Verifies that all completed specs have all tasks marked [x].
Checks for consistency between task status and spec completion.

Usage:
    python verify_task_completion.py [--fix]
"""

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TaskCompletionVerifier:
    """Verifies task completion status in specs."""

    def __init__(self, specs_dir: str = ".kiro/specs"):
        self.specs_dir = Path(specs_dir)
        self.results: Dict[str, Dict] = {}

    def verify_all_specs(self) -> Dict[str, Dict]:
        """Verify task completion for all specs."""
        if not self.specs_dir.exists():
            print(f"Specs directory not found: {self.specs_dir}")
            return {}

        for spec_dir in self.specs_dir.iterdir():
            if spec_dir.is_dir():
                spec_name = spec_dir.name
                result = self.verify_spec(spec_dir)
                self.results[spec_name] = result

        return self.results

    def verify_spec(self, spec_dir: Path) -> Dict:
        """Verify task completion for a single spec."""
        spec_name = spec_dir.name
        result = {
            "name": spec_name,
            "has_tasks": False,
            "total_tasks": 0,
            "completed_tasks": 0,
            "incomplete_tasks": 0,
            "completion_percentage": 0.0,
            "is_fully_complete": False,
            "issues": [],
            "files_missing": []
        }

        # Check for tasks.md
        tasks_file = spec_dir / "tasks.md"
        if not tasks_file.exists():
            result["issues"].append("Missing tasks.md file")
            result["files_missing"].append("tasks.md")
            return result

        result["has_tasks"] = True

        # Analyze tasks.md
        try:
            content = tasks_file.read_text(encoding='utf-8')

            # Count task markers
            completed = len(re.findall(r'^\s*-\s*\[x\]', content, re.MULTILINE))
            in_progress = len(re.findall(r'^\s*-\s*\[-\]', content, re.MULTILINE))
            partial = len(re.findall(r'^\s*-\s*\[~\]', content, re.MULTILINE))
            not_started = len(re.findall(r'^\s*-\s*\[\s\]', content, re.MULTILINE))

            # Count all tasks
            all_tasks = len(re.findall(r'^\s*-\s*\[', content, re.MULTILINE))

            result["total_tasks"] = all_tasks
            result["completed_tasks"] = completed
            result["incomplete_tasks"] = in_progress + partial + not_started

            if all_tasks > 0:
                result["completion_percentage"] = (completed / all_tasks) * 100

            # Check if spec is fully complete
            if all_tasks > 0 and completed == all_tasks:
                result["is_fully_complete"] = True
            else:
                result["is_fully_complete"] = False

            # Check for issues
            if in_progress > 0:
                result["issues"].append(f"Has {in_progress} task(s) marked as in-progress [-]")

            if partial > 0:
                result["issues"].append(f"Has {partial} task(s) marked as partially complete [~]")

            if not_started > 0:
                result["issues"].append(f"Has {not_started} task(s) not started [ ]")

            # Check for mixed status in "completed" spec
            if result["completion_percentage"] == 100 and (in_progress > 0 or partial > 0 or not_started > 0):
                result["issues"].append("Marked as 100% complete but has non-completed tasks")

        except Exception as e:
            result["issues"].append(f"Error reading tasks.md: {e}")

        # Check for other required files
        if not (spec_dir / "requirements.md").exists():
            result["files_missing"].append("requirements.md")
            result["issues"].append("Missing requirements.md")

        if not (spec_dir / "design.md").exists():
            result["files_missing"].append("design.md")
            result["issues"].append("Missing design.md")

        return result

    def generate_verification_report(self) -> str:
        """Generate a verification report."""
        report = []
        report.append("# Task Completion Verification Report")
        report.append("")
        report.append("## Summary")

        total_specs = len(self.results)
        fully_complete = sum(1 for r in self.results.values() if r["is_fully_complete"])
        with_issues = sum(1 for r in self.results.values() if r["issues"])
        missing_files = sum(1 for r in self.results.values() if r["files_missing"])

        report.append(f"- **Total Specs**: {total_specs}")
        report.append(f"- **✅ Fully Complete**: {fully_complete}")
        report.append(f"- **⚠️  With Issues**: {with_issues}")
        report.append(f"- **❌ Missing Files**: {missing_files}")
        report.append("")

        # Detailed results
        report.append("## Spec Details")
        report.append("")
        report.append("| Spec | Tasks | Completion | Status | Issues |")
        report.append("|------|-------|------------|--------|--------|")

        for spec_name, result in sorted(self.results.items()):
            task_summary = f"{result['completed_tasks']}/{result['total_tasks']}"
            completion = f"{result['completion_percentage']:.1f}%"

            # Status emoji
            if result["is_fully_complete"]:
                status = "✅"
            elif result["completion_percentage"] > 0:
                status = "🔄"
            else:
                status = "⏳"

            # Issues summary
            if result["issues"]:
                issues = f"{len(result['issues'])} issue(s)"
            else:
                issues = "✅"

            report.append(f"| `{spec_name}` | {task_summary} | {completion} | {status} | {issues} |")

        report.append("")

        # Issues section
        report.append("## Issues Found")
        report.append("")

        has_issues = False
        for spec_name, result in sorted(self.results.items()):
            if result["issues"]:
                has_issues = True
                report.append(f"### `{spec_name}`")
                for issue in result["issues"]:
                    report.append(f"- {issue}")
                report.append("")

        if not has_issues:
            report.append("✅ No issues found!")
            report.append("")

        # Missing files section
        report.append("## Missing Files")
        report.append("")

        missing_files = False
        for spec_name, result in sorted(self.results.items()):
            if result["files_missing"]:
                missing_files = True
                report.append(f"### `{spec_name}`")
                for file in result["files_missing"]:
                    report.append(f"- ❌ {file}")
                report.append("")

        if not missing_files:
            report.append("✅ All specs have all required files!")
            report.append("")

        # Recommendations
        report.append("## Recommendations")
        report.append("")

        for spec_name, result in sorted(self.results.items()):
            if result["completion_percentage"] == 100 and not result["is_fully_complete"]:
                report.append(f"- ⚠️ **{spec_name}** shows 100% completion but has non-completed tasks")
                report.append(f"  - Review tasks.md and ensure all tasks are marked `[x]`")

            if result["files_missing"]:
                report.append(f"- ⚠️ **{spec_name}** is missing files: {', '.join(result['files_missing'])}")
                report.append(f"  - Create missing files or mark spec as incomplete")

        if not any(r["completion_percentage"] == 100 and not r["is_fully_complete"] for r in self.results.values()):
            report.append("- ✅ All 100% complete specs have all tasks marked `[x]`")

        return "\n".join(report)

    def fix_issues(self, spec_name: str) -> bool:
        """Attempt to fix issues for a spec (placeholder for future implementation)."""
        print(f"⚠️  Fix functionality not yet implemented for {spec_name}")
        print("   Manual review required")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify task completion in specs")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues (not yet implemented)")
    parser.add_argument("--spec", type=str, help="Verify specific spec only")

    args = parser.parse_args()

    verifier = TaskCompletionVerifier()

    if args.spec:
        # Verify specific spec
        spec_dir = Path(".kiro/specs") / args.spec
        if not spec_dir.exists():
            print(f"❌ Spec not found: {args.spec}")
            return

        result = verifier.verify_spec(spec_dir)
        verifier.results[args.spec] = result
    else:
        # Verify all specs
        verifier.verify_all_specs()

    # Generate and print report
    report = verifier.generate_verification_report()
    print(report)

    # Save report to file
    report_dir = Path(".kiro/specs-organized/reports")
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "verification_report.md"
    report_file.write_text(report, encoding='utf-8')

    print(f"📄 Report saved to: {report_file}")

    # Summary statistics
    total = len(verifier.results)
    fully_complete = sum(1 for r in verifier.results.values() if r["is_fully_complete"])

    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total specs: {total}")
    print(f"Fully complete: {fully_complete} ({fully_complete/total*100:.1f}%)")

    if fully_complete == total:
        print("✅ All specs are fully complete!")
    else:
        print(f"⚠️  {total - fully_complete} spec(s) need attention")

if __name__ == "__main__":
    main()
