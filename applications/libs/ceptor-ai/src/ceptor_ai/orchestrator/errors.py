"""Error handling and recovery — pure operators over :class:`ErrorState` and :class:`RecoveryState`.

Decomposed from the legacy :class:`ErrorHandler` and :class:`RecoveryManager`
god-classes. The dataclasses hold the canonical state:

- :class:`ErrorState` — recorded ``errors`` and ``warnings`` lists.
- :class:`RecoveryState` — recorded ``recovery_history`` list.

The operators in this module mutate the dataclass in place (mirroring how
:attr:`OrchestratorState.specs` is mutated by ``load_specs``) and return the
recorded entry where useful.

Naming intentionally omits the parent directory: callers do
``errors.handle_file_system_error(state, ...)`` rather than
``errors.errors_handle_file_system_error``. The parent package already implies
the domain.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exception hierarchy — unchanged
# ---------------------------------------------------------------------------


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Initialize the error."""
        super().__init__(message)
        self.message = message
        self.context = context or {}


class FileSystemError(OrchestratorError):
    """File system related errors."""


class ParsingError(OrchestratorError):
    """Parsing related errors."""


class ExecutionError(OrchestratorError):
    """Task execution errors."""


class IntegrationError(OrchestratorError):
    """Integration related errors."""


class ConfigurationError(OrchestratorError):
    """Configuration related errors."""


# ---------------------------------------------------------------------------
# State dataclasses — canonical state containers
# ---------------------------------------------------------------------------


