"""
Round-trip property tests for SpecParser.

**Validates: Requirements 18.4, 18.6, 18.7**

Grammar under test
------------------
SpecParser parses Kiro spec files (requirements.md, design.md, tasks.md,
bugfix.md, .config) from Markdown/JSON into structured Python objects.

Round-trip property
-------------------
For any valid input ``s``:

    parse(pretty_print(parse(s))) == parse(s)

That is, serialising parsed output back to the source format and re-parsing
must produce an equivalent result.
"""

import json
import string

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from .parser import SpecParser

# Mark all tests as nondestructive (required by pytest-selenium plugin)
pytestmark = pytest.mark.nondestructive


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Safe text: printable ASCII excluding characters that break Markdown structure
_safe_chars = string.ascii_letters + string.digits + " .,!?-_()[]"

st_safe_text = st.text(alphabet=_safe_chars, min_size=1, max_size=80).filter(
    lambda s: s.strip() == s and len(s.strip()) > 0  # no leading/trailing whitespace
)
st_safe_word = st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=30)

# JSON-compatible values for config dicts
st_json_value = st.one_of(
    st.text(alphabet=string.ascii_letters + string.digits + " -_", min_size=0, max_size=40),
    st.booleans(),
    st.integers(min_value=0, max_value=9999),
)

st_config_dict = st.dictionaries(
    keys=st_safe_word,
    values=st_json_value,
    min_size=0,
    max_size=10,
)


# ---------------------------------------------------------------------------
# Property 1: parse_config round-trip
# ---------------------------------------------------------------------------

@given(config=st_config_dict)
@settings(max_examples=200)
def test_parse_config_roundtrip(config):
    """
    **Validates: Requirements 18.4, 18.6**

    For any valid config dict ``d``:
        parse_config(pretty_print_config(d)) == d

    The pretty printer must produce valid JSON that re-parses to the
    original dict.
    """
    parser = SpecParser()
    pretty = SpecParser.pretty_print_config(config)

    # The output must be valid JSON
    assert isinstance(pretty, str)
    reparsed = parser.parse_config(pretty)

    assert reparsed == config, (
        f"Round-trip failed:\n"
        f"  original: {config!r}\n"
        f"  pretty:   {pretty!r}\n"
        f"  reparsed: {reparsed!r}"
    )


@given(config=st_config_dict)
@settings(max_examples=100)
def test_parse_config_double_roundtrip(config):
    """
    **Validates: Requirements 18.4, 18.6**

    parse(pretty_print(parse(pretty_print(d)))) == d

    Applying the round-trip twice must produce the same result.
    """
    parser = SpecParser()
    once = parser.parse_config(SpecParser.pretty_print_config(config))
    twice = parser.parse_config(SpecParser.pretty_print_config(once))
    assert once == twice


# ---------------------------------------------------------------------------
# Property 2: parse_requirements round-trip (structural)
# ---------------------------------------------------------------------------

st_criterion_text = st.text(
    alphabet=string.ascii_letters + string.digits + " .,_-",
    min_size=5,
    max_size=100,
)

st_user_story = st.text(
    alphabet=string.ascii_letters + string.digits + " .,_-",
    min_size=5,
    max_size=120,
).filter(lambda s: s.strip() == s and len(s.strip()) > 0)

st_glossary = st.dictionaries(
    keys=st.text(alphabet=string.ascii_letters, min_size=2, max_size=20),
    values=st.text(
        alphabet=string.ascii_letters + string.digits + " .,_-",
        min_size=1,
        max_size=80,
    ).filter(lambda s: s.strip() == s and len(s.strip()) > 0),  # no leading/trailing whitespace
    min_size=0,
    max_size=5,
)


