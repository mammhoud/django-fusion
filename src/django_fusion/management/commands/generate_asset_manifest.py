from __future__ import annotations

from argparse import ArgumentParser
from typing import Any, final

from django_fusion.management.commands.base import BaseCommand

from django_fusion.comp.manifest import (
    default_manifest_path,
    generate_asset_manifest,
    save_asset_manifest,
)


@final
class Command(BaseCommand):
    help: str = (
        "Generates a manifest of component usage in templates for loading assets"
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Path where the manifest file should be saved. Defaults to STATIC_ROOT/components/manifest.json",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        manifest_data = generate_asset_manifest()
        output_path = options["output"] or default_manifest_path()
        save_asset_manifest(manifest_data, output_path)
        self.stdout.write(
            self.style.SUCCESS(
                f"Asset manifest generated successfully at {output_path}"
            )
        )
