"""
Property-based tests for profile creation failure isolation.

**Validates: Requirements 16.6**

Tests the `_ensure_profile_exists()` function from
`apps.accounts.registration.views`.

Property 6b: When `Person.objects.create()` raises an exception,
`_ensure_profile_exists()` logs a warning and does not re-raise.

Specifically:
  6b-i.  When the Person model raises any exception during get_or_create,
         `_ensure_profile_exists()` must NOT propagate the exception.
  6b-ii. When the Person model raises an exception, a warning must be logged
         (verified via assertLogs).

These tests configure Django minimally with an in-memory SQLite database.
"""

# ---------------------------------------------------------------------------
# Minimal Django setup — must happen before any django.* import.
# ---------------------------------------------------------------------------
import sys
import types

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
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )
    django.setup()

# ---------------------------------------------------------------------------
# Mock the heavy import chain so views.py can be imported without Wagtail.
# ---------------------------------------------------------------------------


def _ensure_mock(name: str) -> types.ModuleType:
    """Return an existing sys.modules entry or create a new mock module."""
    if name not in sys.modules:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
    return sys.modules[name]


# django_osoul.comp.site — needs a PageHandler class
_ensure_mock("django_grep")
_ensure_mock("django_osoul.comp")
_site_mod = _ensure_mock("django_osoul.comp.site")
if not hasattr(_site_mod, "PageHandler"):

    class _PageHandler:
        def dispatch(self, request, *args, **kwargs):
            pass

    _site_mod.PageHandler = _PageHandler

# registration sub-modules
_emails_mod = _ensure_mock("apps.accounts.registration.emails")
if not hasattr(_emails_mod, "send_registration_email"):
    _emails_mod.send_registration_email = lambda *a, **kw: True

_forms_mod = _ensure_mock("apps.accounts.registration.forms")
if not hasattr(_forms_mod, "RegistrationForm"):
    _forms_mod.RegistrationForm = type("RegistrationForm", (), {})
if not hasattr(_forms_mod, "PasswordCreationForm"):
    _forms_mod.PasswordCreationForm = type("PasswordCreationForm", (), {})

_tokens_mod = _ensure_mock("apps.accounts.registration.tokens")
if not hasattr(_tokens_mod, "registration_token_generator"):
    _tokens_mod.registration_token_generator = object()

# ---------------------------------------------------------------------------
# Create the test database tables once at module load time.
# ---------------------------------------------------------------------------
from django.test.runner import DiscoverRunner  # noqa: E402

_runner = DiscoverRunner(verbosity=0)
_old_db_config = _runner.setup_databases()

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import unittest  # noqa: E402

from django.contrib.auth import get_user_model  # noqa: E402

from hypothesis import given, settings as h_settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

User = get_user_model()

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_ALPHANUM = "abcdefghijklmnopqrstuvwxyz0123456789"

email_local_strategy = st.text(alphabet=_ALPHANUM, min_size=3, max_size=20)

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

# Exception types to test — covers the common failure modes
exception_strategy = st.sampled_from([
    RuntimeError("DB connection lost"),
    Exception("Unexpected error"),
    ValueError("Invalid field value"),
    OSError("I/O error"),
])

# ---------------------------------------------------------------------------
# Counter for unique usernames across hypothesis examples
# ---------------------------------------------------------------------------
_counter = [0]


def _unique_username(prefix: str, base: str) -> str:
    """Generate a unique username to avoid DB collisions across examples."""
    _counter[0] += 1
    return f"{prefix}_{base[:10]}_{_counter[0]}"[:150]


# ---------------------------------------------------------------------------
# Property 6b-i: _ensure_profile_exists does not re-raise on exception
# ---------------------------------------------------------------------------


