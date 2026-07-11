"""Unit test locking in `_django_settings.configure()` idempotency contract.

The contract (as documented in `tests/_django_settings.py`):

    `configure()` is idempotent by default — won't override an existing
    Django settings from an inherited `DJANGO_SETTINGS_MODULE`. Pass
    `only_if_unconfigured=False` to force a reset.

This test exercises that contract through **subprocess isolation** —
each scenario runs in a fresh Python interpreter with a clean
`django.conf.LazySettings` state. (Inside a single pytest process,
Django's `LazySettings` is sticky; we can't easily observe the
"before configure()" state.)

Three scenarios:

1. **DJANGO_SETTINGS_MODULE unset** — `configure()` (default) should
   apply `TEST_SETTINGS` (`SECRET_KEY == "test-secret-key"`).
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
    our controlled invocation. Pure `python -c` keeps the test path
    minimal and the observation clean.

Sentinel env-var transport
--------------------------
The subprocess reads its control inputs from env vars whose names
follow the `__DF_TEST_*__` convention (double-underscore prefix +
suffix). This is unambiguous to readers as "test-only internal
sentinel — do not touch":

    __DF_TEST_FAKE_PARENT_NAME__   → fake parent module name
    __DF_TEST_ONLY_IF_UNCONFIGURED__ → "1" or "0"
    __DF_TEST_TESTS_DIR__          → absolute path to tests/

We chose env vars over the prior `script.replace()` mechanism because:
  - `"__DF_TEST_*__"` cannot accidentally match a real Python
    identifier inside the inline script (so a future code edit
    won't silently break the threading).
  - `"__DF_TEST_*__"` cannot accidentally match a real env var set
    by Django, pytest, or the OS (so a pollution in CI env won't
    silently override the test's expected controls).
  - The subprocess reads the values via `os.environ["..."]` —
    failures (missing keys) surface immediately as `KeyError`
    at the subprocess startup, which is the most diagnosable
    failure mode.
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


# ── Project-root discovery (same pattern as test_conftest_debug_is_quiet.py) ──

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

# tests/ must be on sys.path for `import _django_settings` to resolve
# inside the subprocess (the subprocess does NOT have conftest.py
# pre-loaded — `uv run python -c` bypasses pytest plugin discovery).
_TESTS_DIR = _THIS_FILE.parent
sys.path.insert(0, str(_TESTS_DIR))


# ── Sentinel env-var names (referenced from both ends of the transport) ──────
# The actual env var names live in this single block. Anyone who changes
# one MUST change it in lock-step in `_run_configure_subprocess()` below.

_TEST_TESTS_DIR_ENV = "__DF_TEST_TESTS_DIR__"
_FAKE_PARENT_NAME_ENV = "__DF_TEST_FAKE_PARENT_NAME__"
_ONLY_IF_UNCONFIGURED_ENV = "__DF_TEST_ONLY_IF_UNCONFIGURED__"


# ── Sentinel fake parent module name ────────────────────────────────────────
# Pre-injected into the subprocess's `sys.modules` so Django's lazy
# auto-load from `DJANGO_SETTINGS_MODULE` succeeds without filesystem
# side-channel files. The same string is passed via the
# `__DF_TEST_FAKE_PARENT_NAME__` env var.
_FAKE_PARENT_SETTINGS = "_fake_parent_settings_for_idempotency_test"


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

    Args:
        django_settings_module:
            - None: subprocess starts with NO `DJANGO_SETTINGS_MODULE`
              env var (so Django's lazy auto-configure sees no source).
            - str: subprocess starts WITH `DJANGO_SETTINGS_MODULE=<str>`
              env var. Our helper pre-injects that exact name into
              `sys.modules` as a fake module, so the auto-load succeeds.
        only_if_unconfigured: forwarded verbatim to `configure()`.

    Returns:
        dict with keys: `configured`, `settings_module`,
        `secret_key`, `marker` — the snapshot.
    """
    script = textwrap.dedent("""
        import json, os, sys, types

        # ── Sentinel env vars ───────────────────────────────────────────
        # `__DF_TEST_*__` keys are set by the parent test. They are NOT
        # legitimate Django / OS env vars — the double-underscores mark
        # them as test-only internal sentinels. Missing keys surface as
        # `KeyError` immediately at this point in the subprocess, which
        # is the most diagnosable failure mode if the parent ever
        # drops one.

        fake_name = os.environ["__DF_TEST_FAKE_PARENT_NAME__"]
        only_if_unconfigured = (os.environ["__DF_TEST_ONLY_IF_UNCONFIGURED__"] == "1")

        # 1. Pre-inject a fake "parent" django settings module into
        #    `sys.modules` BEFORE django tries to autoconfigure. The
        #    Django lazy loader will find this in `sys.modules`
        #    (avoiding filesystem deps).
        fake = types.ModuleType(fake_name)
        fake.SECRET_KEY = "parent-secret-sentinel"
        fake.IDEMPOTENCY_MARKER = "configured-by-parent"
        sys.modules[fake_name] = fake

        # 2. Make `tests/` importable so `import _django_settings` works.
        sys.path.insert(0, os.environ["__DF_TEST_TESTS_DIR__"])

        # 3. Import django settings. If the env has `DJANGO_SETTINGS_MODULE`
        #    set to our fake module name, Django's lazy auto-configure
        #    fires on first attribute access below.
        from django.conf import settings

        if os.environ.get("DJANGO_SETTINGS_MODULE"):
            _ = settings.SECRET_KEY  # force lazy auto-configure from env

        # 4. Hand off to `_django_settings.configure()` with the test's
        #    controlled kwarg. This is the unit under test.
        import _django_settings
        _django_settings.configure(only_if_unconfigured=only_if_unconfigured)

        # 5. Emit a single JSON line the parent test can parse. The
        #    "marker" key uses `getattr` with a sentinel default so we
        #    can detect when TEST_SETTINGS overrode the parent module
        #    (which doesn't define `IDEMPOTENCY_MARKER`).
        result = {
            "configured": settings.configured,
            "settings_module": str(settings.SETTINGS_MODULE),
            "secret_key": settings.SECRET_KEY,
            "marker": getattr(settings, "IDEMPOTENCY_MARKER", "<not-set>"),
        }
        print("RESULT_JSON:" + json.dumps(result))
    """).strip()

    env = os.environ.copy()
    # Drop knobs that would interfere with the controlled behavior:
    env.pop("DJANGO_DEBUG_CONFTEST", None)  # conftest's banner toggle
    if django_settings_module is None:
        env.pop("DJANGO_SETTINGS_MODULE", None)
    else:
        env["DJANGO_SETTINGS_MODULE"] = django_settings_module

    # Set the sentinel control vars. These all use the `__DF_TEST_*__`
    # double-underscore convention so they cannot collide with real
    # Django/OS env vars or with Python identifiers in the inline script.
    env[_TEST_TESTS_DIR_ENV] = str(_TESTS_DIR)
    env[_FAKE_PARENT_NAME_ENV] = _FAKE_PARENT_SETTINGS
    # "1"/"0" string transport reads as a real bool at the subprocess
    # (`os.environ[...] == "1"`), so the subprocess sees a clean Python
    # bool — not `str(bool)`'s literal "True"/"False" string.
    env[_ONLY_IF_UNCONFIGURED_ENV] = "1" if only_if_unconfigured else "0"

    completed = subprocess.run(
        [
            "uv", "run", "--project", str(_TEST_PROJECT_ROOT),
            "python", "-c", script,
        ],
        cwd=str(_TEST_PROJECT_ROOT),
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

    # Parse the trailing RESULT_JSON:{...} line.
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
    """Scenario 1 — DJANGO_SETTINGS_MODULE NOT in env.

    Django's lazy loader has nothing to autoload → `settings.configured`
    is False → `configure()` (default) applies TEST_SETTINGS → SECRET_KEY
    is "test-secret-key" and IDEMPOTENCY_MARKER is absent.
    """
    result = _run_configure_subprocess(
        django_settings_module=None,
        only_if_unconfigured=True,
    )
    assert result["secret_key"] == "test-secret-key", (
        "configure() should apply TEST_SETTINGS.SECRET_KEY when no "
        "DJANGO_SETTINGS_MODULE is inherited. Got: " + repr(result)
    )
    assert result["marker"] == "<not-set>", (
        "TEST_SETTINGS does not define IDEMPOTENCY_MARKER, so after "
        "configure() applies TEST_SETTINGS the parent's marker should "
        "be absent. Got: " + repr(result)
    )


def test_configure_is_noop_when_parent_settings_module_inherited():
    """Scenario 2 — DJANGO_SETTINGS_MODULE set to a fake parent.

    Django's lazy loader autoloads the (pre-injected) fake module →
    `settings.configured` is True → `configure()` (default) sees
    `settings.configured` and returns early → parent's SECRET_KEY
    and IDEMPOTENCY_MARKER survive.

    This is the **idempotency lock-in**: a refactor that accidentally
    converts the early-return to `settings.configure(**TEST_SETTINGS)`
    would silently clobber any user-supplied settings.
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
    """Scenario 3 — DJANGO_SETTINGS_MODULE set + caller forces reset.

    Even with `settings.configured=True` from auto-load,
    `configure(only_if_unconfigured=False)` MUST skip the guard and
    apply TEST_SETTINGS. This is the explicit "I want a clean slate"
    path — a refactor that drops this kwarg would silently behave
    like the default (no-op), breaking consumers that rely on it
    (e.g., tests that need stable settings between runs).
    """
    result = _run_configure_subprocess(
        django_settings_module=_FAKE_PARENT_SETTINGS,
        only_if_unconfigured=False,
    )
    assert result["secret_key"] == "test-secret-key", (
        "configure(only_if_unconfigured=False) MUST apply TEST_SETTINGS "
        "even when settings were already configured. Got: "
        + repr(result)
    )
    assert result["marker"] == "<not-set>", (
        "After force-apply of TEST_SETTINGS, the parent's "
        "IDEMPOTENCY_MARKER must be gone (TEST_SETTINGS doesn't "
        "define it). Got: " + repr(result)
    )
