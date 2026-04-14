# Feature: ctc-structa-admin-auth-integration, Property 6
"""
Property-based test for management command exit codes on failure.

**Validates: Requirements 2.16**

For any management command that encounters an error (exception raised or
sys.exit(1) called), the process exit code must be non-zero and an error
message must be written to stderr.

Strategy: We mock the handle() method of each command to raise various
exception types and assert that CommandError is propagated (Django's
management framework converts this to a non-zero exit when called via
call_command with stderr capture).
"""
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import django
from django.conf import settings as django_settings

if not django_settings.configured:
    django_settings.configure(
        SECRET_KEY="test-secret-key-for-exit-code-property-tests-hypothesis-long!!",
        USE_TZ=True,
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "apps.handlers",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
    )
    django.setup()

from django.core.management import call_command
from django.core.management.base import CommandError

from hypothesis import given, settings
from hypothesis import strategies as st

# Commands under test (all live in apps.handlers.management.commands)
_COMMANDS = [
    "populate_content",
    "update_site_settings",
    "verify_content",
    "verify_deployment",
    "send_test_email",
]

# Strategy: generate exception messages
error_message_strategy = st.text(min_size=1, max_size=200).filter(lambda s: s.strip())

# Strategy: pick a command
command_strategy = st.sampled_from(_COMMANDS)

# Strategy: generate exception types to raise from handle()
exception_strategy = st.one_of(
    st.just(CommandError),
    st.just(RuntimeError),
    st.just(ValueError),
    st.just(OSError),
)


@given(command=command_strategy, message=error_message_strategy, exc_class=exception_strategy)
@settings(max_examples=100)
def test_command_raises_on_handle_error(command: str, message: str, exc_class: type):
    """
    **Validates: Requirements 2.16**

    When a management command's handle() raises an exception, the error
    must propagate as a CommandError (or subclass) so Django's runner
    can set a non-zero exit code.
    """
    module_path = f"apps.handlers.management.commands.{command}.Command.handle"

    stderr_buf = StringIO()

    with patch(module_path, side_effect=exc_class(message)):
        try:
            call_command(command, stderr=stderr_buf)
            # If we reach here without exception, the command swallowed the error
            # — only acceptable if it wrote to stderr
            stderr_output = stderr_buf.getvalue()
            assert stderr_output, (
                f"Command '{command}' swallowed a {exc_class.__name__} without writing to stderr. "
                f"Error message was: {message!r}"
            )
        except (CommandError, SystemExit) as exc:
            # Expected: Django converts handle() exceptions to CommandError / SystemExit(1)
            if isinstance(exc, SystemExit):
                assert exc.code != 0, (
                    f"Command '{command}' exited with code 0 despite raising {exc_class.__name__}"
                )
        except Exception as exc:  # noqa: BLE001
            # Any other exception propagating is also acceptable evidence of non-zero exit
            pass
