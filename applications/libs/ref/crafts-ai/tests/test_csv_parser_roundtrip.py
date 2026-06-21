"""
Round-trip property tests for CSVParser.

**Validates: Requirements 18.4, 18.6, 18.7**

Grammar under test
------------------
CSVParser parses CSV files with the following format::

    email,role
    user@example.com,instructor/manager
    other@example.com,content_manager

- ``email``: a valid email address (required, non-empty)
- ``role``: one or more role names separated by ``/`` or ``,``
  (optional; roles are normalised to lowercase with spaces replaced by ``_``)

Round-trip property
-------------------
For any valid list of EmailRecord objects ``records``:

    parse(pretty_print(records)) == records

That is, serialising a list of EmailRecord objects back to CSV and
re-parsing must produce an equivalent list.

Note: CSVParser has no Django dependencies, so it can be tested here
in the pure-Python nawaai test suite.
"""

import importlib.util
import os
import tempfile

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Mark all tests as nondestructive (required by pytest-selenium plugin)
pytestmark = pytest.mark.nondestructive

# ---------------------------------------------------------------------------
# Import csv_parser without triggering Django setup (the __init__.py imports
# Django-dependent services, so we load the module directly).
# ---------------------------------------------------------------------------
_CSV_PARSER_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",  # crafts_ai
    "..",  # nawaai root
    "..",  # libs
    "django-rseal",
    "src",
    "django_rseal",
    "services",
    "csv_parser.py",
)
_spec = importlib.util.spec_from_file_location("csv_parser", _CSV_PARSER_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

CSVParser = _mod.CSVParser
EmailRecord = _mod.EmailRecord


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid email local parts: letters, digits, dots, hyphens, underscores, plus
_email_local = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789._+-",
    min_size=1,
    max_size=20,
).filter(lambda s: not s.startswith(".") and not s.endswith(".") and ".." not in s)

# Valid domain labels
_domain_label = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
    min_size=1,
    max_size=15,
).filter(lambda s: not s.startswith("-") and not s.endswith("-"))

# Valid TLDs
_tld = st.sampled_from(["com", "org", "net", "edu", "io", "co"])

# Valid email strategy
st_email = st.builds(
    lambda local, domain, tld: f"{local}@{domain}.{tld}",
    local=_email_local,
    domain=_domain_label,
    tld=_tld,
)

# Valid role name: lowercase letters, digits, underscores
st_role = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
    min_size=1,
    max_size=20,
).filter(lambda s: s and not s.startswith("_") and not s.endswith("_"))

# List of roles (1–4 roles per record)
st_roles = st.lists(st_role, min_size=1, max_size=4)

# EmailRecord strategy
st_email_record = st.builds(EmailRecord, email=st_email, roles=st_roles)

# List of EmailRecord objects (0–20 records)
st_email_records = st.lists(st_email_record, min_size=0, max_size=20)


# ---------------------------------------------------------------------------
# Helper: parse CSV text via CSVParser
# ---------------------------------------------------------------------------

def _parse_csv_text(csv_text: str):
    """Write csv_text to a temp file and parse it."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        f.write(csv_text)
        tmp_path = f.name
    try:
        parser = CSVParser(tmp_path)
        return parser.parse()
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Property 1: round-trip — parse(pretty_print(records)) == records
# ---------------------------------------------------------------------------

@given(records=st_email_records)
@settings(max_examples=200)
def test_csv_parser_roundtrip(records):
    """
    **Validates: Requirements 18.4, 18.6**

    For any valid list of EmailRecord objects:
        parse(pretty_print(records)) == records

    The pretty printer must produce valid CSV that re-parses to the
    original list of records.
    """
    csv_text = CSVParser.pretty_print(records)
    assert isinstance(csv_text, str)

    result = _parse_csv_text(csv_text)

    assert len(result) == len(records), (
        f"Record count mismatch: {len(records)} → {len(result)}"
    )

    for i, (original, reparsed) in enumerate(zip(records, result)):
        assert reparsed.email == original.email, (
            f"Record {i}: email mismatch {original.email!r} → {reparsed.email!r}"
        )
        assert reparsed.roles == original.roles, (
            f"Record {i}: roles mismatch {original.roles!r} → {reparsed.roles!r}"
        )


# ---------------------------------------------------------------------------
# Property 2: double round-trip
# ---------------------------------------------------------------------------

@given(records=st_email_records)
@settings(max_examples=100)
def test_csv_parser_double_roundtrip(records):
    """
    **Validates: Requirements 18.4, 18.6**

    Applying the round-trip twice must produce the same result.
    """
    once = _parse_csv_text(CSVParser.pretty_print(records))
    twice = _parse_csv_text(CSVParser.pretty_print(once))

    assert [(r.email, r.roles) for r in once] == [(r.email, r.roles) for r in twice]


# ---------------------------------------------------------------------------
# Property 3: pretty_print always produces valid CSV with header
# ---------------------------------------------------------------------------

@given(records=st_email_records)
@settings(max_examples=100)
def test_pretty_print_always_produces_valid_csv(records):
    """
    **Validates: Requirements 18.3, 18.6**

    pretty_print must always produce a string starting with the CSV header.
    """
    csv_text = CSVParser.pretty_print(records)
    assert isinstance(csv_text, str)
    assert csv_text.startswith("email,role"), (
        f"CSV output does not start with header: {csv_text[:50]!r}"
    )


# ---------------------------------------------------------------------------
# Property 4: parse raises FileNotFoundError for missing files
# ---------------------------------------------------------------------------

def test_parse_raises_file_not_found_for_missing_file():
    """
    **Validates: Requirements 18.7**

    CSVParser.parse() must raise FileNotFoundError with a descriptive
    message when the CSV file does not exist.
    """
    parser = CSVParser("/nonexistent/path/emails.csv")
    with pytest.raises(FileNotFoundError) as exc_info:
        parser.parse()

    assert "CSV file not found" in str(exc_info.value), (
        f"Error message not descriptive: {exc_info.value!r}"
    )


# ---------------------------------------------------------------------------
# Property 5: empty records list produces only header
# ---------------------------------------------------------------------------

def test_pretty_print_empty_records():
    """
    **Validates: Requirements 18.3**

    pretty_print([]) must produce a CSV with only the header row.
    """
    csv_text = CSVParser.pretty_print([])
    lines = csv_text.strip().splitlines()
    assert len(lines) == 1
    assert lines[0] == "email,role"


# ---------------------------------------------------------------------------
# Property 6: roles with multiple values are preserved
# ---------------------------------------------------------------------------

@given(
    email=st_email,
    roles=st.lists(st_role, min_size=2, max_size=5),
)
@settings(max_examples=100)
def test_multiple_roles_preserved_in_roundtrip(email, roles):
    """
    **Validates: Requirements 18.4, 18.6**

    Records with multiple roles must have all roles preserved through
    the round-trip.
    """
    record = EmailRecord(email=email, roles=roles)
    csv_text = CSVParser.pretty_print([record])
    result = _parse_csv_text(csv_text)

    assert len(result) == 1
    assert result[0].email == email
    assert result[0].roles == roles
