"""Management command: load_fixtures — idempotent loaddata for fixture files."""
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Load one or more fixture files idempotently (skips IntegrityErrors)."

    def add_arguments(self, parser):
        parser.add_argument(
            "fixtures",
            nargs="+",
            help="Fixture file(s) to load",
        )

    def handle(self, *args, **options):
        for fixture in options["fixtures"]:
            self.stdout.write(f"Loading fixture: {fixture} ...")
            try:
                call_command("loaddata", fixture, verbosity=1)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {fixture} loaded"))
            except Exception as exc:
                self.stderr.write(self.style.WARNING(
                    f"  ⚠ {fixture} skipped: {exc}"
                ))
