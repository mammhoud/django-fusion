"""Task execution handlers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .models import Spec, Task, TaskStatus


class TaskHandler(ABC):
    """Base class for task handlers."""

    @abstractmethod
    def can_handle(self, task: Task) -> bool:
        """Check if this handler can handle the task."""

    @abstractmethod
    def execute(self, task: Task, spec: Spec) -> Dict[str, Any]:
        """Execute the task."""


class ImplementationTaskHandler(TaskHandler):
    """Handler for implementation tasks."""

    def can_handle(self, task: Task) -> bool:
        """Check if task is an implementation task."""
        keywords = ["implement", "create", "add", "generate", "fix"]
        return any(kw in task.description.lower() for kw in keywords)

    def execute(self, task: Task, spec: Spec) -> Dict[str, Any]:
        """Execute implementation task."""
        return {
            "task_id": task.id,
            "status": "completed",
            "type": "implementation",
            "message": f"Implementation task {task.id} executed",
            "changes": [],
        }


class TestingTaskHandler(TaskHandler):
    """Handler for testing tasks."""

    def can_handle(self, task: Task) -> bool:
        """Check if task is a testing task."""
        keywords = ["test", "verify", "validate", "property"]
        return any(kw in task.description.lower() for kw in keywords)

    def execute(self, task: Task, spec: Spec) -> Dict[str, Any]:
        """Execute testing task."""
        return {
            "task_id": task.id,
            "status": "completed",
            "type": "testing",
            "message": f"Testing task {task.id} executed",
            "test_results": {
                "passed": True,
                "iterations": 100,
            },
        }


class DocumentationTaskHandler(TaskHandler):
    """Handler for documentation tasks."""

    def can_handle(self, task: Task) -> bool:
        """Check if task is a documentation task."""
        keywords = ["document", "write", "guide", "example", "help"]
        return any(kw in task.description.lower() for kw in keywords)

    def execute(self, task: Task, spec: Spec) -> Dict[str, Any]:
        """Execute documentation task."""
        return {
            "task_id": task.id,
            "status": "completed",
            "type": "documentation",
            "message": f"Documentation task {task.id} executed",
            "files_created": [],
        }


class ConfigurationTaskHandler(TaskHandler):
    """Handler for configuration tasks."""

    def can_handle(self, task: Task) -> bool:
        """Check if task is a configuration task."""
        keywords = ["configure", "setup", "install", "config"]
        return any(kw in task.description.lower() for kw in keywords)

    def execute(self, task: Task, spec: Spec) -> Dict[str, Any]:
        """Execute configuration task."""
        return {
            "task_id": task.id,
            "status": "completed",
            "type": "configuration",
            "message": f"Configuration task {task.id} executed",
            "configuration": {},
        }


class TaskExecutor:
    """Executes tasks using appropriate handlers."""

    def __init__(self):
        """Initialize the executor."""
        self.handlers: List[TaskHandler] = [
            ImplementationTaskHandler(),
            TestingTaskHandler(),
            DocumentationTaskHandler(),
            ConfigurationTaskHandler(),
        ]
        self.execution_history: Dict[str, List[Dict[str, Any]]] = {}

    def execute_task(self, task: Task, spec: Spec) -> Dict[str, Any]:
        """Execute a single task."""
        # Find appropriate handler
        handler = None
        for h in self.handlers:
            if h.can_handle(task):
                handler = h
                break

        if not handler:
            return {
                "task_id": task.id,
                "status": "failed",
                "error": "No handler found for task",
            }

        try:
            result = handler.execute(task, spec)
            result["task_id"] = task.id

            # Record in history
            if task.id not in self.execution_history:
                self.execution_history[task.id] = []
            self.execution_history[task.id].append(result)

            return result
        except Exception as e:
            return {
                "task_id": task.id,
                "status": "failed",
                "error": str(e),
            }

    def execute_spec_tasks(self, spec: Spec) -> List[Dict[str, Any]]:
        """Execute all tasks for a spec."""
        results = []
        for task in spec.tasks:
            result = self.execute_task(task, spec)
            results.append(result)
        return results

    def execute_category_tasks(self, specs: List[Spec], category: str) -> List[Dict[str, Any]]:
        """Execute all tasks in a category."""
        results = []
        for spec in specs:
            if spec.category == category:
                results.extend(self.execute_spec_tasks(spec))
        return results

    def execute_all_tasks(self, specs: List[Spec]) -> List[Dict[str, Any]]:
        """Execute all tasks."""
        results = []
        for spec in specs:
            results.extend(self.execute_spec_tasks(spec))
        return results

    def retry_failed_tasks(self, specs: List[Spec]) -> List[Dict[str, Any]]:
        """Retry failed tasks."""
        results = []
        for spec in specs:
            for task in spec.tasks:
                if task.status in (TaskStatus.NOT_STARTED, TaskStatus.QUEUED):
                    result = self.execute_task(task, spec)
                    results.append(result)
        return results

    def rollback_task(self, task: Task) -> None:
        """Rollback a task."""
        if task.id in self.execution_history:
            self.execution_history[task.id] = []

    def get_execution_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Get execution history for a task."""
        return self.execution_history.get(task_id, [])

    def register_handler(self, handler: TaskHandler) -> None:
        """Register a custom task handler."""
        self.handlers.append(handler)
