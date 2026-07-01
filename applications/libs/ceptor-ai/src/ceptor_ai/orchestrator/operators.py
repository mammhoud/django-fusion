"""Functional-style orchestrator operators.

Each operator takes an :class:`OrchestratorState` (and its arguments) and
returns a value, so the operators can be reused in tests, chained from external
scripts, and composed without first instantiating a god-object.

Naming intentionally omits the parent directory: callers do
``operators.scan_specs(state, path)`` rather than
``operators.orchestrator_scan_specs``. The parent package already implies the
domain.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import progress, tracker
from .compatibility import CompatibilityLayer
from .config import OrchestratorConfig
from .errors import (
    ErrorState,
    RecoveryState,
    get_error_summary,
    get_errors,
    get_warnings,
    handle_file_system_error,
    handle_parsing_error,
)
from .management import ManagementState
from .executor import TaskExecutor
from .filter import TaskQuery
from .io import read_spec_files
from .models import Spec, Task, TaskStatus
from .parser import SpecParser
from .pbt import PBTExecutor
from .scanner import SpecScanner

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorState:
    """Single state container for the orchestrator.

    Cross-cutting mutable state lives here as plain dicts/lists. Sub-components
    (Scanner, Parser, Executor, etc.) are pure helpers. The previous separate
    :class:`TaskTracker` and :class:`ProgressTracker` classes' internal state
    is folded into ``specs``, ``tasks`` and ``status_history`` directly.
    """

    config: OrchestratorConfig
    scanner: SpecScanner = field(default_factory=SpecScanner)
    parser: SpecParser = field(default_factory=SpecParser)
    executor: TaskExecutor = field(default_factory=TaskExecutor)
    pbt_executor: PBTExecutor = field(default_factory=PBTExecutor)
    management_state: ManagementState = field(init=False)
    error_state: ErrorState = field(default_factory=ErrorState)
    recovery_state: RecoveryState = field(default_factory=RecoveryState)
    compatibility_layer: CompatibilityLayer = field(default_factory=CompatibilityLayer)
    specs: Dict[str, Dict[str, Spec]] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    status_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        # ManagementState needs the script paths from config; resolve it
        # post-init because dataclass fields with init=False cannot have a
        # default-factory expression and we want to inject script_paths at
        # construction time.
        self.management_state = ManagementState(self.config.script_paths)


# ---------------------------------------------------------------------------
# Scan / load
# ---------------------------------------------------------------------------


def scan_specs(state: OrchestratorState, base_path: Optional[str] = None) -> Dict[str, Any]:
    """Scan a spec directory tree and report counts by category."""
    path = base_path or state.config.base_path
    try:
        spec_metadata = state.scanner.scan(path)
        return {
            "success": True,
            "specs_found": sum(len(items) for items in spec_metadata.values()),
            "categories": list(spec_metadata.keys()),
            "warnings": state.scanner.get_warnings(),
            "stats": state.scanner.get_stats(),
        }
    except Exception as exc:
        handle_file_system_error(state.error_state, exc, path, "scan")
        return {"success": False, "error": str(exc)}


def _load_spec_from_metadata(state: OrchestratorState, metadata) -> Spec:
    """Parse a single spec on disk into a fully-populated :class:`Spec`."""
    requirements, design, tasks_text = read_spec_files(metadata)

    if requirements:
        is_valid, warnings = state.compatibility_layer.validate_format_compatibility(requirements)
        if not is_valid:
            logger.warning("Format compatibility issue in %s", metadata.requirements_path)
        for warning in warnings:
            logger.warning("Format warning: %s", warning)

    introduction, glossary, req_list = state.parser.parse_requirements(requirements)
    design_obj = state.parser.parse_design(design) if design else None
    task_list = state.parser.parse_tasks(tasks_text, metadata.category, metadata.spec_name)

    return Spec(
        category=metadata.category,
        spec_name=metadata.spec_name,
        introduction=introduction,
        glossary=glossary,
        requirements=req_list,
        design=design_obj,
        tasks=task_list,
    )


def load_specs(state: OrchestratorState, base_path: Optional[str] = None) -> Dict[str, Any]:
    """Scan and parse every spec on disk; populate state.specs and state.tasks."""
    scan_result = scan_specs(state, base_path)
    if not scan_result.get("success"):
        return scan_result

    spec_metadata = state.scanner.specs
    loaded = 0
    failed = 0
    for category, specs in spec_metadata.items():
        state.specs.setdefault(category, {})
        for spec_name, metadata in specs.items():
            try:
                spec = _load_spec_from_metadata(state, metadata)
                state.specs[category][spec_name] = spec
                state.tasks.extend(spec.tasks)
                loaded += 1
            except Exception as exc:
                handle_parsing_error(state.error_state, exc, metadata.path)
                failed += 1

    return {"success": True, "loaded": loaded, "failed": failed, "total": loaded + failed}


# ---------------------------------------------------------------------------
# Queries — pure over state
# ---------------------------------------------------------------------------


def get_spec(state: OrchestratorState, category: str, spec_name: str) -> Optional[Spec]:
    return state.specs.get(category, {}).get(spec_name)


def get_specs_by_category(state: OrchestratorState, category: str) -> List[Spec]:
    return list(state.specs.get(category, {}).values())


def get_all_specs(state: OrchestratorState) -> List[Spec]:
    out: List[Spec] = []
    for category_specs in state.specs.values():
        out.extend(category_specs.values())
    return out


def get_tasks_by_category(state: OrchestratorState, category: str) -> List[Task]:
    return tracker.list_tasks_by_category(state, category)


def get_tasks_by_status(state: OrchestratorState, status: TaskStatus) -> List[Task]:
    return tracker.list_tasks_by_status(state, status)


def filter_tasks(state: OrchestratorState, criteria: Dict[str, Any]) -> List[Task]:
    return tracker.filter_tasks(state, criteria)


def query_tasks(state: OrchestratorState, criteria: Dict[str, Any]) -> List[Task]:
    return TaskQuery(state.tasks).find_by_criteria(criteria)


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def execute_task(state: OrchestratorState, task_id: str) -> Dict[str, Any]:
    task = tracker.get_task_by_id(state, task_id)
    if not task:
        return {"success": False, "error": f"Task not found: {task_id}"}

    spec = get_spec(state, task.spec_category, task.spec_name)
    if not spec:
        return {
            "success": False,
            "error": f"Spec not found: {task.spec_category}/{task.spec_name}",
        }
    return state.executor.execute_task(task, spec)


def execute_spec_tasks(state: OrchestratorState, category: str, spec_name: str) -> List[Dict[str, Any]]:
    spec = get_spec(state, category, spec_name)
    if not spec:
        return []
    return state.executor.execute_spec_tasks(spec)


# ---------------------------------------------------------------------------
# Progress / errors / export / format
# ---------------------------------------------------------------------------


def get_spec_progress(state: OrchestratorState, category: str, spec_name: str) -> Dict[str, Any]:
    return progress.spec_progress_report(state, category, spec_name)


def get_category_summary(state: OrchestratorState, category: str) -> Dict[str, Any]:
    return progress.category_summary(state.specs.get(category, {}))


def get_overall_summary(state: OrchestratorState) -> Dict[str, Any]:
    return progress.overall_summary(state)


def update_task_status(state: OrchestratorState, task_id: str, new_status: TaskStatus) -> bool:
    return tracker.update_task_status(state, task_id, new_status)


def get_errors(state: OrchestratorState) -> List[Dict[str, Any]]:
    return get_errors(state.error_state)


def get_warnings(state: OrchestratorState) -> List[Dict[str, Any]]:
    return get_warnings(state.error_state)


def get_error_summary(state: OrchestratorState) -> Dict[str, Any]:
    return get_error_summary(state.error_state)


def export_to_json(state: OrchestratorState, file_path: str) -> bool:
    try:
        data = {
            "specs": {
                category: {
                    spec_name: spec.to_dict()
                    for spec_name, spec in specs.items()
                }
                for category, specs in state.specs.items()
            },
            "summary": get_overall_summary(state),
        }
        with open(file_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)
        return True
    except Exception as exc:
        handle_file_system_error(state.error_state, exc, file_path, "export")
        return False


def get_execution_history(state: OrchestratorState, task_id: str) -> List[Dict[str, Any]]:
    return state.executor.get_execution_history(task_id)


def get_format_compatibility_info(state: OrchestratorState) -> Dict[str, Any]:
    info = state.compatibility_layer.get_compatibility_info()
    return {
        "current_version": info.current_version.value,
        "supported_versions": [v.value for v in info.supported_versions],
        "deprecated_features": info.deprecated_features,
        "migration_paths": info.migration_paths,
    }


def check_spec_format_compatibility(state: OrchestratorState, spec_path: str) -> Dict[str, Any]:
    try:
        with open(spec_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        is_valid, warnings = state.compatibility_layer.validate_format_compatibility(content)
        detected_version = state.compatibility_layer.detect_format_version(content)
        return {
            "success": True,
            "valid": is_valid,
            "detected_version": detected_version.value,
            "warnings": warnings,
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}
