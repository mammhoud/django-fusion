"""Utilities for planning crafts-ai import migration work."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .inventory import classify_import


@dataclass(frozen=True)
class MigrationItem:
    """One discovered crafts-ai import and its migration decision."""

    path: str
    line: int
    import_path: str
    target: str
    status: str
    note: str

    def as_dict(self) -> dict[str, str | int]:
        """Return a JSON-serialisable representation."""
        return asdict(self)


def _extract_import_path(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("from crafts_ai"):
        return stripped.removeprefix("from ").split(" import ", 1)[0]
    if stripped.startswith("import crafts_ai"):
        return stripped.removeprefix("import ").split(" as ", 1)[0]
    return None


def migration_plan(root: Path) -> list[MigrationItem]:
    """Build a static migration plan for crafts-ai imports under ``root``."""
    items: list[MigrationItem] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in {".venv", "venv", "node_modules", "__pycache__"} for part in path.parts):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            import_path = _extract_import_path(line)
            if import_path is None:
                continue
            rule = classify_import(import_path)
            if rule is None:
                target = import_path
                status = "needs-review"
                note = "No migration rule exists yet for this import family."
            else:
                target = rule.target
                status = rule.status
                note = rule.note
            items.append(
                MigrationItem(
                    path=str(path),
                    line=line_number,
                    import_path=import_path,
                    target=target,
                    status=status,
                    note=note,
                )
            )
    return items
