"""Compatibility wrapper for django-fusion's send_bulk_emails command."""

from django_fusion.management.commands.send_bulk_emails import Command as FusionCommand


class Command(FusionCommand):
    """Expose the shared Fusion command through this site."""

    pass
