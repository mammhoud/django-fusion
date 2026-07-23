"""Unit tests for ``django_fusion.comp.analyzer.parser``.

This module is intentionally structured around **fixtures, not magic
strings**: the 3 ``{% comp %}`` invocation forms (self_closing,
standalone, block) and the real customizer fragment are exposed as
pytest fixtures so individual tests stay focused on the *contract*
they exercise (kind, dedup, source order, kwargs extraction) rather
than re-declaring the same input strings.

Pure-Python (no Django required) -- these tests run under plain pytest
without pytest-django's database setup.

Tests guard three invariants the parser MUST hold:

1. **Form recognition.** Each of the 3 forms parses with the expected
   ``kind``. If a future regex change breaks recognition, the
   corresponding ``Test*Form`` class will fail.
2. **Dedup.** ``parse_template`` on a file that mixes the 3 forms
   returns exactly 3 entries (no double-count, no missed forms).
   If the dedup-by-``(path, opener_start)`` dedup key regresses, the
   ``TestDedupRegression`` class will fail.
3. **Source order.** CompUsages are returned in source-position order
   so callers see a deterministic, intuitive list. Failed order is
   not just cosmetic -- it breaks the regression-budget test pair
   ``test_three_forms_source_order_preserved`` + ``test_three_forms_one_each_kind``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from django_fusion.comp.analyzer.parser import (
    CompUsage,
    parse_kwargs,
    parse_template,
)


# ────────────────────────────────────────────────────────────────────
# FIXTURES: the 3 {% comp %} forms + the real customizer fragment
# ────────────────────────────────────────────────────────────────────
# Each fixture returns a raw template string. We deliberately keep the
# strings as plain Python (no dependency on full-blown Django template
# objects) so the fixtures stay usable in any pytest run-set, including
# ``--noconftest`` invocations.

@pytest.fixture
def self_closing_form() -> str:
    """A canonical ``{% comp \"path\" key=val / %}`` invocation.

    Includes the whitespace-padded terminator (``/ %}``) the
    customizer chat template uses, so this fixture also exercises the
    ``\\s*`` between ``/`` and ``%}`` in ``COMP_SELF_CLOSING_RE``.
    """
    return '{% comp "components/card.html" title="Hi" / %} '


@pytest.fixture
def standalone_form() -> str:
    """The most common form in the customizer codebase:

    ``{% comp \"path\" with\\n  key=val\\n  ...\\n %}``

    Multi-line kwargs, no ``/%}``, no ``{% endcomp %}``.
    """
    return (
        '{% comp "customizer/card" with\n'
        "  title=page.title\n"
        "  path=page.path\n"
        "%}"
    )


@pytest.fixture
def block_form() -> str:
    """A block-form opener with a child slot and ``{% endcomp %}`` close."""
    return (
        '{% comp "components/wrapper.html" title="X" %}\n'
        "  child slot\n"
        "{% endcomp %}"
    )


@pytest.fixture
def three_forms_combined() -> str:
    """THE regression fixture -- a single file containing all 3 forms.

    Parser MUST produce exactly 3 entries, paths in source order
    ``[\"a\", \"b\", \"d\"]``, kinds ``[\"self_closing\", \"block\",
    \"standalone\"]``. This is the test that catches future dedup
    regressions where one regex iterator swallows another's opener.
    """
    return (
        '{% comp "a" /%}\n'
        '{% comp "b" %}c{% endcomp %}\n'
        '{% comp "d" with x=1 %}'
    )


@pytest.fixture
def customizer_fragment_path() -> Path:
    """Path to the real
    ``customizer/templates/fragments/page_card_grid.html`` so the
    fixture can read it from disk instead of duplicating its bytes.

    Resolution strategy: walk up from ``__file__`` looking for a
    directory that contains a ``customizer/templates/fragments/page_card_grid.html``
    sibling. This is robust to renaming the test file's parent
    directories, adding/removing nesting levels, or relocating the
    repo -- the fixture keeps working as long as the customizer
    fragment is somewhere in the ancestor chain.
    """
    here = Path(__file__).resolve().parent
    for ancestor in [here, *here.parents]:
        candidate = (
            ancestor
            / "customizer"
            / "templates"
            / "fragments"
            / "page_card_grid.html"
        )
        if candidate.exists():
            return candidate
    pytest.skip(
        f"customizer fragment not reachable from {here} "
        "(test must be inside the repo to read the real file from disk)"
    )


@pytest.fixture
def customizer_fragment(customizer_fragment_path: Path) -> str:
    """Byte-for-byte copy of
    ``customizer/templates/fragments/page_card_grid.html`` -- the most
    important real-world fixture.

    Rather than duplicating the bytes inline (which would drift from
    the real file the moment someone edits it), we read it from disk
    via ``customizer_fragment_path``. This keeps the test in lockstep
    with the actual fragment the customizer UI uses, so any future
    change to the fragment's comp invocation form will exercise the
    parser against the new bytes.
    """
    return customizer_fragment_path.read_text(encoding="utf-8")


# ────────────────────────────────────────────────────────────────────
# parse_kwargs (smallest unit)
# ────────────────────────────────────────────────────────────────────
class TestParseKwargs:
    def test_empty_blob_returns_empty_dict(self):
        assert parse_kwargs("") == {}

    def test_single_unquoted_value(self):
        assert parse_kwargs("title=Hello") == {"title": "Hello"}

    def test_single_double_quoted_value(self):
        assert parse_kwargs('title="Hello World"') == {"title": "Hello World"}

    def test_single_single_quoted_value(self):
        assert parse_kwargs("title='Hello World'") == {"title": "Hello World"}

    def test_multiple_kwargs_mixed_quote_styles(self):
        result = parse_kwargs('title="Hi" variant=primary size="lg"')
        assert result == {"title": "Hi", "variant": "primary", "size": "lg"}


# ────────────────────────────────────────────────────────────────────
# parse_template -- extends + blocks
# ────────────────────────────────────────────────────────────────────
class TestParseExtendsAndBlocks:
    def test_no_extends_returns_none(self):
        p = parse_template("<html></html>")
        assert p.extends is None

    def test_extends_double_quoted(self):
        p = parse_template('{% extends "base.html" %}')
        assert p.extends == "base.html"

    def test_extends_single_quoted(self):
        p = parse_template("{% extends 'base.html' %}")
        assert p.extends == "base.html"

    def test_block_names_collected_dedup(self):
        # Two nested `{% block ... %}` declarations: names must be unique
        # in the result, in any order (set comparison).
        body = (
            "{% block content %}\n"
            "  {% block inner %}\n"
            "  {% endblock %}\n"
            "{% endblock %}\n"
        )
        p = parse_template(body)
        assert set(p.blocks) == {"content", "inner"}


# ────────────────────────────────────────────────────────────────────
# parse_template -- per-form recognition
# ────────────────────────────────────────────────────────────────────
class TestSelfClosingForm:
    """The self_closing form (``{% comp \"path\" / %}``) is recognised
    even with whitespace between ``/`` and ``%}``.
    """

    def test_extracts_exactly_one_comp(self, self_closing_form):
        p = parse_template(self_closing_form)
        assert len(p.comps) == 1

    def test_kind_is_self_closing(self, self_closing_form):
        c = parse_template(self_closing_form).comps[0]
        assert c.kind == "self_closing"

    def test_path_captured(self, self_closing_form):
        c = parse_template(self_closing_form).comps[0]
        assert c.path == "components/card.html"

    def test_kwargs_extracted(self, self_closing_form):
        c = parse_template(self_closing_form).comps[0]
        assert c.kwargs == {"title": "Hi"}

    def test_no_kwargs_form(self):
        # Plain canonical self-closing with NO kwargs -- must NOT be
        # misclassified as standalone (the regression case from
        # prior turns).
        p = parse_template('{% comp "components/alert.html" /%}')
        assert len(p.comps) == 1
        assert p.comps[0].kind == "self_closing"
        assert p.comps[0].path == "components/alert.html"
        assert p.comps[0].kwargs == {}


class TestStandaloneForm:
    """The standalone open form (``{% comp \"path\" key=val %}``) is
    the most common form in the customizer codebase.
    """

    def test_extracts_exactly_one_comp(self, standalone_form):
        p = parse_template(standalone_form)
        assert len(p.comps) == 1

    def test_kind_is_standalone(self, standalone_form):
        c = parse_template(standalone_form).comps[0]
        assert c.kind == "standalone"

    def test_path_captured(self, standalone_form):
        c = parse_template(standalone_form).comps[0]
        assert c.path == "customizer/card"

    def test_multi_line_kwargs_collapsed_into_dict(self, standalone_form):
        c = parse_template(standalone_form).comps[0]
        assert c.kwargs["title"] == "page.title"
        assert c.kwargs["path"] == "page.path"

    def test_two_distinct_standalone_comps_both_kept(self):
        # Regression -- distinct paths at different opener positions
        # MUST NOT false-dedup against each other.
        body = (
            '{% comp "comp1.html" %}\n'
            '{% comp "comp2.html" with x=1 %}'
        )
        p = parse_template(body)
        assert len(p.comps) == 2
        assert [c.path for c in p.comps] == ["comp1.html", "comp2.html"]
        assert all(c.kind == "standalone" for c in p.comps)


class TestBlockForm:
    """Block-form (``{% comp ... %} body {% endcomp %}``)."""

    def test_extracts_exactly_one_comp(self, block_form):
        p = parse_template(block_form)
        assert len(p.comps) == 1

    def test_kind_is_block(self, block_form):
        c = parse_template(block_form).comps[0]
        assert c.kind == "block"

    def test_path_captured(self, block_form):
        c = parse_template(block_form).comps[0]
        assert c.path == "components/wrapper.html"

    def test_opener_kwargs_extracted(self, block_form):
        # Only the OPENER kwargs count -- child-slot content should NOT
        # be parsed as kwargs.
        c = parse_template(block_form).comps[0]
        assert c.kwargs == {"title": "X"}


# ────────────────────────────────────────────────────────────────────
# Dedup regression -- the test that catches future regressions
# ────────────────────────────────────────────────────────────────────
class TestDedupRegression:
    """GUARD the dedup contract.

    If a future refactor changes iteration order, the negative
    lookahead in ``COMP_BLOCK_RE``, the source-order sort at the end
    of ``parse_template``, or the dedup key ``(path, opener_start)``,
    at least one of these tests will fail. That's the point -- these
    are the contracts that have each broken at least once in the
    project's history.
    """

    def test_three_forms_yield_exactly_three_entries(
        self, three_forms_combined
    ):
        # No double-count (regression 1) and no missed form
        # (regression 2).
        p = parse_template(three_forms_combined)
        assert len(p.comps) == 3

    def test_three_forms_paths_in_source_order(self, three_forms_combined):
        # sort-by-start at the end of parse_template MUST place 'a'
        # before 'b' before 'd'.
        p = parse_template(three_forms_combined)
        assert [c.path for c in p.comps] == ["a", "b", "d"]

    def test_three_forms_kinds_one_each(self, three_forms_combined):
        # Each of the 3 regex iterators MUST contribute exactly one
        # entry -- collaborative recognition across the 3 forms.
        p = parse_template(three_forms_combined)
        assert [c.kind for c in p.comps] == [
            "self_closing",
            "block",
            "standalone",
        ]

    def test_two_distinct_paths_at_different_positions_both_kept(self):
        # Same path is OK at different opener positions -- these are
        # 2 SEPARATE calls.
        body = (
            '{% comp "x" title="1" %}\n'
            '{% comp "x" title="2" %}'
        )
        p = parse_template(body)
        assert len(p.comps) == 2
        assert [c.kwargs["title"] for c in p.comps] == ["1", "2"]

    def test_whitespace_padded_self_closing_recognised(self):
        # Regression -- ``/ %}` (whitespace between slash and `%}`)
        # MUST be self_closing, not standalone.
        p = parse_template('{% comp "x" / %}')
        assert len(p.comps) == 1
        assert p.comps[0].kind == "self_closing"


# ────────────────────────────────────────────────────────────────────
# Real-world customizer fragment
# ────────────────────────────────────────────────────────────────────
class TestCustomizerFragment:
    """End-to-end fixture for the actual ``page_card_grid.html``
    fragment.  The fragment currently uses ``{% include %}`` rather
    than ``{% comp %}``, so the parser correctly reports zero comps.
    If the fragment is ever changed back to use ``{% comp %}``, these
    expectations must be updated to match.
    """

    def test_extracts_zero_comps_with_include_tags(self, customizer_fragment):
        p = parse_template(customizer_fragment)
        # Fragment uses {% include %}, not {% comp %} — zero comps expected.
        assert len(p.comps) == 0

    def test_fragment_contains_include_tag(self, customizer_fragment):
        assert '{% include "components/card.html"' in customizer_fragment

    def test_fragment_renders_without_comp_tags(self, customizer_fragment):
        assert "{% comp" not in customizer_fragment

    def test_all_four_include_kwargs_present(self, customizer_fragment):
        assert "title=page.title" in customizer_fragment
        assert "path=page.path" in customizer_fragment
        assert "page=page" in customizer_fragment
        assert "counter=forloop.counter" in customizer_fragment


# ────────────────────────────────────────────────────────────────────
# CompUsage dataclass shape
# ────────────────────────────────────────────────────────────────────
class TestCompUsageModel:
    def test_fields_are_exactly_path_kind_kwargs(self):
        fields = list(CompUsage.model_fields.keys())
        assert fields == ["path", "kind", "kwargs"]

    def test_three_known_kind_values(self):
        for kind in ("self_closing", "block", "standalone"):
            assert CompUsage(path="x", kind=kind).kind == kind

    def test_kwargs_default_to_empty_dict(self):
        assert CompUsage(path="x", kind="self_closing").kwargs == {}


# ────────────────────────────────────────────────────────────────────
# Concluded-section markers (analyzer-tracked template regions)
# ────────────────────────────────────────────────────────────────────
# Sections are declared with EITHER:
#   1. {# @section: <name> #}  (Django comment, analyzer-only)
#   2. <tag data-section-id="<name>">  (visible HTML wrapper)
# The parser accepts both forms, dedups by name within the same template,
# normalised to source order, and surfaces ``marker_type`` so frontend /
# docs tooling can detect drift between the two forms.
class TestSectionMarkers:
    """Thinks of ``parse_template`` section extraction as a topographic
    layer over the existing extends/blocks/comps surface. The
    invariants these tests guard:

    1. **Both forms recognised** — comment AND HTML wrapper.
    2. **Source-order preserved** — when both forms appear, the markers
       come out in the order they appear in the template text.
    3. **Dedup by name** — the same name twice (e.g. reused via an
       include) produces ONE entry, not two.
    4. **HTML wins over comment for same name** — when both forms
       declare the same name, the entry surfaces with
       ``marker_type="html"`` because the HTML wrapper is the
       authoritative markup.
    5. **No false positives on ordinary comments** — visual separators
       like ``{# ---- Title ---- #}`` are NOT sections.
    """

    def test_comment_marker_extracted(self):
        body = '{# @section: Hero Banner #}\n<p>hello</p>'
        p = parse_template(body)
        assert len(p.sections) == 1
        assert p.sections[0].name == "Hero Banner"
        assert p.sections[0].marker_type == "comment"

    def test_html_wrapper_extracted(self):
        body = '<section data-section-id="contact-form">...</section>'
        p = parse_template(body)
        assert len(p.sections) == 1
        assert p.sections[0].name == "contact-form"
        assert p.sections[0].marker_type == "html"

    def test_hybrid_source_order(self):
        """Both forms in one file → both extracted in source order."""
        body = (
            '{# @section: Hero Banner #}\n'
            'div banner content\n'
            '<section data-section-id="contact-form">form fields</section>\n'
            '{# @section: Footer Block #}\n'
            'div footer content\n'
        )
        p = parse_template(body)
        assert [s.name for s in p.sections] == [
            "Hero Banner",
            "contact-form",
            "Footer Block",
        ]
        assert [s.marker_type for s in p.sections] == [
            "comment",
            "html",
            "comment",
        ]

    def test_section_dedup_by_name(self):
        """Same name declared twice → one entry, no double-count."""
        body = (
            '{# @section: Hero Banner #}\n'
            'div banner\n'
            '{# @section: Hero Banner #}\n'
            'div banner again\n'
        )
        p = parse_template(body)
        assert len(p.sections) == 1
        assert p.sections[0].name == "Hero Banner"

    def test_html_wrapper_wins_over_comment_for_same_name(self):
        """When both forms declare the same name, the HTML form is
        authoritative — frontends target data-section-id, so the
        analyzer surfaces it as html even if the comment form is
        seen first in source order."""
        body = (
            '{# @section: Contact Form #}\n'
            'div\n'
            '<section data-section-id="Contact Form">form</section>\n'
        )
        p = parse_template(body)
        assert len(p.sections) == 1
        assert p.sections[0].name == "Contact Form"
        assert p.sections[0].marker_type == "html"

    def test_standard_visual_separator_is_NOT_a_section(self):
        """``{# ---- Title ---- #}`` style separators must NOT be
        picked up — those are commentary, not analyzable."""
        body = 'before\n{# ---- Section: Foo ---- #}\nafter'
        p = parse_template(body)
        assert p.sections == []

    def test_empty_section_marker_name_is_ignored(self):
        """Bare ``{# @section: #}`` (no name) must not produce an
        empty-name entry; the parser skips empty markers so we don't
        pollute the analyzer output with junk rows."""
        body = '{# @section: #}\np>'
        p = parse_template(body)
        assert p.sections == []

    def test_section_line_number_is_one_indexed(self):
        """``line`` is 1-based so it matches editor / IDE line counts."""
        body = "line0\n{# @section: Hero #}\nline2\n"
        p = parse_template(body)
        assert len(p.sections) == 1
        # The marker opens on the 2nd line (1-based).
        assert p.sections[0].line == 2

    def test_section_extraction_does_not_break_comp_extraction(self):
        """Adding section extraction must NOT regress the comp-extraction
        invariant — the two concerns are independent."""
        body = (
            '{# @section: Hero #}\n'
            '{% comp "components/card.html" /%}\n'
        )
        p = parse_template(body)
        assert len(p.sections) == 1
        assert len(p.comps) == 1
        assert p.comps[0].path == "components/card.html"
