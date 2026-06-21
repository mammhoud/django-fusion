"""Spec Task Orchestrator - Integrated with Django Seed."""

from .models import (
    Spec,
    Task,
    Requirement,
    AcceptanceCriterion,
    Design,
    CorrectnessProperty,
    PBTSpecification,
    ExecutionMetadata,
    TestResult,
    Counterexample,
    SpecMetadata,
    SpecStatus,
    TaskStatus,
    TestType,
)
from .scanner import SpecScanner
from .parser import SpecParser
from .tracker import TaskTracker
from .executor import TaskExecutor, TaskHandler
from .pbt import PBTExecutor
from .progress import ProgressTracker
from .filter import TaskFilter, TaskQuery
from .errors import ErrorHandler, RecoveryManager
from .config import OrchestratorConfig, ConfigLoader
from .compatibility import CompatibilityLayer, SpecFormatVersion
from .orchestrator import SpecTaskOrchestrator

__version__ = "1.0.0"
__all__ = [
    "Spec",
    "Task",
    "Requirement",
    "AcceptanceCriterion",
    "Design",
    "CorrectnessProperty",
    "PBTSpecification",
    "ExecutionMetadata",
    "TestResult",
    "Counterexample",
    "SpecMetadata",
    "SpecStatus",
    "TaskStatus",
    "TestType",
    "SpecScanner",
    "SpecParser",
    "TaskTracker",
    "TaskExecutor",
    "TaskHandler",
    "PBTExecutor",
    "ProgressTracker",
    "TaskFilter",
    "TaskQuery",
    "ErrorHandler",
    "RecoveryManager",
    "OrchestratorConfig",
    "ConfigLoader",
    "CompatibilityLayer",
    "SpecFormatVersion",
    "SpecTaskOrchestrator",
]
