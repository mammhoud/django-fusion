"""
Property-based tests for password complexity validation.

**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

Tests `PasswordCreationForm` from `apps.accounts.registration.forms`.

Property 4: For any password string missing any one of the five complexity
requirements, `PasswordCreationForm` is invalid.

The five requirements are:
  - At least 8 characters long
  - At least 1 uppercase letter (A-Z)
  - At least 1 lowercase letter (a-z)
  - At least 1 digit (0-9)
  - At least 1 special character (!@#$%^&*()_+-=[]{}; etc.)

Sub-properties:
  4a. Any password shorter than 8 characters is rejected.
  4b. Any password with no uppercase letter is rejected.
  4c. Any password with no lowercase letter is rejected.
  4d. Any password with no digit is rejected.
  4e. Any password with no special character is rejected.
"""

# ---------------------------------------------------------------------------
# Minimal Django setup — must happen before any django.* import
# ---------------------------------------------------------------------------
import sys

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        },
        SECRET_KEY="test-secret-key-for-property-tests-at-least-50-chars-long!!",
        USE_TZ=True,
        AUTH_PASSWORD_VALIDATORS=[],  # disable Django's built-in validators
    )
    django.setup()

# ---------------------------------------------------------------------------
# Import the form under test
# ---------------------------------------------------------------------------
# Remove any mock of apps.accounts.registration.forms that may have been
# injected by other test modules (e.g. test_property_group_assignment.py)
# so that we always import the real module here.
sys.modules.pop("apps.accounts.registration.forms", None)

from www.apps.registration.forms import PasswordCreationForm  # noqa: E402

from hypothesis import given, settings as h_settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

# ---------------------------------------------------------------------------
# Character sets
# ---------------------------------------------------------------------------

UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
SPECIAL = "!@#$%^&*()_+-=[]{};\\':\"|,.<>/?"

# A "complete" character pool that satisfies all rules
FULL_POOL = UPPERCASE + LOWERCASE + DIGITS + SPECIAL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _form_is_valid(password: str) -> bool:
    """Return True if PasswordCreationForm accepts the given password."""
    form = PasswordCreationForm(
        data={"password": password, "password_confirm": password}
    )
    return form.is_valid()


def _build_password(chars: str, length: int) -> str:
    """Build a password of the given length by cycling through chars."""
    if not chars:
        return "x" * length
    result = []
    for i in range(length):
        result.append(chars[i % len(chars)])
    return "".join(result)


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Passwords that are too short (1–7 chars) but otherwise contain all char types
# We build them from the full pool so the only failing rule is length.
short_password_strategy = st.integers(min_value=1, max_value=7).map(
    lambda n: _build_password(UPPERCASE + LOWERCASE + DIGITS + SPECIAL, n)
)

# Passwords >= 8 chars with no uppercase: only lowercase + digits + special
no_uppercase_strategy = st.text(
    alphabet=LOWERCASE + DIGITS + SPECIAL,
    min_size=8,
    max_size=64,
).filter(lambda p: any(c in DIGITS for c in p) and any(c in SPECIAL for c in p))

# Passwords >= 8 chars with no lowercase: only uppercase + digits + special
no_lowercase_strategy = st.text(
    alphabet=UPPERCASE + DIGITS + SPECIAL,
    min_size=8,
    max_size=64,
).filter(lambda p: any(c in DIGITS for c in p) and any(c in SPECIAL for c in p))

# Passwords >= 8 chars with no digit: only uppercase + lowercase + special
no_digit_strategy = st.text(
    alphabet=UPPERCASE + LOWERCASE + SPECIAL,
    min_size=8,
    max_size=64,
).filter(lambda p: any(c in UPPERCASE for c in p) and any(c in LOWERCASE for c in p))

# Passwords >= 8 chars with no special char: only uppercase + lowercase + digits
no_special_strategy = st.text(
    alphabet=UPPERCASE + LOWERCASE + DIGITS,
    min_size=8,
    max_size=64,
).filter(lambda p: any(c in UPPERCASE for c in p) and any(c in LOWERCASE for c in p) and any(c in DIGITS for c in p))


# ---------------------------------------------------------------------------
# Property 4a: Passwords shorter than 8 characters are always rejected
# ---------------------------------------------------------------------------


@given(short_password_strategy)
@h_settings(max_examples=200)
def test_password_too_short_is_rejected(password: str):
    """
    **Property 4a — Validates: Requirements 12.1**

    Any password shorter than 8 characters must be rejected by
    PasswordCreationForm, regardless of which other character types it contains.
    """
    assert len(password) < 8, f"Strategy produced password of length {len(password)}"
    assert not _form_is_valid(password), (
        f"Expected password {password!r} (length {len(password)}) to be "
        f"rejected due to insufficient length, but the form accepted it."
    )


# ---------------------------------------------------------------------------
# Property 4b: Passwords with no uppercase letter are always rejected
# ---------------------------------------------------------------------------


@given(no_uppercase_strategy)
@h_settings(max_examples=200)
def test_password_no_uppercase_is_rejected(password: str):
    """
    **Property 4b — Validates: Requirements 12.2**

    Any password of sufficient length that contains no uppercase letter must
    be rejected by PasswordCreationForm.
    """
    assert len(password) >= 8
    assert not any(c in UPPERCASE for c in password), (
        f"Strategy produced password with uppercase: {password!r}"
    )
    assert not _form_is_valid(password), (
        f"Expected password {password!r} (no uppercase) to be rejected, "
        f"but the form accepted it."
    )


# ---------------------------------------------------------------------------
# Property 4c: Passwords with no lowercase letter are always rejected
# ---------------------------------------------------------------------------


@given(no_lowercase_strategy)
@h_settings(max_examples=200)
def test_password_no_lowercase_is_rejected(password: str):
    """
    **Property 4c — Validates: Requirements 12.3**

    Any password of sufficient length that contains no lowercase letter must
    be rejected by PasswordCreationForm.
    """
    assert len(password) >= 8
    assert not any(c in LOWERCASE for c in password), (
        f"Strategy produced password with lowercase: {password!r}"
    )
    assert not _form_is_valid(password), (
        f"Expected password {password!r} (no lowercase) to be rejected, "
        f"but the form accepted it."
    )


# ---------------------------------------------------------------------------
# Property 4d: Passwords with no digit are always rejected
# ---------------------------------------------------------------------------


@given(no_digit_strategy)
@h_settings(max_examples=200)
def test_password_no_digit_is_rejected(password: str):
    """
    **Property 4d — Validates: Requirements 12.4**

    Any password of sufficient length that contains no digit must be rejected
    by PasswordCreationForm.
    """
    assert len(password) >= 8
    assert not any(c in DIGITS for c in password), (
        f"Strategy produced password with digit: {password!r}"
    )
    assert not _form_is_valid(password), (
        f"Expected password {password!r} (no digit) to be rejected, "
        f"but the form accepted it."
    )


# ---------------------------------------------------------------------------
# Property 4e: Passwords with no special character are always rejected
# ---------------------------------------------------------------------------


@given(no_special_strategy)
@h_settings(max_examples=200)
def test_password_no_special_char_is_rejected(password: str):
    """
    **Property 4e — Validates: Requirements 12.5**

    Any password of sufficient length that contains no special character must
    be rejected by PasswordCreationForm.
    """
    assert len(password) >= 8
    assert not any(c in SPECIAL for c in password), (
        f"Strategy produced password with special char: {password!r}"
    )
    assert not _form_is_valid(password), (
        f"Expected password {password!r} (no special char) to be rejected, "
        f"but the form accepted it."
    )
