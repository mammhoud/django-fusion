"""Marker-region editing for ``manage.py plugin attach|detach``.

Owning plan: ``docs/plans/structa-cloud/plugins/product-description-and-attach.md``
§5.2. Two non-negotiable properties shape this module:

* **A2 — marker-delimited.** The command edits *only* between
  ``# region plugins:begin`` / ``# region plugins:end``. When the markers are
  absent it refuses; it never guesses where an app list ends. That is why this
  module is a set of pure text functions: the interesting behaviour is what it
  refuses to touch, and that is easy to test and hard to get wrong in review.

* **A1/A3 — idempotent and reversible.** The region holds one declarative list
  (``PLUGIN_APPS``), not generated code. Attaching is a set insert, detaching is a
  set delete, and re-running either is a no-op — so ``attach`` then ``detach``
  returns the file to its original bytes.

Nothing here imports Django or touches the filesystem: the caller owns those, so
the rules can be tested without a site, a database or settings.

**The region the site must add (once, by hand):**::

    # region plugins:begin
    PLUGIN_APPS: list[str] = []
    # region plugins:end

and then include it in its app list::

    INSTALLED_APPS = list(SHARED_APPS) + [a for a in TENANT_APPS if a not in SHARED_APPS] + PLUGIN_APPS

The site keeps control of *which* app list a plugin joins (shared vs per-tenant —
a real distinction in a multi-tenant product) while the tool owns the membership
of the region. A plugin with per-tenant models and one with only config go in
different lists, and no tool can infer that choice.
"""
from __future__ import annotations

import ast
import difflib

#: The exact marker lines (A2). Compared after ``strip()`` so indentation inside a
#: nested block still matches, but the text itself may not differ.
MARKER_BEGIN = "# region plugins:begin"
MARKER_END = "# region plugins:end"

#: The variable the region declares, and the one the optional-app map uses.
PLUGIN_APPS_NAME = "PLUGIN_APPS"
OPTIONAL_APP_MAP_NAME = "OPTIONAL_APP_MAP"

#: A short note inserted above the list so a reader knows a tool owns it.
REGION_NOTE = "# Managed by `manage.py plugin attach|detach` — edits inside this region are safe."


class RegionMissing(Exception):
    """Raised when a file the command was told to edit carries no marker region."""


def region_bounds(text: str) -> tuple[int, int] | None:
    """Line indices of the ``begin`` and ``end`` markers, or ``None`` if absent."""
    begin = end = None
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if stripped == MARKER_BEGIN and begin is None:
            begin = index
        elif stripped == MARKER_END and begin is not None:
            end = index
            break
    if begin is None or end is None or end < begin:
        return None
    return begin, end


def _assigned_value(text: str, name: str, *, start: int = 0, end: int | None = None) -> ast.expr:
    """The value node of the ``name = ...`` assignment inside a line window.

    Both annotated (``name: list[str] = []``) and bare (``name = []``) forms are
    accepted: the region the plugin plans document uses the annotated form, and
    silently refusing it would have made ``attach`` unusable on the very files it
    was written for.
    """
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        else:
            continue
        if not isinstance(target, ast.Name) or target.id != name or value is None:
            continue
        line = node.lineno - 1
        if line < start or (end is not None and line > end):
            continue
        return value
    raise RegionMissing(f"no `{name}` assignment found between the markers")


def read_plugin_apps(text: str) -> list[str]:
    """The apps currently listed in the region, sorted and de-duplicated."""
    bounds = region_bounds(text)
    if bounds is None:
        raise RegionMissing(
            f"no `{MARKER_BEGIN}` / `{MARKER_END}` region — add it by hand; "
            "the command will not guess where an app list ends"
        )
    node = _assigned_value(text, PLUGIN_APPS_NAME, start=bounds[0], end=bounds[1])
    try:
        value = ast.literal_eval(node)
    except ValueError as exc:  # pragma: no cover - non-literal list
        raise RegionMissing(f"`{PLUGIN_APPS_NAME}` is not a literal list: {exc}") from exc
    if not isinstance(value, list):
        raise RegionMissing(f"`{PLUGIN_APPS_NAME}` must be a list, found {type(value).__name__}")
    return sorted({str(item) for item in value})


def render_plugin_apps(names: list[str]) -> str:
    """Render the region interior for *names* (sorted, stable, one per line)."""
    if not names:
        return f"{REGION_NOTE}\n{PLUGIN_APPS_NAME}: list[str] = []"
    body = "".join(f'    "{name}",\n' for name in sorted(names))
    return f"{REGION_NOTE}\n{PLUGIN_APPS_NAME}: list[str] = [\n{body}]"


def replace_region(text: str, interior: str) -> str:
    """Replace everything between the markers, preserving the markers themselves."""
    bounds = region_bounds(text)
    if bounds is None:
        raise RegionMissing(f"no marker region in this file")
    lines = text.splitlines(keepends=True)
    begin, end = bounds
    newline = "\n"
    # The comprehension already terminates every interior line, so nothing further
    # is appended: adding another newline here produced a blank line before the end
    # marker and broke the byte-for-byte detach round-trip.
    interior_lines = [
        line if line.endswith(newline) else line + newline
        for line in interior.splitlines(keepends=True)
    ]
    return "".join(lines[: begin + 1] + interior_lines + lines[end:])


def with_app(text: str, name: str, *, add: bool) -> str:
    """Add/remove *name* in the region (idempotent — a repeated call returns the same text)."""
    current = read_plugin_apps(text)
    updated = sorted(set(current) | {name}) if add else [item for item in current if item != name]
    if updated == current:
        return text
    return replace_region(text, render_plugin_apps(updated))


def read_optional_map(text: str) -> dict[str, str]:
    """The ``OPTIONAL_APP_MAP`` entries between the markers."""
    bounds = region_bounds(text)
    if bounds is None:
        raise RegionMissing(
            f"no `{MARKER_BEGIN}` / `{MARKER_END}` region in the optional-app map"
        )
    node = _assigned_value(text, OPTIONAL_APP_MAP_NAME, start=bounds[0], end=bounds[1])
    value = ast.literal_eval(node)
    if not isinstance(value, dict):
        raise RegionMissing(f"`{OPTIONAL_APP_MAP_NAME}` must be a dict")
    return {str(key): str(item) for key, item in value.items()}


def render_optional_map(mapping: dict[str, str]) -> str:
    """Render the map region interior (sorted by key for a stable diff)."""
    if not mapping:
        return f"{REGION_NOTE}\n{OPTIONAL_APP_MAP_NAME}: dict[str, str] = {{}}"
    body = "".join(f'    "{key}": "{mapping[key]}",\n' for key in sorted(mapping))
    return f"{REGION_NOTE}\n{OPTIONAL_APP_MAP_NAME}: dict[str, str] = {{\n{body}}}"


def with_optional_app(text: str, name: str, capability: str, *, add: bool) -> str:
    """Add/remove an ``OPTIONAL_APP_MAP`` entry (idempotent)."""
    current = read_optional_map(text)
    updated = dict(current)
    if add:
        updated[name] = capability
    else:
        updated.pop(name, None)
    if updated == current:
        return text
    return replace_region(text, render_optional_map(updated))


def unified_diff(before: str, after: str, path: str) -> str:
    """A reviewable diff for ``--dry-run`` output and the post-write report."""
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
        )
    )
