"""Send invite emails from emails.csv — canonical implementation.

This is a legacy location for the ``send_invites`` command.  Django resolves
the command from ``apps.core`` (registered first), so this module re-exports
the canonical implementation to keep both paths working and consistent.
"""

from apps.core.management.commands.send_invites import Command  # noqa: F401
