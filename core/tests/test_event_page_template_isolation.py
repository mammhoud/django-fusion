"""
Regression lock for the LMS EventPage template isolation

Ensures the Wagtail-aware composition template that powers the LMS /events/
Wagtail page stays out of the shared `applications/assets/templates/` tree,
where CTC and VResume could accidentally pick it up.

This freezes the architectural decision made in the option-(a) cleanup PR:
the LMS-only Wagtail EventPage template lives at
    applications/lms-demo/templates/events/event_page.html
because Django's APP_DIRS chain resolves the lookup key
`events/event_page.html` from there first.

If a future change re-introduces the shared copy, the first assertion fails
loudly before that copy ever reaches a Wagtail EventPage in another site.
"""

from pathlib import Path

# parent[1] is applications/ (parent[0] is applications/tests).
ROOT = Path(__file__).resolve().parents[1]

LMS_ONLY = ROOT / "lms-demo" / "templates" / "events" / "event_page.html"
SHARED = ROOT / "assets" / "templates" / "events" / "event_page.html"


def test_lms_only_event_page_template_exists():
    """LMS-only path must always hold the Wagtail EventPage template."""
    assert LMS_ONLY.exists(), (
        f"Expected LMS-only template at {LMS_ONLY}, but it is missing. "
        f"Wagtail EventPage (template = 'events/event_page.html') would "
        f"TemplateDoesNotExist otherwise."
    )
    content = LMS_ONLY.read_text()
    assert '{% extends "base_page.html" %}' in content
    assert '{% block content %}' in content
    assert '{% comp_include "events/main.html" %}' in content


def test_shared_event_page_template_does_not_exist():
    """The shared tree must never again host this Wagtail-aware template."""
    assert not SHARED.exists(), (
        f"Found a shared event_page.html at {SHARED}. The LMS-only "
        f"composition must not leak into CTC or VResume via the shared "
        f"applications/assets/templates/ tree. Delete the shared copy."
    )
