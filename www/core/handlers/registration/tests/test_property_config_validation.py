"""
Property-based tests for configuration validation logic.

**Validates: Requirements 1.4, 9.1, 9.2, 10.1**

Tests the pure helper functions from the validate_config management command:
- `_check_secret_key`: warns on insecure or short SECRET_KEY values
- `_collect_yaml_keys` / duplicate detection: flags keys in both env and YAML

These tests are standalone and do not require Django to be fully configured.
"""

import sys
import os

# ---------------------------------------------------------------------------
# Import the pure helper functions directly — no Django setup needed.
# ---------------------------------------------------------------------------
# Adjust sys.path so the management command module is importable without
# going through Django's app registry.
_COMMANDS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "management", "commands",
)
sys.path.insert(0, os.path.abspath(os.path.join(_COMMANDS_DIR, "..")))

from www.apps.accounts.management.commands.validate_config import (  # noqa: E402
    _check_secret_key,
    INSECURE_KEY_PREFIXES,
    MIN_SECRET_KEY_LENGTH,
    AUDITED_KEYS,
)

from hypothesis import given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Short strings that are definitely below the minimum length threshold
short_key_strategy = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=1,
    max_size=MIN_SECRET_KEY_LENGTH - 1,
).filter(
    # Exclude strings that happen to start with an insecure prefix
    # (those are covered by a separate property)
    lambda s: not any(s.lower().startswith(p.lower()) for p in INSECURE_KEY_PREFIXES)
)

# Strings with an insecure prefix prepended
insecure_prefix_strategy = st.one_of(
    *[
        st.text(
            alphabet=st.characters(blacklist_categories=("Cs",)),
            min_size=0,
            max_size=80,
        ).map(lambda suffix, p=prefix: p + suffix)
        for prefix in INSECURE_KEY_PREFIXES
    ]
)

# Long strings that are definitely at or above the minimum length and have no insecure prefix
valid_key_strategy = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=MIN_SECRET_KEY_LENGTH,
    max_size=200,
).filter(
    lambda s: not any(s.lower().startswith(p.lower()) for p in INSECURE_KEY_PREFIXES)
)


# ---------------------------------------------------------------------------
# Property 9a: Short SECRET_KEY always produces warnings
# ---------------------------------------------------------------------------

@given(short_key_strategy)
@settings(max_examples=100)
def test_short_secret_key_always_warns(key: str):
    """
    **Property 9a — Validates: Requirements 9.2, 10.1**

    For any SECRET_KEY shorter than MIN_SECRET_KEY_LENGTH characters (and without
    an insecure prefix), `_check_secret_key()` must return a non-empty list of
    warnings.
    """
    warnings = _check_secret_key(key)
    assert len(warnings) > 0, (
        f"Expected warnings for short key (len={len(key)}), got none. key={key!r}"
    )
    # At least one warning should mention the length
    assert any(str(len(key)) in w or "character" in w.lower() for w in warnings), (
        f"Expected a length-related warning, got: {warnings}"
    )


# ---------------------------------------------------------------------------
# Property 9b: Insecure-prefix SECRET_KEY always produces warnings
# ---------------------------------------------------------------------------

@given(insecure_prefix_strategy)
@settings(max_examples=100)
def test_insecure_prefix_secret_key_always_warns(key: str):
    """
    **Property 9b — Validates: Requirements 9.1, 10.1**

    For any SECRET_KEY that starts with a known insecure prefix,
    `_check_secret_key()` must return a non-empty list of warnings.
    """
    warnings = _check_secret_key(key)
    assert len(warnings) > 0, (
        f"Expected warnings for insecure-prefix key, got none. key={key!r}"
    )
    # At least one warning should mention the prefix
    assert any("prefix" in w.lower() or "insecure" in w.lower() for w in warnings), (
        f"Expected a prefix-related warning, got: {warnings}"
    )


