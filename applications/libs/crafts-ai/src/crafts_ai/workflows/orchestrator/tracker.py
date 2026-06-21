"""Task tracking and management."""

from typing import Any, Dict, List, Optional

from .models import Spec, Task, TaskStatus


class TaskTracker:
    """Tracks tasks by category and status."""

    def __init__(self):
        """Initialize the tracker."""
        self.specs: Dict[str, Dict[str, Spec]] = {}
        self.tasks: List[Task] = []

    def add_spec(self, spec: Spec) -> None:
        """Add a spec to tracking."""
        if spec.category not in self.specs:
            self.specs[spec.category] = {}
        self.specs[spec.category][spec.spec_name] = spec
        self.tasks.extend(spec.tasks)

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get all tasks in a category."""
        return [t for t in self.tasks if t.category == category]

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [t for t in self.tasks if t.status == status]

    def get_tasks_by_spec(self, category: str, spec_name: str) -> List[Task]:
        """Get all tasks for a specific spec."""
        return [
            t for t in self.tasks
            if t.spec_category == category and t.spec_name == spec_name
        ]

    def filter_tasks(self, filters: Dict[str, Any]) -> List[Task]:
        """
        Filter tasks by criteria.

        Supported filters:
        - category: str
        - status: TaskStatus
        - spec_name: str
        - keywords: str (search in description)
        """
        result = self.tasks

        if "category" in filters:
            result = [t for t in result if t.category == filters["category"]]

        if "status" in filters:
            status = filters["status"]
            if isinstance(status, str):
                status = TaskStatus(status)
            result = [t for t in result if t.status == status]

        if "spec_name" in filters:
            result = [t for t in result if t.spec_name == filters["spec_name"]]

        if "keywords" in filters:
            keywords = filters["keywords"].lower()
            result = [t for t in result if keywords in t.description.lower()]

        return result

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> None:
        """Update task status."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = new_status
                break

    def calculate_spec_progress(self, category: str, spec_name: str) -> float:
        """
        Calculate spec progress as (completed_tasks / total_tasks) * 100.

        Returns:
            Progress percentage (0-100)
        """
        tasks = self.get_tasks_by_spec(category, spec_name)

        if not tasks:
            return 0.0

        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        return (completed / len(tasks)) * 100

    def get_spec_status(self, category: str, spec_name: str) -> str:
        """Get spec status based on task completion."""
        progress = self.calculate_spec_progress(category, spec_name)

        if progress == 0:
            return "not_started"
        elif progress == 100:
            return "complete"
        else:
            return "in_progress"

    def add_task_dependency(self, task_id: str, dependency_id: str) -> None:
        """Add a task dependency."""
        for task in self.tasks:
            if task.id == task_id:
                if dependency_id not in task.dependencies:
                    task.dependencies.append(dependency_id)
                break

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_category_stats(self, category: str) -> Dict[str, int]:
        """Get statistics for a category."""
        tasks = self.get_tasks_by_category(category)

        return {
            "total": len(tasks),
            "not_started": sum(1 for t in tasks if t.status == TaskStatus.NOT_STARTED),
            "queued": sum(1 for t in tasks if t.status == TaskStatus.QUEUED),
            "in_progress": sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        return {
            "total_tasks": len(self.tasks),
            "not_started": sum(1 for t in self.tasks if t.status == TaskStatus.NOT_STARTED),
            "queued": sum(1 for t in self.tasks if t.status == TaskStatus.QUEUED),
            "in_progress": sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS),
            "completed": sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED),
            "categories": {
                cat: self.get_category_stats(cat)
                for cat in self.specs.keys()
            },
        }

    def get_spec_progress_report(self, category: str, spec_name: str) -> Dict[str, Any]:
        """Get progress report for a spec."""
        tasks = self.get_tasks_by_spec(category, spec_name)
        progress = self.calculate_spec_progress(category, spec_name)

        return {
            "category": category,
            "spec_name": spec_name,
            "total_tasks": len(tasks),
            "completed_tasks": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            "progress_percentage": progress,
            "status": self.get_spec_status(category, spec_name),
            "tasks_by_status": {
                "not_started": sum(1 for t in tasks if t.status == TaskStatus.NOT_STARTED),
                "queued": sum(1 for t in tasks if t.status == TaskStatus.QUEUED),
                "in_progress": sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
                "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            },
        }
