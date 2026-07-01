"""Spec file input/output.

This module owns the *filesystem* side of loading specs from disk. It is kept
deliberately small and dependency-free so it can be reused from tests with
text-only fixtures as easily as from the orchestrator with real spec trees.

Canonical import::

    from ceptor_ai.orchestrator.io import read_spec_files
    # or, equivalently, import directly under the shorter alias:
    from ceptor_ai.orchestrator import io

What lives here
---------------
- File reads only. No parsing (lives in :mod:`.parser`), no orchestration
  glue (lives in :mod:`.operators`), no logging.

What does *not* live here
-------------------------
- Compatibility-layer checks.
- ``logger.warning`` calls for unknown PBT frameworks or invalid format
  versions. Those are operators' concern (``_load_spec_from_metadata``).
- Caching. The :class:`SpecScanner` already owns directory-level caching;
  add file-level caching here only if a real benchmark demands it.
"""

from __future__ import annotations

from typing import Optional, Tuple

from .models import SpecMetadata


def _read_text(path: Optional[str]) -> str:
    """Return the contents of ``path`` as ``str``, or ``""`` if ``path`` is ``None``.

    The empty-string fallback is the contract ``SpecParser`` relies on — it
    treats ``""`` as "this section was absent" rather than as an error, so
    optional sections (e.g. ``bugfix.md``) can simply pass ``None`` here.

    Encoding is fixed at UTF-8: Kiro specs are Markdown and we want the same
    behaviour across platforms. If a spec file is not UTF-8, raising is the
    correct response — the error handler will route it.
    """
    if path is None:
        return ""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def read_spec_files(metadata: SpecMetadata) -> Tuple[str, str, str]:
    """Read the three required spec artefacts described by ``metadata``.

    Returns a 3-tuple ``(requirements, design, tasks_text)``. Each element is
    an empty string when the corresponding section file was absent.

    The function deliberately does not validate presence: the scanner's
    "missing required files" warnings are the source of truth for whether a
    spec has the right shape. Re-raising here would duplicate that signal.
    """
    return (
        _read_text(metadata.requirements_path),
        _read_text(metadata.design_path),
        _read_text(metadata.tasks_path),
    )


__all__ = ["read_spec_files"]