class TestProfileCreationFailureIsolation(unittest.TestCase):
    """
    **Property 6b — Validates: Requirements 16.6**

    When `Person.objects.get_or_create()` raises an exception,
    `_ensure_profile_exists()` must catch it and NOT re-raise.
    """

    @given(
        local=email_local_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
        exc=exception_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_exception_in_person_create_does_not_propagate(
        self,
        local: str,
        first_name: str,
        last_name: str,
        exc: Exception,
    ):
        """
        **Property 6b-i — Validates: Requirements 16.6**

        When `Person.objects.get_or_create()` raises any exception,
        `_ensure_profile_exists()` must swallow it and return normally.

        This ensures that a failed profile creation never breaks the
        registration flow — the user is still activated even if the
        Person profile cannot be created.
        """
        unique_local = _unique_username("iso", local)
        email = f"{unique_local}@example.com"

        user = User.objects.create_user(
            username=unique_local,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        user.save()

        # Build a Person stub whose get_or_create always raises
        class _RaisingManager:
            def get_or_create(self, **kwargs):
                raise exc
            def filter(self, **kwargs):
                class _QS:
                    def exists(self):
                        raise exc
                return _QS()

        class _RaisingPerson:
            objects = _RaisingManager()

        # Patch the Person import inside _ensure_profile_exists
        _users_mod = _ensure_mock("django_rseal.pipelines.models.users.users")
        original_person = getattr(_users_mod, "Person", None)
        _users_mod.Person = _RaisingPerson

        try:
            # Must NOT raise — exception must be caught internally
            try:
                from plugins.accounts.registration import views as _views
                # Reload the Person reference inside the function by patching
                # the module-level import cache
                _ensure_profile_exists_fn = _views._ensure_profile_exists
                _ensure_profile_exists_fn(user)
            except Exception as raised:
                self.fail(
                    f"_ensure_profile_exists() raised {type(raised).__name__}: {raised} "
                    f"but it should have caught the exception silently. "
                    f"username={unique_local!r}"
                )
        finally:
            # Restore original Person
            if original_person is not None:
                _users_mod.Person = original_person
            elif hasattr(_users_mod, "Person"):
                del _users_mod.Person

    @given(
        local=email_local_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
        exc=exception_strategy,
    )
    @h_settings(max_examples=20, deadline=None)
    def test_exception_in_person_create_logs_warning(
        self,
        local: str,
        first_name: str,
        last_name: str,
        exc: Exception,
    ):
        """
        **Property 6b-ii — Validates: Requirements 16.6**

        When `Person.objects.get_or_create()` raises an exception,
        `_ensure_profile_exists()` must log a WARNING (not silently ignore it).

        This ensures failures are observable in production logs.
        """
        unique_local = _unique_username("log", local)
        email = f"{unique_local}@example.com"

        user = User.objects.create_user(
            username=unique_local,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        user.save()

        # Build a Person stub whose get_or_create always raises
        class _RaisingManager:
            def get_or_create(self, **kwargs):
                raise exc
            def filter(self, **kwargs):
                class _QS:
                    def exists(self):
                        raise exc
                return _QS()

        class _RaisingPerson:
            objects = _RaisingManager()

        _users_mod = _ensure_mock("django_rseal.pipelines.models.users.users")
        original_person = getattr(_users_mod, "Person", None)
        _users_mod.Person = _RaisingPerson

        try:
            # assertLogs verifies that at least one WARNING is emitted
            with self.assertLogs("apps.registration", level="WARNING") as log_ctx:
                from plugins.accounts.registration import views as _views
                _views._ensure_profile_exists(user)

            # Confirm the log contains a warning (not just any level)
            warning_records = [
                r for r in log_ctx.records if r.levelname == "WARNING"
            ]
            self.assertGreater(
                len(warning_records),
                0,
                f"Expected at least one WARNING log entry when profile creation fails. "
                f"username={unique_local!r}",
            )
        finally:
            if original_person is not None:
                _users_mod.Person = original_person
            elif hasattr(_users_mod, "Person"):
                del _users_mod.Person
