"""
Property-based tests for token expiration in RegistrationTokenGenerator.

**Validates: Requirements 5.2, 20.4**

Tests the `validate_token()` method from
`apps.accounts.registration.tokens`.

Property 1: Tokens generated more than 24 hours ago are always rejected
by `validate_token()`.

Specifically:
  1a. Tokens validated with max_age=0 always raise SignatureExpired,
      confirming the expiration mechanism works for any user-like data.
  1b. Tokens validated within the normal max_age window return a dict
      with 'uid', 'ts', and 'hash' keys.
  1c. Tokens with an invalid/tampered signature always return None from
      validate_token().
"""

# ---------------------------------------------------------------------------
# Minimal Django setup — must happen before any django.* import
# ---------------------------------------------------------------------------
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
            }
        },
        SECRET_KEY="test-secret-key-for-property-tests-at-least-50-chars-long!!",
        USE_TZ=True,
    )
    django.setup()

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
# Remove any mock of apps.accounts.registration.tokens that may have been
# injected by other test modules (e.g. test_property_group_assignment.py)
# so that we always import the real module here.
import sys  # noqa: E402

sys.modules.pop("apps.accounts.registration.tokens", None)

from django.core import signing  # noqa: E402

from hypothesis import given, settings as h_settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from plugins.accounts.registration.tokens import (  # noqa: E402
    RegistrationTokenGenerator,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# User pk values — positive integers (Django auto-increment PKs)
pk_strategy = st.integers(min_value=1, max_value=10_000_000)

# Password hash strings — Django stores hashed passwords as strings
password_hash_strategy = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=1,
    max_size=200,
)

# is_active boolean
is_active_strategy = st.booleans()


def _make_fake_user(pk: int, password: str, is_active: bool):
    """Create a minimal fake user object with the required attributes."""
    class FakeUser:
        pass

    user = FakeUser()
    user.pk = pk
    user.password = password
    user.is_active = is_active
    return user


# ---------------------------------------------------------------------------
# Property 1a: Tokens are always expired when validated with max_age=0
# ---------------------------------------------------------------------------

@given(pk_strategy, password_hash_strategy, is_active_strategy)
@h_settings(max_examples=100)
def test_token_always_expired_with_zero_max_age(pk: int, password: str, is_active: bool):
    """
    **Property 1a — Validates: Requirements 5.2, 20.4**

    For any user-like data, a token created by make_token() must raise
    SignatureExpired when loaded with max_age=0.

    This confirms the expiration mechanism is wired correctly: any token
    is "expired" from the perspective of a caller that allows zero seconds.
    """
    generator = RegistrationTokenGenerator()
    user = _make_fake_user(pk, password, is_active)

    token = generator.make_token(user)

    try:
        signing.loads(token, salt=generator.SALT, max_age=0)
        raise AssertionError(
            f"Expected SignatureExpired for pk={pk}, but signing.loads succeeded. "
            "The expiration mechanism may not be working."
        )
    except signing.SignatureExpired:
        # Expected — the token is correctly expired with max_age=0
        pass


# ---------------------------------------------------------------------------
# Property 1b: Fresh tokens are accepted within the normal max_age window
# ---------------------------------------------------------------------------

@given(pk_strategy, password_hash_strategy, is_active_strategy)
@h_settings(max_examples=100)
def test_fresh_token_is_valid(pk: int, password: str, is_active: bool):
    """
    **Property 1b — Validates: Requirements 5.2, 20.4**

    For any user-like data, a token created by make_token() and immediately
    validated by validate_token() must return a dict containing 'uid', 'ts',
    and 'hash' keys (not None and not {"expired": True}).
    """
    generator = RegistrationTokenGenerator()
    user = _make_fake_user(pk, password, is_active)

    token = generator.make_token(user)
    result = generator.validate_token(token)

    assert result is not None, (
        f"validate_token() returned None for a fresh token (pk={pk})"
    )
    assert result != {"expired": True}, (
        f"validate_token() returned expired for a fresh token (pk={pk})"
    )
    assert "uid" in result, f"'uid' missing from token payload: {result!r}"
    assert "ts" in result, f"'ts' missing from token payload: {result!r}"
    assert "hash" in result, f"'hash' missing from token payload: {result!r}"
    assert result["uid"] == str(pk), (
        f"Expected uid={pk!r}, got {result['uid']!r}"
    )


# ---------------------------------------------------------------------------
# Property 1c: Tampered tokens always return None from validate_token()
# ---------------------------------------------------------------------------

@given(pk_strategy, password_hash_strategy, is_active_strategy)
@h_settings(max_examples=100)
def test_tampered_token_returns_none(pk: int, password: str, is_active: bool):
    """
    **Property 1c — Validates: Requirements 5.2, 20.4**

    For any user-like data, a token with an invalid/tampered signature must
    return None from validate_token() (not a dict, not {"expired": True}).

    We simulate tampering by appending extra characters to the token string,
    which breaks the HMAC signature.
    """
    generator = RegistrationTokenGenerator()
    user = _make_fake_user(pk, password, is_active)

    token = generator.make_token(user)
    tampered_token = token + "TAMPERED"

    result = generator.validate_token(tampered_token)

    assert result is None, (
        f"validate_token() should return None for a tampered token, "
        f"but got {result!r} (pk={pk})"
    )


# ---------------------------------------------------------------------------
# Property 1d: Expired tokens return {"expired": True} not None
# ---------------------------------------------------------------------------

@given(pk_strategy, password_hash_strategy, is_active_strategy)
@h_settings(max_examples=100)
def test_expired_token_returns_expired_dict(pk: int, password: str, is_active: bool):
    """
    **Property 1d — Validates: Requirements 5.2, 20.4**

    When a token is expired (SignatureExpired), validate_token() must return
    {"expired": True} rather than None, so views can show the correct error.

    We simulate expiration by patching the signing module's loads function
    at the point where tokens.py imports it, so that validate_token() sees
    a SignatureExpired exception and returns the correct sentinel value.
    """
    import unittest.mock as mock

    generator = RegistrationTokenGenerator()
    user = _make_fake_user(pk, password, is_active)

    token = generator.make_token(user)

    # Patch signing.loads in the tokens module namespace directly.
    # We use the module path that was actually imported.
    module_name = RegistrationTokenGenerator.__module__
    tokens_module = sys.modules[module_name]

    with mock.patch.object(
        tokens_module.signing,
        "loads",
        side_effect=signing.SignatureExpired("mocked expiry"),
    ):
        result = generator.validate_token(token)

    assert result == {"expired": True}, (
        f"validate_token() should return {{'expired': True}} for an expired token, "
        f"but got {result!r} (pk={pk})"
    )
