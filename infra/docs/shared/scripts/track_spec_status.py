#!/usr/bin/env python3
"""
Spec Status Tracker

Scans all specs in .kiro/specs/ and generates a master task list
of all incomplete tasks grouped by spec and prioritized.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Task:
    """Represents a single task from a spec."""
    spec_name: str
    task_id: str
    title: str
    is_complete: bool
    is_subtask: bool
    parent_task_id: Optional[str] = None
    line_number: int = 0

    def __hash__(self):
        return hash((self.spec_name, self.task_id))

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return self.spec_name == other.spec_name and self.task_id == other.task_id


@dataclass
class SpecStatus:
    """Status of a single spec."""
    name: str
    path: str
    has_requirements: bool = False
    has_design: bool = False
    has_tasks: bool = False
    total_tasks: int = 0
    completed_tasks: int = 0
    incomplete_tasks: int = 0
    tasks: list[Task] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if spec is complete (all tasks done)."""
        return self.total_tasks > 0 and self.total_tasks == self.completed_tasks

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100


class SpecStatusTracker:
    """Tracks status of all specs and their tasks."""

    def __init__(self, specs_dir: str = ".kiro/specs"):
        self.specs_dir = Path(specs_dir)
        self.specs: dict[str, SpecStatus] = {}
        self.all_incomplete_tasks: list[Task] = []

    def scan_specs(self) -> list[SpecStatus]:
        """Scan all specs and determine their status."""
        if not self.specs_dir.exists():
            print(f"Error: {self.specs_dir} does not exist")
            return []

        spec_dirs = [d for d in self.specs_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

        for spec_dir in sorted(spec_dirs):
            spec_name = spec_dir.name
            spec_status = self._analyze_spec(spec_name, spec_dir)
            self.specs[spec_name] = spec_status

        return list(self.specs.values())

    def _analyze_spec(self, spec_name: str, spec_dir: Path) -> SpecStatus:
        """Analyze a single spec directory."""
        status = SpecStatus(
            name=spec_name,
            path=str(spec_dir)
        )

        # Check for required files
        status.has_requirements = (spec_dir / "requirements.md").exists()
        status.has_design = (spec_dir / "design.md").exists()
        status.has_tasks = (spec_dir / "tasks.md").exists()

        # Parse tasks if tasks.md exists
        if status.has_tasks:
            tasks = self._parse_tasks(spec_name, spec_dir / "tasks.md")
            status.tasks = tasks
            status.total_tasks = len([t for t in tasks if not t.is_subtask])
            status.completed_tasks = len([t for t in tasks if t.is_complete and not t.is_subtask])
            status.incomplete_tasks = status.total_tasks - status.completed_tasks

            # Collect incomplete tasks
            self.all_incomplete_tasks.extend([t for t in tasks if not t.is_complete])

        return status

    def _parse_tasks(self, spec_name: str, tasks_file: Path) -> list[Task]:
        """Parse tasks from a tasks.md file."""
        tasks = []

        try:
            with open(tasks_file, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {tasks_file}: {e}")
            return tasks

        for line_num, line in enumerate(lines, 1):
            # Match task pattern: - [x] or - [ ] followed by task ID and title
            # Pattern: - [x] 1.1 Task Title or - [ ] 1.1 Task Title
            match = re.match(r'^\s*-\s+\[([x\s-])\]\s+(\d+(?:\.\d+)*)\s+(.+)$', line)

            if match:
                is_complete = match.group(1).lower() == 'x'
                task_id = match.group(2)
                title = match.group(3).strip()

                # Determine if this is a subtask (has more than 2 levels: 1.1.1)
                is_subtask = len(task_id.split('.')) > 2
                parent_task_id = None
                if is_subtask:
                    # Parent is the first two levels
                    parent_parts = task_id.split('.')[:2]
                    parent_task_id = '.'.join(parent_parts)

                task = Task(
                    spec_name=spec_name,
                    task_id=task_id,
                    title=title,
                    is_complete=is_complete,
                    is_subtask=is_subtask,
                    parent_task_id=parent_task_id,
                    line_number=line_num
                )
                tasks.append(task)

        return tasks

    def find_incomplete_tasks(self) -> list[Task]:
        """Find all incomplete tasks across all specs."""
        return sorted(
            self.all_incomplete_tasks,
            key=lambda t: (t.spec_name, t.task_id)
        )

    def generate_master_task_list(self) -> str:
        """Generate master task list markdown."""
        output = []
        output.append("# Master Task List: Ecosystem-Wide Architectural Refactoring")
        output.append("")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")

        # Summary section
        output.append("## Summary")
        output.append("")

        total_specs = len(self.specs)
        complete_specs = len([s for s in self.specs.values() if s.is_complete])
        incomplete_specs = total_specs - complete_specs

        total_tasks = sum(s.total_tasks for s in self.specs.values())
        completed_tasks = sum(s.completed_tasks for s in self.specs.values())
        incomplete_tasks = total_tasks - completed_tasks

        output.append(f"- **Total Specs**: {total_specs}")
        output.append(f"  - Completed: {complete_specs}")
        output.append(f"  - In Progress: {incomplete_specs}")
        output.append(f"- **Total Tasks**: {total_tasks}")
        output.append(f"  - Completed: {completed_tasks}")
        output.append(f"  - Incomplete: {incomplete_tasks}")
        output.append(f"- **Overall Completion**: {(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "- **Overall Completion**: 0%")
        output.append("")

        # Spec status overview
        output.append("## Spec Status Overview")
        output.append("")

        for spec_name in sorted(self.specs.keys()):
            spec = self.specs[spec_name]
            status_icon = "✅" if spec.is_complete else "🔄"
            completion = f"{spec.completion_percentage:.0f}%" if spec.total_tasks > 0 else "N/A"
            output.append(f"### {status_icon} {spec_name}")
            output.append(f"- **Status**: {'Complete' if spec.is_complete else 'In Progress'}")
            output.append(f"- **Completion**: {completion} ({spec.completed_tasks}/{spec.total_tasks})")
            output.append(f"- **Files**: requirements.md {'✓' if spec.has_requirements else '✗'}, design.md {'✓' if spec.has_design else '✗'}, tasks.md {'✓' if spec.has_tasks else '✗'}")
            output.append("")

        # Incomplete tasks by spec
        output.append("## Incomplete Tasks by Spec")
        output.append("")

        # Group incomplete tasks by spec
        tasks_by_spec = {}
        for task in self.find_incomplete_tasks():
            if task.spec_name not in tasks_by_spec:
                tasks_by_spec[task.spec_name] = []
            tasks_by_spec[task.spec_name].append(task)

        for spec_name in sorted(tasks_by_spec.keys()):
            spec = self.specs[spec_name]
            tasks = tasks_by_spec[spec_name]

            # Count main tasks vs subtasks
            main_tasks = [t for t in tasks if not t.is_subtask]

            output.append(f"### {spec_name}")
            output.append(f"**Incomplete: {len(main_tasks)} main tasks**")
            output.append("")

            # Group by main task
            for main_task in sorted(main_tasks, key=lambda t: t.task_id):
                output.append(f"#### {main_task.task_id} {main_task.title}")
                output.append("")

                # Find subtasks for this main task
                subtasks = [t for t in tasks if t.parent_task_id == main_task.task_id]

                if subtasks:
                    output.append("**Subtasks:**")
                    for subtask in sorted(subtasks, key=lambda t: t.task_id):
                        output.append(f"- [ ] {subtask.task_id} {subtask.title}")
                    output.append("")
                else:
                    output.append("- [ ] No subtasks defined")
                    output.append("")

            output.append("")

        # Prioritization guide
        output.append("## Prioritization Guide")
        output.append("")
        output.append("Tasks are organized by spec and should be executed in the following order:")
        output.append("")

        # Determine priority based on spec dependencies
        priority_order = [
            "ecosystem-architectural-refactoring",
            "core-logic-consolidation-and-app-restructure",
            "phase-2-website-sync-completion",
            "django-refactoring",
            "finalize-refactor",
            "phase-3-production-deployment",
            "ctc-research-deployment-verification",
        ]

        for i, spec_name in enumerate(priority_order, 1):
            if spec_name in self.specs:
                spec = self.specs[spec_name]
                if spec.incomplete_tasks > 0:
                    output.append(f"{i}. **{spec_name}** ({spec.incomplete_tasks} incomplete tasks)")

        output.append("")

        return "\n".join(output)


def main():
    """Main entry point."""
    tracker = SpecStatusTracker()

    # Scan all specs
    print("Scanning specs...")
    specs = tracker.scan_specs()

    if not specs:
        print("No specs found")
        return

    # Print summary
    print(f"\nFound {len(specs)} specs:")
    for spec in sorted(specs, key=lambda s: s.name):
        status = "✅ Complete" if spec.is_complete else f"🔄 In Progress ({spec.completion_percentage:.0f}%)"
        print(f"  {spec.name}: {status}")

    # Generate master task list
    print("\nGenerating master task list...")
    master_list = tracker.generate_master_task_list()

    # Write to file
    output_file = Path("MASTER_TASK_LIST.md")
    with open(output_file, 'w') as f:
        f.write(master_list)

    print(f"✓ Master task list written to {output_file}")

    # Print incomplete tasks summary
    incomplete = tracker.find_incomplete_tasks()
    print(f"\nTotal incomplete tasks: {len(incomplete)}")


if __name__ == "__main__":
    main()
