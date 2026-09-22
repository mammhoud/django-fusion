"""
Regression test: DB invariant for EventPage rows with slug='events'.

Locks the architectural decision (option-a) at the database level:
all EventPage rows tied to slug='events' must satisfy:

  (i)  header_section + cta_section are empty StreamValues
  (ii) intro_text is empty
  (iii) no concrete field contains legacy event__item / event__area markers

If a future operator pastes legacy markup into the CMS body (header_section,
cta_section, intro_text, or any other editable field), this test will fail
LOUDLY — before the regression reaches users.

Background
----------
The legacy events template (projects/assets/templates/events/events.html)
contained 32 KiB of hardcoded HTML5 with ``event__item`` and ``event__area``
CSS classes in its markup. A DB dump confirmed that zero EventPage rows store
those markers in any concrete database field — the legacy markup lives
exclusively in the now-unreachable template file (shadowed by Wagtail's
catch-all URL route).

This test freezes that invariant. If any future CMS edit introduces
event__item or event__area markers into the database, the assertion below
will trip before users ever see a regression on /events/.
"""

from __future__ import annotations

import functools
import json
import subprocess
from typing import Any

import pytest

# ── docker exec command template ──────────────────────────────────────────
DOCKER_EXEC = [
    "docker", "exec", "-w", "/app/lms",
    "-e", "DJANGO_SETTINGS_MODULE=settings",
    "lms-web", "python", "-c",
]

QUERY_SCRIPT = r"""
import os, sys, json
sys.path.insert(0, '/app/lms')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django; django.setup()

from www.core.content.models.pages.events import EventPage

pages = list(EventPage.objects.filter(slug='events').specific())
rows = []

for page in pages:
    row = {
        'id': page.id,
        'title': page.title,
        'locale': page.locale.language_code,
        'header_section_empty': not bool(page.header_section),
        'cta_section_empty': not bool(page.cta_section),
        'intro_text': page.intro_text or '',
        'markers': {},
    }

    # Scan ALL concrete model fields (including inherited ones) for
    # legacy event__item / event__area markers.
    for field in page._meta.get_fields():
        if not hasattr(field, 'column') or field.column is None:
            continue  # skip non-concrete fields (reverse relations, etc.)
        try:
            val = getattr(page, field.name)
        except Exception:
            continue
        if val is None:
            continue
        s = str(val)
        found = []
        for marker in ('event__item', 'event__area'):
            if marker in s:
                found.append(marker)
        if found:
            row['markers'][field.name] = found

    rows.append(row)

print('JSON_BEGIN')
print(json.dumps(rows, indent=2, ensure_ascii=False))
print('JSON_END')
"""

# ── cached query (runs docker exec once per test session) ─────────────────


def _container_available() -> bool:
    """Return True if the lms-web container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=lms-web", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and "lms-web" in result.stdout


@functools.lru_cache(maxsize=1)
def _query_event_pages() -> tuple[dict[str, Any], ...]:
    """Run the query script inside the lms-web container and return JSON rows.

    Cached via ``lru_cache`` so all 4 test methods share the same container
    exec result — no redundant docker calls.
    """
    if not _container_available():
        pytest.skip("lms-web container is not running")
    try:
        result = subprocess.run(
            DOCKER_EXEC + [QUERY_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        pytest.skip("docker not available on this host")
    except subprocess.TimeoutExpired:
        pytest.fail("docker exec timed out after 30 s")

    if result.returncode != 0:
        pytest.fail(
            f"docker exec exited {result.returncode}:\n"
            f"  stdout: {result.stdout[:2000]}\n"
            f"  stderr: {result.stderr[:2000]}"
        )

    # Extract JSON between sentinel markers (Django may print banners to
    # stdout before our JSON output).
    stdout = result.stdout
    start = stdout.find("JSON_BEGIN")
    end = stdout.find("JSON_END")
    if start == -1 or end == -1:
        pytest.fail(
            f"Could not find JSON sentinels in docker exec output:\n"
            f"  {stdout[:3000]}"
        )
    raw = stdout[start + len("JSON_BEGIN"):end].strip()
    return tuple(json.loads(raw))


# ── tests ─────────────────────────────────────────────────────────────────


class TestEventPageDbInvariant:
    """Lock the DB invariant: all EventPage(slug='events') rows must be clean."""

    # ── (i) header_section + cta_section ──────────────────────────────────

    def test_header_section_is_empty(self) -> None:
        """EventPage(slug='events') must have an empty header_section StreamField."""
        pages = _query_event_pages()
        assert pages, "No EventPage rows found with slug='events'"
        failures: list[str] = []
        for p in pages:
            if not p["header_section_empty"]:
                failures.append(f"  id={p['id']} ({p['locale']}): header_section is NOT empty")
        assert not failures, (
            "All EventPage(slug='events') rows must have an empty header_section.\n"
            "The legacy hero/BEM markup lives in the dedicated base_page.html\n"
            "template composition, not in the CMS body field.\n" + "\n".join(failures)
        )

    def test_cta_section_is_empty(self) -> None:
        """EventPage(slug='events') must have an empty cta_section StreamField."""
        pages = _query_event_pages()
        assert pages, "No EventPage rows found with slug='events'"
        failures: list[str] = []
        for p in pages:
            if not p["cta_section_empty"]:
                failures.append(f"  id={p['id']} ({p['locale']}): cta_section is NOT empty")
        assert not failures, (
            "All EventPage(slug='events') rows must have an empty cta_section.\n"
            "The legacy CTA/BEM markup lives in the dedicated base_page.html\n"
            "template composition, not in the CMS body field.\n" + "\n".join(failures)
        )

    # ── (ii) intro_text ───────────────────────────────────────────────────

    def test_intro_text_is_empty(self) -> None:
        """EventPage(slug='events') must have an empty intro_text RichTextField."""
        pages = _query_event_pages()
        assert pages, "No EventPage rows found with slug='events'"
        failures: list[str] = []
        for p in pages:
            if p["intro_text"]:
                failures.append(
                    f"  id={p['id']} ({p['locale']}): intro_text={p['intro_text'][:100]!r}"
                )
        assert not failures, (
            "All EventPage(slug='events') rows must have empty intro_text.\n"
            + "\n".join(failures)
        )

    # ── (iii) legacy markers ──────────────────────────────────────────────

    def test_no_legacy_event_markers_in_any_field(self) -> None:
        """No EventPage(slug='events') row may contain event__item / event__area in any field."""
        pages = _query_event_pages()
        assert pages, "No EventPage rows found with slug='events'"
        failures: list[str] = []
        for p in pages:
            if p["markers"]:
                for field, markers in p["markers"].items():
                    failures.append(f"  id={p['id']} ({p['locale']}), field={field}: {markers!r}")
        assert not failures, (
            "No EventPage(slug='events') row may store legacy event__item / event__area\n"
            "CSS class markers in any concrete database field. Those markers live\n"
            "exclusively in the (now-unreachable) template at\n"
            "projects/assets/templates/events/events.html.\n"
            + "\n".join(failures)
        )
