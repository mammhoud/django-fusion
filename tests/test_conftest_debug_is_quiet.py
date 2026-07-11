"""Smoke tests guarding the conftest's `DJANGO_DEBUG_CONFTEST=1`
debug gate.

These tests fail the build if the conftest ever starts leaking
"CONFTEST DEBUG" output during normal pytest runs. Two layered
checks plus one positive control:

1. **Static** — assert the gate uses an exact `== "1"` match (not a
   truthy check that would leak on any non-empty value).
2. **Runtime (negative)** — spawn a subprocess pytest invocation
   with `DJANGO_DEBUG_CONFTEST` unset; assert that no `CONFTEST DEBUG`
   banner appears in stdout/stderr.
3. **Runtime (positive control)** — spawn a subprocess pytest
   invocation with `DJANGO_DEBUG_CONFTEST=1` set; assert that the
   banner DOES appear (so the negative test isn't tautologically
   true if someone breaks the gate to NEVER fire).

If anyone loosens the guard (truthy check, wrong value, or removes
it entirely), one or more of these tests will fail.

Subprocess tests use `pytest -s` to disable pytest's stdout capture
— otherwise pytest swallows the conftest banner into its capture
buffer and the test never sees the leak.
"""
import os
import subprocess
from pathlib import Path

# Walk up from this file until we find a `pyproject.toml` — that
# directory is the project root (used as `cwd` and `--project` for
# the uv subprocess).
_THIS_FILE = Path(__file__).resolve()
_TEST_PROJECT_ROOT = _THIS_FILE.parent
while not (_TEST_PROJECT_ROOT / "pyproject.toml").exists():
    parent = _TEST_PROJECT_ROOT.parent
    if parent == _TEST_PROJECT_ROOT:
        raise RuntimeError(
            "pyproject.toml not found above this test file; "
            "expected django-fusion project layout."
        )
    _TEST_PROJECT_ROOT = parent

# Always run a single real test file (fast for --collect-only, but
# also fine for a one-test run with -s). Falls back to any test_*.py
# in tests/ if test_form_components.py is missing.
def _pick_test_path() -> Path:
    primary = _THIS_FILE.parent / "test_form_components.py"
    if primary.exists():
        return primary
    for entry in sorted(os.listdir(_THIS_FILE.parent)):
        if entry.startswith("test_") and entry.endswith(".py"):
            return _THIS_FILE.parent / entry
    raise RuntimeError("No test_*.py file found in tests/ directory")


def _run_collect_subprocess(extra_env: dict[str, str]) -> str:
    """Run pytest in a subprocess with a controlled env, returning
    the combined stdout/stderr. `-s` disables pytest's stdout capture
    so the conftest banner appears in subprocess stdout."""
    env = os.environ.copy()
    env.pop("DJANGO_DEBUG_CONFTEST", None)  # baseline no-leak state
    env.update(extra_env)
    test_path = _pick_test_path()
    result = subprocess.run(
        [
            "uv", "run", "--project", str(_TEST_PROJECT_ROOT),
            "pytest", "--collect-only", "-q", "-s", str(test_path),
        ],
        cwd=str(_TEST_PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (result.stdout or "") + (result.stderr or "")


def test_conftest_debug_block_uses_exact_match_guard():
    """Static check: conftest's debug block must check
    `os.environ.get("DJANGO_DEBUG_CONFTEST") == "1"` with EXACT
    match.

    A truthy check (`if os.environ.get("DJANGO_DEBUG_CONFTEST"):`)
    would fire on any non-empty value (including bogus strings like
    "0") and silently leak debug output. Exact `== "1"` match is the
    only safe form.
    """
    conftest_path = _THIS_FILE.parent / "conftest.py"
    content = conftest_path.read_text()

    assert (
        'os.environ.get("DJANGO_DEBUG_CONFTEST") == "1"' in content
    ), (
        "conftest.py must guard the debug block with "
        '`os.environ.get("DJANGO_DEBUG_CONFTEST") == "1"` '
        "(exact-match, not truthy)."
    )


def test_conftest_does_not_leak_debug_in_normal_runs():
    """Runtime check (negative): with `DJANGO_DEBUG_CONFTEST` UNSET,
    running pytest in a fresh subprocess must NOT emit
    "CONFTEST DEBUG".

    Why subprocess? Pytest's `capsys` fixture only captures stdout
    INSIDE a test function — it cannot capture module-level
    `print()` calls that fire at conftest *import* time (which is
    before any test function runs). Spawning a subprocess gives a
    fresh pytest process whose full stdout/stderr we can inspect.
    """
    output = _run_collect_subprocess(extra_env={})
    assert "CONFTEST DEBUG" not in output, (
        "conftest.py leaked 'CONFTEST DEBUG' output during a normal "
        "pytest run (DJANGO_DEBUG_CONFTEST unset). The guard must be "
        "an exact `== '1'` check; a truthy `if env:` would also "
        "fire on random non-empty values.\n\n"
        f"Subprocess output:\n{output}"
    )


def test_conftest_debug_block_fires_when_env_var_set():
    """Runtime check (positive control): when `DJANGO_DEBUG_CONFTEST=1`
    IS set, the debug block must emit output.

    Without this test, a bug that breaks the guard to NEVER fire
    (e.g., `if env == "2":`, or accidentally inverting the condition)
    would still pass the negative leak test (no leak because never
    fires either way). This test ensures the debug output path is
    exercised at least once per CI run.
    """
    output = _run_collect_subprocess(extra_env={"DJANGO_DEBUG_CONFTEST": "1"})
    assert "CONFTEST DEBUG" in output, (
        "conftest.py failed to emit 'CONFTEST DEBUG' output even "
        "with DJANGO_DEBUG_CONFTEST=1 set — the guard is broken "
        "(e.g., wrong value match, inverted condition, or removed).\n\n"
        f"Subprocess output:\n{output}"
    )
