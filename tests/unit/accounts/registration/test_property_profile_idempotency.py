"""
Property-based tests for profile creation idempotency.

**Validates: Requirements 16.7**

Tests the `_ensure_profile_exists()` function from
`apps.accounts.registration.views`.

Property 6: Calling `_ensure_profile_exists(user)` twice for the same user
creates exactly one `Person` profile.

These tests configure Django minimally with an in-memory SQLite database
and a stub `Person` model that mirrors the real model's interface.
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


# django_fusion.comp.site — needs a PageHandler class
_ensure_mock("django_fusion")
_ensure_mock("django_fusion.comp")
_site_mod = _ensure_mock("django_fusion.comp.site")
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
# Build a minimal in-memory Person model for testing.
# The real Person lives in ceptor_ai.pipelines.models.users.users and
# requires Wagtail + many migrations.  We create a lightweight substitute
# that has the same interface (_ensure_profile_exists uses get_or_create
# with user= as the lookup key and the profile fields as defaults).
# ---------------------------------------------------------------------------
from django.contrib.auth import get_user_model  # noqa: E402
from django.db import models  # noqa: E402

User = get_user_model()


class PersonStub(models.Model):
    """Minimal Person model stub for testing profile creation."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="person_stub",
    )
    first_name = models.CharField(max_length=150, default="")
    last_name = models.CharField(max_length=150, default="")
    email = models.EmailField(default="")
    full_name = models.CharField(max_length=300, default="")
    status = models.CharField(max_length=50, default="")
    is_registered = models.BooleanField(default=False)
    registration_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "auth"  # piggyback on the auth app (already in INSTALLED_APPS)


# Create the PersonStub table in the in-memory database.
from django.db import connection  # noqa: E402

with connection.schema_editor() as schema_editor:
    try:
        schema_editor.create_model(PersonStub)
    except Exception:
        pass  # table may already exist if module is reloaded

# ---------------------------------------------------------------------------
# Patch ceptor_ai.pipelines.models.users.users so that _ensure_profile_exists
# imports PersonStub instead of the real Person model.
# ---------------------------------------------------------------------------
_ensure_mock("ceptor_ai.pipelines")
_ensure_mock("ceptor_ai.pipelines.models")
_ensure_mock("ceptor_ai.pipelines.models.users")
_users_mod = _ensure_mock("ceptor_ai.pipelines.models.users.users")
_users_mod.Person = PersonStub

# ---------------------------------------------------------------------------
# Now import the function under test.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import unittest  # noqa: E402

from hypothesis import given  # noqa: E402
from hypothesis import settings as h_settings
from hypothesis import strategies as st  # noqa: E402
from plugins.accounts.views import _ensure_profile_exists  # noqa: E402

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_ALPHA = "abcdefghijklmnopqrstuvwxyz"
_ALPHANUM = _ALPHA + "0123456789"

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

# ---------------------------------------------------------------------------
# Counter for unique usernames across hypothesis examples
# ---------------------------------------------------------------------------
_counter = [0]


def _unique_username(prefix: str, base: str) -> str:
    """Generate a unique username to avoid DB collisions across examples."""
    _counter[0] += 1
    return f"{prefix}_{base[:10]}_{_counter[0]}"[:150]


# ---------------------------------------------------------------------------
# Property 6: _ensure_profile_exists is idempotent
# ---------------------------------------------------------------------------


class TestProfileCreationIdempotency(unittest.TestCase):
    """
    **Property 6 — Validates: Requirements 16.7**

    Calling `_ensure_profile_exists(user)` twice for the same user must
    create exactly one `Person` profile (idempotent).
    """

    @given(
        local=email_local_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_calling_twice_creates_exactly_one_profile(
        self,
        local: str,
        first_name: str,
        last_name: str,
    ):
        """
        **Property 6 — Validates: Requirements 16.7**

        Calling `_ensure_profile_exists(user)` twice for the same user must
        result in exactly one `Person` profile in the database.

        This verifies that the `get_or_create` pattern prevents duplicate
        profiles even when the function is called multiple times.
        """
        unique_local = _unique_username("idm", local)
        email = f"{unique_local}@example.com"

        user = User.objects.create_user(
            username=unique_local,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        user.save()

        # Precondition: no profile exists yet
        self.assertEqual(
            PersonStub.objects.filter(user=user).count(),
            0,
            "Precondition: no profile should exist before calling _ensure_profile_exists",
        )

        # Call twice
        _ensure_profile_exists(user)
        _ensure_profile_exists(user)

        count = PersonStub.objects.filter(user=user).count()
        self.assertEqual(
            count,
            1,
            f"Expected exactly 1 Person profile after two calls to "
            f"_ensure_profile_exists(), but got {count}. "
            f"username={unique_local!r}",
        )

    @given(
        local=email_local_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_first_call_creates_profile_with_correct_fields(
        self,
        local: str,
        first_name: str,
        last_name: str,
    ):
        """
        **Property 6 — Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5**

        The profile created by `_ensure_profile_exists(user)` must have the
        correct field values: first_name, last_name, email, full_name,
        status="ACTIVE", is_registered=True.
        """
        unique_local = _unique_username("fld", local)
        email = f"{unique_local}@example.com"

        user = User.objects.create_user(
            username=unique_local,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        user.save()

        _ensure_profile_exists(user)

        profile = PersonStub.objects.filter(user=user).first()
        self.assertIsNotNone(profile, "Expected a profile to be created")

        self.assertEqual(profile.first_name, user.first_name)
        self.assertEqual(profile.last_name, user.last_name)
        self.assertEqual(profile.email, user.email)
        self.assertEqual(profile.full_name, user.get_full_name())
        self.assertEqual(profile.status, "ACTIVE")
        self.assertTrue(profile.is_registered)
        self.assertIsNotNone(profile.registration_date)
