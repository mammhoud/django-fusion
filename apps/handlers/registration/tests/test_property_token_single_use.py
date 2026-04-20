"""
Property-based tests for token single-use invalidation in RegistrationTokenGenerator.

**Validates: Requirements 20.5, 20.6**

Tests the `check_token()` method from
`apps.accounts.registration.tokens`.

Property 1b: After `user.is_active = True` and password set,
`check_token()` returns False for the same token.

Specifically:
  1. A token generated for an inactive user (is_active=False, unusable
     password) is valid via `check_token()`.
  2. After simulating password set + activation (is_active=True, new
     password hash), `check_token()` returns False for the same token.
  3. The state hash changes when `is_active` changes from False to True.
  4. The state hash changes when the password changes.

The key mechanism: `_make_hash()` includes `user.pk`, `user.password`,
and `user.is_active`. When these change, the hash in the token no longer
matches the current user state, so `check_token()` returns False.
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

from hypothesis import given, settings as h_settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from www.apps.accounts.registration.tokens import RegistrationTokenGenerator  # noqa: E402

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
# Property 1: Token is valid for inactive user before activation
# ---------------------------------------------------------------------------


@given(pk_strategy, password_hash_strategy)
@h_settings(max_examples=100)
def test_token_valid_for_inactive_user(pk: int, password: str):
    """
    **Property 1b (part 1) — Validates: Requirements 20.5, 20.6**

    A token generated for an inactive user (is_active=False, unusable
    password) must be accepted by `check_token()` when the user state
    has not changed.
    """
    generator = RegistrationTokenGenerator()
    user = _make_fake_user(pk, password, is_active=False)

    token = generator.make_token(user)

    assert generator.check_token(user, token) is True, (
        f"check_token() should return True for a fresh token on an inactive "
        f"user (pk={pk}), but returned False."
    )


# ---------------------------------------------------------------------------
# Property 2: Token is invalid after activation (is_active=True)
# ---------------------------------------------------------------------------


@given(pk_strategy, password_hash_strategy, password_hash_strategy)
@h_settings(max_examples=100)
def test_token_invalid_after_activation(
    pk: int, initial_password: str, new_password: str
):
    """
    **Property 1b (part 2) — Validates: Requirements 20.5, 20.6**

    After simulating password set + activation (is_active=True, new
    password hash), `check_token()` must return False for the same token
    that was valid before activation.

    This confirms the single-use property: once a user activates their
    account, the original token cannot be replayed.
    """
    generator = RegistrationTokenGenerator()

    # Create token for inactive user with initial (unusable) password
    user_before = _make_fake_user(pk, initial_password, is_active=False)
    token = generator.make_token(user_before)

    # Simulate activation: set a real password and mark user active
    user_after = _make_fake_user(pk, new_password, is_active=True)

    assert generator.check_token(user_after, token) is False, (
        f"check_token() should return False after activation "
        f"(pk={pk}), but returned True. Token replay is possible!"
    )


# ---------------------------------------------------------------------------
# Property 3: State hash changes when is_active changes
# ---------------------------------------------------------------------------


@given(pk_strategy, password_hash_strategy)
@h_settings(max_examples=100)
def test_hash_changes_when_is_active_changes(pk: int, password: str):
    """
    **Property 1b (part 3) — Validates: Requirements 20.5, 20.6**

    The state hash produced by `_make_hash()` must differ between an
    inactive user (is_active=False) and an active user (is_active=True)
    with the same pk and password.

    This guarantees that activating a user always invalidates existing tokens.
    """
    generator = RegistrationTokenGenerator()

    user_inactive = _make_fake_user(pk, password, is_active=False)
    user_active = _make_fake_user(pk, password, is_active=True)

    hash_inactive = generator._make_hash(user_inactive)
    hash_active = generator._make_hash(user_active)

    assert hash_inactive != hash_active, (
        f"_make_hash() returned the same hash for is_active=False and "
        f"is_active=True (pk={pk}, password={password!r}). "
        "Changing is_active must change the hash."
    )


# ---------------------------------------------------------------------------
# Property 4: State hash changes when password changes
# ---------------------------------------------------------------------------


@given(pk_strategy, password_hash_strategy, password_hash_strategy)
@h_settings(max_examples=100)
def test_hash_changes_when_password_changes(
    pk: int, password_a: str, password_b: str
):
    """
    **Property 1b (part 4) — Validates: Requirements 20.5, 20.6**

    The state hash produced by `_make_hash()` must differ when the
    password changes, for any fixed pk and is_active value.

    This guarantees that setting a new password always invalidates
    existing tokens, even if is_active remains the same.
    """
    # Only meaningful when the two passwords are actually different
    if password_a == password_b:
        return

    generator = RegistrationTokenGenerator()

    user_a = _make_fake_user(pk, password_a, is_active=False)
    user_b = _make_fake_user(pk, password_b, is_active=False)

    hash_a = generator._make_hash(user_a)
    hash_b = generator._make_hash(user_b)

    assert hash_a != hash_b, (
        f"_make_hash() returned the same hash for two different passwords "
        f"(pk={pk}, password_a={password_a!r}, password_b={password_b!r}). "
        "Changing the password must change the hash."
    )
