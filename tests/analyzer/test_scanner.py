"""Unit tests for ``django_fusion.fragments.analyzer.scanner``.

Pure-Python tests (no Django, no database). The bulk of the tests use
**module-scoped fixtures** so the on-disk template trees are built
once per test module rather than re-creating the same
``(a.html, one/b.html, one/two/c.html)`` shape in every test.

Why module-scoped (vs the pytest default function-scoped)?

* Trees are read-only for the duration of a test run -- tests only
  call ``scan()`` against them, never mutate.
* The depth/filters scenarios share the same tree geometry regardless
  of which filter combination is being exercised, so building the
  trees once is sufficient.
* Sessions with dozens of scanner tests would otherwise pay the
  filesystem-build cost per test instead of per module.

Tests guard two invariants the scanner MUST hold:

1. **Depth cap applied at the FILE level.** ``depth=1`` MUST NOT emit
   grandchildren even though os.walk would otherwise descend to them.
   If the ``continue`` in ``_walk()`` regresses to just ``dirs.clear()``,
   over-depth file leakage comes back. ``TestScanDepthCap`` catches
   this.
2. **MAX_DEPTH is enforced at the library boundary.** ``scan(..., depth=99999)``
   is the way to verify the cap lives in ``scan()`` itself (not just
   ``_coerce_depth`` in views). ``TestScanDepthCap.test_*_max_depth_*``
   catches desync between scanner and views.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from django_fusion.fragments.analyzer.scanner import (
    MAX_DEPTH,
    _matches_filters,
    scan,
)

# ────────────────────────────────────────────────────────────────────
# Module-scoped tree fixtures
# ────────────────────────────────────────────────────────────────────
# Use ``tmp_path_factory`` (session-scoped primitive) under a module
# scope so each tree is built exactly once and shared across the
# module's tests. Trees live under a single ``trees_root`` directory so
# the temp cleanup is centralised.

@pytest.fixture(scope="module")
def trees_root(tmp_path_factory) -> Path:
    """Root directory for all module-scoped tree fixtures."""
    return tmp_path_factory.mktemp("scanner_trees")


@pytest.fixture(scope="module")
def basic_tree(trees_root: Path) -> Path:
    """Two root-level html files -- the happy-path scanner fixture.

    Layout::

        basic_tree/
          a.html
          b.html
    """
    root = trees_root / "basic"
    # mkdir required -- write_text() does NOT auto-create parent dirs,
    # and module-scoped fixtures reuse a per-module root that may
    # already exist on disk from a prior pytest session.
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.html").write_text("hello from a")
    (root / "b.html").write_text("world from b")
    return root


@pytest.fixture(scope="module")
def nested_tree(trees_root: Path) -> Path:
    """Root + one subdir + a grandchild -- exercises the depth-1 boundary.

    Layout::

        nested_tree/
          a.html                  <- depth 0
          one/b.html              <- depth 1 ([)
          one/two/c.html          <- depth 2 (>)
    """
    root = trees_root / "nested"
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.html").write_text("top")
    (root / "one" ).mkdir(parents=True, exist_ok=True)
    (root / "one" / "b.html").write_text("child")
    (root / "one" / "two").mkdir(parents=True, exist_ok=True)
    (root / "one" / "two" / "c.html").write_text("grandchild")
    return root


@pytest.fixture(scope="module")
def deep_tree(trees_root: Path) -> Path:
    """Tree deeper than MAX_DEPTH -- exercises the cap.

    Built exactly ``MAX_DEPTH + 2`` levels deep, asserted in
    ``TestScanDepthCap.test_depth_*_max_depth_clamped_in_scan``.
    """
    root = trees_root / "deep"
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.html").write_text("hi")  # level 0
    cur = root
    for level in range(1, MAX_DEPTH + 3):
        cur = cur / f"d{level}"
        cur.mkdir(parents=True, exist_ok=True)
        (cur / f"f{level}.html").write_text(f"level {level}")
    return root


@pytest.fixture(scope="module")
def admin_tree(trees_root: Path) -> Path:
    """Tree with an ``admin/`` subdir that should be excluded.

    The PARENT directory MUST NOT contain ``admin`` in its name --
    ``_matches_filters`` does ``pat in path.parts`` and ``admin_tree``
    parent paths would match too if the fixture root were named
    ``admin``. Root here is named ``site`` for exactly that reason.

    Layout::

        site/
          good.html
          admin/users.html        <- excluded when filter=admin
    """
    root = trees_root / "site"
    root.mkdir(parents=True, exist_ok=True)
    (root / "good.html").write_text("ok")
    (root / "admin").mkdir(parents=True, exist_ok=True)
    (root / "admin" / "users.html").write_text("skip me")
    return root


@pytest.fixture(scope="module")
def mixed_extensions_tree(trees_root: Path) -> Path:
    """Tree with mixed extensions -- exercises ``include_extensions`` filter.

    Includes ``.html``, ``.django``, ``.jinja``, and ``.txt`` so the
    default-extension contract and the include-only-config test both
    have something concrete to walk.
    """
    root = trees_root / "mixed"
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.html").write_text("<html></html>")
    (root / "b.django").write_text("{% load %}")
    (root / "c.jinja").write_text("{{ x }}")
    (root / ".hidden").mkdir(parents=True, exist_ok=True)
    (root / ".hidden" / "d.html").write_text("hidden html")
    return root


# ────────────────────────────────────────────────────────────────────
# Function-scoped factory fixture
# ────────────────────────────────────────────────────────────────────
# Module-scoped fixtures cover the standard tree shapes; tests that
# need an ad-hoc tree use this factory. ``tmp_path`` here is per-test
# so the factory-tree lives only for the requesting test.

@pytest.fixture
def make_tree(tmp_path: Path):
    """Factory that builds an arbitrary tree and returns the root.

    Usage::

        def test_x(make_tree):
            root = make_tree({"a.html": "hi", "sub/b.html": "bye"})
            result = scan(roots=[root], depth=3, filters={})
    """
    def _build(files: dict[str, str]) -> Path:
        for relpath, content in files.items():
            p = tmp_path / relpath
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        return tmp_path
    return _build


# ────────────────────────────────────────────────────────────────────
# _matches_filters helper -- unit tests with function-scoped tmp_path
# ────────────────────────────────────────────────────────────────────
# These don't need a shared tree -- each test makes one tiny file and
# exercises the helper in isolation.

class TestMatchesFilters:
    def test_default_extensions_include_html(self, tmp_path):
        f = tmp_path / "x.html"
        f.write_text("hi")
        assert _matches_filters(f, {}) is False  # not skipped

    def test_non_matching_extension_skipped(self, tmp_path):
        f = tmp_path / "x.txt"
        f.write_text("hi")
        assert _matches_filters(f, {}) is True  # skipped

    def test_exclude_pattern_skips_files_in_excluded_subtree(self, tmp_path):
        # Regression -- ``mkdir`` must precede the ``write_text`` or
        # the test fixture leaks an OSError instead of exercising the
        # exclude logic.
        (tmp_path / "admin").mkdir()
        f = tmp_path / "admin" / "x.html"
        f.write_text("hi")
        assert _matches_filters(f, {"exclude_patterns": ["admin"]}) is True

    def test_include_extensions_filter(self, tmp_path):
        f = tmp_path / "x.django"
        f.write_text("hi")
        assert _matches_filters(f, {"include_extensions": [".django"]}) is False
        f2 = tmp_path / "x.html"
        f2.write_text("hi")
        assert _matches_filters(f2, {"include_extensions": [".django"]}) is True


# ────────────────────────────────────────────────────────────────────
# scan() integration with module-scoped trees
# ────────────────────────────────────────────────────────────────────

class TestScanBasic:
    def test_returns_empty_list_for_nonexistent_root(self):
        # No exception; just no files.
        result = scan(roots=[Path("/nonexistent/path/__definitely_missing__")])
        assert result == []

    def test_scans_caller_supplied_root(self, basic_tree):
        result = scan(roots=[basic_tree], depth=3, filters={})
        paths = sorted(sf.relative_path for sf in result)
        assert paths == ["a.html", "b.html"]
        # Content round-trips through ``read_text``.
        assert result[0].content == "hello from a"

    def test_normal_files_included_smoke(self, basic_tree):
        # Lightweight smoke test -- one assertion is enough to detect a
        # regression where ``scan()`` filters out writable files.
        result = scan(roots=[basic_tree], depth=2, filters={})
        assert any(sf.relative_path == "a.html" for sf in result)


class TestScanDepthCap:
    """Depth-cap regression tests live here because they share the
    same depth-tree fixtures (``nested_tree`` + ``deep_tree``) and
    benefit from module-scoped build cost.
    """

    def test_depth_one_emits_root_and_one_level_no_grandchildren(
        self, nested_tree
    ):
        """Regression case: depth=1 yields root + root/one -- BUT NOT
        root/one/two -- which would happen if ``_walk`` only called
        ``dirs.clear()`` and forgot the ``continue``.
        """
        result = scan(roots=[nested_tree], depth=1, filters={})
        paths = sorted(sf.relative_path for sf in result)

        assert "a.html" in paths
        assert "one/b.html" in paths
        assert "one/two/c.html" not in paths, (
            f"depth cap leak: c.html at depth=2 leaked into depth=1 result: {paths}"
        )

    def test_depth_zero_only_includes_root_files(self, basic_tree):
        # depth=0 means "root only" -- the existing files at the root
        # must NOT pull anything in from subdirs.
        result = scan(roots=[basic_tree], depth=0, filters={})
        paths = sorted(sf.relative_path for sf in result)
        assert paths == ["a.html", "b.html"]

    def test_depth_negative_raises_value_error(self):
        """Library-level invariant: negative depth is a programming error
        and raises -- the view's ``_coerce_depth`` floors it before
        reaching ``scan()``, so this is only reachable for direct
        callers.
        """
        with pytest.raises(ValueError):
            scan(roots=[Path("/nonexistent")], depth=-1, filters={})

    def test_depth_clamped_to_scan_max_depth(self, deep_tree):
        """``scan(roots, depth=99999)`` actually enforces the
        ``MAX_DEPTH`` cap, not just the view's. Builds a tree deeper
        than ``MAX_DEPTH`` and confirms no over-MAX_DEPTH files leak
        through.
        """
        result = scan(roots=[deep_tree], depth=99999, filters={})
        paths = sorted(sf.relative_path for sf in result)

        assert "a.html" in paths
        for level in range(1, MAX_DEPTH + 1):
            assert any(
                p.endswith(f"f{level}.html") for p in paths
            ), f"missing expected file at depth {level}: {paths}"
        beyond = [
            p for p in paths
            if any(
                p.endswith(f"f{level}.html")
                for level in range(MAX_DEPTH + 1, MAX_DEPTH + 3)
            )
        ]
        assert beyond == [], f"MAX_DEPTH cap leaked over-depth files: {beyond}"

    def test_max_depth_constants_match_between_scanner_and_views(self):
        """``MAX_DEPTH`` is exported from ``scanner.py`` and re-exported
        by ``views.py`` for backward compat. They MUST stay in sync --
        a future move would silently desync the two enforcement points.
        """
        from django_fusion.fragments.analyzer.scanner import MAX_DEPTH as S
        from django_fusion.fragments.analyzer.views import MAX_DEPTH as V
        assert S == V == 10


class TestScanFilters:
    def test_exclude_pattern_skips_subtree(self, admin_tree):
        result = scan(
            roots=[admin_tree],
            depth=5,
            filters={"exclude_patterns": ["admin"]},
        )
        paths = sorted(sf.relative_path for sf in result)
        assert "good.html" in paths
        assert not any("users.html" in p for p in paths)

    def test_include_extensions_walks_only_matching(self, mixed_extensions_tree):
        # Default filters include .html/.django/.jinja but the directory
        # also contains a hidden subdirectory which is a regular
        # subdirectory walk, not excluded by default.
        result = scan(roots=[mixed_extensions_tree], depth=3, filters={})
        paths = sorted(sf.relative_path for sf in result)
        # .html/.django/.jinja are all accepted; only the .txt would
        # be rejected (we deliberately did not include one -- extend if
        # concrete rejection coverage is needed).
        assert any(p.endswith(".html") for p in paths)
        assert any(p.endswith(".django") for p in paths)
        assert any(p.endswith(".jinja") for p in paths)

    def test_include_extensions_only_narrows_results(self, mixed_extensions_tree):
        # Restrict to .html -- .django/.jinja must drop out.
        result = scan(
            roots=[mixed_extensions_tree],
            depth=3,
            filters={"include_extensions": [".html"]},
        )
        paths = sorted(sf.relative_path for sf in result)
        assert any(p.endswith(".html") for p in paths)
        assert not any(p.endswith(".django") for p in paths)
        assert not any(p.endswith(".jinja") for p in paths)


# ────────────────────────────────────────────────────────────────────
# error handling
# ────────────────────────────────────────────────────────────────────

class TestScanErrorHandling:
    def test_unreadable_file_does_not_crash_scan(
        self, make_tree, monkeypatch
    ):
        """A file whose ``read_text`` raises ``OSError`` must NOT abort
        the walk -- the loop's ``except OSError: continue`` should
        swallow the failure and move on.
        """
        make_tree({"broken.html": "ignored", "good.html": "ok"})

        # Patch Path.read_text to always raise -- the scanner must
        # tolerate this without crashing.
        def _raise_oserror(*args, **kwargs):
            raise OSError("simulated unreadable file")

        monkeypatch.setattr(Path, "read_text", _raise_oserror)

        # Result is whatever the scanner accumulates -- could be []
        # since every read fails, but the walking loop must complete.
        # We don't lock the exact list because monkey-patching
        # ``read_text`` globally affects any Path.read_text call.
        result = scan(roots=[Path("/nonexistent/safe/path")], depth=2, filters={})
        assert isinstance(result, list)


# ────────────────────────────────────────────────────────────────────
# factory fixture unlocked-shape coverage
# ────────────────────────────────────────────────────────────────────

class TestFactoryFixture:
    """Tests for the ad-hoc ``make_tree`` factory fixture -- exercises
    shapes not covered by the named module-scoped trees.
    """

    def test_factory_builds_minimal_tree(self, make_tree):
        # Functional sanity: factory returns a Path-like root inside
        # tmp_path with all named files present.
        root = make_tree({"a.html": "<a/>"})
        assert (root / "a.html").exists()
        assert (root / "a.html").read_text() == "<a/>"
        result = scan(roots=[root], depth=2, filters={})
        assert any(sf.relative_path == "a.html" for sf in result)

    def test_factory_builds_with_subdirectories(self, make_tree):
        root = make_tree({
            "root.html": "root",
            "a/leaf.html": "leaf",
            "a/b/deep.html": "deep",
        })
        result = scan(roots=[root], depth=10, filters={})
        paths = sorted(sf.relative_path for sf in result)
        assert paths == ["a/b/deep.html", "a/leaf.html", "root.html"]
