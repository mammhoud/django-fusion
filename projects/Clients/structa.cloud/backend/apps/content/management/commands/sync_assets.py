"""Django management command — sync asset manifest for frontend bundler integration.

Usage:
    python manage.py sync_assets

Generates a static/assets/manifest.json that mirrors the FUSION_ASSETS config,
making the frontend bundler aware of backend-managed fonts, preconnect hints,
and CSS/JS bundles. Run this before 'astro build' in CI.
"""

import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sync the FUSION_ASSETS config to a static manifest for the Astro frontend."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=None,
            help="Output path for manifest.json (default: STATIC_ROOT/components/manifest.json)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be written without touching the filesystem.",
        )

    def handle(self, **options):
        output = options["output"]
        dry_run = options["dry_run"]

        fusion_assets = getattr(settings, "FUSION_ASSETS", {}) or {}
        static_root = Path(settings.STATIC_ROOT) if hasattr(settings, "STATIC_ROOT") else Path("staticfiles")

        manifest = {
            "version": hex(hash(json.dumps(fusion_assets, sort_keys=True)) & 0xFFFFFFFF)[2:],
            "static_url": getattr(settings, "STATIC_URL", "/static/"),
            "top": fusion_assets.get("top", {}),
            "bottom": fusion_assets.get("bottom", {}),
            "fonts": fusion_assets.get("fonts", []),
            "preconnect": fusion_assets.get("preconnect", []),
        }

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run — would write:"))
            self.stdout.write(json.dumps(manifest, indent=2))
            return

        output_path = Path(output) if output else static_root / "components" / "manifest.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(
                f"Asset manifest written to {output_path} "
                f"(version={manifest['version']}, "
                f"fonts={len(manifest.get('fonts',[]))}, "
                f"preconnect={len(manifest.get('preconnect',[]))})"
            )
        )