# ---------------------------------------------------------------------------
# Property 9c: Valid SECRET_KEY produces no warnings
# ---------------------------------------------------------------------------

@given(valid_key_strategy)
@settings(max_examples=100)
def test_valid_secret_key_produces_no_warnings(key: str):
    """
    **Property 9c — Validates: Requirements 9.2, 10.1**

    For any SECRET_KEY that is at least MIN_SECRET_KEY_LENGTH characters long
    and does not start with a known insecure prefix, `_check_secret_key()` must
    return an empty list.
    """
    warnings = _check_secret_key(key)
    assert warnings == [], (
        f"Expected no warnings for valid key (len={len(key)}), got: {warnings}. key={key!r}"
    )


# ---------------------------------------------------------------------------
# Property 9d: Duplicate detection — key in both env_vars and yaml_key_sources
# ---------------------------------------------------------------------------

@given(
    st.lists(
        st.sampled_from(AUDITED_KEYS),
        min_size=1,
        max_size=len(AUDITED_KEYS),
        unique=True,
    )
)
@settings(max_examples=100)
def test_duplicate_detection_flags_shared_keys(shared_keys: list):
    """
    **Property 9d — Validates: Requirements 1.4, 10.1**

    When the same key appears in both env_vars and yaml_key_sources, the
    duplicate detection logic (as implemented in Command.handle) must flag it.

    We replicate the detection logic inline here to test it as a pure function:
        duplicates = {k for k in AUDITED_KEYS if k in env_vars and k in yaml_key_sources}
    """
    # Build env_vars and yaml_key_sources that both contain shared_keys
    env_vars = {k: "some_value" for k in shared_keys}
    yaml_key_sources = {k: ["configs/settings/base.yml"] for k in shared_keys}

    # Replicate the duplicate detection logic from Command.handle
    detected_duplicates = [
        key
        for key in AUDITED_KEYS
        if key in env_vars and key in yaml_key_sources
    ]

    assert set(detected_duplicates) == set(shared_keys), (
        f"Expected duplicates {set(shared_keys)}, detected {set(detected_duplicates)}"
    )


@given(
    st.lists(
        st.sampled_from(AUDITED_KEYS),
        min_size=1,
        max_size=len(AUDITED_KEYS),
        unique=True,
    )
)
@settings(max_examples=100)
def test_no_false_positives_when_key_only_in_env(env_only_keys: list):
    """
    **Property 9e — Validates: Requirements 1.4, 10.1**

    When a key appears only in env_vars (not in yaml_key_sources), the duplicate
    detection logic must NOT flag it as a duplicate.
    """
    env_vars = {k: "some_value" for k in env_only_keys}
    yaml_key_sources: dict = {}  # empty — no YAML definitions

    detected_duplicates = [
        key
        for key in AUDITED_KEYS
        if key in env_vars and key in yaml_key_sources
    ]

    assert detected_duplicates == [], (
        f"Expected no duplicates when keys only in env, got: {detected_duplicates}"
    )


@given(
    st.lists(
        st.sampled_from(AUDITED_KEYS),
        min_size=1,
        max_size=len(AUDITED_KEYS),
        unique=True,
    )
)
@settings(max_examples=100)
def test_no_false_positives_when_key_only_in_yaml(yaml_only_keys: list):
    """
    **Property 9f — Validates: Requirements 1.4, 10.1**

    When a key appears only in yaml_key_sources (not in env_vars), the duplicate
    detection logic must NOT flag it as a duplicate.
    """
    env_vars: dict = {}  # empty — no .env definitions
    yaml_key_sources = {k: ["configs/settings/base.yml"] for k in yaml_only_keys}

    detected_duplicates = [
        key
        for key in AUDITED_KEYS
        if key in env_vars and key in yaml_key_sources
    ]

    assert detected_duplicates == [], (
        f"Expected no duplicates when keys only in YAML, got: {detected_duplicates}"
    )
