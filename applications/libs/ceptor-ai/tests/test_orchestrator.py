"""Lightweight Hypothesis-based property tests for the orchestrator.

These tests intentionally pick up partial-failure cases that broke under prior
refactors — covering both progress aggregation pins and tracker-side no-op
pins:

* Missing category / missing spec when computing
  ``progress.spec_progress_report``, ``progress.category_summary``, and
  ``progress.overall_summary``.
* Unknown task id when calling ``tracker.update_task_status``, plus four
  tracker aggregation surfaces whose missing-input contracts are pinned
  alongside as no-op or empty-list returns.

Future refactors must keep returning the same empty-dict / ``False`` / ``[]`` shape
on these edges; if anyone "improves" the partial-failure contract without
updating these tests, the suite fails immediately. That is the *pin* the
tests provide.

The full random search space stays small (``max_examples=10``) — the goal is
to lock the edge case in place, not to explore invariants.
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st
from hypothesis.strategies import composite

from ceptor_ai.orchestrator.config import OrchestratorConfig
from ceptor_ai.orchestrator.errors import RecoveryState, get_recovery_history
from ceptor_ai.orchestrator.models import Spec, SpecStatus, Task, TaskStatus
from ceptor_ai.orchestrator.operators import OrchestratorState
from ceptor_ai.orchestrator.progress import (
    category_summary,
    overall_summary,
    spec_progress_report,
)
from ceptor_ai.orchestrator.tracker import (
    filter_tasks,
    list_tasks_by_category,
    list_tasks_by_status,
    update_task_status,
)


# Lightweight profile honours the user's "lightweight" request: 10 examples
# per property, no deadline pressure for Hypothesis's shrinker to evaluate.
settings.register_profile(
    "lightweight",
    max_examples=10,
    deadline=None,
    derandomize=False,
    print_blob=False,
)
settings.load_profile("lightweight")


def _empty_state() -> OrchestratorState:
    """Fresh, empty ``OrchestratorState`` for each test."""
    return OrchestratorState(config=OrchestratorConfig())


# ---------------------------------------------------------------------------
# progress.* — pin: missing category returns {} / zero-summary
# ---------------------------------------------------------------------------


def test_spec_progress_report_returns_empty_on_missing_category() -> None:
    """``spec_progress_report`` returns ``{}`` for any (category, spec_name)
    pair the state doesn't have — never ``None``, never a partial dict,
    never a raised exception.

    Pins the legacy ``ProgressTracker`` contract.  A future refactor that
    changes "missing-category returns empty dict" to "raises KeyError" or
    "returns None" will fail this test immediately.
    """
    state = _empty_state()
    assert spec_progress_report(state, "__missing_category__", "any_spec") == {}
    assert spec_progress_report(state, "__missing_category_under_dummy__", "__missing_spec__") == {}


def test_category_summary_on_empty_input_returns_zero_summary() -> None:
    """``category_summary({})`` returns the canonical zero-summary.

    Pins the missing-category contract for the aggregation operator: an
    empty / unknown category must yield ``total_specs == 0`` and
    ``average_progress == 0.0``, *not* a ``ZeroDivisionError`` from the
    naive division by zero in the averaging step.
    """
    assert category_summary({}) == {
        "total_specs": 0,
        "complete_specs": 0,
        "in_progress_specs": 0,
        "not_started_specs": 0,
        "average_progress": 0.0,
    }


def test_overall_summary_on_empty_state_returns_zero_summary() -> None:
    """``overall_summary(<empty state>)`` returns the canonical zero-summary.

    Pins the third missing-category aggregation surface: the averaging path
    in ``overall_summary`` must guard against division-by-zero for an empty
    ``state.specs`` map.  A naive ``weighted_progress_sum / total_specs``
    would raise ``ZeroDivisionError``; the canonical guard returns 0.0.
    """
    assert overall_summary(_empty_state()) == {
        "total_specs": 0,
        "complete_specs": 0,
        "in_progress_specs": 0,
        "not_started_specs": 0,
        "average_progress": 0.0,
        "categories": {},
    }


# ---------------------------------------------------------------------------
# tracker.update_task_status — pin: unknown id is no-op returning False
# ---------------------------------------------------------------------------


def test_update_task_status_unknown_id_returns_false_and_does_not_mutate() -> None:
    """``update_task_status`` returns ``False`` and never reclassifies any
    task when ``task_id`` is not in ``state.tasks``.

    Pins the legacy ``TaskTracker.update_task_status`` contract: unknown
    ids must be a silent no-op (returning ``False``), not a crash and not a
    spurious status flip.  Run for every ``TaskStatus`` value so a
    refactor that special-cases, say, only ``COMPLETED`` will be caught.
    """
    state = _empty_state()
    for new_status in TaskStatus:
        result = update_task_status(
            state,
            "__definitely_not_a_real_id__",
            new_status,
        )
        assert result is False
        assert all(t.status != new_status for t in state.tasks)


# ---------------------------------------------------------------------------
# tracker.* — pin: missing-input aggregation surfaces return []
# ---------------------------------------------------------------------------


def test_list_tasks_by_category_returns_empty_for_missing_category() -> None:
    """``list_tasks_by_category`` returns ``[]`` for any category the state
    has no tasks under.  Pins the partial-failure contract from the legacy
    ``TaskTracker``.
    """
    assert list_tasks_by_category(_empty_state(), "__missing_category__") == []


def test_list_tasks_by_status_returns_empty_on_empty_state() -> None:
    """``list_tasks_by_status`` returns ``[]`` for any status on an empty
    state.  A naive implementation could special-case ``COMPLETED`` or
    attempt to count tasks before filtering — this pin locks the simple
    comprehension semantics.
    """
    assert list_tasks_by_status(_empty_state(), TaskStatus.COMPLETED) == []


def test_filter_tasks_returns_empty_for_missing_category_filter() -> None:
    """``filter_tasks`` with a single ``category`` key whose value is absent
    from the state returns ``[]``, mirroring the missing-category pin in
    ``progress.spec_progress_report`` so the partial-failure contract is
    consistent across both modules.
    """
    assert filter_tasks(_empty_state(), {"category": "__missing_category__"}) == []


def test_get_recovery_history_returns_empty_on_empty_recovery_state() -> None:
    """``get_recovery_history`` returns ``[]`` for a fresh ``RecoveryState``
    — the third missing-input aggregation surface.  The recovery-history
    log lives in :mod:`orchestrator.errors` (where the dataclass moved
    under the recent decomposition); this pin locks the empty-state
    contract so a future refactor that adds hidden initialisation cannot
    silently introduce entries.
    """
    assert get_recovery_history(RecoveryState()) == []


# ---------------------------------------------------------------------------
# Slim Hypothesis-based round-trip — variation across random spec trees
# ---------------------------------------------------------------------------


# Restrict generated ids to URL-safe ascii so failure messages stay diff-able
# and "obviously fake" sentinels (those starting with ``__``) cannot collide.
_safe_id = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), max_codepoint=127),
    min_size=1,
    max_size=8,
).filter(lambda s: not s.startswith("_"))


@composite
def spec_with_tasks(draw) -> Spec:
    """Build a small Spec with realistic structure but minimal variation.

    Only ``category`` / ``spec_name`` / task ``id`` fields vary; every
    other dataclass field is filled with stable defaults so the test
    exercises the progress + tracker functions, not model construction.
    """
    category = draw(_safe_id)
    spec_name = draw(_safe_id)
    task_count = draw(st.integers(min_value=0, max_value=5))
    tasks = [
        Task(
            id=draw(_safe_id),
            description="",
            status=TaskStatus.NOT_STARTED,
            category=category,
            spec_name=spec_name,
            spec_category=category,
            requirements_traceability=[],
        )
        for _ in range(task_count)
    ]
    return Spec(
        category=category,
        spec_name=spec_name,
        introduction="",
        glossary={},
        requirements=[],
        design=None,
        tasks=tasks,
        status=SpecStatus.NOT_STARTED,
    )


@settings(max_examples=10)
@given(specs_list=st.lists(spec_with_tasks(), min_size=1, max_size=3))
def test_update_task_status_first_known_task_round_trips(specs_list) -> None:
    """For the first task in a randomly built state, ``update_task_status``
    returns ``True`` and the new status is reflected on that task;
    a subsequent ``update_task_status`` for an unknown id does **not**
    flip it back.
    """
    state = _empty_state()
    for spec in specs_list:
        state.specs.setdefault(spec.category, {})[spec.spec_name] = spec
        state.tasks.extend(spec.tasks)

    target_task = state.tasks[0]
    new_status = TaskStatus.COMPLETED

    # Real id, real update.
    assert update_task_status(state, target_task.id, new_status) is True
    assert target_task.status == new_status

    # Unknown id does not flip the real task.
    update_task_status(state, "__no_such_task__", TaskStatus.NOT_STARTED)
    assert target_task.status == new_status


@settings(max_examples=10)
@given(specs_list=st.lists(spec_with_tasks(), min_size=1, max_size=3))
def test_spec_progress_report_unknown_category_remains_empty_among_loaded_data(
    specs_list,
) -> None:
    """Even when the state has plenty of loaded specs, querying a category
    that isn't there must still return ``{}`` — no leakage from siblings.
    """
    state = _empty_state()
    for spec in specs_list:
        state.specs.setdefault(spec.category, {})[spec.spec_name] = spec
        state.tasks.extend(spec.tasks)

    assert (
        spec_progress_report(state, "__never_present__", "any_spec") == {}
    )
