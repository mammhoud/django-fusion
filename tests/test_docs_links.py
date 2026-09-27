"""Every relative link in the shipped documentation must resolve.

The repository was pruned down to the library, and the documentation was
renamed from loose uppercase files (``COMPONENT_TAG.md``, ``ROUTING_SYSTEM.md``,
…) to the numbered ``DF-0NN`` series. Cross-references were left pointing at the
old names for a while, which ``ruff`` and the test suite both happily ignored —
twenty-one links resolved to nothing, including the "related" footers of the
most-linked guides.

These tests keep that class of rot out of the published sdist. They only check
that a target *exists*: anchors, heading text, and whether the prose is still
accurate are out of scope.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

#: ``[label](target)`` — labels may contain anything but a closing bracket.
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

#: Documentation that ships in the sdist and is read by consumers.
TOP_LEVEL_DOCS = (
    "README.md",
    "QUICKSTART.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "PROMPTS.md",
)

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _documented_files() -> list[Path]:
    if not (_REPO_ROOT / "docs").is_dir():
        pytest.skip("docs/ is absent — running outside a codebase checkout")
    files = sorted((_REPO_ROOT / "docs").rglob("*.md"))
    files += [_REPO_ROOT / name for name in TOP_LEVEL_DOCS]
    return [path for path in files if path.is_file()]


def _relative_targets(path: Path) -> list[tuple[int, str]]:
    found = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for target in _LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            # A bare fragment points inside the current file; there is nothing
            # on disk to resolve.
            if target.startswith("#"):
                continue
            found.append((lineno, target))
    return found


def test_shipped_documentation_has_relative_links_to_check():
    """Guard the guard: a silent zero-link run would be a false pass."""
    total = sum(len(_relative_targets(path)) for path in _documented_files())
    assert total > 50, f"only {total} relative links found — glob or regex broke"


def test_every_relative_documentation_link_resolves():
    """No shipped document may link to a path that does not exist."""
    broken: list[str] = []
    for path in _documented_files():
        for lineno, target in _relative_targets(path):
            on_disk = target.split("#", 1)[0]
            if not on_disk:
                continue
            if not (path.parent / on_disk).resolve().exists():
                broken.append(f"{path.relative_to(_REPO_ROOT)}:{lineno} -> {target}")

    assert not broken, "broken relative links:\n  " + "\n  ".join(broken)