@given(
    introduction=st_safe_text,
    glossary=st_glossary,
    user_stories=st.lists(st_user_story, min_size=0, max_size=5),
)
@settings(max_examples=100)
def test_parse_requirements_roundtrip_structure(introduction, glossary, user_stories):
    """
    **Validates: Requirements 18.4, 18.6**

    For any valid requirements structure, pretty-printing and re-parsing
    must preserve:
    - The number of requirements
    - Requirement IDs (R1, R2, ...)
    - User stories
    - Glossary terms and definitions
    """
    from .models import AcceptanceCriterion, Requirement

    parser = SpecParser()

    requirements = [
        Requirement(
            id=f"R{i + 1}",
            user_story=story,
            acceptance_criteria=[
                AcceptanceCriterion(
                    id=f"AC{i + 1}",
                    description=f"WHEN something THEN system SHALL do thing {i + 1}",
                    testable=True,
                )
            ],
        )
        for i, story in enumerate(user_stories)
    ]

    pretty = SpecParser.pretty_print_requirements(introduction, glossary, requirements)

    assert isinstance(pretty, str)

    intro2, glossary2, reqs2 = parser.parse_requirements(pretty)

    # Introduction must be preserved
    assert intro2 == introduction, (
        f"Introduction mismatch:\n  original: {introduction!r}\n  reparsed: {intro2!r}"
    )

    # Glossary must be preserved
    assert glossary2 == glossary, (
        f"Glossary mismatch:\n  original: {glossary!r}\n  reparsed: {glossary2!r}"
    )

    # Number of requirements must be preserved
    assert len(reqs2) == len(requirements), (
        f"Requirement count mismatch: {len(requirements)} → {len(reqs2)}"
    )

    # Requirement IDs must be preserved
    assert [r.id for r in reqs2] == [r.id for r in requirements], (
        f"Requirement IDs mismatch: {[r.id for r in requirements]} → {[r.id for r in reqs2]}"
    )

    # User stories must be preserved
    assert [r.user_story for r in reqs2] == [r.user_story for r in requirements], (
        f"User stories mismatch"
    )


# ---------------------------------------------------------------------------
# Property 3: parse_config error handling
# ---------------------------------------------------------------------------

st_invalid_json = st.one_of(
    st.just(""),
    st.just("{invalid json}"),
    st.just("not json at all"),
    st.just("{key: value}"),  # missing quotes
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=20),
)


@given(invalid_input=st_invalid_json)
@settings(max_examples=50)
def test_parse_config_invalid_input_returns_empty(invalid_input):
    """
    **Validates: Requirements 18.7**

    When an invalid JSON string is provided, parse_config must return an
    empty dict (not raise an exception) and record the error.

    When valid JSON that is not a dict is provided (e.g., ``null``, ``[]``),
    parse_config returns whatever json.loads returns (may be None or list).
    The key requirement is that it never raises an exception.
    """
    parser = SpecParser()

    # Must never raise an exception
    try:
        result = parser.parse_config(invalid_input)
    except Exception as e:
        pytest.fail(
            f"parse_config({invalid_input!r}) raised {type(e).__name__}: {e}"
        )

    # If input is invalid JSON, result must be empty dict and errors recorded
    try:
        json.loads(invalid_input)
        # Valid JSON — no error expected, result may be any type
    except json.JSONDecodeError:
        # Invalid JSON — result must be empty dict
        assert result == {}, (
            f"parse_config({invalid_input!r}) returned {result!r}, expected {{}}"
        )
        assert len(parser.get_errors()) > 0, (
            f"parse_config({invalid_input!r}) did not record any errors"
        )


# ---------------------------------------------------------------------------
# Property 4: pretty_print_config always produces valid JSON
# ---------------------------------------------------------------------------

@given(config=st_config_dict)
@settings(max_examples=200)
def test_pretty_print_config_always_valid_json(config):
    """
    **Validates: Requirements 18.3, 18.6**

    pretty_print_config must always produce a string that is valid JSON.
    """
    pretty = SpecParser.pretty_print_config(config)
    assert isinstance(pretty, str)

    # Must be parseable as JSON without error
    try:
        parsed = json.loads(pretty)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"pretty_print_config({config!r}) produced invalid JSON: {e}\n"
            f"Output: {pretty!r}"
        )

    assert isinstance(parsed, dict)


# ---------------------------------------------------------------------------
# Property 5: pretty_print_requirements always produces valid Markdown
# ---------------------------------------------------------------------------

@given(
    introduction=st_safe_text,
    glossary=st_glossary,
)
@settings(max_examples=100)
def test_pretty_print_requirements_contains_required_sections(introduction, glossary):
    """
    **Validates: Requirements 18.3, 18.5**

    pretty_print_requirements must always produce a string containing the
    required Markdown section headers.
    """
    pretty = SpecParser.pretty_print_requirements(introduction, glossary, [])

    assert isinstance(pretty, str)
    assert "## Introduction" in pretty
    assert "## Glossary" in pretty
    assert "## Requirements" in pretty
