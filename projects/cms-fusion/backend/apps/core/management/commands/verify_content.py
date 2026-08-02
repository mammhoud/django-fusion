"""Compatibility wrapper for django-fusion's verify_content command."""

from django_fusion.management.commands.verify_content import Command as FusionCommand


class Command(FusionCommand):
    """Expose the shared Fusion command through this site."""

    pass
