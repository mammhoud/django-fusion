"""Filesystem scanner for template directories.

Walks the Django project's configured `TEMPLATES_DIRS` (or a caller-supplied
list of root paths), respecting `depth` and `filters.include_extensions` /
`filters.exclude_patterns` from the analyzer request payload.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict

# Server-side cap on traversal depth. Library callers that bypass the view
# (e.g. `scan(roots, depth=99999)`) get this cap from `scan()` itself; the
# view's `_coerce_depth` is now redundant for the cap and only retains the
# floor-at-1 / parse-from-string behavior.
MAX_DEPTH = 10


class ScannedFile(BaseModel):
    path: Path
    relative_path: str
    content: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={Path: str},
    )


def _resolve_template_dirs() -> list[Path]:
    """Get the configured TEMPLATES_DIRS at runtime.

    Returns an empty list if Django isn't configured (e.g. during library tests
    where no settings module is loaded).
    """
    try:
        from django.template import engines
    except Exception:  # pragma: no cover - django not available
        return []

    try:
        engine = engines["django"]
    except KeyError:
        return []

    dirs = getattr(engine.engine, "dirs", None) or []
    return [Path(d) for d in dirs if d]


def _matches_filters(path: Path, filters: dict) -> bool:
    exts = filters.get("include_extensions") or [".html", ".django", ".jinja"]
    excludes = filters.get("exclude_patterns") or ["admin", "static", "media"]

    if path.is_file() and path.suffix not in exts:
        return True  # skip this file
    for pat in excludes:
        if pat and pat in path.parts:
            return True  # any excluded segment match -> skip
    return False


def scan(
    roots: list[Path] | None = None,
    depth: int = 3,
    filters: dict | None = None,
) -> list[ScannedFile]:
    """Walk `roots` (or configured TEMPLATES_DIRS) up to `depth` levels.

    Semantics: `depth=N` means "root files + N levels of subdirs", so:
    - depth=0 emits only root-level files
    - depth=1 emits root + 1 subdir level (grandchildren excluded)
    - depth=MAX_DEPTH emits every file in the tree

    Negative depth is a programming error and raises ValueError -- the view's
    `_coerce_depth` floors negative values to 1 at the HTTP boundary, so this
    library invariant is unreachable through the view but visible to anyone
    who calls `scan()` directly.

    Files matching `filters` are skipped. Returns the list of scanned files
    with their raw content read into memory.
    """
    if depth < 0:
        raise ValueError(f"depth must be >= 0, got {depth}")
    depth = min(depth, MAX_DEPTH)
    filters = filters or {}
    roots = roots or _resolve_template_dirs()

    accepted = []
    for root in roots:
        if not root.exists():
            continue
        for current, dirs, files in _walk(root, depth):
            for fname in files:
                fpath = Path(current) / fname
                rel = str(fpath.relative_to(root))
                if _matches_filters(fpath, filters):
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                accepted.append(ScannedFile(path=fpath, relative_path=rel, content=content))
    return accepted


def _walk(root: Path, depth: int):
    """Recursive walk with depth cap. Skips BOTH recursion AND file
    emission at over-depth levels -- previously the depth cap only
    cleared `dirs`, which stopped os.walk from descending but still
    yielded files at the over-depth node.
    """
    root_depth = len(root.parts)
    for current, dirs, files in _walk_recursive(root):
        cur_depth = len(Path(current).parts) - root_depth
        if cur_depth > depth:
            dirs.clear()  # prevent descent into deeper subdirs
            continue  # also skip emitting this level's files
        yield current, dirs, files


def _walk_recursive(root: Path):
    """Plain os.walk wrapper kept separate for testability."""
    import os

    yield from os.walk(str(root))
