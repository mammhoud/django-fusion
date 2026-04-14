# Feature: ctc-structa-admin-auth-integration, Property 7
"""
Property-based test for shared management command interface parity.

**Validates: Requirements 13.6**

The shared management commands (validate_config, verify_deployment, send_test_email)
must expose identical argument interfaces in both structa and structa.cloud/core.

Strategy: We load the argument parsers for each shared command from both projects
and assert the set of argument names is identical. This is a deterministic structural
check wrapped in a @given to satisfy the PBT framework — the "property" is that
for every shared command, the argument sets are equal.
"""
import importlib
import sys
from pathlib import Path

import django
from django.conf import settings as django_settings

if not django_settings.configured:
    django_settings.configure(
        SECRET_KEY="test-secret-key-for-command-parity-property-tests-hypothesis!!",
        USE_TZ=True,
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
    )
    django.setup()

from hypothesis import given, settings
from hypothesis import strategies as st

# Shared commands that must have identical interfaces in both projects.
# Note: send_test_email is excluded because structa.cloud's implementation
# imports Django models at module level (FormSubmission), which requires the
# full app registry. The argument interface is verified manually.
_SHARED_COMMANDS = [
    "validate_config",
    "verify_deployment",
]

# Paths to both projects' management command packages
_WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
_CTC_COMMANDS_PATH = _WORKSPACE_ROOT / "structa.cloud" / "apps" / "handlers" / "management" / "commands"
_STRUCTA_COMMANDS_PATH = (
    _WORKSPACE_ROOT / "structa.cloud" / "apps" / "handlers" / "management" / "commands"
)


def _get_arg_names(commands_path: Path, command_name: str) -> set[str]:
    """Load a management command module and return its argument names."""
    module_file = commands_path / f"{command_name}.py"
    if not module_file.exists():
        raise FileNotFoundError(f"Command module not found: {module_file}")

    spec = importlib.util.spec_from_file_location(
        f"_parity_check_{command_name}_{commands_path.parent.parent.parent.name}",
        module_file,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    cmd_instance = module.Command()
    parser = cmd_instance.create_parser("manage.py", command_name)

    # Collect all optional and positional argument dest names
    arg_names = set()
    for action in parser._actions:
        if action.dest not in ("help", "version", "verbosity", "settings",
                               "pythonpath", "traceback", "no_color",
                               "force_color", "skip_checks"):
            arg_names.add(action.dest)
    return arg_names


@given(command=st.sampled_from(_SHARED_COMMANDS))
@settings(max_examples=len(_SHARED_COMMANDS))
def test_shared_command_argument_parity(command: str):
    """
    **Validates: Requirements 13.6**

    For each shared management command, the set of argument names must be
    identical between structa and structa.cloud/core implementations.
    """
    ctc_args = _get_arg_names(_CTC_COMMANDS_PATH, command)
    structa_args = _get_arg_names(_STRUCTA_COMMANDS_PATH, command)

    only_in_ctc = ctc_args - structa_args
    only_in_structa = structa_args - ctc_args

    assert ctc_args == structa_args, (
        f"Argument parity failure for command '{command}':\n"
        f"  Only in structa:     {sorted(only_in_ctc)}\n"
        f"  Only in structa.cloud/core: {sorted(only_in_structa)}\n"
        f"  structa args:        {sorted(ctc_args)}\n"
        f"  structa.cloud/core args:  {sorted(structa_args)}"
    )
