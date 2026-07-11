"""
Regression lock for the pagination standardisation of events_grid.html.

The shared ``events/includes/events_grid.html`` partial was switched from
a model-injected ``events`` queryset to ``page_items`` — the paginated
iteration variable provided by ``BaseIndexPage.get_context()``.

- LMS ``EventPage.get_listed_items()`` returns the ``Event`` queryset.
- CTC ``EventPage.get_listed_items()`` returns the ``Event`` queryset.
- VResume ``EventPage.get_listed_items()`` returns the ``Event`` queryset.

The loop in the partial must iterate over ``page_items`` so that
BaseIndexPage pagination drives the rendering.  If a future change
reverts the loop back to ``events`` the pages go quiet — the BEM event
grid wrapper still renders (via the ``{% empty %}`` block) but the
actual event cards are never produced.

These tests read the source file directly (no Django template engine
involvement) so they run instantly and need no database.
"""
from __future__ import annotations

from pathlib import Path

# core/ is parent[1] (parent[0] is core/tests).
ROOT = Path(__file__).resolve().parents[1]

GRID_PARTIAL = (
    ROOT / "assets" / "templates" / "events" / "includes" / "events_grid.html"
)

# ---------------------------------------------------------------------------
# File-level assertions (no DB, no Django template engine)
# ---------------------------------------------------------------------------


def test_grid_partial_exists():
    """The shared events_grid.html partial must exist."""
    assert GRID_PARTIAL.exists(), (
        f"Expected the shared partial at {GRID_PARTIAL}, but it is missing. "
        f"events/main.html includes this partial via "
        f"{{% include 'events/includes/events_grid.html' %}}."
    )


def test_grid_partial_iterates_page_items():
    """
    The ``{% for %}`` loop must iterate over ``page_items``, not ``events``.

    ``BaseIndexPage.get_context()`` paginates ``get_listed_items()`` into a
    ``page_items`` variable — that is what every Wagtail EventPage provides.
    Iterating over ``events`` would bypass pagination and silently render
    nothing (since the old ``EventListView`` that injected ``events`` has
    been deleted from all three sites).
    """
    content = GRID_PARTIAL.read_text()

    # The loop MUST use page_items
    assert "{% for event in page_items %}" in content, (
        "The events_grid.html partial must iterate over ``page_items`` "
        "(populated by BaseIndexPage pagination).  Found:\n"
        f"{_extract_for_loops(content)}"
    )

    # The loop MUST NOT use events
    assert "{% for event in events %}" not in content, (
        "The events_grid.html partial must NOT iterate over a raw ``events`` "
        "queryset.  The old EventListView that injected ``events`` has been "
        "deleted from all three sites — iterating over ``events`` would "
        "silently produce zero event cards and display the empty state."
    )


def test_grid_partial_contains_bem_wrapper_class():
    """
    The source must contain the ``.rbt-event-grid`` BEM wrapper class.

    The ``{% empty %}`` block in the template renders this class so the
    grid wrapper is always structurally present even when no events exist.
    This is a static file-content check (not a Django template render).
    """
    content = GRID_PARTIAL.read_text()
    assert 'class="rbt-event-grid"' in content, (
        "The `{% empty %}` block must render <div class=\"rbt-event-grid\"> "
        "so the BEM grid wrapper is always present in the response, even "
        "when there are no events."
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_for_loops(content: str) -> str:
    """Return all ``{% for ... %}`` lines found in *content*."""
    return "\n".join(
        line.strip()
        for line in content.splitlines()
        if "{% for " in line
    ) or "(no for-loops found)"