@dataclass
class ErrorState:
    """Mutable container for recorded errors and warnings.

    Operators in this module append to ``errors`` and ``warnings`` in place;
    :func:`get_errors`, :func:`get_warnings`, and :func:`get_error_summary`
    expose them to read-only callers without copying on every read.
    """

    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RecoveryState:
    """Mutable container for the recovery-history log.

    Each entry is one of three shapes driven by the operator that produced it:

    - ``retry_operation`` success → operation name, status='success', attempts
    - ``retry_operation`` failure → operation name, status='failed', error
    - ``skip_operation`` → operation_id, status='skipped', reason
    - ``rollback_operation`` → operation_id, status='rolled_back'
    """

    recovery_history: List[Dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Record operators — pure over :class:`ErrorState`, mutating in place
# ---------------------------------------------------------------------------


def handle_file_system_error(
    state: ErrorState,
    error: Exception,
    file_path: str,
    operation: str,
) -> Dict[str, Any]:
    """Record a file-system error and return the recorded info."""
    error_info = {
        "type": "file_system",
        "error": str(error),
        "file_path": file_path,
        "operation": operation,
        "recovery_options": ["retry", "skip", "manual_review"],
    }
    state.errors.append(error_info)
    logger.error(f"File system error: {error} ({file_path}, {operation})")
    return error_info


def handle_parsing_error(
    state: ErrorState,
    error: Exception,
    file_path: str,
    line_number: Optional[int] = None,
) -> Dict[str, Any]:
    """Record a parsing error and return the recorded info."""
    error_info = {
        "type": "parsing",
        "error": str(error),
        "file_path": file_path,
        "line_number": line_number,
        "recovery_options": ["skip_spec", "manual_fix", "use_defaults"],
    }
    state.errors.append(error_info)
    logger.error(f"Parsing error: {error} ({file_path}:{line_number})")
    return error_info


def handle_execution_error(
    state: ErrorState,
    error: Exception,
    task_id: str,
    spec_name: str,
) -> Dict[str, Any]:
    """Record a task-execution error and return the recorded info."""
    error_info = {
        "type": "execution",
        "error": str(error),
        "task_id": task_id,
        "spec_name": spec_name,
        "recovery_options": ["retry", "skip", "rollback"],
    }
    state.errors.append(error_info)
    logger.error(f"Execution error: {error} (task: {task_id}, spec: {spec_name})")
    return error_info


def handle_integration_error(
    state: ErrorState,
    error: Exception,
    script_name: str,
) -> Dict[str, Any]:
    """Record an integration error (typically a management-script failure)."""
    error_info = {
        "type": "integration",
        "error": str(error),
        "script_name": script_name,
        "recovery_options": ["retry", "skip", "manual_intervention"],
    }
    state.errors.append(error_info)
    logger.error(f"Integration error: {error} (script: {script_name})")
    return error_info


def handle_configuration_error(
    state: ErrorState,
    error: Exception,
    setting_name: str,
) -> Dict[str, Any]:
    """Record a configuration error and return the recorded info."""
    error_info = {
        "type": "configuration",
        "error": str(error),
        "setting_name": setting_name,
        "recovery_options": ["use_default", "manual_fix", "skip"],
    }
    state.errors.append(error_info)
    logger.error(f"Configuration error: {error} (setting: {setting_name})")
    return error_info


def add_warning(
    state: ErrorState,
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Append a warning to ``state.warnings`` and surface it via the logger."""
    state.warnings.append({"message": message, "context": context or {}})
    logger.warning(message)


# ---------------------------------------------------------------------------
# Read-only views + clear helpers
# ---------------------------------------------------------------------------


def get_errors(state: ErrorState) -> List[Dict[str, Any]]:
    """Return the recorded errors list. Reference, not a snapshot."""
    return state.errors


def get_warnings(state: ErrorState) -> List[Dict[str, Any]]:
    """Return the recorded warnings list. Reference, not a snapshot."""
    return state.warnings


def get_error_summary(state: ErrorState) -> Dict[str, Any]:
    """Count errors grouped by ``type`` and total warnings."""
    error_types: Dict[str, int] = {}
    for error in state.errors:
        t = error.get("type", "unknown")
        error_types[t] = error_types.get(t, 0) + 1
    return {
        "total_errors": len(state.errors),
        "total_warnings": len(state.warnings),
        "errors_by_type": error_types,
    }


def clear_errors(state: ErrorState) -> None:
    state.errors = []


def clear_warnings(state: ErrorState) -> None:
    state.warnings = []


# ---------------------------------------------------------------------------
# Recovery operators — pure over :class:`RecoveryState`
# ---------------------------------------------------------------------------


def retry_operation(
    state: RecoveryState,
    operation: Callable[[], Any],
    max_retries: int = 3,
    backoff_factor: float = 2.0,
) -> Any:
    """Run ``operation`` with exponential backoff; record outcome in ``state``.

    On success, records ``{operation, status='success', attempts}`` and returns
    the operation's value. On the final failure, records
    ``{operation, status='failed', error}`` and re-raises the last exception,
    matching the legacy :class:`RecoveryManager.retry_operation` contract.
    """
    last_error: Optional[BaseException] = None
    op_name = getattr(operation, "__name__", repr(operation))
    for attempt in range(max_retries):
        try:
            result = operation()
            state.recovery_history.append({
                "operation": op_name,
                "status": "success",
                "attempts": attempt + 1,
            })
            return result
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Retry attempt {attempt + 1}/{max_retries} "
                    f"after {wait_time}s: {exc}"
                )
                time.sleep(wait_time)

    state.recovery_history.append({
        "operation": op_name,
        "status": "failed",
        "attempts": max_retries,
        "error": str(last_error),
    })
    assert last_error is not None
    raise last_error


def skip_operation(state: RecoveryState, operation_id: str, reason: str) -> None:
    """Record a skip and log it."""
    state.recovery_history.append({
        "operation_id": operation_id,
        "status": "skipped",
        "reason": reason,
    })
    logger.info(f"Skipped operation {operation_id}: {reason}")


def rollback_operation(state: RecoveryState, operation_id: str) -> None:
    """Record a rollback and log it."""
    state.recovery_history.append({
        "operation_id": operation_id,
        "status": "rolled_back",
    })
    logger.info(f"Rolled back operation {operation_id}")


def get_recovery_history(state: RecoveryState) -> List[Dict[str, Any]]:
    """Return the recorded recovery-history list. Reference, not a snapshot."""
    return state.recovery_history


__all__ = [
    # Exceptions
    "OrchestratorError",
    "FileSystemError",
    "ParsingError",
    "ExecutionError",
    "IntegrationError",
    "ConfigurationError",
    # State
    "ErrorState",
    "RecoveryState",
    # Error recording
    "handle_file_system_error",
    "handle_parsing_error",
    "handle_execution_error",
    "handle_integration_error",
    "handle_configuration_error",
    "add_warning",
    # Error views + clear
    "get_errors",
    "get_warnings",
    "get_error_summary",
    "clear_errors",
    "clear_warnings",
    # Recovery
    "retry_operation",
    "skip_operation",
    "rollback_operation",
    "get_recovery_history",
]
