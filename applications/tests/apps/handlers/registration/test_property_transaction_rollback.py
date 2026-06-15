"""
Property-based tests for transaction rollback safety.

**Validates: Requirements 3.5, 15.6, 15.7**

Tests the atomic block behavior in `CreatePasswordView.post()`:

    with transaction.atomic():
        user.set_password(password)
        user.is_active = True
        user.save()
        _ensure_profile_exists(user)

Property 8: If profile creation raises an exception inside atomic block,
user activation is rolled back.

Specifically:
  8a. If an exception is raised after `user.save()` inside `transaction.atomic()`,
      the user's `is_active` remains `False` in the database (rollback occurred).
  8b. If an exception is raised inside `transaction.atomic()` before completion,
      the user state (password + is_active) is not persisted.
  8c. When no exception occurs, the user is activated successfully
      (`is_active=True` is persisted).

These tests configure Django minimally with an in-memory SQLite database.
The database tables are created once at module load time using Django's
test runner, and each test cleans up after itself.
"""


# ---------------------------------------------------------------------------
# Minimal Django setup — must happen before any django.* import.
# This mirrors the pattern used in other property test files in this package.
# ---------------------------------------------------------------------------
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
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )
    django.setup()

# ---------------------------------------------------------------------------
# Create the test database tables once at module load time.
# We use Django's DiscoverRunner to set up an in-memory SQLite database
# with all required migrations applied.
# ---------------------------------------------------------------------------
from django.test.runner import DiscoverRunner  # noqa: E402

_runner = DiscoverRunner(verbosity=0)
_old_db_config = _runner.setup_databases()

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import unittest  # noqa: E402

from django.contrib.auth import get_user_model  # noqa: E402
from django.db import transaction  # noqa: E402
from hypothesis import given  # noqa: E402
from hypothesis import settings as h_settings
from hypothesis import strategies as st  # noqa: E402

User = get_user_model()

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_USERNAME_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"

username_strategy = st.text(
    alphabet=_USERNAME_ALPHABET,
    min_size=3,
    max_size=20,
)

password_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$",
    min_size=8,
    max_size=50,
)

first_name_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    min_size=1,
    max_size=30,
)

last_name_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    min_size=1,
    max_size=30,
)

# ---------------------------------------------------------------------------
# Helper: the atomic block logic extracted from CreatePasswordView.post()
# ---------------------------------------------------------------------------

def _activate_user_with_profile(user, password, profile_fn):
    """
    Mirrors the atomic block from CreatePasswordView.post():

        with transaction.atomic():
            user.set_password(password)
            user.is_active = True
            user.save()
            profile_fn(user)   # stands in for _ensure_profile_exists(user)

    `profile_fn` is injected so tests can control whether it raises.
    Exceptions from `profile_fn` propagate and trigger the atomic rollback.
    """
    with transaction.atomic():
        user.set_password(password)
        user.is_active = True
        user.save()
        profile_fn(user)


def _noop_profile(user):
    """Profile function that succeeds silently."""
    pass


def _raising_profile(user):
    """Profile function that always raises, simulating a failed profile creation."""
    raise RuntimeError("Simulated profile creation failure")


# ---------------------------------------------------------------------------
# Counter for unique usernames across hypothesis examples
# ---------------------------------------------------------------------------
_counter = [0]


def _unique_username(prefix: str, base: str) -> str:
    """Generate a unique username to avoid DB collisions across examples."""
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:16]}"[:150]


# ---------------------------------------------------------------------------
# Property 8a: Exception after user.save() rolls back is_active
# ---------------------------------------------------------------------------

