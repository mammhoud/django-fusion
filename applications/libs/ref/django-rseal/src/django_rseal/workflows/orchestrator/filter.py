"""Task filtering and querying."""

from typing import Any, Dict, List

from .models import Task, TaskStatus


class TaskFilter:
    """Filters and queries tasks."""

    def __init__(self, tasks: List[Task]):
        """Initialize the filter."""
        self.tasks = tasks
        self.current_results = tasks

    def by_category(self, category: str) -> "TaskFilter":
        """Filter by category."""
        self.current_results = [t for t in self.current_results if t.category == category]
        return self

    def by_status(self, status: TaskStatus) -> "TaskFilter":
        """Filter by status."""
        if isinstance(status, str):
            status = TaskStatus(status)
        self.current_results = [t for t in self.current_results if t.status == status]
        return self

    def by_spec(self, spec_name: str) -> "TaskFilter":
        """Filter by spec name."""
        self.current_results = [t for t in self.current_results if t.spec_name == spec_name]
        return self

    def by_keywords(self, keywords: str) -> "TaskFilter":
        """Filter by keywords in description."""
        keywords_lower = keywords.lower()
        self.current_results = [
            t for t in self.current_results
            if keywords_lower in t.description.lower()
        ]
        return self

    def by_requirements(self, requirement_id: str) -> "TaskFilter":
        """Filter by requirement traceability."""
        self.current_results = [
            t for t in self.current_results
            if requirement_id in t.requirements_traceability
        ]
        return self

    def with_pbt(self) -> "TaskFilter":
        """Filter to only tasks with PBT specifications."""
        self.current_results = [
            t for t in self.current_results
            if t.pbt_specification is not None
        ]
        return self

    def with_dependencies(self) -> "TaskFilter":
        """Filter to only tasks with dependencies."""
        self.current_results = [
            t for t in self.current_results
            if t.dependencies
        ]
        return self

    def sort_by_status(self, reverse: bool = False) -> "TaskFilter":
        """Sort by status priority."""
        status_priority = {
            TaskStatus.COMPLETED: 0,
            TaskStatus.IN_PROGRESS: 1,
            TaskStatus.QUEUED: 2,
            TaskStatus.NOT_STARTED: 3,
        }
        self.current_results.sort(
            key=lambda t: status_priority.get(t.status, 999),
            reverse=reverse,
        )
        return self

    def sort_by_description(self, reverse: bool = False) -> "TaskFilter":
        """Sort by description."""
        self.current_results.sort(
            key=lambda t: t.description,
            reverse=reverse,
        )
        return self

    def sort_by_id(self, reverse: bool = False) -> "TaskFilter":
        """Sort by task ID."""
        self.current_results.sort(
            key=lambda t: t.id,
            reverse=reverse,
        )
        return self

    def paginate(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Paginate results."""
        total = len(self.current_results)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
            "results": self.current_results[start:end],
        }

    def get_results(self) -> List[Task]:
        """Get current results."""
        return self.current_results

    def reset(self) -> "TaskFilter":
        """Reset to all tasks."""
        self.current_results = self.tasks
        return self

    def count(self) -> int:
        """Count current results."""
        return len(self.current_results)


class TaskQuery:
    """Complex task queries."""

    def __init__(self, tasks: List[Task]):
        """Initialize the query builder."""
        self.tasks = tasks

    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Task]:
        """
        Find tasks by multiple criteria.

        Supported criteria:
        - category: str
        - status: TaskStatus or str
        - spec_name: str
        - keywords: str
        - requirement_id: str
        - has_pbt: bool
        - has_dependencies: bool
        """
        results = self.tasks

        if "category" in criteria:
            results = [t for t in results if t.category == criteria["category"]]

        if "status" in criteria:
            status = criteria["status"]
            if isinstance(status, str):
                status = TaskStatus(status)
            results = [t for t in results if t.status == status]

        if "spec_name" in criteria:
            results = [t for t in results if t.spec_name == criteria["spec_name"]]

        if "keywords" in criteria:
            keywords = criteria["keywords"].lower()
            results = [
                t for t in results
                if keywords in t.description.lower()
            ]

        if "requirement_id" in criteria:
            req_id = criteria["requirement_id"]
            results = [
                t for t in results
                if req_id in t.requirements_traceability
            ]

        if criteria.get("has_pbt"):
            results = [t for t in results if t.pbt_specification is not None]

        if criteria.get("has_dependencies"):
            results = [t for t in results if t.dependencies]

        return results

    def find_blocking_tasks(self, task_id: str) -> List[Task]:
        """Find tasks that block a given task."""
        blocking = []
        for task in self.tasks:
            if task_id in task.dependencies:
                blocking.append(task)
        return blocking

    def find_blocked_tasks(self, task_id: str) -> List[Task]:
        """Find tasks blocked by a given task."""
        blocked = []
        for task in self.tasks:
            if task_id in task.dependencies:
                blocked.append(task)
        return blocked

    def find_dependency_chain(self, task_id: str) -> List[str]:
        """Find the dependency chain for a task."""
        chain = [task_id]
        current_task = None

        for task in self.tasks:
            if task.id == task_id:
                current_task = task
                break

        if not current_task:
            return chain

        for dep_id in current_task.dependencies:
            chain.extend(self.find_dependency_chain(dep_id))

        return chain

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies."""
        cycles = []

        for task in self.tasks:
            visited = set()
            if self._has_cycle(task.id, visited):
                cycles.append(list(visited))

        return cycles

    def _has_cycle(self, task_id: str, visited: set) -> bool:
        """Check if a task has circular dependencies."""
        if task_id in visited:
            return True

        visited.add(task_id)

        for task in self.tasks:
            if task.id == task_id:
                for dep_id in task.dependencies:
                    if self._has_cycle(dep_id, visited.copy()):
                        return True

        return False

    def get_execution_order(self) -> List[str]:
        """Get topological sort of tasks (execution order)."""
        # Simple topological sort
        visited = set()
        order = []

        def visit(task_id: str):
            if task_id in visited:
                return
            visited.add(task_id)

            for task in self.tasks:
                if task.id == task_id:
                    for dep_id in task.dependencies:
                        visit(dep_id)
                    order.append(task_id)
                    break

        for task in self.tasks:
            visit(task.id)

        return order
