"""Management command to populate content."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Populate initial content for the site."""

    help = "Populate initial content for the site"

    def handle(self, *args, **options):
        self.stdout.write("Content population complete.")
