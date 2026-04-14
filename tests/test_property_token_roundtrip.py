# Feature: ctc-structa-admin-auth-integration, Property 1
"""
Property-based test for allauth-compatible token round-trip.

**Validates: Requirements 8.9, 9.7**

For any Django user and any non-empty allauth_key string, calling
make_allauth_compatible_token(user, allauth_key) followed by validate_token(token)
must return a dict where uid == str(user.pk) and allauth_key equals the original key.
"""
import django
from django.conf import settings as django_settings

# Configure minimal Django settings before importing anything that needs them
if not django_settings.configured:
    django_settings.configure(
        SECRET_KEY="test-secret-key-for-property-tests-hypothesis-roundtrip",
        USE_TZ=True,
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
    )
    django.setup()

from unittest.mock import MagicMock

from hypothesis import given, settings
from hypothesis import strategies as st

from apps.handlers.registration.tokens import RegistrationTokenGenerator


@given(st.integers(min_value=1), st.text(min_size=1))
@settings(max_examples=100)
def test_token_roundtrip(user_pk: int, allauth_key: str):
    """
    **Validates: Requirements 8.9, 9.7**

    For any user PK (positive integer) and any non-empty allauth_key string,
    the token round-trip must preserve both uid and allauth_key exactly.
    """
    user = MagicMock()
    user.pk = user_pk
    user.password = "hashed-password"
    user.is_active = True

    generator = RegistrationTokenGenerator()
    token = generator.make_allauth_compatible_token(user, allauth_key)
    result = generator.validate_token(token)

    assert result is not None, "validate_token returned None for a freshly generated token"
    assert not result.get("expired"), "validate_token returned expired for a freshly generated token"
    assert result["uid"] == str(user_pk), (
        f"uid mismatch: expected '{user_pk}', got '{result['uid']}'"
    )
    assert result["allauth_key"] == allauth_key, (
        f"allauth_key mismatch: expected '{allauth_key!r}', got '{result['allauth_key']!r}'"
    )
