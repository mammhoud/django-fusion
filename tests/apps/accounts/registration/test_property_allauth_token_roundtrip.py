# Feature: auth-allauth-enhancement, Property 8: Allauth-compatible token round-trip
"""
Property test: make_allauth_compatible_token + validate_token round-trip.
For any user PK and non-empty allauth_key, the token must decode back to
the same uid and allauth_key.
"""
from unittest.mock import MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from www.apps.accounts.registration.tokens import RegistrationTokenGenerator


def _make_mock_user(pk: int):
    user = MagicMock()
    user.pk = pk
    user.password = "hashed"
    user.is_active = True
    return user


@given(
    pk=st.integers(min_value=1, max_value=10**9),
    allauth_key=st.text(min_size=1, max_size=200),
)
@settings(max_examples=100)
def test_allauth_token_roundtrip(pk, allauth_key):
    gen = RegistrationTokenGenerator()
    user = _make_mock_user(pk)
    token = gen.make_allauth_compatible_token(user, allauth_key)
    result = gen.validate_token(token)
    assert result is not None
    assert not result.get("expired")
    assert result["uid"] == str(pk)
    assert result["allauth_key"] == allauth_key


@pytest.mark.parametrize("bad_key", ["", None])
def test_empty_allauth_key_raises(bad_key):
    gen = RegistrationTokenGenerator()
    user = _make_mock_user(1)
    with pytest.raises((ValueError, TypeError)):
        gen.make_allauth_compatible_token(user, bad_key)
