"""Regression-detection guard for the analyzer test layout.

Historical context: the analyzer tests were once kept as flat
``tests/test_analyzer_*.py`` files. They were migrated into the
``tests/analyzer/`` sub-package (with proper ``__init__.py``,
fixtures, and class organisation). This module is a small
**fail-fast sentinel** so that a future contributor cannot
re-introduce a flat ``tests/test_analyzer_*.py`` file by accident
(e.g. from git history, copy-paste from another project, or
``git mv`` rollback).

If the assertion below ever fires, the offending file MUST be moved
into ``tests/analyzer/`` and split into per-concern test classes
under the fixture-driven layout described in
``tests/analyzer/__init__.py`` and the existing
``tests/analyzer/test_*.py`` modules.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# --------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------
# Module-scoped so the glob runs once per pytest session -- this is a
# static layout check, not a per-test computation. Resolved relative
# to this test file so the guard works regardless of pytest's CWD.

@pytest.fixture(scope="module")
def tests_root() -> Path:
    """Path to the ``tests/`` directory (parent of ``tests/analyzer/``)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def legacy_analyzer_tests(tests_root: Path) -> list[Path]:
    """Glob result for the legacy flat ``test_analyzer_*.py`` layout.

    Single glob (``test_analyzer_*.py``) matches **direct children
    only** -- ``tests/analyzer/test_parser.py`` is intentionally
    NOT matched because the glob pattern has no recursive ``**``.
    Pytest's pathlib glob semantics guarantee this restriction.
    """
    return sorted(tests_root.glob("test_analyzer_*.py"))


@pytest.fixture(scope="module")
def analyzer_dir(tests_root: Path) -> Path:
    """Path to the legitimate analyzer test sub-package."""
    return tests_root / "analyzer"


# --------------------------------------------------------------------
# The fail-fast regression-guard
# --------------------------------------------------------------------

class TestNoLegacyFlatAnalyzerTests:
    """If a ``tests/test_analyzer_*.py`` file is found at the top
    level of ``tests/``, pytest MUST fail with a message that
    points the contributor at ``tests/analyzer/`` as the correct
    location.

    The class is named so a failure shows up under the same broken
    intent that introduced the regression (e.g. a future engineer
    can grep ``TestNoLegacyFlatAnalyzerTests`` in CI logs).
    """

    def test_no_legacy_flat_test_analyzer_files_under_tests_root(
        self, legacy_analyzer_tests: list[Path], tests_root: Path
    ) -> None:
        # The single glob result is the entire verification surface --
        # assert together with the error message so a future failure
        # is unambiguous.
        assert not legacy_analyzer_tests, (
            "Found legacy flat analyzer test files at the WRONG "
            "location. All analyzer tests MUST live under "
            "tests/analyzer/ (a sub-package with __init__.py), NOT "
            "as flat siblings of tests/.\n"
            f"Offending files (rel to tests/): "
            f"{[p.relative_to(tests_root).as_posix() for p in legacy_analyzer_tests]}\n"
            f"Move each file into tests/analyzer/ and reorganise its "
            f"test classes + fixtures to follow the fixture-driven "
            f"layout used by the existing tests/analyzer/test_*.py "
            f"modules. The migration pattern is documented in "
            f"tests/analyzer/test_layout.py."
        )


# --------------------------------------------------------------------
# Companion guard: the legitimate location must exist and be non-empty
# --------------------------------------------------------------------
# Inverse direction -- protects against an accidental wipe of the
# migrated tests (e.g. someone runs ``rm tests/analyzer`` instead of
# moving it). Cheap to keep alongside the regression test.

class TestAnalyzerSubdirIsPopulated:
    def test_analyzer_subdir_exists(self, analyzer_dir: Path) -> None:
        assert analyzer_dir.is_dir(), (
            f"Expected the analyzer test sub-package at "
            f"{analyzer_dir}, but it is missing or not a directory. "
            f"The migration removed tests/test_analyzer_*.py without "
            f"creating tests/analyzer/ -- restore the subdir."
        )

    def test_analyzer_subdir_has_at_least_one_test_module(
        self, analyzer_dir: Path
    ) -> None:
        test_modules = sorted(analyzer_dir.glob("test_*.py"))
        assert test_modules, (
            f"tests/analyzer/ exists but contains ZERO test_*.py "
            f"modules. The migration target should hold at least "
            f"the parser/scanner/views test modules. Restore them."
        )
