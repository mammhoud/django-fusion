"""Main orchestrator class.

:class:`SpecTaskOrchestrator` is a thin facade that owns an
:class:`OrchestratorState` and delegates every public method to a free
function — either in :mod:`orchestrator.operators` for cross-cutting concerns
or in :mod:`orchestrator.tracker` / :mod:`orchestrator.progress` for
querying and progress aggregation. New code should call those free functions
directly so the state container can be passed around explicitly.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import operators
from .config import OrchestratorConfig
from .models import Spec, Task, TaskStatus
from .operators import OrchestratorState


class SpecTaskOrchestrator:
    """Main orchestrator for spec task management."""

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """Initialize the orchestrator."""
        self.state = OrchestratorState(config=config or OrchestratorConfig())
        # Backwards-compatible attribute aliases for callers that introspect
        # the orchestrator's sub-components directly. ``tracker`` and
        # ``progress_tracker`` are intentionally absent — the corresponding
        # free functions live in :mod:`orchestrator.tracker` and
        # :mod:`orchestrator.progress` and operate on ``state`` directly.
        # State containers (``*_state``) are the post-refactor names for the
        # former ``management_runner`` / ``error_handler`` / ``recovery_manager``
        # god-classes; they hold the canonical mutable state and the
        # corresponding operators in :mod:`orchestrator.errors` and
        # :mod:`orchestrator.management` mutate them in place.
        self.config = self.state.config
        self.scanner = self.state.scanner
        self.parser = self.state.parser
        self.executor = self.state.executor
        self.pbt_executor = self.state.pbt_executor
        self.management_state = self.state.management_state
        self.error_state = self.state.error_state
        self.recovery_state = self.state.recovery_state
        self.compatibility_layer = self.state.compatibility_layer
        self.specs = self.state.specs
        self.tasks = self.state.tasks
        self.status_history = self.state.status_history

    def scan_specs(self, base_path: Optional[str] = None) -> Dict[str, Any]:
        return operators.scan_specs(self.state, base_path)

    def load_specs(self, base_path: Optional[str] = None) -> Dict[str, Any]:
        return operators.load_specs(self.state, base_path)

    def get_spec(self, category: str, spec_name: str) -> Optional[Spec]:
        return operators.get_spec(self.state, category, spec_name)

    def get_specs_by_category(self, category: str) -> List[Spec]:
        return operators.get_specs_by_category(self.state, category)

    def get_all_specs(self) -> List[Spec]:
        return operators.get_all_specs(self.state)

    def get_tasks_by_category(self, category: str) -> List[Task]:
        return operators.get_tasks_by_category(self.state, category)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return operators.get_tasks_by_status(self.state, status)

    def filter_tasks(self, criteria: Dict[str, Any]) -> List[Task]:
        return operators.filter_tasks(self.state, criteria)

    def query_tasks(self, criteria: Dict[str, Any]) -> List[Task]:
        return operators.query_tasks(self.state, criteria)

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        return operators.execute_task(self.state, task_id)

    def execute_spec_tasks(self, category: str, spec_name: str) -> List[Dict[str, Any]]:
        return operators.execute_spec_tasks(self.state, category, spec_name)

    def get_spec_progress(self, category: str, spec_name: str) -> Dict[str, Any]:
        return operators.get_spec_progress(self.state, category, spec_name)

    def get_category_summary(self, category: str) -> Dict[str, Any]:
        return operators.get_category_summary(self.state, category)

    def get_overall_summary(self) -> Dict[str, Any]:
        return operators.get_overall_summary(self.state)

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> bool:
        return operators.update_task_status(self.state, task_id, new_status)

    def get_errors(self) -> List[Dict[str, Any]]:
        return operators.get_errors(self.state)

    def get_warnings(self) -> List[Dict[str, Any]]:
        return operators.get_warnings(self.state)

    def get_error_summary(self) -> Dict[str, Any]:
        return operators.get_error_summary(self.state)

    def export_to_json(self, file_path: str) -> bool:
        return operators.export_to_json(self.state, file_path)

    def get_execution_history(self, task_id: str) -> List[Dict[str, Any]]:
        return operators.get_execution_history(self.state, task_id)

    def get_format_compatibility_info(self) -> Dict[str, Any]:
        return operators.get_format_compatibility_info(self.state)

    def check_spec_format_compatibility(self, spec_path: str) -> Dict[str, Any]:
        return operators.check_spec_format_compatibility(self.state, spec_path)
