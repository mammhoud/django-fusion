"""Compatibility wrapper for django-fusion's populate_homepage command."""

from django_fusion.management.commands.populate_homepage import Command as FusionCommand


class Command(FusionCommand):
    """Expose the shared Fusion command through this site's models."""

    home_page_model = "apps.content.models.pages.home.HomePage"
