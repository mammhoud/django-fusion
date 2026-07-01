from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand

from ceptor_ai.customizer.bem import convert_paths


class Command(BaseCommand):
    help = "Convert template and style classes/IDs to strict BEM names."

    def add_arguments(self, parser):
        parser.add_argument("--root", default=".")
        parser.add_argument("--block", default="component")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        root = Path(options["root"]).resolve()
        patterns = ["**/assets/templates/**/*.html", "**/templates/**/*.html", "**/theme/**/*.scss", "**/assets/static/styles/**/*.scss"]
        paths = []
        for pattern in patterns:
            paths.extend(root.glob(pattern))
        mapping = convert_paths(paths, block=options["block"], write=not options["dry_run"])
        self.stdout.write(self.style.SUCCESS(f"Processed {len(paths)} files; mapped {len(mapping)} identifiers."))
