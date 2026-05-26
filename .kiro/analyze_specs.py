#!/usr/bin/env python3
"""
Spec Analysis Script

Analyzes all specs in .kiro/specs/ directory and generates comprehensive status report.
Provides detailed analysis of task completion, file requirements, and spec organization.

Usage:
    python analyze_specs.py
"""

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class SpecStatus:
    """Represents the status of a spec."""
    name: str
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    partial_tasks: int = 0
    not_started_tasks: int = 0
    has_requirements: bool = False
    has_design: bool = False
    has_tasks: bool = False
    completion_percentage: float = 0.0
    category: str = "uncategorized"
    description: str = ""
    last_updated: Optional[str] = None

class SpecAnalyzer:
    """Analyzes spec directories and generates status reports."""

    def __init__(self, specs_dir: str = ".kiro/specs"):
        self.specs_dir = Path(specs_dir)
        self.specs: Dict[str, SpecStatus] = {}

    def analyze_all_specs(self) -> Dict[str, SpecStatus]:
        """Analyze all specs in the directory."""
        if not self.specs_dir.exists():
            print(f"Specs directory not found: {self.specs_dir}")
            return {}

        for spec_dir in self.specs_dir.iterdir():
            if spec_dir.is_dir():
                spec_name = spec_dir.name
                status = self.analyze_spec(spec_dir)
                self.specs[spec_name] = status

        return self.specs

    def analyze_spec(self, spec_dir: Path) -> SpecStatus:
        """Analyze a single spec directory."""
        spec_name = spec_dir.name
        status = SpecStatus(name=spec_name)

        # Check for required files
        status.has_requirements = (spec_dir / "requirements.md").exists()
        status.has_design = (spec_dir / "design.md").exists()
        status.has_tasks = (spec_dir / "tasks.md").exists()

        # Analyze tasks.md if it exists
        if status.has_tasks:
            tasks_file = spec_dir / "tasks.md"
            task_stats = self.analyze_tasks_file(tasks_file)
            status.total_tasks = task_stats["total"]
            status.completed_tasks = task_stats["completed"]
            status.in_progress_tasks = task_stats["in_progress"]
            status.partial_tasks = task_stats["partial"]
            status.not_started_tasks = task_stats["not_started"]

            if status.total_tasks > 0:
                status.completion_percentage = (status.completed_tasks / status.total_tasks) * 100

        # Determine category based on spec name
        status.category = self.determine_category(spec_name)

        # Try to get description from requirements.md
        if status.has_requirements:
            description = self.extract_description(spec_dir / "requirements.md")
            if description:
                status.description = description

        return status

    def analyze_tasks_file(self, tasks_file: Path) -> Dict[str, int]:
        """Analyze a tasks.md file and count task status markers."""
        if not tasks_file.exists():
            return {"total": 0, "completed": 0, "in_progress": 0, "partial": 0, "not_started": 0}

        try:
            content = tasks_file.read_text(encoding='utf-8')

            # Count task markers
            completed = len(re.findall(r'^\s*-\s*\[x\]', content, re.MULTILINE))
            in_progress = len(re.findall(r'^\s*-\s*\[-\]', content, re.MULTILINE))
            partial = len(re.findall(r'^\s*-\s*\[~\]', content, re.MULTILINE))
            not_started = len(re.findall(r'^\s*-\s*\[\s\]', content, re.MULTILINE))

            # Count all tasks (including sub-tasks)
            all_tasks = len(re.findall(r'^\s*-\s*\[', content, re.MULTILINE))

            return {
                "total": all_tasks,
                "completed": completed,
                "in_progress": in_progress,
                "partial": partial,
                "not_started": not_started
            }
        except Exception as e:
            print(f"Error analyzing tasks file {tasks_file}: {e}")
            return {"total": 0, "completed": 0, "in_progress": 0, "partial": 0, "not_started": 0}

    def determine_category(self, spec_name: str) -> str:
        """Determine category based on spec name patterns."""
        name_lower = spec_name.lower()

        if any(word in name_lower for word in ["refactor", "restructure", "reorganize"]):
            return "refactoring"
        elif any(word in name_lower for word in ["deployment", "production", "deploy"]):
            return "deployment"
        elif any(word in name_lower for word in ["django", "package", "module"]):
            return "django"
        elif any(word in name_lower for word in ["phase", "completion", "sync"]):
            return "phases"
        elif any(word in name_lower for word in ["ecosystem", "architectural", "architecture"]):
            return "architecture"
        elif any(word in name_lower for word in ["verification", "validation", "test"]):
            return "verification"
        elif any(word in name_lower for word in ["core", "logic", "consolidation"]):
            return "core"
        else:
            return "other"

    def extract_description(self, requirements_file: Path) -> str:
        """Extract description from requirements.md file."""
        try:
            content = requirements_file.read_text(encoding='utf-8')
            # Look for first paragraph after title
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('#') and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('#'):
                        return next_line[:200]  # Limit length
        except Exception as e:
            print(f"Error extracting description from {requirements_file}: {e}")

        return ""

    def generate_status_report(self) -> str:
        """Generate a comprehensive status report."""
        report = []
        report.append("# Spec Status Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Specs: {len(self.specs)}")
        report.append("")

        # Summary statistics
        total_completed = sum(1 for s in self.specs.values() if s.completion_percentage == 100)
        total_in_progress = sum(1 for s in self.specs.values() if 0 < s.completion_percentage < 100)
        total_not_started = sum(1 for s in self.specs.values() if s.completion_percentage == 0)

        report.append("## Summary")
        report.append(f"- ✅ **Completed**: {total_completed} specs")
        report.append(f"- 🔄 **In Progress**: {total_in_progress} specs")
        report.append(f"- ⏳ **Not Started**: {total_not_started} specs")
        report.append("")

        # Category breakdown
        categories = {}
        for spec in self.specs.values():
            categories[spec.category] = categories.get(spec.category, 0) + 1

        report.append("## Categories")
        for category, count in sorted(categories.items()):
            report.append(f"- **{category.title()}**: {count} specs")
        report.append("")

        # Detailed spec table
        report.append("## Spec Details")
        report.append("")
        report.append("| Spec | Category | Status | Tasks | Completion | Files |")
        report.append("|------|----------|--------|-------|------------|-------|")

        for spec_name, status in sorted(self.specs.items()):
            # Determine status emoji
            if status.completion_percentage == 100:
                status_emoji = "✅"
            elif status.completion_percentage > 0:
                status_emoji = "🔄"
            else:
                status_emoji = "⏳"

            # Task summary
            task_summary = f"{status.completed_tasks}/{status.total_tasks}"

            # Completion percentage
            completion = f"{status.completion_percentage:.1f}%"

            # File status
            files = []
            if status.has_requirements:
                files.append("📋")
            else:
                files.append("❌")
            if status.has_design:
                files.append("📐")
            else:
                files.append("❌")
            if status.has_tasks:
                files.append("📝")
            else:
                files.append("❌")
            file_status = " ".join(files)

            report.append(f"| `{spec_name}` | {status.category} | {status_emoji} | {task_summary} | {completion} | {file_status} |")

        report.append("")

        # File requirements section
        report.append("## File Requirements Status")
        report.append("")

        missing_files = []
        for spec_name, status in self.specs.items():
            missing = []
            if not status.has_requirements:
                missing.append("requirements.md")
            if not status.has_design:
                missing.append("design.md")
            if not status.has_tasks:
                missing.append("tasks.md")

            if missing:
                missing_files.append((spec_name, missing))

        if missing_files:
            report.append("### Specs with Missing Files")
            for spec_name, missing in missing_files:
                report.append(f"- `{spec_name}`: {', '.join(missing)}")
        else:
            report.append("✅ All specs have all required files!")

        report.append("")

        # Recommendations
        report.append("## Recommendations")
        report.append("")

        # Check for completed specs with missing files
        for spec_name, status in self.specs.items():
            if status.completion_percentage == 100:
                if not status.has_design:
                    report.append(f"- ⚠️ **{spec_name}** is marked as completed but missing `design.md`")

        # Check for specs with no tasks
        for spec_name, status in self.specs.items():
            if status.total_tasks == 0 and status.has_tasks:
                report.append(f"- ⚠️ **{spec_name}** has `tasks.md` but no tasks found")

        return "\n".join(report)

    def generate_json_report(self) -> str:
        """Generate JSON report for programmatic use."""
        report_data = {
            "generated": datetime.now().isoformat(),
            "total_specs": len(self.specs),
            "specs": {}
        }

        for spec_name, status in self.specs.items():
            report_data["specs"][spec_name] = {
                "name": status.name,
                "category": status.category,
                "description": status.description,
                "tasks": {
                    "total": status.total_tasks,
                    "completed": status.completed_tasks,
                    "in_progress": status.in_progress_tasks,
                    "partial": status.partial_tasks,
                    "not_started": status.not_started_tasks,
                    "completion_percentage": status.completion_percentage
                },
                "files": {
                    "has_requirements": status.has_requirements,
                    "has_design": status.has_design,
                    "has_tasks": status.has_tasks
                }
            }

        return json.dumps(report_data, indent=2)

    def generate_pydoc_report(self) -> str:
        """Generate pydoc-style documentation for specs."""
        pydoc = []
        pydoc.append("Spec Documentation")
        pydoc.append("=" * 80)
        pydoc.append("")
        pydoc.append("Overview")
        pydoc.append("-" * 40)
        pydoc.append("")
        pydoc.append("This document provides pydoc-style documentation for all specs.")
        pydoc.append("Each spec includes methods (tasks), use cases, and usage examples.")
        pydoc.append("")

        for spec_name, status in sorted(self.specs.items()):
            pydoc.append(f"{spec_name}")
            pydoc.append("-" * 40)
            pydoc.append("")

            if status.description:
                pydoc.append(f"Description: {status.description}")
                pydoc.append("")

            pydoc.append(f"Category: {status.category}")
            pydoc.append(f"Status: {status.completion_percentage:.1f}% complete")
            pydoc.append("")

            # File status
            pydoc.append("Files:")
            pydoc.append(f"  - requirements.md: {'✅' if status.has_requirements else '❌'}")
            pydoc.append(f"  - design.md: {'✅' if status.has_design else '❌'}")
            pydoc.append(f"  - tasks.md: {'✅' if status.has_tasks else '❌'}")
            pydoc.append("")

            # Task summary
            if status.total_tasks > 0:
                pydoc.append("Task Summary:")
                pydoc.append(f"  - Total tasks: {status.total_tasks}")
                pydoc.append(f"  - Completed: {status.completed_tasks}")
                pydoc.append(f"  - In progress: {status.in_progress_tasks}")
                pydoc.append(f"  - Partial: {status.partial_tasks}")
                pydoc.append(f"  - Not started: {status.not_started_tasks}")
                pydoc.append("")

            # Use cases
            pydoc.append("Use Cases:")
            use_cases = self.generate_use_cases(spec_name, status.category)
            for use_case in use_cases:
                pydoc.append(f"  - {use_case}")
            pydoc.append("")

            # Usage examples
            pydoc.append("Usage Examples:")
            examples = self.generate_usage_examples(spec_name)
            for example in examples:
                pydoc.append(f"  - {example}")
            pydoc.append("")

            pydoc.append("")  # Empty line between specs

        return "\n".join(pydoc)

    def generate_use_cases(self, spec_name: str, category: str) -> List[str]:
        """Generate use cases based on spec name and category."""
        use_cases = []

        if category == "refactoring":
            use_cases.extend([
                "Code structure improvement",
                "Technical debt reduction",
                "Maintainability enhancement"
            ])
        elif category == "deployment":
            use_cases.extend([
                "Production deployment verification",
                "Infrastructure validation",
                "Service health monitoring"
            ])
        elif category == "django":
            use_cases.extend([
                "Django package organization",
                "Module extraction and consolidation",
                "Framework-specific optimizations"
            ])
        elif category == "architecture":
            use_cases.extend([
                "System-wide architectural improvements",
                "Cross-project consistency",
                "Scalability enhancements"
            ])
        elif category == "verification":
            use_cases.extend([
                "Quality assurance validation",
                "Test coverage verification",
                "Compliance checking"
            ])
        else:
            use_cases.append("Project-specific implementation")

        return use_cases

    def generate_usage_examples(self, spec_name: str) -> List[str]:
        """Generate usage examples for the spec."""
        examples = [
            f"Review spec requirements: `cat .kiro/specs/{spec_name}/requirements.md`",
            f"Check task status: `grep -c '\\[x\\]' .kiro/specs/{spec_name}/tasks.md`",
            f"View design document: `cat .kiro/specs/{spec_name}/design.md`"
        ]

        return examples

