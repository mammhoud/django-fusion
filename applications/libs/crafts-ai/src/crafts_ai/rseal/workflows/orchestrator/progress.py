"""Spec status and progress tracking."""

from datetime import datetime
from typing import Any, Dict, List

from .models import Spec, TaskStatus


class ProgressTracker:
    """Tracks spec progress and status."""

    def __init__(self):
        """Initialize the progress tracker."""
        self.specs: Dict[str, Dict[str, Spec]] = {}
        self.status_history: List[Dict[str, Any]] = []

    def add_spec(self, spec: Spec) -> None:
        """Add a spec to tracking."""
        if spec.category not in self.specs:
            self.specs[spec.category] = {}
        self.specs[spec.category][spec.spec_name] = spec

    def calculate_progress(self, spec: Spec) -> float:
        """
        Calculate spec progress as (completed_tasks / total_tasks) * 100.

        Returns:
            Progress percentage (0-100)
        """
        if not spec.tasks:
            return 0.0

        completed = sum(1 for t in spec.tasks if t.status == TaskStatus.COMPLETED)
        return (completed / len(spec.tasks)) * 100

    def update_spec_progress(self, category: str, spec_name: str) -> float:
        """Update and return spec progress."""
        spec = self.specs.get(category, {}).get(spec_name)

        if not spec:
            return 0.0

        progress = self.calculate_progress(spec)
        spec.progress = progress
        spec.last_updated = datetime.now()

        return progress

    def get_spec_status(self, category: str, spec_name: str) -> str:
        """Get spec status based on progress."""
        progress = self.update_spec_progress(category, spec_name)

        if progress == 0:
            return "not_started"
        elif progress == 100:
            return "complete"
        else:
            return "in_progress"

    def get_category_summary(self, category: str) -> Dict[str, Any]:
        """Get summary for a category."""
        specs = self.specs.get(category, {})

        if not specs:
            return {
                "category": category,
                "total_specs": 0,
                "complete_specs": 0,
                "in_progress_specs": 0,
                "not_started_specs": 0,
                "average_progress": 0.0,
            }

        total_specs = len(specs)
        complete_specs = 0
        in_progress_specs = 0
        not_started_specs = 0
        total_progress = 0.0

        for spec in specs.values():
            progress = self.calculate_progress(spec)
            total_progress += progress

            if progress == 0:
                not_started_specs += 1
            elif progress == 100:
                complete_specs += 1
            else:
                in_progress_specs += 1

        return {
            "category": category,
            "total_specs": total_specs,
            "complete_specs": complete_specs,
            "in_progress_specs": in_progress_specs,
            "not_started_specs": not_started_specs,
            "average_progress": total_progress / total_specs if total_specs > 0 else 0.0,
        }

    def get_overall_summary(self) -> Dict[str, Any]:
        """Get overall project summary."""
        total_specs = 0
        complete_specs = 0
        in_progress_specs = 0
        not_started_specs = 0
        total_progress = 0.0

        for category_specs in self.specs.values():
            for spec in category_specs.values():
                total_specs += 1
                progress = self.calculate_progress(spec)
                total_progress += progress

                if progress == 0:
                    not_started_specs += 1
                elif progress == 100:
                    complete_specs += 1
                else:
                    in_progress_specs += 1

        return {
            "total_specs": total_specs,
            "complete_specs": complete_specs,
            "in_progress_specs": in_progress_specs,
            "not_started_specs": not_started_specs,
            "average_progress": total_progress / total_specs if total_specs > 0 else 0.0,
            "categories": {
                cat: self.get_category_summary(cat)
                for cat in self.specs.keys()
            },
        }

    def get_spec_progress_report(self, category: str, spec_name: str) -> Dict[str, Any]:
        """Get detailed progress report for a spec."""
        spec = self.specs.get(category, {}).get(spec_name)

        if not spec:
            return {}

        progress = self.calculate_progress(spec)
        tasks_by_status = {
            "not_started": sum(1 for t in spec.tasks if t.status == TaskStatus.NOT_STARTED),
            "queued": sum(1 for t in spec.tasks if t.status == TaskStatus.QUEUED),
            "in_progress": sum(1 for t in spec.tasks if t.status == TaskStatus.IN_PROGRESS),
            "completed": sum(1 for t in spec.tasks if t.status == TaskStatus.COMPLETED),
        }

        return {
            "category": category,
            "spec_name": spec_name,
            "total_tasks": len(spec.tasks),
            "completed_tasks": tasks_by_status["completed"],
            "progress_percentage": progress,
            "status": self.get_spec_status(category, spec_name),
            "tasks_by_status": tasks_by_status,
            "last_updated": spec.last_updated.isoformat(),
            "owner": spec.owner,
        }

    def log_status_change(
        self,
        category: str,
        spec_name: str,
        old_status: str,
        new_status: str,
    ) -> None:
        """Log a status change."""
        self.status_history.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "spec_name": spec_name,
            "old_status": old_status,
            "new_status": new_status,
        })

    def get_status_history(self) -> List[Dict[str, Any]]:
        """Get status change history."""
        return self.status_history

    def get_incomplete_specs(self) -> List[Dict[str, Any]]:
        """Get list of incomplete specs."""
        incomplete = []

        for category, specs in self.specs.items():
            for spec_name, spec in specs.items():
                progress = self.calculate_progress(spec)
                if progress < 100:
                    incomplete.append({
                        "category": category,
                        "spec_name": spec_name,
                        "progress": progress,
                        "missing_tasks": sum(
                            1 for t in spec.tasks
                            if t.status != TaskStatus.COMPLETED
                        ),
                    })

        return incomplete
