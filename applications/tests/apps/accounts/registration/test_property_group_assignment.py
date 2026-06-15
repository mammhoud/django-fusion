"""
Property-based tests for group assignment.

**Validates: Requirements 6.5, 6.7**

Tests the `assign_default_group()` and `ensure_groups_exist()` functions
from `apps.accounts.registration.views`.

Property 7: For any user created via normal registration,
`user.groups.filter(name="Content Manager").exists()` is True after
`assign_default_group()`.

Specifically:
  7a. After calling `assign_default_group(user)`, the user belongs to
      the "Content Manager" group.
  7b. Calling `assign_default_group(user)` twice does not create duplicate
      group memberships (idempotent assignment).
  7c. `ensure_groups_exist()` creates both "Instructor" and "Content Manager"
      groups if they don't exist.
  7d. `ensure_groups_exist()` is idempotent — calling it multiple times
      doesn't create duplicate groups.

These tests configure Django minimally with an in-memory SQLite database.
The database tables are created once at module load time using Django's
test runner, and each test cleans up after itself.
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
from django.contrib.auth.models import Group  # noqa: E402
from hypothesis import given  # noqa: E402
from hypothesis import settings as h_settings
from hypothesis import strategies as st  # noqa: E402
from www.apps.accounts.registration.views import (  # noqa: E402
    assign_default_group,
    ensure_groups_exist,
)

User = get_user_model()

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
# Property 7a: assign_default_group assigns "Content Manager"
# ---------------------------------------------------------------------------

class TestAssignDefaultGroup(unittest.TestCase):
    """
    **Property 7a — Validates: Requirements 6.5, 6.7**

    After calling `assign_default_group(user)`, the user must belong to
    the "Content Manager" group.
    """

    @given(
        local=email_local_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_assign_default_group_adds_content_manager(
        self,
        local: str,
        first_name: str,
        last_name: str,
    ):
        """
        **Property 7a — Validates: Requirements 6.5, 6.7**

        For any user created via normal registration,
        `user.groups.filter(name="Content Manager").exists()` is True
        after `assign_default_group(user)` is called.
        """
        unique_local = _unique_username("a", local)
        email = f"{unique_local}@example.com"

        user = User.objects.create_user(
            username=unique_local,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )
        user.set_unusable_password()
        user.save()

        # Precondition: user has no groups
        self.assertFalse(
            user.groups.filter(name="Content Manager").exists(),
            "Precondition: user should not be in Content Manager group yet",
        )

        assign_default_group(user)

        self.assertTrue(
            user.groups.filter(name="Content Manager").exists(),
            f"Expected user to be in 'Content Manager' group after assign_default_group(). "
            f"username={unique_local!r}",
        )


# ---------------------------------------------------------------------------
# Property 7b: assign_default_group is idempotent (no duplicate memberships)
# ---------------------------------------------------------------------------

class TestAssignDefaultGroupIdempotent(unittest.TestCase):
    """
    **Property 7b — Validates: Requirements 6.5, 6.7**

    Calling `assign_default_group(user)` twice must not create duplicate
    group memberships. The user should belong to "Content Manager" exactly once.
    """

    @given(
        local=email_local_strategy,
        first_name=first_name_strategy,
        last_name=last_name_strategy,
    )
    @h_settings(max_examples=30, deadline=None)
    def test_assign_default_group_twice_no_duplicates(
        self,
        local: str,
        first_name: str,
        last_name: str,
    ):
        """
        **Property 7b — Validates: Requirements 6.5, 6.7**

        Calling `assign_default_group(user)` twice must not create duplicate
        group memberships. The count of "Content Manager" memberships must be 1.
        """
        unique_local = _unique_username("b", local)
        email = f"{unique_local}@example.com"

        user = User.objects.create_user(
            username=unique_local,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )
        user.set_unusable_password()
        user.save()

        assign_default_group(user)
        assign_default_group(user)

        count = user.groups.filter(name="Content Manager").count()
        self.assertEqual(
            count,
            1,
            f"Expected exactly 1 'Content Manager' membership after two calls, "
            f"but got {count}. username={unique_local!r}",
        )


# ---------------------------------------------------------------------------
# Property 7c: ensure_groups_exist creates both required groups
# ---------------------------------------------------------------------------

class TestEnsureGroupsExist(unittest.TestCase):
    """
    **Property 7c — Validates: Requirements 6.1, 6.2, 6.3**

    `ensure_groups_exist()` must create both "Instructor" and "Content Manager"
    groups if they don't already exist.
    """

    def setUp(self):
        """Remove the groups before each test to start from a clean state."""
        Group.objects.filter(name__in=["Instructor", "Content Manager"]).delete()

    def test_ensure_groups_exist_creates_instructor_group(self):
        """
        **Property 7c — Validates: Requirements 6.1, 6.3**

        `ensure_groups_exist()` must create the "Instructor" group if missing.
        """
        self.assertFalse(
            Group.objects.filter(name="Instructor").exists(),
            "Precondition: Instructor group should not exist",
        )

        ensure_groups_exist()

        self.assertTrue(
            Group.objects.filter(name="Instructor").exists(),
            "Expected 'Instructor' group to exist after ensure_groups_exist()",
        )

    def test_ensure_groups_exist_creates_content_manager_group(self):
        """
        **Property 7c — Validates: Requirements 6.2, 6.3**

        `ensure_groups_exist()` must create the "Content Manager" group if missing.
        """
        self.assertFalse(
            Group.objects.filter(name="Content Manager").exists(),
            "Precondition: Content Manager group should not exist",
        )

        ensure_groups_exist()

        self.assertTrue(
            Group.objects.filter(name="Content Manager").exists(),
            "Expected 'Content Manager' group to exist after ensure_groups_exist()",
        )


# ---------------------------------------------------------------------------
# Property 7d: ensure_groups_exist is idempotent
# ---------------------------------------------------------------------------

class TestEnsureGroupsExistIdempotent(unittest.TestCase):
    """
    **Property 7d — Validates: Requirements 6.3, 6.8**

    Calling `ensure_groups_exist()` multiple times must not create duplicate
    groups. Each group must exist exactly once.
    """

    def setUp(self):
        """Remove the groups before each test to start from a clean state."""
        Group.objects.filter(name__in=["Instructor", "Content Manager"]).delete()

    def test_ensure_groups_exist_idempotent_instructor(self):
        """
        **Property 7d — Validates: Requirements 6.3, 6.8**

        Calling `ensure_groups_exist()` multiple times must not create
        duplicate "Instructor" groups.
        """
        ensure_groups_exist()
        ensure_groups_exist()
        ensure_groups_exist()

        count = Group.objects.filter(name="Instructor").count()
        self.assertEqual(
            count,
            1,
            f"Expected exactly 1 'Instructor' group after multiple calls, but got {count}",
        )

    def test_ensure_groups_exist_idempotent_content_manager(self):
        """
        **Property 7d — Validates: Requirements 6.3, 6.8**

        Calling `ensure_groups_exist()` multiple times must not create
        duplicate "Content Manager" groups.
        """
        ensure_groups_exist()
        ensure_groups_exist()
        ensure_groups_exist()

        count = Group.objects.filter(name="Content Manager").count()
        self.assertEqual(
            count,
            1,
            f"Expected exactly 1 'Content Manager' group after multiple calls, but got {count}",
        )
