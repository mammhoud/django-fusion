"""Compatibility package for legacy ``ceptor_ai.pipelines`` imports."""

from __future__ import annotations

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "workflows" / "pipelines")]
