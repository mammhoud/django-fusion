"""Regression test: the shared `events/main.html` template must include the
`events/includes/events_grid.html` partial so the BEM events grid is
exercised in the live `/events/` response.

The partial's BEM classes (`.rbt-event-grid`, `.rbt-event-card`) are the
source-of-truth for the new shared events CSS partial
(`core/assets/static/styles/components/_events.scss`). If this
include is ever removed, the partial becomes orphan code that is no
longer exercised at runtime.

This is a **static file-content test** (no Django template engine) so it
avoids template-tag loading issues in the test environment while still
verifying the structural contract.
"""

from __future__ import annotations

from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2] / "core"  # core/


class EventsMainGridIncludeTest(SimpleTestCase):
    """The shared events/main.html must include the events_grid.html partial."""

    def test_events_main_renders_bem_grid_wrapper(self):
        template_path = ROOT / "assets" / "templates" / "events" / "main.html"
        content = template_path.read_text(encoding="utf-8")

        # The template must include the events_grid partial (via comp_include or include)
        assert "events/includes/events_grid.html" in content, (
            "The shared events/main.html must include the events_grid.html "
            "partial so the BEM events grid is rendered."
        )

        # The partial itself must contain the BEM wrapper class
        grid_path = ROOT / "assets" / "templates" / "events" / "includes" / "events_grid.html"
        grid_content = grid_path.read_text(encoding="utf-8")
        self.assertIn(
            'class="rbt-event-grid"',
            grid_content,
            msg=(
                "The events_grid.html partial must contain the rbt-event-grid "
                "BEM wrapper class in its {% empty %} block so the grid wrapper "
                "is always structurally present in the response."
            ),
        )