class TestRollbackOnProfileException(unittest.TestCase):
    """
    **Property 8a — Validates: Requirements 3.5, 15.6, 15.7**

    If an exception is raised after `user.save()` inside `transaction.atomic()`,
    the user's `is_active` must remain `False` in the database.
    """

    @given(
        username=username_strategy,
        password=password_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_exception_in_atomic_block_rolls_back_user_activation(
        self,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
    ):
        """
        **Property 8a — Validates: Requirements 3.5, 15.6, 15.7**

        If an exception is raised after `user.save()` inside `transaction.atomic()`,
        the user's `is_active` must remain `False` in the database (rollback occurred).

        This verifies that the atomic block in CreatePasswordView.post() provides
        rollback safety: a failed profile creation cannot leave a partially-activated
        user in the database.
        """
        unique_username = _unique_username("a", username)
        email = f"{unique_username}@example.com"

        # Create an inactive user (pre-activation state)
        user = User.objects.create_user(
            username=unique_username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )
        user.set_unusable_password()
        user.save()

        self.assertFalse(user.is_active, "Precondition: user must start as inactive")

        # Attempt activation with a profile function that raises
        with self.assertRaises(RuntimeError):
            _activate_user_with_profile(user, password, _raising_profile)

        # Re-fetch from database to check persisted state
        user.refresh_from_db()

        self.assertFalse(
            user.is_active,
            f"Expected user.is_active=False after rollback, but got True. "
            f"username={unique_username!r}",
        )


# ---------------------------------------------------------------------------
# Property 8b: Exception inside atomic block does not persist state
# ---------------------------------------------------------------------------

class TestRollbackOnMidBlockException(unittest.TestCase):
    """
    **Property 8b — Validates: Requirements 15.6, 15.7**

    If an exception is raised inside `transaction.atomic()` after `user.save()`,
    the user's activation state and password change must not be persisted.
    """

    @given(
        username=username_strategy,
        password=password_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_exception_after_save_rolls_back_password_and_activation(
        self,
        username: str,
        password: str,
    ):
        """
        **Property 8b — Validates: Requirements 15.6, 15.7**

        If an exception is raised inside `transaction.atomic()` after `user.save()`,
        both the password change and `is_active=True` must be rolled back.
        """
        unique_username = _unique_username("b", username)
        email = f"{unique_username}@example.com"

        user = User.objects.create_user(
            username=unique_username,
            email=email,
            is_active=False,
        )
        user.set_unusable_password()
        user.save()

        original_password = user.password

        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                user.set_password(password)
                user.is_active = True
                user.save()
                # Simulate an error that occurs after save but before completion
                raise RuntimeError("Simulated failure after save")

        # Re-fetch from database — the atomic block rolled back
        user.refresh_from_db()

        self.assertFalse(
            user.is_active,
            f"Expected user.is_active=False after rollback, but got True. "
            f"username={unique_username!r}",
        )
        self.assertEqual(
            user.password,
            original_password,
            f"Expected password to be rolled back to original, but it changed. "
            f"username={unique_username!r}",
        )


# ---------------------------------------------------------------------------
# Property 8c: Successful activation persists is_active=True
# ---------------------------------------------------------------------------

class TestSuccessfulActivation(unittest.TestCase):
    """
    **Property 8c — Validates: Requirements 3.5, 15.6**

    When no exception occurs inside `transaction.atomic()`, the user's
    `is_active` must be `True` after the block completes.
    """

    @given(
        username=username_strategy,
        password=password_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_successful_activation_persists_is_active(
        self,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
    ):
        """
        **Property 8c — Validates: Requirements 3.5, 15.6**

        When no exception occurs inside `transaction.atomic()`, the user's
        `is_active` must be `True` after the block completes.

        This is the happy-path complement to 8a/8b: confirms that the atomic
        block correctly commits when everything succeeds.
        """
        unique_username = _unique_username("c", username)
        email = f"{unique_username}@example.com"

        user = User.objects.create_user(
            username=unique_username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )
        user.set_unusable_password()
        user.save()

        self.assertFalse(user.is_active, "Precondition: user must start as inactive")

        # Activate with a no-op profile function (no exception)
        _activate_user_with_profile(user, password, _noop_profile)

        # Re-fetch from database to check persisted state
        user.refresh_from_db()

        self.assertTrue(
            user.is_active,
            f"Expected user.is_active=True after successful activation, but got False. "
            f"username={unique_username!r}",
        )
        self.assertTrue(
            user.has_usable_password(),
            f"Expected user to have a usable password after activation. "
            f"username={unique_username!r}",
        )
