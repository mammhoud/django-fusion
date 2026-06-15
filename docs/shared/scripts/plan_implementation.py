#!/usr/bin/env python3
"""
Implementation Planner for Ecosystem-Wide Architectural Refactoring

Reads MASTER_TASK_LIST.md and produces IMPLEMENTATION_PLAN.md with:
- All phases and their tasks
- Task dependencies in topological order
- Effort estimates for each task
- Rollback points for major phases
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class Task:
    """Represents a single task with dependencies and metadata."""
    id: str
    title: str
    phase: int
    subtasks: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    effort_hours: float = 0.0
    rollback_point: bool = False
    description: str = ""

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.id == other.id
        return self.id == other


@dataclass
class Phase:
    """Represents a phase of the implementation plan."""
    number: int
    name: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    rollback_point: str = ""
    estimated_hours: float = 0.0

    def calculate_total_effort(self):
        """Calculate total effort for all tasks in phase."""
        self.estimated_hours = sum(t.effort_hours for t in self.tasks)


class ImplementationPlanner:
    """
    Builds a complete implementation plan with dependency ordering and validation checkpoints.
    """

    # Task effort estimates (in hours)
    EFFORT_ESTIMATES = {
        # Phase 1: Analysis and Planning
        "1.1.1": 8.0,   # Write DuplicationAnalyzer
        "1.1.2": 4.0,   # Run analyzer
        "1.1.3": 3.0,   # Categorize duplicates
        "1.1.4": 2.0,   # Write report
        "1.2.1": 6.0,   # Write BoundaryChecker
        "1.2.2": 3.0,   # Run checker
        "1.2.3": 4.0,   # Write CircularDependencyDetector
        "1.2.4": 2.0,   # Run cycle detector
        "1.3.1": 4.0,   # Write SpecStatusTracker
        "1.3.2": 2.0,   # Run tracker
        "1.4.1": 6.0,   # Write ImplementationPlanner
        "1.4.2": 3.0,   # Produce IMPLEMENTATION_PLAN.md
        "1.4.3": 1.0,   # Create git tags
        "1.4.4": 2.0,   # Write BACKUP_LOG.md template

        # Phase 2: django_osoul extractions (simplified estimates)
        "2.1": 12.0,    # Extract handlers
        "2.2": 6.0,     # Extract managers
        "2.3": 4.0,     # Extract user/group managers
        "2.4": 8.0,     # Extract mixins
        "2.5": 6.0,     # Extract backends
        "2.6": 4.0,     # Extract adapters
        "2.7": 4.0,     # Extract services
        "2.8": 4.0,     # Extract middleware
        "2.9": 3.0,     # Extract validators
        "2.10": 3.0,    # Extract forms
        "2.11": 4.0,    # Extract UI components
        "2.12": 4.0,    # Extract contrib utilities
        "2.13": 6.0,    # Extract foundation models
        "2.14": 4.0,    # Boundary check

        # Phase 3: django_rseal extractions
        "3.1": 8.0,     # Extract Wagtail handlers
        "3.2": 8.0,     # Extract CartServiceBase
        "3.3": 6.0,     # Extract PersonServiceBase
        "3.4": 6.0,     # Extract MessageServiceBase
        "3.5": 4.0,     # Extract FormSubmissionService
        "3.6": 4.0,     # Extract email components
        "3.7": 6.0,     # Extract Wagtail blocks
        "3.8": 4.0,     # Extract snippets
        "3.9": 3.0,     # Extract hooks
        "3.10": 4.0,    # Extract admin customizations
        "3.11": 3.0,    # Extract privacy middleware
        "3.12": 3.0,    # Extract cache utilities
        "3.13": 3.0,    # Extract signals
        "3.14": 3.0,    # Extract debug tools
        "3.15": 3.0,    # Extract email config
        "3.16": 4.0,    # Extract orchestrator
        "3.17": 4.0,    # Boundary check

        # Phase 4: django_grep
        "4.1": 4.0,     # Create BaseTestCase
        "4.2": 6.0,     # Create factories
        "4.3": 4.0,     # Create fixtures
        "4.4": 3.0,     # Create assertions
        "4.5": 3.0,     # Create test mixins
        "4.6": 2.0,     # Register pytest plugin
        "4.7": 6.0,     # Create health check system
        "4.8": 12.0,    # Migrate tests
        "4.9": 6.0,     # Move seeder infrastructure
        "4.10": 4.0,    # Boundary check

        # Phase 5: nawaai
        "5.1": 8.0,     # Audit and remove Django imports

        # Phase 6: Domain restructuring
        "6.1": 8.0,     # Rename handlers to accounts (ctc)
        "6.2": 8.0,     # Rename handlers to accounts (structa)
        "6.3": 6.0,     # Rename LMS to lms (ctc)
        "6.4": 6.0,     # Rename LMS to alliance (structa)
        "6.5": 8.0,     # Rename pages to content
        "6.6": 12.0,    # Enforce sub-module layout
        "6.7": 8.0,     # Eliminate cross-domain leakage
        "6.8": 8.0,     # Eliminate circular dependencies
        "6.9": 4.0,     # Commit domain restructuring

        # Phase 7: Project simplification
        "7.1": 6.0,     # Audit thin layer violations
        "7.2": 8.0,     # Convert services to thin subclasses
        "7.3": 4.0,     # Remove duplicate managers
        "7.4": 4.0,     # Remove duplicate mixins
        "7.5": 3.0,     # Remove duplicate forms
        "7.6": 3.0,     # Remove duplicate middleware
        "7.7": 4.0,     # Verify structural patterns
        "7.8": 4.0,     # Unify settings structure
        "7.9": 4.0,     # Commit project simplification

        # Phase 8: Naming conventions
        "8.1": 6.0,     # Enforce snake_case modules
        "8.2": 6.0,     # Enforce PascalCase classes
        "8.3": 6.0,     # Enforce snake_case functions
        "8.4": 4.0,     # Verify naming conventions
        "8.5": 8.0,     # Maintain CHANGELOG files

        # Phase 9: Templates and static files
        "9.1": 6.0,     # Verify no templates in packages
        "9.2": 4.0,     # Verify template structure
        "9.3": 4.0,     # Update template references

        # Phase 10: Dependencies
        "10.1": 4.0,    # Analyze dependencies
        "10.2": 6.0,    # Unify versions
        "10.3": 4.0,    # Remove unused dependencies
        "10.4": 3.0,    # Ensure explicit declarations
        "10.5": 3.0,    # Update lock files

        # Phase 11: Recovery and merging
        "11.1": 6.0,    # Scan git history
        "11.2": 12.0,   # Recover and reintegrate code
        "11.3": 4.0,    # Document unrecoverable code
        "11.4": 6.0,    # Analyze branches
        "11.5": 12.0,   # Merge improvements

        # Phase 12: Parsers and serializers
        "12.1": 4.0,    # Identify parsers
        "12.2": 6.0,    # Create pretty printers
        "12.3": 8.0,    # Implement round-trip tests

        # Phase 13: CI and automation
        "13.1": 4.0,    # Create importlinter config
        "13.2": 6.0,    # Create GitHub Actions workflow
        "13.3": 2.0,    # Verify CI passes

        # Phase 14: Documentation
        "14.1": 6.0,    # Create ARCHITECTURE.md
        "14.2": 4.0,    # Create MIGRATION_GUIDE.md
        "14.3": 4.0,    # Write django_osoul README
        "14.4": 4.0,    # Write django_rseal README
        "14.5": 4.0,    # Write django_grep README
        "14.6": 3.0,    # Write nawaai README
        "14.7": 4.0,    # Write ctc-research README
        "14.8": 4.0,    # Write structa.cloud README
        "14.9": 4.0,    # Update docstrings
        "14.10": 2.0,   # Organize specs

        # Phase 15: Migration safety
        "15.1": 4.0,    # Validate migrations
        "15.2": 8.0,    # Test migration reversal
        "15.3": 4.0,    # Verify Docker migrations

        # Phase 16: Final validation
        "16.1": 2.0,    # Verify zero duplication
        "16.2": 2.0,    # Verify zero boundary violations
        "16.3": 4.0,    # Run full test suite
        "16.4": 4.0,    # Verify Docker health
        "16.5": 2.0,    # Verify zero import errors
        "16.6": 2.0,    # Verify migrations applied
        "16.7": 2.0,    # Verify naming conventions
        "16.8": 2.0,    # Verify template organization
        "16.9": 2.0,    # Verify specs complete
        "16.10": 4.0,   # Generate COMPLETION_REPORT
        "16.11": 2.0,   # Final commit and tag
    }

    # Task dependencies (task_id -> set of task_ids it depends on)
    DEPENDENCIES = {
        # Phase 1 dependencies
        "1.2": {"1.1"},      # Boundary check needs duplication analysis first
        "1.3": {"1.1", "1.2"},  # Spec tracking needs analysis
        "1.4": {"1.1", "1.2", "1.3"},  # Planning needs all analysis

        # Phase 2 dependencies (all depend on Phase 1 completion)
        "2.1": {"1.4"},
        "2.2": {"2.1"},
        "2.3": {"2.2"},
        "2.4": {"2.3"},
        "2.5": {"2.4"},
        "2.6": {"2.5"},
        "2.7": {"2.6"},
        "2.8": {"2.7"},
        "2.9": {"2.8"},
        "2.10": {"2.9"},
        "2.11": {"2.10"},
        "2.12": {"2.11"},
        "2.13": {"2.12"},
        "2.14": {"2.13"},

        # Phase 3 depends on Phase 2
        "3.1": {"2.14"},
        "3.2": {"3.1"},
        "3.3": {"3.2"},
        "3.4": {"3.3"},
        "3.5": {"3.4"},
        "3.6": {"3.5"},
        "3.7": {"3.6"},
        "3.8": {"3.7"},
        "3.9": {"3.8"},
        "3.10": {"3.9"},
        "3.11": {"3.10"},
        "3.12": {"3.11"},
        "3.13": {"3.12"},
        "3.14": {"3.13"},
        "3.15": {"3.14"},
        "3.16": {"3.15"},
        "3.17": {"3.16"},

        # Phase 4 depends on Phase 3
        "4.1": {"3.17"},
        "4.2": {"4.1"},
        "4.3": {"4.2"},
        "4.4": {"4.3"},
        "4.5": {"4.4"},
        "4.6": {"4.5"},
        "4.7": {"4.6"},
        "4.8": {"4.7"},
        "4.9": {"4.8"},
        "4.10": {"4.9"},

        # Phase 5 depends on Phase 4
        "5.1": {"4.10"},

        # Phase 6 depends on Phase 5
        "6.1": {"5.1"},
        "6.2": {"6.1"},
        "6.3": {"6.2"},
        "6.4": {"6.3"},
        "6.5": {"6.4"},
        "6.6": {"6.5"},
        "6.7": {"6.6"},
        "6.8": {"6.7"},
        "6.9": {"6.8"},

        # Phase 7 depends on Phase 6
        "7.1": {"6.9"},
        "7.2": {"7.1"},
        "7.3": {"7.2"},
        "7.4": {"7.3"},
        "7.5": {"7.4"},
        "7.6": {"7.5"},
        "7.7": {"7.6"},
        "7.8": {"7.7"},
        "7.9": {"7.8"},

        # Phase 8 depends on Phase 7
        "8.1": {"7.9"},
        "8.2": {"8.1"},
        "8.3": {"8.2"},
        "8.4": {"8.3"},
        "8.5": {"8.4"},

        # Phase 9 depends on Phase 8
        "9.1": {"8.5"},
        "9.2": {"9.1"},
        "9.3": {"9.2"},

        # Phase 10 depends on Phase 9
        "10.1": {"9.3"},
        "10.2": {"10.1"},
        "10.3": {"10.2"},
        "10.4": {"10.3"},
        "10.5": {"10.4"},

        # Phase 11 depends on Phase 10
        "11.1": {"10.5"},
        "11.2": {"11.1"},
        "11.3": {"11.2"},
        "11.4": {"11.3"},
        "11.5": {"11.4"},

        # Phase 12 depends on Phase 11
        "12.1": {"11.5"},
        "12.2": {"12.1"},
        "12.3": {"12.2"},

        # Phase 13 depends on Phase 12
        "13.1": {"12.3"},
        "13.2": {"13.1"},
        "13.3": {"13.2"},

        # Phase 14 depends on Phase 13
        "14.1": {"13.3"},
        "14.2": {"14.1"},
        "14.3": {"14.2"},
        "14.4": {"14.3"},
        "14.5": {"14.4"},
        "14.6": {"14.5"},
        "14.7": {"14.6"},
        "14.8": {"14.7"},
        "14.9": {"14.8"},
        "14.10": {"14.9"},

        # Phase 15 depends on Phase 14
        "15.1": {"14.10"},
        "15.2": {"15.1"},
        "15.3": {"15.2"},

        # Phase 16 depends on Phase 15
        "16.1": {"15.3"},
        "16.2": {"16.1"},
        "16.3": {"16.2"},
        "16.4": {"16.3"},
        "16.5": {"16.4"},
        "16.6": {"16.5"},
        "16.7": {"16.6"},
        "16.8": {"16.7"},
        "16.9": {"16.8"},
        "16.10": {"16.9"},
        "16.11": {"16.10"},
    }

    PHASE_DESCRIPTIONS = {
        1: "Analysis and Planning",
        2: "django_osoul — Extract Pure Django/Python Foundation",
        3: "django_rseal — Extract Wagtail + Automation Logic",
        4: "django_grep — Extract Testing Infrastructure and Health Checks",
        5: "nawaai — Verify Pure Python Boundary",
        6: "Domain Restructuring — App Renames and Module Reorganization",
        7: "Project Simplification — Thin Layer Pattern",
        8: "Cross-Project Consistency and Naming Conventions",
        9: "Template Strategy and Static Files",
        10: "Dependency Alignment and Version Unification",
        11: "Code Recovery and Branch Merging",
        12: "Parser and Serializer Requirements",
        13: "Continuous Integration and Automated Validation",
        14: "Documentation Organization and Spec Completion",
        15: "Migration Safety and Reversibility",
        16: "Final Validation and Deliverables",
    }

    ROLLBACK_POINTS = {
        1: "rollback-phase-1-start",
        2: "rollback-phase-2-start",
        3: "rollback-phase-3-start",
        4: "rollback-phase-4-start",
        5: "rollback-phase-5-start",
        6: "rollback-phase-6-start",
        7: "rollback-phase-7-start",
        8: "rollback-phase-8-start",
        9: "rollback-phase-9-start",
        10: "rollback-phase-10-start",
        11: "rollback-phase-11-start",
        12: "rollback-phase-12-start",
        13: "rollback-phase-13-start",
        14: "rollback-phase-14-start",
        15: "rollback-phase-15-start",
        16: "rollback-phase-16-start",
    }

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.phases: Dict[int, Phase] = {}

    def build_plan(self) -> List[Phase]:
        """Build the complete implementation plan."""
        self._create_tasks()
        self._create_phases()
        self._topological_sort()
        return [self.phases[i] for i in sorted(self.phases.keys())]

    def _create_tasks(self):
        """Create all tasks from EFFORT_ESTIMATES."""
        for task_id, effort in self.EFFORT_ESTIMATES.items():
            phase = int(task_id.split(".")[0])
            dependencies = self.DEPENDENCIES.get(task_id, set())

            self.tasks[task_id] = Task(
                id=task_id,
                title=f"Task {task_id}",
                phase=phase,
                effort_hours=effort,
                dependencies=dependencies,
            )

    def _create_phases(self):
        """Create phases and assign tasks."""
        for phase_num in range(1, 17):
            phase = Phase(
                number=phase_num,
                name=self.PHASE_DESCRIPTIONS[phase_num],
                description=f"Phase {phase_num}: {self.PHASE_DESCRIPTIONS[phase_num]}",
                rollback_point=self.ROLLBACK_POINTS[phase_num],
            )

            # Add tasks for this phase
            for task_id, task in self.tasks.items():
                if task.phase == phase_num:
                    phase.tasks.append(task)

            phase.calculate_total_effort()
            self.phases[phase_num] = phase

    def _topological_sort(self):
        """Sort tasks within each phase by dependencies."""
        for phase in self.phases.values():
            sorted_tasks = self._sort_tasks_by_dependency(phase.tasks)
            phase.tasks = sorted_tasks

    def _sort_tasks_by_dependency(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks topologically by dependencies."""
        sorted_list = []
        visited = set()
        visiting = set()

        def visit(task: Task):
            if task.id in visited:
                return
            if task.id in visiting:
                return  # Cycle detected, skip

            visiting.add(task.id)

            # Visit dependencies first
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.phase == task.phase:  # Only sort within phase
                        visit(dep_task)

            visiting.remove(task.id)
            visited.add(task.id)
            sorted_list.append(task)

        for task in tasks:
            visit(task)

        return sorted_list

    def generate_markdown(self) -> str:
        """Generate IMPLEMENTATION_PLAN.md content."""
        phases = self.build_plan()

        lines = [
            "# Implementation Plan: Ecosystem-Wide Architectural Refactoring",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
            f"- **Total Phases**: {len(phases)}",
            f"- **Total Tasks**: {sum(len(p.tasks) for p in phases)}",
            f"- **Total Estimated Effort**: {sum(p.estimated_hours for p in phases):.1f} hours",
            f"- **Estimated Duration**: {sum(p.estimated_hours for p in phases) / 40:.1f} weeks (at 40 hrs/week)",
            "",
            "## Dependency Graph",
            "",
            "```",
            "Phase 1: Analysis and Planning",
            "  ↓",
            "Phase 2: django_osoul (Pure Django Foundation)",
            "  ↓",
            "Phase 3: django_rseal (Wagtail + Automation)",
            "  ↓",
            "Phase 4: django_grep (Testing Infrastructure)",
            "  ↓",
            "Phase 5: nawaai (Pure Python Boundary)",
            "  ↓",
            "Phase 6: Domain Restructuring (App Renames)",
            "  ↓",
            "Phase 7: Project Simplification (Thin Layers)",
            "  ↓",
            "Phase 8: Naming Conventions",
            "  ↓",
            "Phase 9: Templates and Static Files",
            "  ↓",
            "Phase 10: Dependency Alignment",
            "  ↓",
            "Phase 11: Code Recovery and Merging",
            "  ↓",
            "Phase 12: Parsers and Serializers",
            "  ↓",
            "Phase 13: CI and Automation",
            "  ↓",
            "Phase 14: Documentation",
            "  ↓",
            "Phase 15: Migration Safety",
            "  ↓",
            "Phase 16: Final Validation",
            "```",
            "",
            "## Validation Checkpoints",
            "",
            "After each phase, the following validations MUST pass:",
            "",
            "1. **Boundary Check**: `import-linter --config .importlinter` returns zero violations",
            "2. **Duplication Check**: `scripts/analyze_duplication.py --threshold 0.70` finds no new duplication",
            "3. **Test Suite**: All tests pass in all packages and projects",
            "4. **Import Check**: No ImportError or ModuleNotFoundError",
            "5. **Git Status**: All changes committed with descriptive messages",
            "",
            "## Rollback Strategy",
            "",
            "Before each phase, a git tag is created for recovery:",
            "",
        ]

        for phase_num in range(1, 17):
            lines.append(f"- `{self.ROLLBACK_POINTS[phase_num]}`: Before Phase {phase_num}")

        lines.extend([
            "",
            "To rollback to a previous phase:",
            "```bash",
            "git checkout <rollback-tag>",
            "git reset --hard <rollback-tag>",
            "```",
            "",
            "## Detailed Phase Plans",
            "",
        ])

        # Add detailed phase information
        for phase in phases:
            lines.extend(self._format_phase(phase))

        return "\n".join(lines)

    def _format_phase(self, phase: Phase) -> List[str]:
        """Format a single phase for markdown."""
        lines = [
            f"### Phase {phase.number}: {phase.name}",
            "",
            f"**Rollback Point**: `{phase.rollback_point}`",
            "",
            f"**Estimated Effort**: {phase.estimated_hours:.1f} hours",
            "",
            f"**Tasks**: {len(phase.tasks)}",
            "",
            "| Task ID | Title | Effort (hrs) | Dependencies |",
            "|---------|-------|-------------|--------------|",
        ]

        for task in phase.tasks:
            deps = ", ".join(sorted(task.dependencies)) if task.dependencies else "None"
            lines.append(
                f"| {task.id} | {task.title} | {task.effort_hours:.1f} | {deps} |"
            )

        lines.extend([
            "",
            "**Validation Checkpoints**:",
            "",
            "- [ ] All tasks completed",
            "- [ ] Boundary check passes",
            "- [ ] All tests pass",
            "- [ ] No import errors",
            "- [ ] Changes committed",
            "",
        ])

        return lines


def main():
    """Main entry point."""
    planner = ImplementationPlanner()
    markdown = planner.generate_markdown()

    # Write to file
    output_path = Path("IMPLEMENTATION_PLAN.md")
    output_path.write_text(markdown)

    print(f"✓ Generated {output_path}")
    print(f"  - {len(planner.tasks)} tasks across 16 phases")
    print(f"  - Total estimated effort: {sum(p.estimated_hours for p in planner.phases.values()):.1f} hours")


if __name__ == "__main__":
    main()
