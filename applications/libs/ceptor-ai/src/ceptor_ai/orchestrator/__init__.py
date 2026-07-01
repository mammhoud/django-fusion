"""Autonomous task orchestration engine.

Key classes
-----------
SpecTaskOrchestrator    Main orchestrator — parses, classifies, and executes tasks.
OrchestratorConfig      Configuration model (paths, filters, output format).
ExecutionContext         Per-run execution state container.
TaskResult              Result object with status, output, and error info.

Usage::

    from ceptor_ai.orchestrator import SpecTaskOrchestrator
    from ceptor_ai.orchestrator.config import OrchestratorConfig
"""

from .orchestrator import SpecTaskOrchestrator

# Canonical alias — callers can also use ``Orchestrator`` as a shorthand
Orchestrator = SpecTaskOrchestrator

__all__ = ["Orchestrator", "SpecTaskOrchestrator"]
