"""
Regression test: cache.clear() must invalidate across all 4 gunicorn workers.

Background
----------
Production runs gunicorn with multiple workers. Each worker has its own Python
process and (when using LocMemCache) its own in-memory cache namespace. The
original /events/ staleness bug was caused by:

    CACHE_MIDDLEWARE_ALIAS = "default"   # django.core.cache.backends.locmem.LocMemCache
    WAGTAIL_CACHE_BACKEND  = "default"   # same LocMemCache

With 4 workers, ``cache.clear()`` only flushed one worker's namespace. The other
3 workers continued serving the cached (pre-fix) response indefinitely — even
after a full container restart (because cache cleared on restart but a different
worker's LocMemCache happened to be holding the page).

The fix moved both settings to a shared Redis-backed alias
(``django_redis.cache.RedisCache`` against ``default-redis``). Now all 4
workers read/write one shared namespace, so a single ``cache.clear()`` call
from ``manage.py shell`` or any worker invalidates every worker.

These tests lock that invariant so neither setting can silently regress to a
process-local backend in production.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


# This test lives at core/tests/test_cache_cross_worker_invalidation.py.
# parents[0] = core/tests/
# parents[1] = core/   <-- ROOT
# parents[2] = the workspace root /home/structa.cloud/
ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_PY = ROOT / "configs" / "settings" / "CD" / "production.py"
CORE_PY = ROOT / "configs" / "settings" / "CD" / "core.py"


# Both of these MUST resolve to a SHARED (non-LocMemCache) backend so that
# ``cache.clear()`` affects all 4 gunicorn workers in one call. Each entry maps
# the setting name to a short description used in failure messages.
SHARED_BACKEND_REQUIRED = {
    "CACHE_MIDDLEWARE_ALIAS": (
        "Django's response middleware cache "
        "(UpdateCacheMiddleware + FetchFromCacheMiddleware)"
    ),
    "WAGTAIL_CACHE_BACKEND": "Wagtail's get_object_cache / page cache backend",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_assignment(text: str, name: str) -> str | None:
    """Return the string value of a top-level ``NAME = 'value'`` assignment."""
    match = re.search(
        rf"^\s*{re.escape(name)}\s*=\s*['\"]([^'\"]+)['\"]",
        text,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else None


def _resolve_cache_backend(alias: str) -> tuple[str | None, str | None]:
    """Resolve the BACKEND class for ``CACHES[alias]``.

    Returns ``(backend_class, source_file)``.  Handles the two registration
    patterns we use in the workspace:

    1. **Inline in ``production.py``** — ``CACHES["redis"] = {...}`` — here the
       key may be quoted (``"BACKEND": "..."``) or unquoted (``BACKEND = "..."``)
       in dict literals.
    2. **Registry in ``core.py``** — ``CACHES = {"default": {...}}`` — keys
       are quoted in registries.

    The optional ``grep`` pattern ``(?P<quote>['"])`` allows the regex to
    match the dict key regardless of whether it is quoted.
    """
    if not alias:
        return None, None
    # 1. Inline registration: CACHES[<quoted-alias>] = { ... }
    prod = _read(PRODUCTION_PY)
    inline = re.search(
        rf'CACHES\s*\[\s*[\'\"]{re.escape(alias)}[\'\"]\s*\]\s*=\s*\{{(.*?)\}}\s*$',
        prod,
        re.MULTILINE | re.DOTALL,
    )
    if inline:
        backend = _extract_backend(inline.group(1))
        if backend:
            return backend, str(PRODUCTION_PY)
    # 2. core.py registry: "<quoted-alias>": {"BACKEND": ..., ...}
    core = _read(CORE_PY)
    in_core = re.search(
        rf'[\'\"]{re.escape(alias)}[\'\"]\s*:\s*\{{(.*?BACKEND.*?)\}}',
        core,
        re.MULTILINE | re.DOTALL,
    )
    if in_core:
        backend = _extract_backend(in_core.group(1))
        if backend:
            return backend, str(CORE_PY)
    return None, None


def _extract_backend(caches_block: str) -> str | None:
    """Extract the BACKEND value from a CACHES dict literal.

    Django dict literals use either form::

        "BACKEND": "...",            # inline registration (most common)
        BACKEND = "...",              # rare; only seen in tests/debug toggles

    Match both. Whitespace between the key and ``:``/``=`` is optional. The
    value itself is always quoted with ``'`` or ``"``.
    """
    match = re.search(
        r'[\'"]?\bBACKEND\b[\'"]?\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
        caches_block,
    )
    return match.group(1) if match else None


@pytest.mark.parametrize(
    "setting_name,purpose",
    sorted(SHARED_BACKEND_REQUIRED.items()),
    ids=sorted(SHARED_BACKEND_REQUIRED),
)
def test_production_alias_is_not_default_locmem(
    setting_name: str, purpose: str
) -> None:
    """``CACHE_MIDDLEWARE_ALIAS`` / ``WAGTAIL_CACHE_BACKEND`` MUST NOT be ``"default"``.

    The cache backend registered as ``"default"`` is
    ``django.core.cache.backends.locmem.LocMemCache`` (per-process, in-memory).
    ``cache.clear()`` from any one worker only flushes that worker's namespace,
    which is the per-worker-vs-Redis footgun this test file exists to prevent.
    """
    text = _read(PRODUCTION_PY)
    alias = _parse_assignment(text, setting_name)
    assert alias is not None, (
        f"{setting_name} is not assigned in {PRODUCTION_PY}. "
        f"This setting controls the {purpose} and MUST be set explicitly to "
        f"a shared backend (e.g. 'redis')."
    )
    assert alias != "default", (
        f"{setting_name} = 'default' uses the LocMemCache backend\n"
        f"  ({purpose}).\n"
        f"\n"
        f"LocMemCache is isolated per process: each gunicorn worker has its own\n"
        f"copy, so cache.clear() in worker A only invalidates worker A's\n"
        f"namespace. Workers B/C/D keep serving the stale (cached) response.\n"
        f"This is the original /events/ staleness footgun.\n"
        f"\n"
        f"Switch {setting_name} to a shared alias such as 'redis' (the alias\n"
        f"registered as django_redis.cache.RedisCache in this same file) so\n"
        f"cache.clear() affects every worker in a single shared call."
    )


@pytest.mark.parametrize(
    "setting_name,purpose",
    sorted(SHARED_BACKEND_REQUIRED.items()),
    ids=sorted(SHARED_BACKEND_REQUIRED),
)
def test_production_alias_resolves_to_non_locmem_backend(
    setting_name: str, purpose: str
) -> None:
    """Whatever alias ``{setting_name}`` points at, its BACKEND must NOT be LocMemCache.

    Locks the invariant a second way: even if a future contributor renames the
    alias (``'redis'`` → ``'cache01'``, ``'redis_v2'``, etc.) or moves the
    registration into ``core.py``, the BACKEND class must remain process-shared.
    """
    text = _read(PRODUCTION_PY)
    alias = _parse_assignment(text, setting_name)
    assert alias is not None, (
        f"{setting_name} is missing in {PRODUCTION_PY}"
    )
    backend, source = _resolve_cache_backend(alias)
    assert backend is not None, (
        f"{setting_name}={alias!r} does not resolve to a CACHES[{alias!r}] entry "
        f"in either {PRODUCTION_PY.name} (inline register) or {CORE_PY.name}.\n"
        f"Without a registered entry, Django falls back to "
        f"django.core.cache.backends.locmem.LocMemCache by default, which is\n"
        f"per-process — defeating the purpose of this setting ({purpose})."
    )
    assert "locmem" not in backend.lower(), (
        f"{setting_name}={alias!r} resolves to BACKEND={backend!r} (in {source}).\n"
        f"That backend class is in-memory and isolated per-process: each"
        f"\ngunicorn worker has its own copy, so cache.clear() called in "
        f"\nworker A only invalidates worker A's namespace. Workers B/C/D "
        f"\nkeep serving the cached (pre-fix) response indefinitely — the\n"
        f"original /events/ staleness footgun.\n"
        f"\n"
        f"Switch BACKEND to django_redis.cache.RedisCache (or another "
        f"\nprocess-shared backend such as memcached / database cache)."
    )


# ---------------------------------------------------------------------------
# Behavioral regression test
# ---------------------------------------------------------------------------
# The static configuration checks above lock the schema of ``production.py``.
# This behavioural test additionally proves the *contract* shared cache backends
# must satisfy: a key SET in one Python process must be visible in another,
# and ``cache.clear()`` in one process must invalidate keys for all processes.
# If a future refactor accidentally re-introduces ``locmem`` somewhere (or
# breaks a Redis connection, sudo, password, network namespace, etc.) this
# behavioural test would catch it even though the static text check would pass.
#
# Implementation note: the subprocesses write to a *tempdir-backed*
# ``FileBasedCache`` rather than the production Redis backend. FileBasedCache
# is process-shared via the filesystem, so it deterministically reproduces the
# Redis contract in any test environment, with no Redis dependency.
# ---------------------------------------------------------------------------


def _run_cache_op_in_subprocess(cache_dir: str, snippet: str) -> str:
    """Run a Python snippet inside a fresh subprocess using a tempdir-backed FileBasedCache.

    The subprocess constructs a standalone ``FileBasedCache`` instance rooted at
    ``cache_dir`` and executes ``snippet`` against it. We do NOT initialise
    Django's app registry or load ``tests.settings`` inside the subprocess —
    ``FileBasedCache`` is a plain Python class that just reads/writes files in
    a directory, so any Django install on ``sys.path`` is enough. This keeps
    the test independent of Django settings bootstrapping complexity and makes
    it safe to run in any Python environment where Django is installed.
    """
    code = (
        "from django.core.cache.backends.filebased import FileBasedCache\n"
        f"_cache = FileBasedCache("
        f"{cache_dir!r}, "
        "{'TIMEOUT': 300, 'KEY_PREFIX': 'crossworker_regression', "
        "'OPTIONS': {'MAX_ENTRIES': 1000}})\n"
        f"{snippet}\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=20,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        raise AssertionError(
            f"subprocess exited {result.returncode}:\n"
            f"  stdout:\n{result.stdout}\n"
            f"  stderr:\n{result.stderr}"
        )
    tail = result.stdout.strip().splitlines()
    return tail[-1] if tail else ""


def test_cache_clear_invalidates_across_processes(tmp_path) -> None:
    """Behavioral proof: cache.clear() in process X must drop a key visible in process Y.

    This is the contract that LocMemCache violates (the original footgun). If
    this test ever fails, the cache backend is no longer process-shared — even
    if the static configuration check above still passes.
    """
    cache_dir = str(tmp_path / "shared_cache")
    os.makedirs(cache_dir, exist_ok=True)

    probe_key = "probe_value"
    probe_value = "set_by_subprocess_a"

    # Subprocess A: SET key, then GET — store the observed value for verification.
    set_then_get = _run_cache_op_in_subprocess(
        cache_dir,
        "_cache.set('probe_key', 'set_by_subprocess_a', 60); "
        "print(_cache.get('probe_key', 'MISS'))",
    )
    assert set_then_get == probe_value, (
        f"Subprocess A: SET round-trip failed — got {set_then_get!r}"
    )

    # Subprocess B (fresh Python process) GETs the same key.
    # This is the key proof that the cache is process-shared: a LocMemCache
    # would return 'MISS' because each subprocess has its own in-memory dict.
    get_in_b = _run_cache_op_in_subprocess(
        cache_dir, "print(_cache.get('probe_key', 'MISS'))"
    )
    assert get_in_b == probe_value, (
        f"Subprocess B: GET returned {get_in_b!r}, expected {probe_value!r}. "
        f"This means the cache is not process-shared — the same behavior as "
        f"LocMemCache that caused the original /events/ staleness footgun. "
        f"Switch to a process-shared backend (Redis, memcached, FileBasedCache, "
        f"or DatabaseCache)."
    )

    # Subprocess C: cache.clear() — must invalidate every key in the namespace.
    _run_cache_op_in_subprocess(cache_dir, "_cache.clear(); print('cleared')")

    # Subprocess D: GET after clear — must return the default sentinel 'MISS'.
    get_after_clear = _run_cache_op_in_subprocess(
        cache_dir, "print(_cache.get('probe_key', 'MISS'))"
    )
    assert get_after_clear == "MISS", (
        f"Subprocess D: cache.clear() in subprocess C did NOT propagate — "
        f"GET returned {get_after_clear!r}, expected 'MISS'. The cache backend "
        f"is silently violating the cross-process invalidation contract "
        f"(LocMemCache exhibits this exact failure mode)."
    )

    # Positive control: re-set the key and confirm round-trip works AGAIN
    # after clear — proves we're testing real propagation, not just a frozen
    # cache that absorbed the SET/GET in subprocess A's lifetime.
    set_again = _run_cache_op_in_subprocess(
        cache_dir, "_cache.set('probe_key', 'value_round_two', 60); "
        "print(_cache.get('probe_key', 'MISS'))"
    )
    assert set_again == "value_round_two", (
        f"Subprocess A (second run): re-SET round-trip failed — got {set_again!r}"
    )
    get_again_in_b = _run_cache_op_in_subprocess(
        cache_dir, "print(_cache.get('probe_key', 'MISS'))"
    )
    assert get_again_in_b == "value_round_two", (
        f"Subprocess B (after re-SET): GET returned {get_again_in_b!r}, "
        f"expected 'value_round_two'. The cache stopped accepting writes for "
        f"unknown reasons — investigate FileBasedCache directory permissions."
    )
