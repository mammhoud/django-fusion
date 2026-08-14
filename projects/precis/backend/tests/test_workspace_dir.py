"""Regression tests for ``WORKSPACE_DIR`` resolution (host vs container layout).

The historical ``parents[5]`` heuristic resolved the monorepo root on the host
(``<repo>/projects/precis/backend/configs/settings/conf.py`` is six levels
deep), but overran with ``IndexError`` inside the container
(``/app/lms-fusion/configs/settings/conf.py`` is only four levels deep). That
silently broke the entrypoint's database-readiness check and the Dramatiq
worker. ``_resolve_workspace_dir()`` now walks up to the directory owning
``libs/`` instead — the repo root on the host and ``/app`` in the container
both carry it.

These tests simulate both layouts with fake filesystem trees under
``tmp_path`` so the regression cannot return without the test failing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from configs.settings import conf


@pytest.fixture(autouse=True)
def _clear_workspace_env(monkeypatch):
    """Layout tests must not be influenced by a real WORKSPACE_DIR env var."""
    monkeypatch.delenv("WORKSPACE_DIR", raising=False)


def _fake_conf(monkeypatch, tmp_path: Path, rel_path: str) -> Path:
    """Point ``conf.__file__`` at a fake settings file inside ``tmp_path``.

    The fake file itself never needs to exist: the walk-up only stats
    ``<parent>/libs`` directories, and ``Path.resolve()`` defaults to
    ``strict=False`` so it happily resolves non-existent paths.
    """
    fake_file = tmp_path / rel_path
    monkeypatch.setattr(conf, "__file__", str(fake_file))
    return fake_file


class TestWorkspaceDirHostLayout:
    """Repository checkout on the build machine (six levels deep)."""

    def test_resolves_to_dir_owning_libs(self, monkeypatch, tmp_path):
        """Host layout resolves to the repo root (the ancestor with libs/)."""
        (tmp_path / "libs").mkdir()
        fake = _fake_conf(
            monkeypatch, tmp_path, "projects/precis/backend/configs/settings/conf.py"
        )

        resolved = conf._resolve_workspace_dir()

        assert resolved == tmp_path
        assert (resolved / "libs").is_dir()
        # Sanity: the fake file is genuinely six levels deep, as on the host.
        assert len(fake.resolve().parents) > 5

    def test_matches_historical_parents5(self, monkeypatch, tmp_path):
        """On the host layout the new walk-up agrees with the old parents[5]."""
        (tmp_path / "libs").mkdir()
        fake = _fake_conf(
            monkeypatch, tmp_path, "projects/precis/backend/configs/settings/conf.py"
        )

        assert conf._resolve_workspace_dir() == fake.resolve().parents[5]


class TestWorkspaceDirContainerLayout:
    """Baked image layout: /app/lms-fusion/configs/settings/conf.py (4 deep)."""

    def test_resolves_to_app_when_libs_present(self, monkeypatch, tmp_path):
        """Container layout resolves to /app (the ancestor owning libs/)."""
        (tmp_path / "app" / "libs").mkdir(parents=True)
        fake = _fake_conf(
            monkeypatch, tmp_path, "app/lms-fusion/configs/settings/conf.py"
        )

        resolved = conf._resolve_workspace_dir()

        assert resolved == tmp_path / "app"
        assert (resolved / "libs").is_dir()

    def test_old_parents5_would_crash_here(self, monkeypatch, tmp_path):
        """Regression guard: the old heuristic raises IndexError at 4 levels."""
        # The literal baked-image path is only four levels deep — parents[5]
        # overruns (Path math is filesystem-independent, so this holds
        # whether or not /app exists on the test machine).
        container_conf = Path("/app/lms-fusion/configs/settings/conf.py")
        with pytest.raises(IndexError):
            _ = container_conf.resolve().parents[5]

        # The fixed implementation resolves cleanly on the same shallow
        # layout when the ancestor owns libs/.
        (tmp_path / "app" / "libs").mkdir(parents=True)
        _fake_conf(monkeypatch, tmp_path, "app/lms-fusion/configs/settings/conf.py")
        assert conf._resolve_workspace_dir() == tmp_path / "app"


class TestWorkspaceDirEnvOverride:
    """An explicit WORKSPACE_DIR environment variable always wins."""

    def test_env_override_takes_precedence(self, monkeypatch, tmp_path):
        override = tmp_path / "custom-root"
        override.mkdir()
        monkeypatch.setenv("WORKSPACE_DIR", str(override))
        _fake_conf(monkeypatch, tmp_path, "app/lms-fusion/configs/settings/conf.py")

        assert conf._resolve_workspace_dir() == override

    def test_env_override_ignores_layout(self, monkeypatch, tmp_path):
        """Even with no libs/ anywhere, the env override still wins."""
        override = tmp_path / "bare-root"
        override.mkdir()
        monkeypatch.setenv("WORKSPACE_DIR", str(override))
        _fake_conf(monkeypatch, tmp_path, "app/lms-fusion/configs/settings/conf.py")

        assert conf._resolve_workspace_dir() == override


class TestWorkspaceDirRealModule:
    """The real module import resolves to a directory that owns libs/."""

    def test_imported_workspace_dir_owns_libs(self):
        """Whatever the ambient layout, WORKSPACE_DIR must own libs/."""
        assert (conf.WORKSPACE_DIR / "libs").is_dir()
