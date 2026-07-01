"""Management-script integration — pure operators over :class:`ManagementState`.

Decomposed from the legacy :class:`ManagementScriptRunner` god-class. The
:class:`ManagementState` dataclass holds the canonical state:

- ``script_paths``: maps a script name (e.g. ``"manage-specs.sh"``) to its
  absolute filesystem path.
- ``execution_log``: accumulated output of every :func:`run_script` call,
  for later introspection via :func:`get_execution_log`.

Operators in this module mutate ``script_paths``-derived state in place and
return subprocess output dicts that mirror the legacy class's contract
bit-for-bit, including the same ``success``, ``returncode``, ``stdout``,
``stderr`` keys and the same TimeoutExpired / generic-exception mapping.

Naming intentionally omits the parent directory: callers do
``management.run_script(state, name, args)`` rather than
``management.management_run_script``. The parent package already implies
the domain.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State dataclass — canonical state container
# ---------------------------------------------------------------------------


@dataclass
class ManagementState:
    """Mutable container for the management-script runner.

    Construct via ``OrchestratorState.__post_init__`` (which seeds
    ``script_paths`` from ``OrchestratorConfig.script_paths``) or directly
    with ``ManagementState({"manage-specs.sh": "/abs/path", ...})``.
    """

    script_paths: Dict[str, str] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Subprocess operators — pure over :class:`ManagementState`
# ---------------------------------------------------------------------------


def run_script(
    state: ManagementState,
    script_name: str,
    args: List[str],
    timeout: int = 30,
) -> Dict[str, Any]:
    """Run ``script_path + args`` with capture_output, text, and a 30s timeout.

    Returns the same dict shape as the legacy :meth:`ManagementScriptRunner.run_script`:

    - On success (``returncode == 0``): ``{success: True, script, args, returncode, stdout, stderr}``.
      The dict is also appended to ``state.execution_log``.
    - On missing config: ``{success: False, error: "Script path not configured: <name>"}``.
    - On :class:`subprocess.TimeoutExpired`: ``{success: False, script, error: "Script execution timed out"}``.
    - On any other exception: ``{success: False, script, error: str(exc)}``.

    Never raises; all failures are folded into the returned error dict.
    """
    script_path = state.script_paths.get(script_name)
    if not script_path:
        return {
            "script": script_name,
            "success": False,
            "error": f"Script path not configured: {script_name}",
        }
    try:
        cmd = [script_path] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = {
            "script": script_name,
            "args": args,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
        state.execution_log.append(output)
        return output
    except subprocess.TimeoutExpired:
        return {
            "script": script_name,
            "success": False,
            "error": "Script execution timed out",
        }
    except Exception as exc:
        return {
            "script": script_name,
            "success": False,
            "error": str(exc),
        }


def list_specs(
    state: ManagementState,
    category: Optional[str] = None,
) -> List[str]:
    """List specs via ``manage-specs.sh list [category]``.

    Successful output is split on ``"\\n"`` and stripped. Failures return an
    empty list (matching the legacy contract — silent on failure).
    """
    args = ["list"]
    if category:
        args.append(category)
    result = run_script(state, "manage-specs.sh", args)
    if result.get("success"):
        return [
            line.strip()
            for line in result.get("stdout", "").split("\n")
            if line.strip()
        ]
    return []


def check_duplicates(state: ManagementState) -> Dict[str, List[Tuple[str, str]]]:
    """Run ``check-duplicates.py`` and parse the JSON output."""
    result = run_script(state, "check-duplicates.py", [])
    if result.get("success"):
        try:
            return json.loads(result.get("stdout", "{}"))
        except json.JSONDecodeError:
            return {}
    return {}


def find_similar_specs(
    state: ManagementState,
    spec_name: str,
) -> List[Tuple[str, str]]:
    """Ask ``check-duplicates.py`` for specs similar to ``spec_name``."""
    result = run_script(state, "check-duplicates.py", ["--find-similar", spec_name])
    if result.get("success"):
        try:
            data = json.loads(result.get("stdout", "[]"))
            return [(item[0], item[1]) for item in data]
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def suggest_category(state: ManagementState, spec_name: str) -> List[str]:
    """Ask ``check-duplicates.py`` for category suggestions for ``spec_name``."""
    result = run_script(state, "check-duplicates.py", ["--suggest-category", spec_name])
    if result.get("success"):
        try:
            return json.loads(result.get("stdout", "[]"))
        except json.JSONDecodeError:
            return []
    return []


def add_category_context(
    state: ManagementState,
    category: str,
    spec_name: str,
) -> bool:
    """Add ``category`` context to ``spec_name`` via ``add-category-context.py``."""
    result = run_script(
        state,
        "add-category-context.py",
        ["--category", category, "--spec", spec_name],
    )
    return result.get("success", False)


def get_stats(state: ManagementState) -> Dict[str, Any]:
    """Run ``manage-specs.sh stats`` and parse the JSON output."""
    result = run_script(state, "manage-specs.sh", ["stats"])
    if result.get("success"):
        try:
            return json.loads(result.get("stdout", "{}"))
        except json.JSONDecodeError:
            return {}
    return {}


def get_execution_log(state: ManagementState) -> List[Dict[str, Any]]:
    """Return the recorded execution log. Reference, not a snapshot."""
    return state.execution_log


def clear_execution_log(state: ManagementState) -> None:
    state.execution_log = []


__all__ = [
    "ManagementState",
    "run_script",
    "list_specs",
    "check_duplicates",
    "find_similar_specs",
    "suggest_category",
    "add_category_context",
    "get_stats",
    "get_execution_log",
    "clear_execution_log",
]
