"""Spec progress tracking — pure operator functions over plain dicts/lists.

Decomposed from the legacy ``ProgressTracker`` class. State lives on
:class:`~.operators.OrchestratorState` (``specs`` and ``status_history``
fields). These functions operate on those fields directly without holding any
class-level caches.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from .models import Spec, TaskStatus


# ---------------------------------------------------------------------------
# Per-spec computation
# ---------------------------------------------------------------------------


def calculate_progress(spec: Spec) -> float:
    """Return the percentage (0..100) of completed tasks for one spec."""
    if not spec.tasks:
        return 0.0
    completed = sum(1 for t in spec.tasks if t.status == TaskStatus.COMPLETED)
    return (completed / len(spec.tasks)) * 100


def update_progress(spec: Spec) -> float:
    """Update ``spec.progress`` and ``last_updated`` in place; return the new value."""
    progress = calculate_progress(spec)
    spec.progress = progress
    spec.last_updated = datetime.now()
    return progress


def get_status(spec: Spec) -> str:
    """Map ``spec`` progress to ``not_started``/``in_progress``/``complete``."""
    progress = calculate_progress(spec)
    if progress == 0:
        return "not_started"
    if progress == 100:
        return "complete"
    return "in_progress"


def spec_progress_report(state, category: str, spec_name: str) -> Dict[str, Any]:
    """Detailed progress report for one spec on the state.

    Single canonical source of truth — supersedes the duplicated report
    that ``TaskTracker`` used to emit.
    """
    spec = state.specs.get(category, {}).get(spec_name)
    if not spec:
        return {}
    progress = calculate_progress(spec)
    counts = {
        "not_started": sum(1 for t in spec.tasks if t.status == TaskStatus.NOT_STARTED),
        "queued": sum(1 for t in spec.tasks if t.status == TaskStatus.QUEUED),
        "in_progress": sum(1 for t in spec.tasks if t.status == TaskStatus.IN_PROGRESS),
        "completed": sum(1 for t in spec.tasks if t.status == TaskStatus.COMPLETED),
    }
    return {
        "category": category,
        "spec_name": spec_name,
        "total_tasks": len(spec.tasks),
        "completed_tasks": counts["completed"],
        "progress_percentage": progress,
        "status": get_status(spec),
        "tasks_by_status": counts,
        "last_updated": spec.last_updated.isoformat(),
        "owner": spec.owner,
    }


# ---------------------------------------------------------------------------
# Aggregations across a category or all categories
# ---------------------------------------------------------------------------


def category_summary(specs_in_category: Dict[str, Spec]) -> Dict[str, Any]:
    """Aggregate progress over a single category's specs."""
    if not specs_in_category:
        return {
            "total_specs": 0,
            "complete_specs": 0,
            "in_progress_specs": 0,
            "not_started_specs": 0,
            "average_progress": 0.0,
        }

    total = len(specs_in_category)
    complete = in_progress = not_started = 0
    total_progress = 0.0
    for spec in specs_in_category.values():
        p = calculate_progress(spec)
        total_progress += p
        if p == 0:
            not_started += 1
        elif p == 100:
            complete += 1
        else:
            in_progress += 1

    return {
        "total_specs": total,
        "complete_specs": complete,
        "in_progress_specs": in_progress,
        "not_started_specs": not_started,
        "average_progress": total_progress / total,
    }


def overall_summary(state) -> Dict[str, Any]:
    """Aggregate progress across every loaded spec on the state."""
    total_specs = complete = in_progress = not_started = 0
    weighted_progress_sum = 0.0
    for specs_by_name in state.specs.values():
        s = category_summary(specs_by_name)
        total_specs += s["total_specs"]
        complete += s["complete_specs"]
        in_progress += s["in_progress_specs"]
        not_started += s["not_started_specs"]
        weighted_progress_sum += s["average_progress"] * s["total_specs"]
    return {
        "total_specs": total_specs,
        "complete_specs": complete,
        "in_progress_specs": in_progress,
        "not_started_specs": not_started,
        "average_progress": (weighted_progress_sum / total_specs) if total_specs else 0.0,
        "categories": {
            category: category_summary(specs)
            for category, specs in state.specs.items()
        },
    }


# ---------------------------------------------------------------------------
# Status-history audit log (lives on state.status_history)
# ---------------------------------------------------------------------------


def log_status_change(
    state,
    category: str,
    spec_name: str,
    old_status: str,
    new_status: str,
) -> None:
    """Append a Spec-level status change record to ``state.status_history``."""
    state.status_history.append({
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "spec_name": spec_name,
        "old_status": old_status,
        "new_status": new_status,
    })


def get_status_history(state) -> List[Dict[str, Any]]:
    """Return all logged Spec status changes, oldest first."""
    return list(state.status_history)


# ---------------------------------------------------------------------------
# Incomplete-spec listing
# ---------------------------------------------------------------------------


def list_incomplete_specs(state) -> List[Dict[str, Any]]:
    """Return specs whose progress is below 100%, with their missing task count."""
    incomplete: List[Dict[str, Any]] = []
    for category, specs_by_name in state.specs.items():
        for spec_name, spec in specs_by_name.items():
            progress = calculate_progress(spec)
            if progress < 100:
                incomplete.append({
                    "category": category,
                    "spec_name": spec_name,
                    "progress": progress,
                    "missing_tasks": sum(
                        1 for t in spec.tasks if t.status != TaskStatus.COMPLETED
                    ),
                })
    return incomplete
