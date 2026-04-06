"""Error handling and recovery."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Initialize the error."""
        super().__init__(message)
        self.message = message
        self.context = context or {}


class FileSystemError(OrchestratorError):
    """File system related errors."""
    pass


class ParsingError(OrchestratorError):
    """Parsing related errors."""
    pass


class ExecutionError(OrchestratorError):
    """Task execution errors."""
    pass


class IntegrationError(OrchestratorError):
    """Integration related errors."""
    pass


class ConfigurationError(OrchestratorError):
    """Configuration related errors."""
    pass


class ErrorHandler:
    """Handles errors and provides recovery options."""

    def __init__(self):
        """Initialize the error handler."""
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.recovery_options: Dict[str, List[str]] = {}

    def handle_file_system_error(
        self,
        error: Exception,
        file_path: str,
        operation: str,
    ) -> Dict[str, Any]:
        """Handle file system errors."""
        error_info = {
            "type": "file_system",
            "error": str(error),
            "file_path": file_path,
            "operation": operation,
            "recovery_options": [
                "retry",
                "skip",
                "manual_review",
            ],
        }

        self.errors.append(error_info)
        logger.error(f"File system error: {error} ({file_path}, {operation})")

        return error_info

    def handle_parsing_error(
        self,
        error: Exception,
        file_path: str,
        line_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Handle parsing errors."""
        error_info = {
            "type": "parsing",
            "error": str(error),
            "file_path": file_path,
            "line_number": line_number,
            "recovery_options": [
                "skip_spec",
                "manual_fix",
                "use_defaults",
            ],
        }

        self.errors.append(error_info)
        logger.error(f"Parsing error: {error} ({file_path}:{line_number})")

        return error_info

    def handle_execution_error(
        self,
        error: Exception,
        task_id: str,
        spec_name: str,
    ) -> Dict[str, Any]:
        """Handle task execution errors."""
        error_info = {
            "type": "execution",
            "error": str(error),
            "task_id": task_id,
            "spec_name": spec_name,
            "recovery_options": [
                "retry",
                "skip",
                "rollback",
            ],
        }

        self.errors.append(error_info)
        logger.error(f"Execution error: {error} (task: {task_id}, spec: {spec_name})")

        return error_info

    def handle_integration_error(
        self,
        error: Exception,
        script_name: str,
    ) -> Dict[str, Any]:
        """Handle integration errors."""
        error_info = {
            "type": "integration",
            "error": str(error),
            "script_name": script_name,
            "recovery_options": [
                "retry",
                "skip",
                "manual_intervention",
            ],
        }

        self.errors.append(error_info)
        logger.error(f"Integration error: {error} (script: {script_name})")

        return error_info

    def handle_configuration_error(
        self,
        error: Exception,
        setting_name: str,
    ) -> Dict[str, Any]:
        """Handle configuration errors."""
        error_info = {
            "type": "configuration",
            "error": str(error),
            "setting_name": setting_name,
            "recovery_options": [
                "use_default",
                "manual_fix",
                "skip",
            ],
        }

        self.errors.append(error_info)
        logger.error(f"Configuration error: {error} (setting: {setting_name})")

        return error_info

    def add_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a warning."""
        warning_info = {
            "message": message,
            "context": context or {},
        }

        self.warnings.append(warning_info)
        logger.warning(message)

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self.errors

    def get_warnings(self) -> List[Dict[str, Any]]:
        """Get all warnings."""
        return self.warnings

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary."""
        error_types = {}
        for error in self.errors:
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors_by_type": error_types,
        }

    def clear_errors(self) -> None:
        """Clear all errors."""
        self.errors = []

    def clear_warnings(self) -> None:
        """Clear all warnings."""
        self.warnings = []


class RecoveryManager:
    """Manages recovery operations."""

    def __init__(self):
        """Initialize the recovery manager."""
        self.recovery_history: List[Dict[str, Any]] = []

    def retry_operation(
        self,
        operation,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ) -> Any:
        """
        Retry an operation with exponential backoff.

        Args:
            operation: Callable to retry
            max_retries: Maximum number of retries
            backoff_factor: Backoff multiplier

        Returns:
            Result of operation
        """
        import time

        last_error = None
        for attempt in range(max_retries):
            try:
                result = operation()
                self.recovery_history.append({
                    "operation": operation.__name__,
                    "status": "success",
                    "attempts": attempt + 1,
                })
                return result
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} "
                        f"after {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)

        self.recovery_history.append({
            "operation": operation.__name__,
            "status": "failed",
            "attempts": max_retries,
            "error": str(last_error),
        })

        raise last_error

    def skip_operation(self, operation_id: str, reason: str) -> None:
        """Skip an operation."""
        self.recovery_history.append({
            "operation_id": operation_id,
            "status": "skipped",
            "reason": reason,
        })
        logger.info(f"Skipped operation {operation_id}: {reason}")

    def rollback_operation(self, operation_id: str) -> None:
        """Rollback an operation."""
        self.recovery_history.append({
            "operation_id": operation_id,
            "status": "rolled_back",
        })
        logger.info(f"Rolled back operation {operation_id}")

    def get_recovery_history(self) -> List[Dict[str, Any]]:
        """Get recovery history."""
        return self.recovery_history