def main():
    """Main entry point."""
    analyzer = SpecAnalyzer()
    specs = analyzer.analyze_all_specs()

    print(f"Analyzed {len(specs)} specs")
    print()

    # Generate reports
    status_report = analyzer.generate_status_report()
    json_report = analyzer.generate_json_report()
    pydoc_report = analyzer.generate_pydoc_report()

    # Write reports to files
    reports_dir = Path(".kiro/specs-organized/reports")
    reports_dir.mkdir(exist_ok=True)

    (reports_dir / "status_report.md").write_text(status_report, encoding='utf-8')
    (reports_dir / "specs_status.json").write_text(json_report, encoding='utf-8')
    (reports_dir / "specs_pydoc.md").write_text(pydoc_report, encoding='utf-8')

    print("Reports generated:")
    print(f"  - {reports_dir / 'status_report.md'}")
    print(f"  - {reports_dir / 'specs_status.json'}")
    print(f"  - {reports_dir / 'specs_pydoc.md'}")

    # Print summary to console
    print("\n" + "="*60)
    print("SPEC ANALYSIS SUMMARY")
    print("="*60)

    completed = sum(1 for s in specs.values() if s.completion_percentage == 100)
    in_progress = sum(1 for s in specs.values() if 0 < s.completion_percentage < 100)
    not_started = sum(1 for s in specs.values() if s.completion_percentage == 0)

    print(f"✅ Completed: {completed}")
    print(f"🔄 In Progress: {in_progress}")
    print(f"⏳ Not Started: {not_started}")

    # Check for missing files
    missing_design = [name for name, s in specs.items() if not s.has_design]
    if missing_design:
        print(f"\n⚠️  Missing design.md: {', '.join(missing_design)}")

    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
