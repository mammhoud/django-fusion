"""Main orchestrator class."""

import json
import logging
from typing import Any, Dict, List, Optional

from .compatibility import CompatibilityLayer
from .config import OrchestratorConfig
from .errors import ErrorHandler, RecoveryManager
from .executor import TaskExecutor
from .filter import TaskQuery
from .management import ManagementScriptRunner
from .models import Spec, Task, TaskStatus
from .parser import SpecParser
from .pbt import PBTExecutor
from .progress import ProgressTracker
from .scanner import SpecScanner
from .tracker import TaskTracker

logger = logging.getLogger(__name__)


class SpecTaskOrchestrator:
    """Main orchestrator for spec task management."""

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """Initialize the orchestrator."""
        self.config = config or OrchestratorConfig()
        self.scanner = SpecScanner()
        self.parser = SpecParser()
        self.tracker = TaskTracker()
        self.executor = TaskExecutor()
        self.pbt_executor = PBTExecutor()
        self.progress_tracker = ProgressTracker()
        self.management_runner = ManagementScriptRunner(self.config.script_paths)
        self.error_handler = ErrorHandler()
        self.recovery_manager = RecoveryManager()
        self.compatibility_layer = CompatibilityLayer()

        self.specs: Dict[str, Dict[str, Spec]] = {}
        self.tasks: List[Task] = []

    def scan_specs(self, base_path: Optional[str] = None) -> Dict[str, Any]:
        """Scan spec directory."""
        path = base_path or self.config.base_path

        try:
            spec_metadata = self.scanner.scan(path)

            return {
                "success": True,
                "specs_found": sum(len(s) for s in spec_metadata.values()),
                "categories": list(spec_metadata.keys()),
                "warnings": self.scanner.get_warnings(),
                "stats": self.scanner.get_stats(),
            }
        except Exception as e:
            self.error_handler.handle_file_system_error(e, path, "scan")
            return {
                "success": False,
                "error": str(e),
            }

    def load_specs(self, base_path: Optional[str] = None) -> Dict[str, Any]:
        """Load and parse all specs."""
        path = base_path or self.config.base_path

        # First scan
        scan_result = self.scan_specs(path)
        if not scan_result.get("success"):
            return scan_result

        # Get metadata
        spec_metadata = self.scanner.specs

        # Parse each spec
        loaded_count = 0
        failed_count = 0

        for category, specs in spec_metadata.items():
            if category not in self.specs:
                self.specs[category] = {}

            for spec_name, metadata in specs.items():
                try:
                    spec = self._load_spec(metadata)
                    self.specs[category][spec_name] = spec
                    self.tracker.add_spec(spec)
                    self.progress_tracker.add_spec(spec)
                    self.tasks.extend(spec.tasks)
                    loaded_count += 1
                except Exception as e:
                    self.error_handler.handle_parsing_error(
                        e,
                        metadata.path,
                    )
                    failed_count += 1

        return {
            "success": True,
            "loaded": loaded_count,
            "failed": failed_count,
            "total": loaded_count + failed_count,
        }

    def _load_spec(self, metadata) -> Spec:
        """Load a single spec."""
        # Read files
        requirements_content = ""
        design_content = ""
        tasks_content = ""

        if metadata.requirements_path:
            with open(metadata.requirements_path, "r") as f:
                requirements_content = f.read()

        if metadata.design_path:
            with open(metadata.design_path, "r") as f:
                design_content = f.read()

        if metadata.tasks_path:
            with open(metadata.tasks_path, "r") as f:
                tasks_content = f.read()

        # Check format compatibility
        if requirements_content:
            is_valid, warnings = self.compatibility_layer.validate_format_compatibility(
                requirements_content
            )
            if not is_valid:
                logger.warning(f"Format compatibility issue in {metadata.requirements_path}")
            for warning in warnings:
                logger.warning(f"Format warning: {warning}")

        # Parse
        introduction, glossary, requirements = self.parser.parse_requirements(
            requirements_content
        )
        design = self.parser.parse_design(design_content) if design_content else None
        tasks = self.parser.parse_tasks(
            tasks_content,
            metadata.category,
            metadata.spec_name,
        )

        return Spec(
            category=metadata.category,
            spec_name=metadata.spec_name,
            introduction=introduction,
            glossary=glossary,
            requirements=requirements,
            design=design,
            tasks=tasks,
        )

    def get_spec(self, category: str, spec_name: str) -> Optional[Spec]:
        """Get a specific spec."""
        return self.specs.get(category, {}).get(spec_name)

    def get_specs_by_category(self, category: str) -> List[Spec]:
        """Get all specs in a category."""
        return list(self.specs.get(category, {}).values())

    def get_all_specs(self) -> List[Spec]:
        """Get all specs."""
        specs = []
        for category_specs in self.specs.values():
            specs.extend(category_specs.values())
        return specs

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get tasks by category."""
        return self.tracker.get_tasks_by_category(category)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status."""
        return self.tracker.get_tasks_by_status(status)

    def filter_tasks(self, criteria: Dict[str, Any]) -> List[Task]:
        """Filter tasks by criteria."""
        return self.tracker.filter_tasks(criteria)

    def query_tasks(self, criteria: Dict[str, Any]) -> List[Task]:
        """Query tasks with complex criteria."""
        query = TaskQuery(self.tasks)
        return query.find_by_criteria(criteria)

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a single task."""
        task = self.tracker.get_task_by_id(task_id)
        if not task:
            return {"success": False, "error": f"Task not found: {task_id}"}

        spec = self.get_spec(task.spec_category, task.spec_name)
        if not spec:
            return {"success": False, "error": f"Spec not found: {task.spec_category}/{task.spec_name}"}

        result = self.executor.execute_task(task, spec)
        return result

    def execute_spec_tasks(self, category: str, spec_name: str) -> List[Dict[str, Any]]:
        """Execute all tasks for a spec."""
        spec = self.get_spec(category, spec_name)
        if not spec:
            return []

        return self.executor.execute_spec_tasks(spec)

    def get_spec_progress(self, category: str, spec_name: str) -> Dict[str, Any]:
        """Get spec progress."""
        return self.progress_tracker.get_spec_progress_report(category, spec_name)

    def get_category_summary(self, category: str) -> Dict[str, Any]:
        """Get category summary."""
        return self.progress_tracker.get_category_summary(category)

    def get_overall_summary(self) -> Dict[str, Any]:
        """Get overall summary."""
        return self.progress_tracker.get_overall_summary()

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> bool:
        """Update task status."""
        try:
            self.tracker.update_task_status(task_id, new_status)
            return True
        except Exception as e:
            self.error_handler.handle_execution_error(e, task_id, "unknown")
            return False

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self.error_handler.get_errors()

    def get_warnings(self) -> List[Dict[str, Any]]:
        """Get all warnings."""
        return self.error_handler.get_warnings()

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary."""
        return self.error_handler.get_error_summary()

    def export_to_json(self, file_path: str) -> bool:
        """Export specs to JSON."""
        try:
            data = {
                "specs": {
                    category: {
                        spec_name: spec.to_dict()
                        for spec_name, spec in specs.items()
                    }
                    for category, specs in self.specs.items()
                },
                "summary": self.get_overall_summary(),
            }

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            return True
        except Exception as e:
            self.error_handler.handle_file_system_error(e, file_path, "export")
            return False

    def get_execution_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Get execution history for a task."""
        return self.executor.get_execution_history(task_id)

    def get_format_compatibility_info(self) -> Dict[str, Any]:
        """Get format compatibility information."""
        info = self.compatibility_layer.get_compatibility_info()
        return {
            "current_version": info.current_version.value,
            "supported_versions": [v.value for v in info.supported_versions],
            "deprecated_features": info.deprecated_features,
            "migration_paths": info.migration_paths,
        }

    def check_spec_format_compatibility(self, spec_path: str) -> Dict[str, Any]:
        """Check format compatibility of a spec file."""
        try:
            with open(spec_path, "r") as f:
                content = f.read()

            is_valid, warnings = self.compatibility_layer.validate_format_compatibility(content)
            detected_version = self.compatibility_layer.detect_format_version(content)

            return {
                "success": True,
                "valid": is_valid,
                "detected_version": detected_version.value,
                "warnings": warnings,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
