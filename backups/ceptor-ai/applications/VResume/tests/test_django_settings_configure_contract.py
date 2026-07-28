"""Unit test locking in `VResume` tests' `_django_settings.configure()` idempotency contract.

The contract (as documented in `tests/_django_settings.py`):

    `configure()` is idempotent by default — won't override an existing
    Django settings from an inherited `DJANGO_SETTINGS_MODULE`. Pass
    `only_if_unconfigured=False` to force a reset.

This test exercises that contract through **subprocess isolation** —
each scenario runs in a fresh Python interpreter with a clean
`django.conf.LazySettings` state.

Three scenarios (mirrors `applications/libs/django-fusion/tests/test_django_settings_configure_contract.py`):

1. **DJANGO_SETTINGS_MODULE unset** — `configure()` (default) should
   apply `TEST_SETTINGS` (`SECRET_KEY == "vresume-test-secret-key"`).
2. **DJANGO_SETTINGS_MODULE set to a fake parent module** —
   `configure()` (default) should be a **no-op** (parent's settings
   win, including our `IDEMPOTENCY_MARKER` sentinel).
3. **DJANGO_SETTINGS_MODULE set + `only_if_unconfigured=False`** —
   `configure()` should **force-apply** `TEST_SETTINGS` and wipe the
   parent module's marker.

Why subprocess?
  - Pytest's `capsys`/`monkeypatch` fixtures can't reset Django's
    global `LazySettings` between scenarios.
  - A subprocess gives each scenario a fresh `LazySettings` so the
    "real" before-configure state is observable.

Why `uv run python -c`, not pytest?
  - We deliberately do NOT trigger `conftest.py` in the subprocess —
    that would re-call `_django_settings.configure()` and obscure
    our controlled invocation.

Why `--project <workspace_root>` (the workspace `applications/`)?
  - `VResume/pyproject.toml` declares no runtime dependencies; the
    workspace `applications/pyproject.toml` is the source of truth
    for runtime deps (django, django-fusion).

Sentinel env-var transport
--------------------------
Reads inputs from env vars named with the `__DF_TEST_*__` convention
(double-underscore prefix + suffix, internal sentinel).
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


# ── Workspace-root discovery ──────────────────────────────────────────────────

_THIS_FILE = Path(__file__).resolve()
# Test file lives at `<workspace>/<site>/tests/test_*.py`. Workspace
# root (the directory holding `applications/pyproject.toml`) is 2
# levels up. Fixed by monorepo layout convention.
_TEST_WORKSPACE_ROOT = _THIS_FILE.parent.parent.parent
if not (_TEST_WORKSPACE_ROOT / "pyproject.toml").exists():
    raise RuntimeError(
        f"workspace pyproject.toml not found at {_TEST_WORKSPACE_ROOT}; "
        "expected VResume parent to be the workspace root."
    )

# tests/ must be on sys.path for `import _django_settings` to resolve
# inside the subprocess (the subprocess does NOT have conftest.py
# pre-loaded — `uv run python -c` bypasses pytest plugin discovery).
_TESTS_DIR = _THIS_FILE.parent
sys.path.insert(0, str(_TESTS_DIR))


# ── Sentinel env-var names ────────────────────────────────────────────────────
# Doubly-private (`__DF_TEST_*__`) so they cannot collide with real
# Python identifiers in the inline script or with real env vars set by
# Django / pytest / the OS.

_TEST_TESTS_DIR_ENV = "__DF_TEST_TESTS_DIR__"
_FAKE_PARENT_NAME_ENV = "__DF_TEST_FAKE_PARENT_NAME__"
_ONLY_IF_UNCONFIGURED_ENV = "__DF_TEST_ONLY_IF_UNCONFIGURED__"


# ── Sentinel fake parent module name (VResume-specific) ──────────────────────
_FAKE_PARENT_SETTINGS = "_fake_parent_settings_for_vresume_idempotency_test"


# ── Sentinel SECRET_KEY per site (matches `tests/_django_settings.TEST_SETTINGS`) ──
_TEST_SETTINGS_SECRET_KEY = "vresume-test-secret-key"


# ── Helper: spawn a subprocess, invoke configure(), parse JSON snapshot ──────

def _run_configure_subprocess(
    *,
    django_settings_module: str | None,
    only_if_unconfigured: bool,
    timeout: int = 30,
) -> dict:
    """Spawn a subprocess that imports `_django_settings`, calls
    `configure()` with the requested kwarg, then prints the resulting
    Django settings state as a `RESULT_JSON:{...}` line on stdout.
    """
    script = textwrap.dedent("""
        import json, os, sys, types

        # ── Sentinel env vars ───────────────────────────────────────────
        # `__DF_TEST_*__` keys are set by the parent test. They are NOT
        # legitimate Django / OS env vars — the double-underscores mark
        # them as test-only internal sentinels. Missing keys surface as
        # `KeyError` immediately at this point, which is the most
        # diagnosable failure mode if the parent ever drops one.

        fake_name = os.environ["__DF_TEST_FAKE_PARENT_NAME__"]
        only_if_unconfigured = (os.environ["__DF_TEST_ONLY_IF_UNCONFIGURED__"] == "1")

        fake = types.ModuleType(fake_name)
        fake.SECRET_KEY = "parent-secret-sentinel"
        fake.IDEMPOTENCY_MARKER = "configured-by-parent"
        sys.modules[fake_name] = fake

        sys.path.insert(0, os.environ["__DF_TEST_TESTS_DIR__"])

        from django.conf import settings

        if os.environ.get("DJANGO_SETTINGS_MODULE"):
            _ = settings.SECRET_KEY  # force lazy auto-configure from env

        import _django_settings
        _django_settings.configure(only_if_unconfigured=only_if_unconfigured)

        result = {
            "configured": settings.configured,
            "settings_module": str(settings.SETTINGS_MODULE),
            "secret_key": settings.SECRET_KEY,
            "marker": getattr(settings, "IDEMPOTENCY_MARKER", "<not-set>"),
        }
        print("RESULT_JSON:" + json.dumps(result))
    """).strip()

    env = os.environ.copy()
    env.pop("DJANGO_DEBUG_CONFTEST", None)
    if django_settings_module is None:
        env.pop("DJANGO_SETTINGS_MODULE", None)
    else:
        env["DJANGO_SETTINGS_MODULE"] = django_settings_module

    env[_TEST_TESTS_DIR_ENV] = str(_TESTS_DIR)
    env[_FAKE_PARENT_NAME_ENV] = _FAKE_PARENT_SETTINGS
    env[_ONLY_IF_UNCONFIGURED_ENV] = "1" if only_if_unconfigured else "0"

    completed = subprocess.run(
        [
            "uv", "run", "--project", str(_TEST_WORKSPACE_ROOT),
            "python", "-c", script,
        ],
        cwd=str(_TEST_WORKSPACE_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"subprocess failed (rc={completed.returncode})\n"
            f"--- stdout ---\n{completed.stdout}\n"
            f"--- stderr ---\n{completed.stderr}"
        )

    for line in reversed((completed.stdout or "").splitlines()):
        if line.startswith("RESULT_JSON:"):
            return json.loads(line[len("RESULT_JSON:"):])

    raise AssertionError(
        f"subprocess did not emit a RESULT_JSON line.\n"
        f"--- stdout ---\n{completed.stdout}\n"
        f"--- stderr ---\n{completed.stderr}"
    )


# ── Tests ────────────────────────────────────────────────────────────────────


def test_configure_applies_test_settings_when_django_settings_module_unset():
    """Scenario 1 — DJANGO_SETTINGS_MODULE NOT in env."""
    result = _run_configure_subprocess(
        django_settings_module=None,
        only_if_unconfigured=True,
    )
    assert result["secret_key"] == _TEST_SETTINGS_SECRET_KEY, (
        "configure() should apply TEST_SETTINGS.SECRET_KEY "
        f"({_TEST_SETTINGS_SECRET_KEY!r}) when no DJANGO_SETTINGS_MODULE "
        "is inherited. Got: " + repr(result)
    )
    assert result["marker"] == "<not-set>", (
        "TEST_SETTINGS does not define IDEMPOTENCY_MARKER, so after "
        "configure() applies TEST_SETTINGS the parent's marker should "
        "be absent. Got: " + repr(result)
    )


def test_configure_is_noop_when_parent_settings_module_inherited():
    """Scenario 2 — DJANGO_SETTINGS_MODULE set to a fake parent.

    The idempotency lock-in: a refactor that accidentally converts
    the early-return to `settings.configure(**TEST_SETTINGS)` would
    silently clobber any user-supplied settings.
    """
    result = _run_configure_subprocess(
        django_settings_module=_FAKE_PARENT_SETTINGS,
        only_if_unconfigured=True,
    )
    assert result["secret_key"] == "parent-secret-sentinel", (
        "configure() with the default `only_if_unconfigured=True` must "
        "be a no-op when DJANGO_SETTINGS_MODULE is inherited — but it "
        "clobbered SECRET_KEY with TEST_SETTINGS. Got: " + repr(result)
    )
    assert result["marker"] == "configured-by-parent", (
        "configure() must NOT wipe the parent's IDEMPOTENCY_MARKER in "
        "default mode. Got: " + repr(result)
    )
    assert result["settings_module"] == _FAKE_PARENT_SETTINGS, (
        "settings.SETTINGS_MODULE must still reflect the parent's "
        "module name (configure() should not have replaced it). "
        "Got: " + repr(result)
    )


def test_configure_force_overrides_when_only_if_unconfigured_false():
    """Scenario 3 — DJANGO_SETTINGS_MODULE set + caller forces reset."""
    result = _run_configure_subprocess(
        django_settings_module=_FAKE_PARENT_SETTINGS,
        only_if_unconfigured=False,
    )
    assert result["secret_key"] == _TEST_SETTINGS_SECRET_KEY, (
        f"configure(only_if_unconfigured=False) MUST apply "
        f"TEST_SETTINGS.SECRET_KEY ({_TEST_SETTINGS_SECRET_KEY!r}) even "
        "when settings were already configured. Got: " + repr(result)
    )
    assert result["marker"] == "<not-set>", (
        "After force-apply of TEST_SETTINGS, the parent's "
        "IDEMPOTENCY_MARKER must be gone (TEST_SETTINGS doesn't "
        "define it). Got: " + repr(result)
    )
