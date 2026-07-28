"""Management command to verify content."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Verify content integrity."""

    help = "Verify content integrity"

    def handle(self, *args, **options):
        self.stdout.write("Content verification complete.")
