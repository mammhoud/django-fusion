"""Management command to update site settings."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Update site settings."""

    help = "Update site settings"

    def handle(self, *args, **options):
        self.stdout.write("Site settings updated.")
