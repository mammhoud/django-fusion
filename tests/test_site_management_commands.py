"""Regression tests for reusable Fusion site management commands."""

from django.core.management.base import BaseCommand

# Commands that ship with django-fusion. Product seeders such as
# ``populate_courses`` / ``populate_content`` / ``populate_homepage`` were
# relocated to the consuming projects: they encode a site's page and model
# vocabulary, which is customization, not framework behavior.
LIBRARY_COMMANDS = (
    "analyze_components_to_webpack",
    "generate_asset_manifest",
    "generate_skeleton_manifest",
    "send_bulk_emails",
    "sync_task_history",
    "verify_content",
    "webpack_validate",
)


def test_shared_commands_are_importable_and_have_command_classes():

    for name in LIBRARY_COMMANDS:
        module = __import__(
            f"django_fusion.management.commands.{name}", fromlist=["Command"]
        )
        assert issubclass(module.Command, BaseCommand), name
        assert module.Command.help, name


def test_relocated_product_commands_are_not_shipped_in_the_library():
    """The library must stay product-agnostic.

    A regression here means a site-specific seeder was reintroduced into the
    base package instead of living in the consuming project.
    """
    import importlib

    for name in ("populate_courses", "populate_content", "populate_homepage"):
        try:
            importlib.import_module(f"django_fusion.management.commands.{name}")
        except ModuleNotFoundError:
            continue
        raise AssertionError(
            f"{name} is product-specific and must not ship in django-fusion"
        )
