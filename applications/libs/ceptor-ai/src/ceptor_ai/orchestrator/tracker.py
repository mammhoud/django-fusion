"""Task indexing, lookup, status updates — pure operator functions.

Decomposed from the legacy ``TaskTracker`` class. State hangs off
:class:`~.operators.OrchestratorState` (the canonical ``specs`` dict and
``tasks`` list); these functions read or mutate those collections directly.

Note: ``update_task_status`` does **not** mirror Spec-level status changes
into ``state.status_history``. That log is reserved for Spec transitions; see
:mod:`orchestrator.progress`. (This matches the original ``TaskTracker``
behaviour — it updated task.status without raising a Spec-level audit event.)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import Task, TaskStatus


# ---------------------------------------------------------------------------
# Pure queries over state.tasks
# ---------------------------------------------------------------------------


def list_tasks_by_category(state, category: str) -> List[Task]:
    """Return every Task whose ``category`` matches."""
    return [t for t in state.tasks if t.category == category]


def list_tasks_by_status(state, status: TaskStatus) -> List[Task]:
    """Return every Task whose ``status`` matches."""
    return [t for t in state.tasks if t.status == status]


def list_tasks_by_spec(state, category: str, spec_name: str) -> List[Task]:
    """Return every Task belonging to a specific spec."""
    return [
        t for t in state.tasks
        if t.spec_category == category and t.spec_name == spec_name
    ]


def filter_tasks(state, criteria: Dict[str, Any]) -> List[Task]:
    """Filter tasks by ``category`` / ``status`` / ``spec_name`` / ``keywords``."""
    result = state.tasks
    if "category" in criteria:
        result = [t for t in result if t.category == criteria["category"]]
    if "status" in criteria:
        status = criteria["status"]
        if isinstance(status, str):
            status = TaskStatus(status)
        result = [t for t in result if t.status == status]
    if "spec_name" in criteria:
        result = [t for t in result if t.spec_name == criteria["spec_name"]]
    if "keywords" in criteria:
        keywords = criteria["keywords"].lower()
        result = [t for t in result if keywords in t.description.lower()]
    return result


def get_task_by_id(state, task_id: str) -> Optional[Task]:
    """Return the task whose id matches, or ``None``."""
    return next((t for t in state.tasks if t.id == task_id), None)


# ---------------------------------------------------------------------------
# Pure aggregations
# ---------------------------------------------------------------------------


def category_stats(state, category: str) -> Dict[str, int]:
    """Status counts for one category, derived from ``list_tasks_by_category``."""
    tasks = list_tasks_by_category(state, category)
    return {
        "total": len(tasks),
        "not_started": sum(1 for t in tasks if t.status == TaskStatus.NOT_STARTED),
        "queued": sum(1 for t in tasks if t.status == TaskStatus.QUEUED),
        "in_progress": sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
        "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
    }


def all_stats(state) -> Dict[str, Any]:
    """Counts grouped by category for the whole project."""
    return {
        "total_tasks": len(state.tasks),
        "not_started": sum(1 for t in state.tasks if t.status == TaskStatus.NOT_STARTED),
        "queued": sum(1 for t in state.tasks if t.status == TaskStatus.QUEUED),
        "in_progress": sum(1 for t in state.tasks if t.status == TaskStatus.IN_PROGRESS),
        "completed": sum(1 for t in state.tasks if t.status == TaskStatus.COMPLETED),
        "categories": {
            category: category_stats(state, category)
            for category in state.specs.keys()
        },
    }


# ---------------------------------------------------------------------------
# In-place mutations on state.tasks
# ---------------------------------------------------------------------------


def update_task_status(state, task_id: str, new_status: TaskStatus) -> bool:
    """Set the task's status in place. Return ``True`` if a task was updated."""
    for task in state.tasks:
        if task.id == task_id:
            task.status = new_status
            return True
    return False


def add_task_dependency(state, task_id: str, dependency_id: str) -> bool:
    """Append a dependency id to a task. Returns ``True`` if added."""
    for task in state.tasks:
        if task.id == task_id:
            if dependency_id not in task.dependencies:
                task.dependencies.append(dependency_id)
            return True
    return False
