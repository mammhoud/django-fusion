"""Core interfaces for the orchestrator."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    Spec,
    SpecMetadata,
    Task,
    TaskStatus,
    TestResult,
)


class SpecIndex(ABC):
    """Interface for spec indexing and discovery."""

    @abstractmethod
    def scan(self, base_path: str) -> List[SpecMetadata]:
        """Scan directory and discover specs."""

    @abstractmethod
    def get_spec(self, category: str, spec_name: str) -> Optional[Spec]:
        """Get a specific spec."""

    @abstractmethod
    def get_specs_by_category(self, category: str) -> List[Spec]:
        """Get all specs in a category."""

    @abstractmethod
    def get_specs_by_status(self, status: TaskStatus) -> List[Task]:
        """Get specs by task status."""

    @abstractmethod
    def find_similar_specs(self, name: str) -> List[Tuple[str, str]]:
        """Find similar specs by name."""

    @abstractmethod
    def update_spec(self, spec: Spec) -> None:
        """Update a spec."""

    @abstractmethod
    def remove_spec(self, category: str, spec_name: str) -> None:
        """Remove a spec."""

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about specs."""


class TaskTracker(ABC):
    """Interface for task tracking."""

    @abstractmethod
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get tasks by category."""

    @abstractmethod
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status."""

    @abstractmethod
    def get_tasks_by_spec(self, category: str, spec_name: str) -> List[Task]:
        """Get tasks for a specific spec."""

    @abstractmethod
    def filter_tasks(self, filters: Dict[str, Any]) -> List[Task]:
        """Filter tasks by criteria."""

    @abstractmethod
    def update_task_status(self, task: Task, new_status: TaskStatus) -> None:
        """Update task status."""

    @abstractmethod
    def calculate_spec_progress(self, category: str, spec_name: str) -> float:
        """Calculate spec progress percentage."""

    @abstractmethod
    def get_spec_status(self, category: str, spec_name: str) -> str:
        """Get spec status."""

    @abstractmethod
    def add_task_dependency(self, task: Task, dependency: Task) -> None:
        """Add a task dependency."""


class TaskExecutor(ABC):
    """Interface for task execution."""

    @abstractmethod
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task."""

    @abstractmethod
    def execute_spec_tasks(self, category: str, spec_name: str) -> List[Dict[str, Any]]:
        """Execute all tasks for a spec."""

    @abstractmethod
    def execute_category_tasks(self, category: str) -> List[Dict[str, Any]]:
        """Execute all tasks in a category."""

    @abstractmethod
    def execute_all_tasks(self) -> List[Dict[str, Any]]:
        """Execute all tasks."""

    @abstractmethod
    def retry_failed_tasks(self) -> List[Dict[str, Any]]:
        """Retry failed tasks."""

    @abstractmethod
    def rollback_task(self, task: Task) -> None:
        """Rollback a task."""

    @abstractmethod
    def get_execution_history(self, task: Task) -> List[Dict[str, Any]]:
        """Get execution history for a task."""


class PBTExecutor(ABC):
    """Interface for property-based testing."""

    @abstractmethod
    def execute_property_test(self, property_id: str, framework: str) -> TestResult:
        """Execute a property-based test."""

    @abstractmethod
    def execute_round_trip_test(self, data: Any, serialize, deserialize) -> bool:
        """Execute a round-trip test."""

    @abstractmethod
    def execute_idempotence_test(self, data: Any, operation) -> bool:
        """Execute an idempotence test."""

    @abstractmethod
    def execute_metamorphic_test(self, data: Any, transform, verify) -> bool:
        """Execute a metamorphic test."""

    @abstractmethod
    def capture_counterexample(self, failure: Exception) -> Dict[str, Any]:
        """Capture a counterexample from a test failure."""

    @abstractmethod
    def store_test_results(self, results: List[TestResult]) -> None:
        """Store test results."""
